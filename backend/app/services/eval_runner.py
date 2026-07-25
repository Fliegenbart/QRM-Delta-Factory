from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.schemas.domain import EvidenceSupport, FindingStatus, RiskFinding, Severity
from app.schemas.evals import (
    EvalDataset,
    EvalFixture,
    EvalMetrics,
    EvalReport,
    GoldFinding,
)
from app.schemas.risk import RiskDecision

RUNNER_VERSION = "eval-runner-v0.1"
DEFAULT_FIXTURE_DIR = Path("examples/evals")


class EvalFixtureNotFoundError(Exception):
    pass


class EvalRunner:
    def __init__(self, *, fixture_dir: Path | None = None) -> None:
        self.fixture_dir = fixture_dir or Path(get_settings().eval_fixture_dir)

    def list_datasets(self) -> list[EvalFixture]:
        fixtures = [
            self.load_fixture(path)
            for path in sorted(self.fixture_dir.glob("*.json"))
        ]
        return fixtures

    def load_fixture(self, path: Path) -> EvalFixture:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return EvalFixture.model_validate(payload)

    def run_fixture(self, dataset_id: str) -> EvalReport:
        fixture = self._fixture_by_dataset_id(dataset_id)
        return self.evaluate(
            dataset=fixture.dataset,
            system_findings=fixture.system_findings,
            risk_decision=fixture.risk_decision,
        )

    def evaluate(
        self,
        *,
        dataset: EvalDataset,
        system_findings: Sequence[RiskFinding | dict[str, object]],
        risk_decision: RiskDecision,
    ) -> EvalReport:
        findings = [RiskFinding.model_validate(finding) for finding in system_findings]
        matches = _match_findings(dataset.gold_findings, findings)
        matched_gold_ids = [gold.gold_finding_id for gold, _finding in matches]
        unmatched_gold = [
            gold
            for gold in dataset.gold_findings
            if gold.gold_finding_id not in set(matched_gold_ids)
        ]
        matched_finding_ids = {finding.finding_id for _gold, finding in matches}
        duplicate_finding_ids = _duplicate_finding_ids(
            gold_findings=dataset.gold_findings,
            findings=findings,
            matches=matches,
        )
        false_positive_findings = [
            finding
            for finding in findings
            if finding.finding_id not in matched_finding_ids
            and finding.finding_id not in duplicate_finding_ids
        ]
        metrics = _metrics(
            dataset=dataset,
            findings=findings,
            matches=matches,
            unmatched_gold=unmatched_gold,
            false_positive_findings=false_positive_findings,
            duplicate_finding_ids=duplicate_finding_ids,
            risk_decision=risk_decision,
        )
        failures = _failures(
            dataset=dataset,
            unmatched_gold=unmatched_gold,
            risk_decision=risk_decision,
        )
        passed = not failures
        report_without_markdown = EvalReport(
            dataset=dataset,
            metrics=metrics,
            passed=passed,
            failures=failures,
            matched_gold_finding_ids=matched_gold_ids,
            unmatched_gold_finding_ids=[
                gold.gold_finding_id for gold in unmatched_gold
            ],
            false_positive_finding_ids=[
                finding.finding_id for finding in false_positive_findings
            ],
            markdown_report="pending",
            generated_at=datetime.now(UTC),
            runner_version=RUNNER_VERSION,
        )
        markdown = self.render_markdown(report_without_markdown)
        return report_without_markdown.model_copy(update={"markdown_report": markdown})

    def render_markdown(self, report: EvalReport) -> str:
        status = "PASS" if report.passed else "FAIL"
        lines = [
            f"# Eval Report: {report.dataset.name}",
            "",
            "## Pass/Fail",
            f"Status: {status}",
            "",
            "## Dataset",
            f"- ID: `{report.dataset.dataset_id}`",
            f"- Version: `{report.dataset.version}`",
            f"- Document type: `{report.dataset.document_type}`",
            f"- Process area: `{report.dataset.process_area}`",
            "",
            "## Metrics",
        ]
        metrics_payload = report.metrics.model_dump(mode="json")
        for key, value in metrics_payload.items():
            lines.append(f"- {key}: `{value}`")
        lines.extend(["", "## Failures"])
        if report.failures:
            lines.extend(f"- {failure}" for failure in report.failures)
        else:
            lines.append("- None")
        lines.extend(
            [
                "",
                "## Matched Gold Findings",
                *(f"- `{item}`" for item in report.matched_gold_finding_ids),
                "",
                "## Unmatched Gold Findings",
                *(f"- `{item}`" for item in report.unmatched_gold_finding_ids),
            ]
        )
        return "\n".join(lines)

    def _fixture_by_dataset_id(self, dataset_id: str) -> EvalFixture:
        for fixture in self.list_datasets():
            if fixture.dataset.dataset_id == dataset_id:
                return fixture
        raise EvalFixtureNotFoundError(f"Eval dataset {dataset_id} not found")


