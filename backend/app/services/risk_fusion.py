from __future__ import annotations

import re
from collections.abc import Sequence
from datetime import UTC, datetime
from hashlib import sha256
from typing import Protocol

from app.audit.events import InMemoryAuditLog
from app.core.config import get_settings
from app.db.in_memory import InMemoryDocumentRepository
from app.risk.gates import CoverageService, OODService
from app.schemas.domain import (
    AdversarialChallenge,
    Document,
    DocumentSet,
    EvidenceSupport,
    ModelRun,
    ModelRunStatus,
    RiskFinding,
    Severity,
)
from app.schemas.risk import FindingCluster, RiskDecision, RiskDecisionClass

POLICY_VERSION = "risk-fusion-policy-v0.2"


class RiskFusionDocumentSetNotFoundError(Exception):
    pass


class FindingSimilarityStrategy(Protocol):
    def cluster_findings(self, findings: Sequence[RiskFinding]) -> list[FindingCluster]:
        ...


class DeterministicFindingClusterer:
    """Group findings that report the same issue, whichever agent phrased it.

    Grouping on ``(risk_category, requirement_references)`` alone left most
    repetition intact, because agents restate one issue under different
    categories and requirement tags: the last suite run cut 244 findings to
    207, while 113 of them were repeats of an error already reported.

    Evidence is the reliable signal, and it was computed but only ever stored
    as a score. It cannot be used alone, though. Distinct issues routinely
    share a citation -- CASE_01 has a future-dated signature and an unfounded
    Minor classification in the same chunk -- so grouping on evidence by
    itself merged eight pairs of separate planted errors. Requiring the risk
    statements to agree as well separates those, and holds every planted error
    apart at thresholds down to 0.20.

    Shared evidence is added to the original rule rather than replacing it.
    Agents also restate an issue in wording too different to score as similar
    while still landing on the same category and requirement, and dropping
    that rule stopped those from being offered as supporting signals on the
    published risk. Together they take the same run from 244 findings to 130,
    against 207 for the original rule alone, still without merging two
    planted errors.
    """

    #: Statement agreement required alongside shared evidence. Chosen with margin:
    #: 0.18 starts merging distinct errors, and 0.20 only just survives on one
    #: run's data, which is not something to tune a safety property against.
    statement_similarity_threshold = 0.25

    def cluster_findings(self, findings: Sequence[RiskFinding]) -> list[FindingCluster]:
        ordered = sorted(findings, key=lambda item: item.finding_id)
        groups = _group_by_shared_evidence_and_statement(
            ordered,
            threshold=self.statement_similarity_threshold,
        )

        clusters: list[FindingCluster] = []
        for cluster_findings in groups:
            finding_ids = [finding.finding_id for finding in cluster_findings]
            root_finding = _published_root_finding(cluster_findings)
            # A merged group can span categories and requirements. The published
            # finding names the cluster, and every requirement stays listed so
            # nothing silently drops out of the requirement trail.
            representative = root_finding or cluster_findings[0]
            requirement_references = sorted(
                {
                    requirement_id
                    for finding in cluster_findings
                    for requirement_id in finding.requirement_references
                }
            )
            cluster_id = _cluster_id(
                representative.risk_category,
                requirement_references,
                finding_ids,
            )
            clusters.append(
                FindingCluster(
                    cluster_id=cluster_id,
                    risk_category=representative.risk_category,
                    requirement_references=requirement_references,
                    finding_ids=finding_ids,
                    max_severity=_max_severity(cluster_findings),
                    evidence_overlap_score=_evidence_overlap_score(cluster_findings),
                    similarity_basis=[
                        "risk_category",
                        "requirement_id",
                        "shared evidence chunk",
                        "risk statement agreement",
                    ],
                    root_finding_id=(
                        root_finding.finding_id if root_finding is not None else None
                    ),
                    published_finding_id=(
                        root_finding.finding_id if root_finding is not None else None
                    ),
                )
            )
        return sorted(clusters, key=lambda cluster: cluster.cluster_id)


