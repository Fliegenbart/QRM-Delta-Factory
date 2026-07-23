from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from hashlib import sha256

from app.audit.events import InMemoryAuditLog
from app.db.in_memory import InMemoryDocumentRepository
from app.schemas.domain import (
    AdversarialChallenge,
    EvidenceItem,
    EvidenceSupport,
    ReviewDecision,
    ReviewDecisionValue,
    ReviewerId,
    RiskFinding,
    Severity,
)
from app.schemas.review import CoverageSummary
from app.schemas.review_pack import (
    ModelPosition,
    ReviewerActionRecommendation,
    ReviewPack,
    ReviewPackEvidenceQuote,
    ReviewPackEvidenceRow,
    ReviewPackSupportingSignal,
    ReviewPackTopRisk,
)
from app.schemas.risk import RiskDecision
from app.services.review_calibration import ReviewCalibrationService


class ReviewPackDocumentSetNotFoundError(Exception):
    pass


class ReviewPackRiskDecisionNotFoundError(Exception):
    pass


class ReviewDecisionFindingNotFoundError(Exception):
    pass


class ReviewPackService:
    def __init__(
        self,
        *,
        repository: InMemoryDocumentRepository,
        audit_log: InMemoryAuditLog,
    ) -> None:
        self.repository = repository
        self.audit_log = audit_log

    def get_review_pack(self, document_set_id: str) -> ReviewPack:
        document_set = self.repository.get_document_set(document_set_id)
        if document_set is None:
            raise ReviewPackDocumentSetNotFoundError(f"DocumentSet {document_set_id} not found")

        decision = self.repository.get_latest_risk_decision(document_set_id)
        if decision is None:
            raise ReviewPackRiskDecisionNotFoundError(
                "Review pack requires a generated RiskDecision"
            )

        raw_findings = _findings_for_pack(self.repository, document_set_id)
        findings = _published_findings_for_pack(raw_findings, decision.published_finding_ids)
        if not findings:
            findings = _source_matched_reviewable_findings(raw_findings)
        review_decisions_by_finding = {
            finding.finding_id: self.repository.list_review_decisions(finding.finding_id)
            for finding in findings
        }
        review_progress = _review_progress(
            findings=findings,
            review_decisions_by_finding=review_decisions_by_finding,
        )
        challenges = self.repository.list_adversarial_challenges(document_set_id)
        coverage_summaries = self.repository.list_coverage_summaries(document_set_id)
        raw_findings_by_id = {finding.finding_id: finding for finding in raw_findings}
        supporting_findings_by_root = _supporting_findings_by_root(
            decision=decision,
            findings_by_id=raw_findings_by_id,
        )
        top_risks = [
            _top_risk(
                finding=finding,
                review_decisions=review_decisions_by_finding.get(finding.finding_id, []),
                challenges=challenges,
                coverage_summaries=coverage_summaries,
                decision_reasons=decision.required_human_review_reasons,
                supporting_findings=supporting_findings_by_root.get(finding.finding_id, []),
            )
            for finding in _sort_findings(findings)
        ]
        evidence_table = [
            _evidence_row(finding=finding, evidence=evidence)
            for finding in _sort_findings(findings)
            for evidence in finding.evidence_items
        ]
        model_positions = [
            _model_position(
                finding=finding,
                challenges=challenges,
                coverage_summaries=coverage_summaries,
            )
            for finding in _sort_findings(findings)
        ]
        verifier_results = [
            finding.verification_result
            for finding in _sort_findings(findings)
            if finding.verification_result is not None
        ]
        missing_information = _missing_information(
            findings=raw_findings,
            decision_blockers=decision.auto_clear_blockers,
        )
        recommended_actions = _recommended_actions(
            findings=raw_findings,
            missing_information=missing_information,
            human_review_required=bool(decision.required_human_review_reasons),
        )
        review_pack = ReviewPack(
            review_pack_id=_review_pack_id(document_set_id, decision.policy_version, findings),
            document_set_id=document_set_id,
            decision=decision,
            summary=_summary(
                decision_class=str(decision.decision),
                findings=findings,
                blocker_count=len(decision.auto_clear_blockers),
                ood_reason_count=len(decision.ood_reasons),
                coverage_gap_count=len(decision.coverage_gap_reasons),
            ),
            decision_summary=_decision_summary(decision=decision, findings=findings),
            operational_warnings=_operational_warnings(decision=decision),
            raw_finding_count=len(raw_findings),
            review_progress_percent=review_progress["percent"],
            reviewed_finding_count=review_progress["reviewed"],
            total_finding_count=review_progress["total"],
            top_risks=top_risks,
            finding_clusters=decision.finding_clusters,
            evidence_table=evidence_table,
            model_positions=model_positions,
            verifier_results=verifier_results,
            ood_reasons=decision.ood_reasons,
            coverage_gap_reasons=decision.coverage_gap_reasons,
            missing_information=missing_information,
            recommended_reviewer_actions=recommended_actions,
            audit_references=_audit_references(self.audit_log, document_set_id),
        )
        self.audit_log.append(
            event_type="review_pack_created",
            actor_id="service_review_pack",
            actor_type="service",
            entity_type="ReviewPack",
            entity_id=review_pack.review_pack_id,
            payload={
                "document_set_id": document_set_id,
                "risk_decision": decision.decision,
                "top_risk_count": len(review_pack.top_risks),
                "evidence_row_count": len(review_pack.evidence_table),
                "missing_information_count": len(review_pack.missing_information),
                "review_progress_percent": review_pack.review_progress_percent,
                "reviewed_finding_count": review_pack.reviewed_finding_count,
                "total_finding_count": review_pack.total_finding_count,
            },
        )
        return review_pack

    def record_review_decision(
        self,
        *,
        finding_id: str,
        reviewer_id: ReviewerId,
        decision: ReviewDecisionValue,
        rationale: str,
    ) -> ReviewDecision:
        finding = self.repository.find_risk_finding(finding_id)
        if finding is None:
            raise ReviewDecisionFindingNotFoundError(f"Finding {finding_id} not found")
        created_at = datetime.now(UTC)
        review_decision = ReviewDecision(
            review_id=_review_decision_id(
                finding_id=finding_id,
                reviewer_id=reviewer_id,
                decision=decision,
                created_at=created_at,
            ),
            finding_id=finding.finding_id,
            reviewer_id=reviewer_id,
            decision=decision,
            rationale=rationale,
            created_at=created_at,
        )
        self.repository.add_review_decision(review_decision)
        calibration_example = ReviewCalibrationService(
            repository=self.repository,
            audit_log=self.audit_log,
        ).record_feedback_decision(review_decision)
        audit_payload = {
            "finding_id": finding.finding_id,
            "document_set_id": finding.document_set_id,
            "review_id": review_decision.review_id,
            "decision": review_decision.decision,
            "calibration_example_id": calibration_example.calibration_example_id,
        }
        self.audit_log.append(
            event_type="human_review_decision_created",
            actor_id=reviewer_id,
            actor_type="user",
            entity_type="RiskFinding",
            entity_id=finding.finding_id,
            payload=audit_payload,
        )
        self.audit_log.append(
            event_type="review_decision_recorded",
            actor_id=reviewer_id,
            entity_type="RiskFinding",
            entity_id=finding.finding_id,
            payload=audit_payload,
        )
        return review_decision