def _match_findings(
    gold_findings: Sequence[GoldFinding],
    findings: Sequence[RiskFinding],
) -> list[tuple[GoldFinding, RiskFinding]]:
    matches: list[tuple[GoldFinding, RiskFinding]] = []
    used_finding_ids: set[str] = set()
    for gold in gold_findings:
        best_match = next(
            (
                finding
                for finding in findings
                if finding.finding_id not in used_finding_ids
                and _finding_matches_gold(finding, gold)
            ),
            None,
        )
        if best_match is not None:
            used_finding_ids.add(best_match.finding_id)
            matches.append((gold, best_match))
    return matches


def _finding_matches_gold(finding: RiskFinding, gold: GoldFinding) -> bool:
    if finding.risk_category != gold.expected_risk_category:
        return False
    if gold.expected_requirement_ids and not set(
        gold.expected_requirement_ids
    ).intersection(finding.requirement_references):
        return False
    # Category plus requirement id alone is far too loose to mean "detected": a
    # case yields ~20 findings spread over a handful of categories, so an
    # unrelated finding lands on the right category by chance. When the gold
    # finding names the evidence it must be grounded in, require the finding to
    # actually cite it.
    if not gold.expected_evidence_refs:
        return True
    return any(
        _evidence_item_matches_ref(evidence_item, ref)
        for ref in gold.expected_evidence_refs
        for evidence_item in finding.evidence_items
    )


def _evidence_item_matches_ref(evidence_item: Any, ref: Any) -> bool:
    """Accept a citation that points at the expected source and quotes it.

    Chunk ids are an ingestion detail and shift when chunking changes, so a
    matching document plus an overlapping quote is enough. The quote comparison
    is containment in either direction: a finding may cite a longer span than
    the gold reference names, or vice versa.
    """
    if evidence_item.document_id != ref.document_id:
        return False
    quote = _normalize_quote(evidence_item.quote)
    expected = _normalize_quote(ref.quote)
    if not quote or not expected:
        return False
    return expected in quote or quote in expected


def _normalize_quote(value: str) -> str:
    return " ".join(value.lower().split())


