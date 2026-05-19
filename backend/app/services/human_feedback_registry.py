from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime

from app.audit.events import AuditEvent, InMemoryAuditLog
from app.db.in_memory import InMemoryDocumentRepository
from app.schemas.analytics import (
    HumanFeedbackModelCard,
    HumanFeedbackRecord,
    HumanFeedbackRegistryReport,
)
from app.schemas.domain import (
    DocumentSet,
    ReviewDecision,
    ReviewDecisionValue,
    RiskFinding,
    Severity,
)


class HumanFeedbackRegistry:
    """Builds model-performance feedback records from human review decisions."""

    def __init__(
        self,
        *,
        repository: InMemoryDocumentRepository,
        audit_log: InMemoryAuditLog,
    ) -> None:
        self.repository = repository
        self.audit_log = audit_log

    def report(self, *, tenant_id: str | None = None) -> HumanFeedbackRegistryReport:
        records = self._collect_records(tenant_id=tenant_id)
        model_cards = _model_cards(records)
        report = HumanFeedbackRegistryReport(
            generated_at=datetime.now(UTC),
            total_feedback_records=len(records),
            model_card_count=len(model_cards),
            records=records,
            model_cards=model_cards,
            limitations=[
                "Feedback records are observational datapoints and do not retrain models.",
                (
                    "Prompt, model, requirement, or verifier changes must be versioned "
                    "and evaluated before operational use."
                ),
                (
                    "High and Critical findings remain protected by recall guards even "
                    "when reviewers downgrade or reject a finding."
                ),
            ],
        )
        self.audit_log.append(
            event_type="human_feedback_registry_viewed",
            actor_id="service_human_feedback_registry",
            actor_type="service",
            entity_type="Analytics",
            entity_id="human_feedback_registry",
            tenant_id=tenant_id,
            payload={
                "total_feedback_records": report.total_feedback_records,
                "model_card_count": report.model_card_count,
            },
        )
        return report

    def _collect_records(self, *, tenant_id: str | None) -> list[HumanFeedbackRecord]:
        records: list[HumanFeedbackRecord] = []
        for decision in self.repository.list_review_decisions_all():
            finding = self.repository.find_risk_finding(decision.finding_id)
            if finding is None:
                continue
            document_set = self.repository.get_document_set(finding.document_set_id)
            if document_set is None:
                continue
            if tenant_id is not None and document_set.tenant_id != tenant_id:
                continue
            records.append(_record_from_decision(decision, finding, document_set, self.audit_log))
        return sorted(records, key=lambda record: record.created_at, reverse=True)


@dataclass(frozen=True)
class _FindingAuditContext:
    agent_role: str
    prompt_version: str


@dataclass(frozen=True)
class _ModelCardKey:
    model_provider: str
    model_name: str
    model_version: str
    prompt_version: str
    agent_role: str


def _record_from_decision(
    decision: ReviewDecision,
    finding: RiskFinding,
    document_set: DocumentSet,
    audit_log: InMemoryAuditLog,
) -> HumanFeedbackRecord:
    audit_context = _finding_audit_context(audit_log=audit_log, finding=finding)
    verifier_evidence_support = (
        str(finding.verification_result.evidence_support)
        if finding.verification_result is not None
        else None
    )
    return HumanFeedbackRecord(
        feedback_id=f"hfb_{decision.review_id}",
        review_id=decision.review_id,
        document_set_id=document_set.document_set_id,
        finding_id=finding.finding_id,
        tenant_id=document_set.tenant_id,
        document_type=document_set.declared_document_type,
        process_area=document_set.declared_process_area,
        agent_role=audit_context.agent_role,
        model_provider=finding.model_provider,
        model_name=finding.model_name,
        model_version=finding.model_version,
        prompt_version=audit_context.prompt_version,
        requirement_references=finding.requirement_references,
        risk_category=finding.risk_category,
        original_severity=finding.severity,
        original_evidence_support=str(finding.evidence_support),
        verifier_evidence_support=verifier_evidence_support,
        human_decision=decision.decision,
        feedback_outcome=_feedback_outcome(decision.decision),
        reviewer_id=decision.reviewer_id,
        rationale=decision.rationale,
        created_at=decision.created_at,
        high_critical_recall_guard=finding.severity in {Severity.HIGH, Severity.CRITICAL},
    )


