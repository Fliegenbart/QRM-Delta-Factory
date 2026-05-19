from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime

from app.schemas.domain import Severity
from app.schemas.evals import (
    EvalReport,
    RegressionBlockingCriterion,
    RegressionGateCriterionType,
    RegressionGateReport,
    RegressionRun,
)

GATE_POLICY_VERSION = "regression-gate-policy-v0.1"


class RegressionGateService:
    def __init__(
        self,
        *,
        citation_precision_threshold: float = 0.9,
        requirement_match_accuracy_threshold: float = 0.9,
        max_human_review_rate_increase: float = 0.25,
    ) -> None:
        self.citation_precision_threshold = citation_precision_threshold
        self.requirement_match_accuracy_threshold = requirement_match_accuracy_threshold
        self.max_human_review_rate_increase = max_human_review_rate_increase

    def compare(
        self,
        *,
        baseline: RegressionRun,
        candidate: RegressionRun,
    ) -> RegressionGateReport:
        baseline_summary = _run_summary(baseline)
        candidate_summary = _run_summary(candidate)
        blocking_criteria = [
            *self._critical_miss_blockers(candidate.eval_reports),
            *self._high_miss_blockers(candidate.eval_reports),
            *self._auto_clear_blockers(candidate.eval_reports),
            *self._metric_threshold_blockers(candidate.eval_reports),
            *self._human_review_rate_blockers(
                baseline_summary=baseline_summary,
                candidate_summary=candidate_summary,
            ),
        ]
        passed = not blocking_criteria
        generated_at = datetime.now(UTC)
        markdown_report = _markdown_report(
            baseline=baseline,
            candidate=candidate,
            passed=passed,
            blocking_criteria=blocking_criteria,
            baseline_summary=baseline_summary,
            candidate_summary=candidate_summary,
            gate_policy_version=GATE_POLICY_VERSION,
        )
        json_report = {
            "passed": passed,
            "gate_policy_version": GATE_POLICY_VERSION,
            "baseline_run_id": baseline.regression_run_id,
            "candidate_run_id": candidate.regression_run_id,
            "baseline_config_version_id": baseline.config_version.config_version_id,
            "candidate_config_version_id": candidate.config_version.config_version_id,
            "blocking_criteria": [
                criterion.model_dump(mode="json") for criterion in blocking_criteria
            ],
            "baseline_summary": baseline_summary,
            "candidate_summary": candidate_summary,
            "generated_at": generated_at.isoformat(),
        }
        return RegressionGateReport(
            baseline_run_id=baseline.regression_run_id,
            candidate_run_id=candidate.regression_run_id,
            baseline_config_version_id=baseline.config_version.config_version_id,
            candidate_config_version_id=candidate.config_version.config_version_id,
            passed=passed,
            blocking_criteria=blocking_criteria,
            baseline_summary=baseline_summary,
            candidate_summary=candidate_summary,
            markdown_report=markdown_report,
            json_report=json_report,
            generated_at=generated_at,
            gate_policy_version=GATE_POLICY_VERSION,
        )

    def _critical_miss_blockers(
        self,
        reports: Sequence[EvalReport],
    ) -> list[RegressionBlockingCriterion]:
        blockers: list[RegressionBlockingCriterion] = []
        for report in reports:
            unmatched_gold_ids = set(report.unmatched_gold_finding_ids)
            for gold in report.dataset.gold_findings:
                if (
                    gold.must_detect
                    and gold.expected_severity == Severity.CRITICAL
                    and gold.gold_finding_id in unmatched_gold_ids
                ):
                    blockers.append(
                        RegressionBlockingCriterion(
                            criterion=(
                                RegressionGateCriterionType.MISSED_CRITICAL_MUST_DETECT
                            ),
                            dataset_id=report.dataset.dataset_id,
                            reason=(
                                "Candidate missed a Critical must_detect gold finding: "
                                f"{gold.gold_finding_id}."
                            ),
                            baseline_value="detected or baseline reference",
                            candidate_value="missed",
                            threshold="Critical must_detect recall must be complete",
                        )
                    )
        return blockers

    def _high_miss_blockers(
        self,
        reports: Sequence[EvalReport],
    ) -> list[RegressionBlockingCriterion]:
        blockers: list[RegressionBlockingCriterion] = []
        for report in reports:
            unmatched_gold_ids = set(report.unmatched_gold_finding_ids)
            for gold in report.dataset.gold_findings:
                if (
                    gold.must_detect
                    and gold.expected_severity == Severity.HIGH
                    and gold.gold_finding_id in unmatched_gold_ids
                ):
                    blockers.append(
                        RegressionBlockingCriterion(
                            criterion=RegressionGateCriterionType.MISSED_HIGH_MUST_DETECT,
                            dataset_id=report.dataset.dataset_id,
                            reason=(
                                "Candidate missed a High must_detect gold finding: "
                                f"{gold.gold_finding_id}."
                            ),
                            baseline_value="detected or baseline reference",
                            candidate_value="missed",
                            threshold="High must_detect recall must be complete",
                        )
                    )
        return blockers

    def _auto_clear_blockers(
        self,
        reports: Sequence[EvalReport],
    ) -> list[RegressionBlockingCriterion]:
        blockers: list[RegressionBlockingCriterion] = []
        for report in reports:
            if report.metrics.auto_clear_false_negative_count <= 0:
                continue
            blockers.append(
                RegressionBlockingCriterion(
                    criterion=RegressionGateCriterionType.AUTO_CLEAR_HIGH_CRITICAL_GOLD,
                    dataset_id=report.dataset.dataset_id,
                    reason=(
                        "Candidate allowed auto-clear despite known High/Critical "
                        "must-detect gold finding(s)."
                    ),
                    candidate_value=float(report.metrics.auto_clear_false_negative_count),
                    threshold=0.0,
                )
            )
        return blockers

    def _metric_threshold_blockers(
        self,
        reports: Sequence[EvalReport],
    ) -> list[RegressionBlockingCriterion]:
        blockers: list[RegressionBlockingCriterion] = []
        for report in reports:
            if report.metrics.citation_precision < self.citation_precision_threshold:
                blockers.append(
                    RegressionBlockingCriterion(
                        criterion=(
                            RegressionGateCriterionType.CITATION_PRECISION_BELOW_THRESHOLD
                        ),
                        dataset_id=report.dataset.dataset_id,
                        reason="Candidate citation precision is below the release threshold.",
                        candidate_value=report.metrics.citation_precision,
                        threshold=self.citation_precision_threshold,
                    )
                )
            if (
                report.metrics.requirement_match_accuracy
                < self.requirement_match_accuracy_threshold
            ):
                blockers.append(
                    RegressionBlockingCriterion(
                        criterion=(
                            RegressionGateCriterionType.
                            REQUIREMENT_MATCH_ACCURACY_BELOW_THRESHOLD
                        ),
                        dataset_id=report.dataset.dataset_id,
                        reason=(
                            "Candidate requirement match accuracy is below the release "
                            "threshold."
                        ),
                        candidate_value=report.metrics.requirement_match_accuracy,
                        threshold=self.requirement_match_accuracy_threshold,
                    )
                )
        return blockers

    def _human_review_rate_blockers(
        self,
        *,
        baseline_summary: dict[str, float],
        candidate_summary: dict[str, float],
    ) -> list[RegressionBlockingCriterion]:
        baseline_rate = baseline_summary["human_review_rate"]
        candidate_rate = candidate_summary["human_review_rate"]
        rate_increase = round(candidate_rate - baseline_rate, 4)
        recall_improved = (
            candidate_summary["must_detect_recall"]
            > baseline_summary["must_detect_recall"]
        )
        if rate_increase <= self.max_human_review_rate_increase or recall_improved:
            return []
        return [
            RegressionBlockingCriterion(
                criterion=(
                    RegressionGateCriterionType.
                    HUMAN_REVIEW_RATE_INCREASE_WITHOUT_RECALL_GAIN
                ),
                reason=(
                    "Candidate increases human review workload beyond the configured "
                    "limit without improving must-detect recall."
                ),
                baseline_value=baseline_rate,
                candidate_value=candidate_rate,
                threshold=self.max_human_review_rate_increase,
            )
        ]