def _findings_for_pack(
    repository: InMemoryDocumentRepository,
    document_set_id: str,
) -> list[RiskFinding]:
    fusion_findings = repository.list_risk_fusion_findings(document_set_id)
    if fusion_findings:
        return fusion_findings
    return repository.list_risk_findings(document_set_id)


def _published_findings_for_pack(
    findings: Sequence[RiskFinding],
    published_finding_ids: Sequence[str],
) -> list[RiskFinding]:
    findings_by_id = {finding.finding_id: finding for finding in findings}
    if published_finding_ids:
        return [
            findings_by_id[finding_id]
            for finding_id in published_finding_ids
            if finding_id in findings_by_id
        ]
    return []


def _source_matched_reviewable_findings(
    findings: Sequence[RiskFinding],
) -> list[RiskFinding]:
    """Keep QA-visible signals when a strict canonical publication gate yields none.

    These findings are not auto-clear evidence: the verifier label and missing
    information stay visible, while an exact source quote and requirement match
    prevent unsupported model prose from appearing as a QA item.
    """
    return [
        finding
        for finding in findings
        if finding.evidence_support in {"strong", "partial"}
        and finding.verification_result is not None
        and finding.verification_result.quote_matches_chunk
        and finding.verification_result.requirement_applicable
        and finding.verification_result.evidence_support
        in {EvidenceSupport.STRONG, EvidenceSupport.PARTIAL}
    ]