def _metrics(
    *,
    dataset: EvalDataset,
    findings: Sequence[RiskFinding],
    matches: Sequence[tuple[GoldFinding, RiskFinding]],
    unmatched_gold: Sequence[GoldFinding],
    false_positive_findings: Sequence[RiskFinding],
    duplicate_finding_ids: set[str],
    risk_decision: RiskDecision,
) -> EvalMetrics:
    must_detect_gold = [gold for gold in dataset.gold_findings if gold.must_detect]
    missed_must_detect = [gold for gold in unmatched_gold if gold.must_detect]
    recall_by_severity = _recall_by_severity(dataset.gold_findings, matches)
    false_omission_rate = _safe_ratio(len(missed_must_detect), len(must_detect_gold))
    false_positive_rate = _safe_ratio(len(false_positive_findings), len(findings))
    citation_precision = _citation_precision(dataset.gold_findings, findings)
    requirement_match_accuracy = _requirement_match_accuracy(matches)
    auto_clear_false_negative_count = _auto_clear_false_negative_count(
        dataset=dataset,
        risk_decision=risk_decision,
    )
    human_review_rate = 0.0 if risk_decision.auto_clear_allowed else 1.0
    must_detect_recall = _must_detect_recall(dataset.gold_findings, matches)
    severity_metrics = _severity_metrics(matches)
    unsupported_findings = [
        finding
        for finding in findings
        if finding.evidence_support != EvidenceSupport.STRONG
        and finding.status != FindingStatus.REJECTED
    ]
    unsupported_high_critical = [
        finding
        for finding in unsupported_findings
        if finding.severity in {Severity.HIGH, Severity.CRITICAL}
    ]
    boundary_violations = [
        finding
        for finding in false_positive_findings
        if _violates_false_positive_boundary(
            finding, dataset.acceptable_false_positive_boundaries
        )
    ]
    return EvalMetrics(
        recall_by_severity=recall_by_severity,
        false_omission_rate=false_omission_rate,
        false_positive_rate=false_positive_rate,
        citation_precision=citation_precision,
        requirement_match_accuracy=requirement_match_accuracy,
        auto_clear_false_negative_count=auto_clear_false_negative_count,
        human_review_rate=human_review_rate,
        must_detect_recall=must_detect_recall,
        duplicate_finding_count=len(duplicate_finding_ids),
        duplicate_finding_rate=_safe_ratio(
            len(duplicate_finding_ids), len(matches)
        ),
        unsupported_finding_rate=_safe_ratio(len(unsupported_findings), len(findings)),
        unsupported_high_critical_published_count=len(unsupported_high_critical),
        false_positive_boundary_violation_count=len(boundary_violations),
        **severity_metrics,
    )


def _recall_by_severity(
    gold_findings: Sequence[GoldFinding],
    matches: Sequence[tuple[GoldFinding, RiskFinding]],
) -> dict[str, float]:
    matched_ids = {gold.gold_finding_id for gold, _finding in matches}
    recall: dict[str, float] = {}
    for severity in Severity:
        gold_at_severity = [
            gold
            for gold in gold_findings
            if gold.must_detect and gold.expected_severity == severity
        ]
        if not gold_at_severity:
            continue
        detected = [
            gold for gold in gold_at_severity if gold.gold_finding_id in matched_ids
        ]
        recall[str(severity)] = _safe_ratio(len(detected), len(gold_at_severity))
    return recall


def _citation_precision(
    gold_findings: Sequence[GoldFinding],
    findings: Sequence[RiskFinding],
) -> float:
    evidence_items = [
        evidence for finding in findings for evidence in finding.evidence_items
    ]
    if not evidence_items:
        return 1.0 if not any(gold.expected_evidence_refs for gold in gold_findings) else 0.0
    expected_refs = [
        expected
        for gold in gold_findings
        for expected in gold.expected_evidence_refs
    ]
    matching_citations = [
        evidence
        for evidence in evidence_items
        if any(
            _evidence_matches_expected(evidence.model_dump(), expected.model_dump())
            for expected in expected_refs
        )
    ]
    return _safe_ratio(len(matching_citations), len(evidence_items))


def _requirement_match_accuracy(
    matches: Sequence[tuple[GoldFinding, RiskFinding]],
) -> float:
    if not matches:
        return 1.0
    correct = [
        gold
        for gold, finding in matches
        if set(gold.expected_requirement_ids).issubset(set(finding.requirement_references))
    ]
    return _safe_ratio(len(correct), len(matches))


def _auto_clear_false_negative_count(
    *,
    dataset: EvalDataset,
    risk_decision: RiskDecision,
) -> int:
    if not risk_decision.auto_clear_allowed:
        return 0
    return len(
        [
            gold
            for gold in dataset.gold_findings
            if gold.should_block_auto_clear
            or (
                gold.must_detect
                and gold.expected_severity in {Severity.HIGH, Severity.CRITICAL}
            )
        ]
    )