def _run_summary(run: RegressionRun) -> dict[str, float]:
    reports = run.eval_reports
    return {
        "dataset_count": float(len(reports)),
        "must_detect_recall": _must_detect_recall(reports),
        "citation_precision": _average(
            [report.metrics.citation_precision for report in reports]
        ),
        "requirement_match_accuracy": _average(
            [report.metrics.requirement_match_accuracy for report in reports]
        ),
        "human_review_rate": _average(
            [report.metrics.human_review_rate for report in reports]
        ),
        "auto_clear_false_negative_count": float(
            sum(report.metrics.auto_clear_false_negative_count for report in reports)
        ),
    }


def _must_detect_recall(reports: Sequence[EvalReport]) -> float:
    total_must_detect = 0
    detected_must_detect = 0
    for report in reports:
        matched_gold_ids = set(report.matched_gold_finding_ids)
        for gold in report.dataset.gold_findings:
            if not gold.must_detect:
                continue
            total_must_detect += 1
            if gold.gold_finding_id in matched_gold_ids:
                detected_must_detect += 1
    if total_must_detect == 0:
        return 1.0
    return round(detected_must_detect / total_must_detect, 4)


def _average(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 4)


def _markdown_report(
    *,
    baseline: RegressionRun,
    candidate: RegressionRun,
    passed: bool,
    blocking_criteria: Sequence[RegressionBlockingCriterion],
    baseline_summary: dict[str, float],
    candidate_summary: dict[str, float],
    gate_policy_version: str,
) -> str:
    status = "PASS" if passed else "FAIL"
    lines = [
        "# Regression Gate Report",
        "",
        "## Pass/Fail",
        f"Status: {status}",
        f"Gate policy: `{gate_policy_version}`",
        "",
        "## Compared Runs",
        f"- Baseline run: `{baseline.regression_run_id}`",
        f"- Baseline config: `{baseline.config_version.config_version_id}`",
        f"- Candidate run: `{candidate.regression_run_id}`",
        f"- Candidate config: `{candidate.config_version.config_version_id}`",
        "",
        "## Summary Metrics",
        "| Metric | Baseline | Candidate |",
        "| --- | ---: | ---: |",
    ]
    for metric in sorted(set(baseline_summary) | set(candidate_summary)):
        lines.append(
            f"| {metric} | {baseline_summary.get(metric, 0.0)} | "
            f"{candidate_summary.get(metric, 0.0)} |"
        )
    lines.extend(["", "## Blocking Criteria"])
    if blocking_criteria:
        for criterion in blocking_criteria:
            dataset = f" Dataset: `{criterion.dataset_id}`." if criterion.dataset_id else ""
            lines.append(f"- `{criterion.criterion}`: {criterion.reason}{dataset}")
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Release Rule",
            (
                "Any prompt, model configuration, RequirementSet, or RiskFusionPolicy "
                "change must pass this gate before release."
            ),
        ]
    )
    return "\n".join(lines)