def _supporting_findings_by_root(
    *,
    decision: RiskDecision,
    findings_by_id: dict[str, RiskFinding],
) -> dict[str, list[RiskFinding]]:
    # FindingCluster is deliberately the source of this mapping: raw model
    # candidates are never promoted to a separate QA card.
    clusters = decision.finding_clusters
    supporting: dict[str, list[RiskFinding]] = {}
    for cluster in clusters:
        root_id = cluster.published_finding_id
        if root_id is None:
            continue
        supporting[root_id] = [
            findings_by_id[finding_id]
            for finding_id in cluster.finding_ids
            if finding_id != root_id and finding_id in findings_by_id
        ]
    return supporting


def _top_risk(
    *,
    finding: RiskFinding,
    review_decisions: Sequence[ReviewDecision],
    challenges: Sequence[AdversarialChallenge],
    coverage_summaries: Sequence[CoverageSummary],
    decision_reasons: Sequence[str],
    supporting_findings: Sequence[RiskFinding],
) -> ReviewPackTopRisk:
    latest_review_decision = _latest_review_decision(review_decisions)
    return ReviewPackTopRisk(
        finding_id=finding.finding_id,
        risk_statement=finding.risk_statement,
        severity=finding.severity,
        risk_category=finding.risk_category,
        requirement_references=finding.requirement_references,
        evidence_quotes=[_evidence_quote(evidence) for evidence in finding.evidence_items],
        found_by_agents=[finding.model_name],
        contradicted_by_agents=_contradicted_by_agents(finding, challenges),
        no_issue_agents=_no_issue_agents(coverage_summaries),
        verifier_status=_verifier_status(finding),
        human_review_reason=_human_review_reason(finding, decision_reasons),
        review_status="reviewed" if review_decisions else "open",
        review_decision_count=len(review_decisions),
        latest_review_decision=(
            latest_review_decision.decision if latest_review_decision is not None else None
        ),
        latest_reviewed_at=(
            latest_review_decision.created_at if latest_review_decision is not None else None
        ),
        supporting_finding_ids=[finding.finding_id for finding in supporting_findings],
        supporting_finding_count=len(supporting_findings),
        supporting_signals=[
            ReviewPackSupportingSignal(
                finding_id=supporting.finding_id,
                risk_statement=supporting.risk_statement,
                severity=supporting.severity,
                evidence_quotes=[
                    _evidence_quote(evidence) for evidence in supporting.evidence_items
                ],
                verifier_status=_verifier_status(supporting),
            )
            for supporting in _sort_findings(supporting_findings)
        ],
    )


def _evidence_quote(evidence: EvidenceItem) -> ReviewPackEvidenceQuote:
    return ReviewPackEvidenceQuote(
        document_id=evidence.document_id,
        chunk_id=evidence.chunk_id,
        page=evidence.page,
        quote=evidence.quote,
        support_type=evidence.support_type,
    )


def _evidence_row(*, finding: RiskFinding, evidence: EvidenceItem) -> ReviewPackEvidenceRow:
    return ReviewPackEvidenceRow(
        finding_id=finding.finding_id,
        risk_statement=finding.risk_statement,
        document_id=evidence.document_id,
        page=evidence.page,
        chunk_id=evidence.chunk_id,
        quote=evidence.quote,
        requirement_references=finding.requirement_references,
        verifier_status=_verifier_status(finding),
    )


def _model_position(
    *,
    finding: RiskFinding,
    challenges: Sequence[AdversarialChallenge],
    coverage_summaries: Sequence[CoverageSummary],
) -> ModelPosition:
    return ModelPosition(
        finding_id=finding.finding_id,
        found_by_agents=[finding.model_name],
        contradicted_by_agents=_contradicted_by_agents(finding, challenges),
        no_issue_agents=_no_issue_agents(coverage_summaries),
    )


def _contradicted_by_agents(
    finding: RiskFinding,
    challenges: Sequence[AdversarialChallenge],
) -> list[str]:
    return _dedupe_text(
        [
            challenge.agent_role
            for challenge in challenges
            if challenge.target_type == "finding" and challenge.target_id == finding.finding_id
        ]
    )


def _no_issue_agents(coverage_summaries: Sequence[CoverageSummary]) -> list[str]:
    return _dedupe_text(
        [
            coverage_summary.role
            for coverage_summary in coverage_summaries
            if coverage_summary.finding_count == 0
        ]
    )