def _group_by_shared_evidence_and_statement(
    findings: Sequence[RiskFinding],
    *,
    threshold: float,
) -> list[list[RiskFinding]]:
    """Union findings that cite a common chunk and make the same claim."""
    parent = list(range(len(findings)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    chunk_ids = [
        {item.chunk_id for item in finding.evidence_items} for finding in findings
    ]
    statement_tokens = [
        _statement_tokens(finding.risk_statement) for finding in findings
    ]
    requirement_keys = [
        (finding.risk_category, tuple(sorted(finding.requirement_references)))
        for finding in findings
    ]
    requirement_sets = [set(finding.requirement_references) for finding in findings]
    for left in range(len(findings)):
        for right in range(left + 1, len(findings)):
            same_requirement_scope = requirement_keys[left] == requirement_keys[right]
            same_issue_restated = (
                bool(chunk_ids[left] & chunk_ids[right])
                and _token_similarity(statement_tokens[left], statement_tokens[right])
                >= threshold
                # Only one finding of a cluster is published, so merging a finding
                # that cites a requirement the other does not would drop that
                # requirement out of the pack. Restatements that carry an extra
                # requirement stay separate risks; letting them merge would trade
                # a shorter list for a gap in the requirement trail.
                and _requirement_scopes_are_interchangeable(
                    requirement_sets[left], requirement_sets[right]
                )
            )
            if same_requirement_scope or same_issue_restated:
                parent[find(left)] = find(right)

    grouped: dict[int, list[RiskFinding]] = {}
    for index, finding in enumerate(findings):
        grouped.setdefault(find(index), []).append(finding)
    return list(grouped.values())


def _requirement_scopes_are_interchangeable(left: set[str], right: set[str]) -> bool:
    """True when neither finding contributes a requirement the other lacks."""
    return left == right or not left or not right


def _statement_tokens(risk_statement: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[^\W_]+", risk_statement.lower(), flags=re.UNICODE)
        if len(token) >= 4 and token not in _STATEMENT_STOPWORDS
    }


def _token_similarity(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


_STATEMENT_STOPWORDS = {
    "aber",
    "auch",
    "aus",
    "bei",
    "dass",
    "dem",
    "den",
    "der",
    "des",
    "die",
    "dies",
    "eine",
    "einen",
    "einer",
    "eines",
    "für",
    "ist",
    "nicht",
    "noch",
    "nur",
    "oder",
    "sind",
    "und",
    "vor",
    "von",
    "wird",
    "wurde",
}


class RiskFusionService:
    def __init__(
        self,
        *,
        repository: InMemoryDocumentRepository,
        audit_log: InMemoryAuditLog,
        clusterer: FindingSimilarityStrategy | None = None,
        policy_version: str = POLICY_VERSION,
    ) -> None:
        self.repository = repository
        self.audit_log = audit_log
        self.clusterer = clusterer or DeterministicFindingClusterer()
        self.policy_version = policy_version
        self.document_quality_threshold = get_settings().parsing_quality_threshold

    def run_risk_fusion(self, document_set_id: str) -> RiskDecision:
        document_set = self.repository.get_document_set(document_set_id)
        if document_set is None:
            raise RiskFusionDocumentSetNotFoundError(f"DocumentSet {document_set_id} not found")

        findings = _dedupe_findings(
            [
                *self.repository.list_risk_findings(document_set_id),
                *self.repository.list_risk_fusion_findings(document_set_id),
            ]
        )
        documents = _documents_for_set(self.repository, document_set)
        challenges = self.repository.list_adversarial_challenges(document_set_id)
        model_runs = _latest_model_runs_by_agent(
            self.repository.list_model_runs(document_set_id)
        )
        clusters = self.clusterer.cluster_findings(findings)
        published_finding_ids = [
            cluster.published_finding_id
            for cluster in clusters
            if cluster.published_finding_id is not None
        ]

        document_quality_score = _document_quality_score(documents)
        ood_result = OODService(repository=self.repository, audit_log=self.audit_log).evaluate(
            document_set_id
        )
        coverage_result = CoverageService(
            repository=self.repository,
            audit_log=self.audit_log,
        ).evaluate(document_set_id)
        ood_score = ood_result.score
        missing_attachments = _missing_required_attachments(documents)
        high_or_critical_findings = [
            finding for finding in findings if _is_high_or_critical(finding.severity)
        ]
        high_or_critical_challenges = [
            challenge for challenge in challenges if _is_high_or_critical(challenge.severity)
        ]
        credible_high_or_critical_exists = bool(
            high_or_critical_findings or high_or_critical_challenges
        )
        model_disagreement_score = _model_disagreement_score(
            findings=findings,
            clusters=clusters,
            challenges=challenges,
        )
        failed_model_runs_exist = any(run.status == ModelRunStatus.FAILED for run in model_runs)
        operational_blockers = _operational_blockers(
            failed_model_runs_exist=failed_model_runs_exist,
        )
        model_coverage_status = _model_coverage_status(
            failed_model_runs_exist=failed_model_runs_exist,
        )
        missing_knowledge_pack_ids = _missing_knowledge_pack_ids(model_runs)
        missing_knowledge_packs_exist = bool(missing_knowledge_pack_ids)
        unverified_high_risk_exists = any(
            _high_or_critical_is_unverified(finding) for finding in high_or_critical_findings
        )

        auto_clear_blockers: list[str] = []
        required_human_review_reasons: list[str] = []

        if document_quality_score < self.document_quality_threshold:
            auto_clear_blockers.append("document quality below threshold")
        if ood_result.auto_clear_blocked:
            auto_clear_blockers.append("OOD score above threshold")
        if ood_score >= 1:
            auto_clear_blockers.append("document set is outside active requirement scope")
        if coverage_result.gap_reasons:
            auto_clear_blockers.append("coverage gap blocks auto-clear")
        if coverage_result.high_or_critical_coverage_gap:
            auto_clear_blockers.append("coverage gap for high/critical scope")
        auto_clear_blockers.extend(operational_blockers)
        if missing_knowledge_packs_exist:
            auto_clear_blockers.append("required knowledge pack was not retrieved")
        if unverified_high_risk_exists:
            auto_clear_blockers.append("high/critical finding has weak or partial evidence")
        for attachment in missing_attachments:
            auto_clear_blockers.append(f"missing required attachment: {attachment}")
        if any(finding.missing_information for finding in findings):
            auto_clear_blockers.append("finding missing required information")
        if any(challenge.missing_evidence for challenge in challenges):
            auto_clear_blockers.append("adversarial challenge names missing evidence")
        if high_or_critical_challenges:
            auto_clear_blockers.append("adversarial high/critical challenge requires human review")
        if model_disagreement_score > 0 and credible_high_or_critical_exists:
            auto_clear_blockers.append("model disagreement on possible high/critical risk")

        if credible_high_or_critical_exists:
            required_human_review_reasons.append(
                "single high/critical finding is sufficient for human review"
            )
        required_human_review_reasons.extend(ood_result.reasons)
        required_human_review_reasons.extend(coverage_result.gap_reasons)
        if model_disagreement_score > 0 and credible_high_or_critical_exists:
            required_human_review_reasons.append(
                "model disagreement on possible high/critical severity"
            )
        if high_or_critical_challenges:
            required_human_review_reasons.append(
                "adversarial challenge involves possible high/critical risk"
            )
        for knowledge_pack_id in missing_knowledge_pack_ids:
            required_human_review_reasons.append(
                f"required knowledge pack not retrieved: {knowledge_pack_id}"
            )

        decision_class = _select_decision(
            document_quality_score=document_quality_score,
            document_quality_threshold=self.document_quality_threshold,
            ood_score=ood_score,
            ood_over_threshold=ood_result.auto_clear_blocked,
            coverage_gap_exists=bool(coverage_result.gap_reasons),
            coverage_high_or_critical_gap=coverage_result.high_or_critical_coverage_gap,
            failed_model_runs_exist=failed_model_runs_exist,
            missing_knowledge_packs_exist=missing_knowledge_packs_exist,
            unverified_high_risk_exists=unverified_high_risk_exists,
            missing_attachments=missing_attachments,
            findings=findings,
            challenges=challenges,
            credible_high_or_critical_exists=credible_high_or_critical_exists,
            reviewable_findings_exist=_reviewable_findings_exist(
                findings=findings,
                published_finding_ids=published_finding_ids,
            ),
            model_disagreement_score=model_disagreement_score,
        )
        auto_clear_allowed = (
            decision_class == RiskDecisionClass.AUTO_CLEAR_CANDIDATE
            and not auto_clear_blockers
        )

        decision = RiskDecision(
            document_set_id=document_set_id,
            decision=decision_class,
            max_severity=_max_severity(findings),
            credible_high_or_critical_exists=credible_high_or_critical_exists,
            model_disagreement_score=model_disagreement_score,
            document_quality_score=document_quality_score,
            ood_score=ood_score,
            coverage_score=coverage_result.coverage_score,
            ood_reasons=ood_result.reasons,
            coverage_gap_reasons=coverage_result.gap_reasons,
            auto_clear_allowed=auto_clear_allowed,
            auto_clear_blockers=_dedupe_text(auto_clear_blockers),
            operational_blockers=operational_blockers,
            model_coverage_status=model_coverage_status,
            required_human_review_reasons=_dedupe_text(required_human_review_reasons),
            finding_clusters=clusters,
            published_finding_ids=published_finding_ids,
            generated_at=datetime.now(UTC),
            policy_version=self.policy_version,
        )
        self.repository.add_risk_decision(
            document_set_id=document_set_id,
            risk_decision=decision,
        )
        audit_payload = {
            "document_set_id": document_set_id,
            "decision": decision.decision,
            "policy_version": decision.policy_version,
            "finding_count": len(findings),
            "cluster_count": len(clusters),
            "auto_clear_allowed": decision.auto_clear_allowed,
            "auto_clear_blockers": decision.auto_clear_blockers,
            "operational_blockers": decision.operational_blockers,
            "model_coverage_status": decision.model_coverage_status,
            "published_finding_ids": decision.published_finding_ids,
            "missing_knowledge_pack_ids": missing_knowledge_pack_ids,
            "ood_score": decision.ood_score,
            "ood_reasons": decision.ood_reasons,
            "coverage_score": decision.coverage_score,
            "coverage_gap_reasons": decision.coverage_gap_reasons,
        }
        self.audit_log.append(
            event_type="risk_fusion_completed",
            actor_id="service_risk_fusion",
            actor_type="service",
            entity_type="RiskDecision",
            entity_id=f"{document_set_id}:{self.policy_version}",
            tenant_id=document_set.tenant_id,
            payload=audit_payload,
        )
        self.audit_log.append(
            event_type="risk_fusion_decision_generated",
            actor_id=document_set.uploaded_by,
            entity_type="RiskDecision",
            entity_id=f"{document_set_id}:{self.policy_version}",
            tenant_id=document_set.tenant_id,
            payload=audit_payload,
        )
        return decision


def _select_decision(
    *,
    document_quality_score: float,
    document_quality_threshold: float,
    ood_score: float,
    ood_over_threshold: bool,
    coverage_gap_exists: bool,
    coverage_high_or_critical_gap: bool,
    failed_model_runs_exist: bool,
    missing_knowledge_packs_exist: bool,
    unverified_high_risk_exists: bool,
    missing_attachments: list[str],
    findings: Sequence[RiskFinding],
    challenges: Sequence[AdversarialChallenge],
    credible_high_or_critical_exists: bool,
    reviewable_findings_exist: bool,
    model_disagreement_score: float,
) -> RiskDecisionClass:
    if document_quality_score < document_quality_threshold:
        return RiskDecisionClass.INSUFFICIENT_DOCUMENT_QUALITY
    if ood_score >= 1:
        return RiskDecisionClass.OUT_OF_SCOPE
    if reviewable_findings_exist:
        return RiskDecisionClass.HUMAN_REVIEW_REQUIRED
    if failed_model_runs_exist:
        return RiskDecisionClass.BLOCKED_DUE_TO_MODEL_FAILURE
    if missing_knowledge_packs_exist:
        return RiskDecisionClass.HUMAN_REVIEW_REQUIRED
    if unverified_high_risk_exists:
        return RiskDecisionClass.BLOCKED_DUE_TO_UNVERIFIED_HIGH_RISK
    if missing_attachments or any(finding.missing_information for finding in findings):
        return RiskDecisionClass.NEEDS_MORE_INFORMATION
    if coverage_gap_exists:
        return RiskDecisionClass.HUMAN_REVIEW_REQUIRED
    if coverage_high_or_critical_gap:
        return RiskDecisionClass.HUMAN_REVIEW_REQUIRED
    if ood_over_threshold:
        return RiskDecisionClass.HUMAN_REVIEW_REQUIRED
    if any(challenge.missing_evidence for challenge in challenges):
        return RiskDecisionClass.NEEDS_MORE_INFORMATION
    if credible_high_or_critical_exists or model_disagreement_score > 0:
        return RiskDecisionClass.HUMAN_REVIEW_REQUIRED
    return RiskDecisionClass.AUTO_CLEAR_CANDIDATE


def _documents_for_set(
    repository: InMemoryDocumentRepository,
    document_set: DocumentSet,
) -> list[Document]:
    documents: list[Document] = []
    for document_id in document_set.document_ids:
        document = repository.get_document(document_id)
        if document is not None:
            documents.append(document)
    return documents


def _document_quality_score(documents: Sequence[Document]) -> float:
    if not documents:
        return 1.0
    return min(document.parsing_quality_score for document in documents)


def _missing_required_attachments(documents: Sequence[Document]) -> list[str]:
    missing: list[str] = []
    for document in documents:
        for key in (
            "required_attachments_missing",
            "missing_required_documents",
            "required_documents_missing",
        ):
            attachments = document.metadata.get(key, [])
            if isinstance(attachments, list):
                missing.extend(str(attachment) for attachment in attachments)
            elif isinstance(attachments, str):
                missing.append(attachments)
    return _dedupe_text(missing)


def _high_or_critical_is_unverified(finding: RiskFinding) -> bool:
    if finding.evidence_support in {
        EvidenceSupport.PARTIAL,
        EvidenceSupport.WEAK,
        EvidenceSupport.NONE,
    }:
        return True
    if finding.verification_result is None:
        return False
    return not finding.verification_result.deterministic_checks_passed


def _published_root_finding(findings: Sequence[RiskFinding]) -> RiskFinding | None:
    eligible_findings = [finding for finding in findings if _is_publishable(finding)]
    if not eligible_findings:
        return None
    return min(
        eligible_findings,
        key=lambda finding: (-_severity_rank(finding.severity), finding.finding_id),
    )


def _is_publishable(finding: RiskFinding) -> bool:
    if finding.evidence_support != EvidenceSupport.STRONG or finding.missing_information:
        return False
    verification = finding.verification_result
    return (
        verification is not None
        and verification.evidence_support == EvidenceSupport.STRONG
        and verification.deterministic_checks_passed
    )


def _reviewable_findings_exist(
    *,
    findings: Sequence[RiskFinding],
    published_finding_ids: Sequence[str],
) -> bool:
    findings_by_id = {finding.finding_id: finding for finding in findings}
    published_reviewable_exists = any(
        not findings_by_id[finding_id].auto_close_allowed
        for finding_id in published_finding_ids
        if finding_id in findings_by_id
    )
    if published_reviewable_exists:
        return True
    return any(_is_source_matched_reviewable_hint(finding) for finding in findings)


def _is_source_matched_reviewable_hint(finding: RiskFinding) -> bool:
    if finding.auto_close_allowed:
        return False
    if finding.evidence_support not in {EvidenceSupport.STRONG, EvidenceSupport.PARTIAL}:
        return False
    verification = finding.verification_result
    if verification is None:
        return False
    return (
        verification.quote_matches_chunk
        and verification.requirement_applicable
        and verification.evidence_support
        in {EvidenceSupport.STRONG, EvidenceSupport.PARTIAL}
    )


def _operational_blockers(*, failed_model_runs_exist: bool) -> list[str]:
    if failed_model_runs_exist:
        return ["failed model run affects review coverage"]
    return []


def _model_coverage_status(*, failed_model_runs_exist: bool) -> str:
    return "incomplete" if failed_model_runs_exist else "complete"


def _model_disagreement_score(
    *,
    findings: Sequence[RiskFinding],
    clusters: Sequence[FindingCluster],
    challenges: Sequence[AdversarialChallenge],
) -> float:
    if not findings and not challenges:
        return 0.0
    max_score = 0.0
    findings_by_id = {finding.finding_id: finding for finding in findings}
    for cluster in clusters:
        severities = [
            _severity_rank(findings_by_id[finding_id].severity)
            for finding_id in cluster.finding_ids
            if finding_id in findings_by_id
        ]
        if len(severities) < 2:
            continue
        max_score = max(max_score, (max(severities) - min(severities)) / 4)
    if any(challenge.target_type == "no_issue_claim" for challenge in challenges):
        max_score = max(max_score, 0.5)
    return round(min(max_score, 1.0), 3)


def _missing_knowledge_pack_ids(model_runs: Sequence[ModelRun]) -> list[str]:
    missing: list[str] = []
    for model_run in model_runs:
        if model_run.status != ModelRunStatus.SUCCEEDED:
            continue
        missing.extend(model_run.missing_knowledge_pack_ids)
    return _dedupe_text(missing)


def _latest_model_runs_by_agent(model_runs: Sequence[ModelRun]) -> list[ModelRun]:
    latest_by_agent: dict[tuple[str, str], ModelRun] = {}
    for model_run in model_runs:
        agent_key = (model_run.agent_id, model_run.agent_role)
        existing = latest_by_agent.get(agent_key)
        if existing is None or _model_run_finished_at(model_run) > _model_run_finished_at(existing):
            latest_by_agent[agent_key] = model_run
    return list(latest_by_agent.values())


def _model_run_finished_at(model_run: ModelRun) -> datetime:
    return model_run.completed_at or model_run.started_at


def _max_severity(findings: Sequence[RiskFinding]) -> Severity:
    if not findings:
        return Severity.INFORMATIONAL
    return max((finding.severity for finding in findings), key=_severity_rank)


def _severity_rank(severity: Severity) -> int:
    return {
        Severity.INFORMATIONAL: 0,
        Severity.LOW: 1,
        Severity.MEDIUM: 2,
        Severity.HIGH: 3,
        Severity.CRITICAL: 4,
    }[severity]


def _is_high_or_critical(severity: Severity) -> bool:
    return severity in {Severity.HIGH, Severity.CRITICAL}


def _cluster_id(
    risk_category: str,
    requirement_references: list[str],
    finding_ids: list[str],
) -> str:
    seed = "|".join([risk_category, ",".join(requirement_references), ",".join(finding_ids)])
    return f"cluster_{sha256(seed.encode()).hexdigest()[:16]}"


def _evidence_overlap_score(findings: Sequence[RiskFinding]) -> float:
    if len(findings) < 2:
        return 1.0
    evidence_sets = [
        {
            f"{item.document_id}:{item.chunk_id}:{item.quote_hash}"
            for item in finding.evidence_items
        }
        for finding in findings
    ]
    shared = set.intersection(*evidence_sets) if evidence_sets else set()
    total = set.union(*evidence_sets) if evidence_sets else set()
    if not total:
        return 0.0
    return round(len(shared) / len(total), 3)


def _dedupe_findings(findings: Sequence[RiskFinding]) -> list[RiskFinding]:
    deduped: dict[str, RiskFinding] = {}
    for finding in findings:
        deduped[finding.finding_id] = finding
    return [deduped[finding_id] for finding_id in sorted(deduped)]


def _dedupe_text(items: Sequence[str]) -> list[str]:
    deduped: list[str] = []
    for item in items:
        if item and item not in deduped:
            deduped.append(item)
    return deduped