def _finding_audit_context(
    *,
    audit_log: InMemoryAuditLog,
    finding: RiskFinding,
) -> _FindingAuditContext:
    events = audit_log.get_events_for_entity("RiskFinding", finding.finding_id)
    created_event = _latest_finding_created_event(events)
    if created_event is None:
        return _FindingAuditContext(
            agent_role=finding.model_name,
            prompt_version=finding.prompt_version,
        )
    metadata = created_event.metadata
    return _FindingAuditContext(
        agent_role=str(
            metadata.get("agent_role")
            or metadata.get("role")
            or metadata.get("agent_id")
            or finding.model_name
        ),
        prompt_version=str(metadata.get("prompt_version") or finding.prompt_version),
    )


def _latest_finding_created_event(events: list[AuditEvent]) -> AuditEvent | None:
    for event in reversed(events):
        if event.event_type == "finding_created":
            return event
    return None


def _feedback_outcome(decision: ReviewDecisionValue) -> str:
    return {
        ReviewDecisionValue.CONFIRM: "confirmed_risk",
        ReviewDecisionValue.DOWNGRADE: "severity_overstated",
        ReviewDecisionValue.REJECT: "false_positive",
        ReviewDecisionValue.REJECT_FALSE_POSITIVE: "false_positive",
        ReviewDecisionValue.SEVERITY_INCORRECT: "severity_issue",
        ReviewDecisionValue.EVIDENCE_INCORRECT: "evidence_issue",
        ReviewDecisionValue.REQUIREMENT_INCORRECT: "requirement_issue",
        ReviewDecisionValue.MISSED_FINDING: "missed_finding",
        ReviewDecisionValue.REQUEST_MORE_INFO: "missing_information",
        ReviewDecisionValue.REQUEST_MORE_INFORMATION: "missing_information",
        ReviewDecisionValue.LINK_TO_CAPA: "linked_to_capa",
        ReviewDecisionValue.ESCALATE_TO_QA: "escalated",
    }[decision]


def _model_cards(records: list[HumanFeedbackRecord]) -> list[HumanFeedbackModelCard]:
    grouped_records: dict[_ModelCardKey, list[HumanFeedbackRecord]] = defaultdict(list)
    for record in records:
        grouped_records[
            _ModelCardKey(
                model_provider=record.model_provider,
                model_name=record.model_name,
                model_version=record.model_version,
                prompt_version=record.prompt_version,
                agent_role=record.agent_role,
            )
        ].append(record)

    cards = [
        _model_card(key=key, records=card_records)
        for key, card_records in grouped_records.items()
    ]
    return sorted(
        cards,
        key=lambda card: (
            -card.total_human_decisions,
            -card.false_positive_rate,
            -card.downgrade_rate,
            card.agent_role,
            card.model_name,
        ),
    )


def _model_card(
    *,
    key: _ModelCardKey,
    records: list[HumanFeedbackRecord],
) -> HumanFeedbackModelCard:
    total = len(records)
    confirmed_count = _count_outcomes(records, {"confirmed_risk"})
    downgrade_count = _count_outcomes(records, {"severity_overstated"})
    severity_issue_count = _count_outcomes(records, {"severity_overstated", "severity_issue"})
    false_positive_count = _count_outcomes(records, {"false_positive"})
    evidence_issue_count = _count_outcomes(records, {"evidence_issue"})
    requirement_issue_count = _count_outcomes(records, {"requirement_issue"})
    missed_finding_count = _count_outcomes(records, {"missed_finding"})
    more_information_count = _count_outcomes(records, {"missing_information"})
    escalation_count = _count_outcomes(records, {"escalated"})
    return HumanFeedbackModelCard(
        model_provider=key.model_provider,
        model_name=key.model_name,
        model_version=key.model_version,
        prompt_version=key.prompt_version,
        agent_role=key.agent_role,
        total_human_decisions=total,
        confirmed_count=confirmed_count,
        downgrade_count=downgrade_count,
        false_positive_count=false_positive_count,
        severity_issue_count=severity_issue_count,
        evidence_issue_count=evidence_issue_count,
        requirement_issue_count=requirement_issue_count,
        missed_finding_count=missed_finding_count,
        more_information_count=more_information_count,
        escalation_count=escalation_count,
        confirmation_rate=_rate(confirmed_count, total),
        downgrade_rate=_rate(downgrade_count, total),
        false_positive_rate=_rate(false_positive_count, total),
    )


def _count_outcomes(records: list[HumanFeedbackRecord], outcomes: set[str]) -> int:
    return sum(1 for record in records if record.feedback_outcome in outcomes)


def _rate(count: int, total: int) -> float:
    if total == 0:
        return 0
    return round(count / total, 4)