def _verifier_status(finding: RiskFinding) -> str:
    if finding.verification_result is not None:
        return str(finding.verification_result.evidence_support)
    return str(finding.evidence_support)


def _human_review_reason(
    finding: RiskFinding,
    decision_reasons: Sequence[str],
) -> str:
    reasons = list(decision_reasons)
    if finding.severity in {Severity.HIGH, Severity.CRITICAL}:
        reasons.append("human review required for high/critical risk")
    if finding.missing_information:
        reasons.append("missing information must be resolved by reviewer")
    if (
        finding.verification_result is not None
        and not finding.verification_result.deterministic_checks_passed
    ):
        reasons.append("verifier did not pass all deterministic checks")
    return "; ".join(_dedupe_text(reasons)) or "reviewer confirmation required"


def _missing_information(
    *,
    findings: Sequence[RiskFinding],
    decision_blockers: Sequence[str],
) -> list[str]:
    missing: list[str] = []
    for finding in findings:
        missing.extend(finding.missing_information)
        if finding.verification_result is not None:
            missing.extend(finding.verification_result.missing_evidence)
    missing.extend(
        blocker.removeprefix("missing required attachment: ")
        for blocker in decision_blockers
        if blocker.startswith("missing required attachment: ")
    )
    return _dedupe_text(missing)


def _recommended_actions(
    *,
    findings: Sequence[RiskFinding],
    missing_information: Sequence[str],
    human_review_required: bool,
) -> list[ReviewerActionRecommendation]:
    first_finding_id = findings[0].finding_id if findings else None
    actions = [
        ReviewerActionRecommendation(
            action=ReviewDecisionValue.CONFIRM,
            rationale=(
                "Confirm the finding if the cited evidence and requirement basis "
                "are acceptable."
            ),
            finding_id=first_finding_id,
        ),
        ReviewerActionRecommendation(
            action=ReviewDecisionValue.DOWNGRADE,
            rationale="Downgrade only with documented reviewer rationale and source support.",
            finding_id=first_finding_id,
        ),
        ReviewerActionRecommendation(
            action=ReviewDecisionValue.REJECT_FALSE_POSITIVE,
            rationale=(
                "Reject only if the reviewer documents why the evidence does not "
                "support risk."
            ),
            finding_id=first_finding_id,
        ),
        ReviewerActionRecommendation(
            action=ReviewDecisionValue.EVIDENCE_INCORRECT,
            rationale="Mark when the cited source does not prove the finding.",
            finding_id=first_finding_id,
        ),
        ReviewerActionRecommendation(
            action=ReviewDecisionValue.REQUIREMENT_INCORRECT,
            rationale="Mark when the linked requirement does not fit the case.",
            finding_id=first_finding_id,
        ),
        ReviewerActionRecommendation(
            action=ReviewDecisionValue.MISSED_FINDING,
            rationale="Record an omitted risk so it becomes part of calibration data.",
            finding_id=first_finding_id,
        ),
    ]
    if missing_information:
        actions.append(
            ReviewerActionRecommendation(
                action=ReviewDecisionValue.REQUEST_MORE_INFORMATION,
                rationale="Request missing evidence before accepting or closing the review item.",
                finding_id=first_finding_id,
            )
        )
    if human_review_required or any(
        finding.severity in {Severity.HIGH, Severity.CRITICAL} for finding in findings
    ):
        actions.append(
            ReviewerActionRecommendation(
                action=ReviewDecisionValue.ESCALATE_TO_QA,
                rationale="Escalate high-impact or blocked items to qualified QA review.",
                finding_id=first_finding_id,
            )
        )
    if any("capa" in finding.risk_category.lower() for finding in findings):
        actions.append(
            ReviewerActionRecommendation(
                action=ReviewDecisionValue.LINK_TO_CAPA,
                rationale="Link the finding to CAPA when reviewer confirms CAPA relevance.",
                finding_id=first_finding_id,
            )
        )
    return actions


def _review_progress(
    *,
    findings: Sequence[RiskFinding],
    review_decisions_by_finding: dict[str, list[ReviewDecision]],
) -> dict[str, int]:
    total = len(findings)
    reviewed = sum(
        1
        for finding in findings
        if review_decisions_by_finding.get(finding.finding_id)
    )
    percent = 0 if total == 0 else round((reviewed / total) * 100)
    return {"percent": percent, "reviewed": reviewed, "total": total}


