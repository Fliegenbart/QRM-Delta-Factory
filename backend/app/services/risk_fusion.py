from __future__ import annotations

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
    def cluster_findings(self, findings: Sequence[RiskFinding]) -> list[FindingCluster]:
        grouped: dict[tuple[str, tuple[str, ...]], list[RiskFinding]] = {}
        for finding in findings:
            key = (
                finding.risk_category,
                tuple(sorted(finding.requirement_references)),
            )
            grouped.setdefault(key, []).append(finding)

        clusters: list[FindingCluster] = []
        for (risk_category, requirement_references), cluster_findings in grouped.items():
            finding_ids = [finding.finding_id for finding in cluster_findings]
            cluster_id = _cluster_id(risk_category, list(requirement_references), finding_ids)
            clusters.append(
                FindingCluster(
                    cluster_id=cluster_id,
                    risk_category=risk_category,
                    requirement_references=list(requirement_references),
                    finding_ids=finding_ids,
                    max_severity=_max_severity(cluster_findings),
                    evidence_overlap_score=_evidence_overlap_score(cluster_findings),
                    similarity_basis=[
                        "risk_category",
                        "requirement_id",
                        "deterministic evidence overlap",
                    ],
                )
            )
        return sorted(clusters, key=lambda cluster: cluster.cluster_id)


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
        model_runs = self.repository.list_model_runs(document_set_id)
        clusters = self.clusterer.cluster_findings(findings)

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
        if failed_model_runs_exist:
            auto_clear_blockers.append("failed model run affects review coverage")
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
            required_human_review_reasons=_dedupe_text(required_human_review_reasons),
            finding_clusters=clusters,
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
    model_disagreement_score: float,
) -> RiskDecisionClass:
    if document_quality_score < document_quality_threshold:
        return RiskDecisionClass.INSUFFICIENT_DOCUMENT_QUALITY
    if ood_score >= 1:
        return RiskDecisionClass.OUT_OF_SCOPE
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
    return list(deduped.values())


def _dedupe_text(items: Sequence[str]) -> list[str]:
    deduped: list[str] = []
    for item in items:
        if item and item not in deduped:
            deduped.append(item)
    return deduped