def _failures(
    *,
    dataset: EvalDataset,
    unmatched_gold: Sequence[GoldFinding],
    risk_decision: RiskDecision,
) -> list[str]:
    failures: list[str] = []
    for gold in unmatched_gold:
        if gold.must_detect and gold.expected_severity == Severity.CRITICAL:
            failures.append(f"Critical must_detect finding missed: {gold.gold_finding_id}")
        if gold.must_detect and gold.expected_severity == Severity.HIGH:
            failures.append(f"High must_detect finding missed: {gold.gold_finding_id}")
    if risk_decision.auto_clear_allowed:
        for gold in dataset.gold_findings:
            if gold.should_block_auto_clear:
                failures.append(
                    "Auto-clear despite blocking gold finding: "
                    f"{gold.gold_finding_id}"
                )
            elif gold.must_detect and gold.expected_severity in {Severity.HIGH, Severity.CRITICAL}:
                failures.append(
                    "Auto-clear despite known high/critical gold finding: "
                    f"{gold.gold_finding_id}"
                )
    return failures


def _duplicate_finding_ids(
    *,
    gold_findings: Sequence[GoldFinding],
    findings: Sequence[RiskFinding],
    matches: Sequence[tuple[GoldFinding, RiskFinding]],
) -> set[str]:
    matched_by_gold = {gold.gold_finding_id: finding.finding_id for gold, finding in matches}
    duplicate_ids: set[str] = set()
    for gold in gold_findings:
        matched_finding_id = matched_by_gold.get(gold.gold_finding_id)
        if matched_finding_id is None:
            continue
        duplicate_ids.update(
            finding.finding_id
            for finding in findings
            if finding.finding_id != matched_finding_id
            and _finding_matches_gold(finding, gold)
        )
    return duplicate_ids


def _must_detect_recall(
    gold_findings: Sequence[GoldFinding],
    matches: Sequence[tuple[GoldFinding, RiskFinding]],
) -> float:
    must_detect = [gold for gold in gold_findings if gold.must_detect]
    matched_ids = {gold.gold_finding_id for gold, _finding in matches}
    return _safe_ratio(
        sum(gold.gold_finding_id in matched_ids for gold in must_detect), len(must_detect)
    )


def _severity_metrics(
    matches: Sequence[tuple[GoldFinding, RiskFinding]],
) -> dict[str, int]:
    exact = 0
    under = 0
    over = 0
    high_or_critical_under = 0
    for gold, finding in matches:
        expected_rank = _severity_rank(gold.expected_severity)
        actual_rank = _severity_rank(finding.severity)
        if actual_rank == expected_rank:
            exact += 1
        elif actual_rank < expected_rank:
            under += 1
            if gold.expected_severity in {Severity.HIGH, Severity.CRITICAL}:
                high_or_critical_under += 1
        else:
            over += 1
    return {
        "severity_exact_count": exact,
        "severity_undercall_count": under,
        "severity_overcall_count": over,
        "high_or_critical_undercall_count": high_or_critical_under,
    }


def _violates_false_positive_boundary(
    finding: RiskFinding,
    boundaries: Sequence[str],
) -> bool:
    finding_text = " ".join(
        [
            finding.risk_statement,
            finding.recommended_action,
            *(item.quote for item in finding.evidence_items),
        ]
    )
    normalized_finding = _normalized_text(finding_text)
    return any(
        (boundary_text := _normalized_text(boundary))
        and boundary_text in normalized_finding
        for boundary in boundaries
    )


def _normalized_text(value: str) -> str:
    return " ".join("".join(char.lower() if char.isalnum() else " " for char in value).split())


def _evidence_matches_expected(evidence: dict[str, Any], expected: dict[str, Any]) -> bool:
    return (
        evidence.get("document_id") == expected.get("document_id")
        and evidence.get("chunk_id") == expected.get("chunk_id")
        and evidence.get("page") == expected.get("page")
        and str(expected.get("quote", "")) in str(evidence.get("quote", ""))
    )


def _severity_rank(severity: Severity) -> int:
    return {
        Severity.INFORMATIONAL: 0,
        Severity.LOW: 1,
        Severity.MEDIUM: 2,
        Severity.HIGH: 3,
        Severity.CRITICAL: 4,
    }[severity]


def _safe_ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)