def _latest_review_decision(
    review_decisions: Sequence[ReviewDecision],
) -> ReviewDecision | None:
    if not review_decisions:
        return None
    return max(review_decisions, key=lambda review_decision: review_decision.created_at)


def _sort_findings(findings: Sequence[RiskFinding]) -> list[RiskFinding]:
    return sorted(
        findings,
        key=lambda finding: (-_severity_rank(finding.severity), finding.finding_id),
    )


def _severity_rank(severity: Severity) -> int:
    return {
        Severity.INFORMATIONAL: 0,
        Severity.LOW: 1,
        Severity.MEDIUM: 2,
        Severity.HIGH: 3,
        Severity.CRITICAL: 4,
    }[severity]


def _summary(
    *,
    decision_class: str,
    findings: Sequence[RiskFinding],
    blocker_count: int,
    ood_reason_count: int,
    coverage_gap_count: int,
) -> str:
    max_severity = _sort_findings(findings)[0].severity if findings else Severity.INFORMATIONAL
    return (
        f"Risk decision {decision_class} based on {len(findings)} finding(s), "
        f"max severity {max_severity}, {blocker_count} auto-clear blocker(s), "
        f"and {ood_reason_count + coverage_gap_count} OOD/Coverage reason(s)."
    )


def _decision_summary(*, decision: RiskDecision, findings: Sequence[RiskFinding]) -> str:
    decision_class = str(decision.decision)
    if decision_class == "blocked_due_to_model_failure" and findings:
        return (
            f"QA-Prüfung erforderlich: {len(findings)} quellenverknüpfte Prüfhinweise "
            "sind sichtbar. Die technische Abdeckung ist unvollständig."
        )
    if findings and decision_class != "auto_clear_candidate":
        return (
            f"QA-Prüfung erforderlich: {len(findings)} quellenverknüpfte Prüfhinweise "
            "vor einer Freigabe bewerten."
        )
    if decision_class == "human_review_required":
        return (
            f"QA-Prüfung erforderlich: {len(findings)} Kernrisiko"
            f"{'n' if len(findings) != 1 else ''} vor einer Freigabe bewerten."
        )
    if decision_class == "needs_more_information":
        return "Weitere Unterlagen erforderlich, bevor QA eine Freigabe bewerten kann."
    if decision_class == "blocked_due_to_model_failure":
        return (
            "Die technische Prüfung ist unvollständig; "
            "eine fachliche Freigabe ist nicht möglich."
        )
    if decision_class == "auto_clear_candidate":
        return (
            "Keine veröffentlichten Kernrisiken; "
            "QA-Freigabe bleibt nachvollziehbar zu dokumentieren."
        )
    return "Der Prüffall benötigt eine menschliche QA-Bewertung."


def _operational_warnings(*, decision: RiskDecision) -> list[str]:
    warnings: list[str] = []
    if decision.model_coverage_status != "complete":
        warnings.append(
            "Ein technischer Prüfschritt konnte nicht vollständig abgeschlossen werden."
        )
    warnings.extend(decision.operational_blockers)
    return _dedupe_text(warnings)


def _audit_references(audit_log: InMemoryAuditLog, document_set_id: str) -> list[str]:
    references: list[str] = []
    for event in audit_log.list_events():
        if (
            event.entity_id == document_set_id
            or event.payload.get("document_set_id") == document_set_id
        ):
            references.append(event.event_id)
    return references


def _review_pack_id(
    document_set_id: str,
    policy_version: str,
    findings: Sequence[RiskFinding],
) -> str:
    seed = "|".join(
        [
            document_set_id,
            policy_version,
            ",".join(sorted(finding.finding_id for finding in findings)),
        ]
    )
    return f"rpack_{sha256(seed.encode()).hexdigest()[:20]}"


def _review_decision_id(
    *,
    finding_id: str,
    reviewer_id: str,
    decision: ReviewDecisionValue,
    created_at: datetime,
) -> str:
    seed = "|".join([finding_id, reviewer_id, str(decision), created_at.isoformat()])
    return f"review_{sha256(seed.encode()).hexdigest()[:20]}"


def _dedupe_text(items: Sequence[str]) -> list[str]:
    deduped: list[str] = []
    for item in items:
        if item and item not in deduped:
            deduped.append(item)
    return deduped
