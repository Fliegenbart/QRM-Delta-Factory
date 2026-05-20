from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from typing import Any

from app.audit.events import AuditEvent, InMemoryAuditLog
from app.db.in_memory import InMemoryDocumentRepository
from app.schemas.calibration import (
    CalibrationExample,
    CalibrationExampleStatus,
    CalibrationPack,
    CalibrationPromptExample,
    ReviewCalibrationReport,
)
from app.schemas.domain import (
    DocumentSet,
    Requirement,
    ReviewDecision,
    ReviewDecisionValue,
    ReviewerId,
    RiskFinding,
    Severity,
)


class CalibrationExampleNotFoundError(Exception):
    pass


class CalibrationActivationGateError(Exception):
    pass


class CalibrationFeedbackContextMissingError(Exception):
    pass


class ReviewCalibrationService:
    """Controlled few-shot calibration from reviewed human feedback."""

    def __init__(
        self,
        *,
        repository: InMemoryDocumentRepository,
        audit_log: InMemoryAuditLog,
    ) -> None:
        self.repository = repository
        self.audit_log = audit_log

    def record_feedback_decision(self, review_decision: ReviewDecision) -> CalibrationExample:
        existing = self.repository.get_calibration_example(
            _calibration_example_id(review_decision.review_id)
        )
        if existing is not None:
            return existing

        finding = self.repository.find_risk_finding(review_decision.finding_id)
        if finding is None:
            raise CalibrationFeedbackContextMissingError(
                f"Finding {review_decision.finding_id} not found"
            )
        document_set = self.repository.get_document_set(finding.document_set_id)
        if document_set is None:
            raise CalibrationFeedbackContextMissingError(
                f"DocumentSet {finding.document_set_id} not found"
            )

        audit_context = _finding_audit_context(audit_log=self.audit_log, finding=finding)
        example = CalibrationExample(
            calibration_example_id=_calibration_example_id(review_decision.review_id),
            source_review_id=review_decision.review_id,
            source_feedback_id=f"hfb_{review_decision.review_id}",
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
            human_decision=review_decision.decision,
            feedback_outcome=_feedback_outcome(review_decision.decision),
            reviewer_id=review_decision.reviewer_id,
            reviewer_rationale=review_decision.rationale,
            risk_statement=finding.risk_statement,
            evidence_quotes=[item.quote for item in finding.evidence_items[:3]],
            high_critical_recall_guard=finding.severity in {Severity.HIGH, Severity.CRITICAL},
            status=CalibrationExampleStatus.RAW_FEEDBACK,
            created_at=review_decision.created_at,
        )
        self.repository.add_calibration_example(example)
        self.audit_log.append(
            event_type="review_calibration_feedback_captured",
            actor_id=review_decision.reviewer_id,
            actor_type="user",
            entity_type="CalibrationExample",
            entity_id=example.calibration_example_id,
            tenant_id=example.tenant_id,
            payload={
                "source_review_id": example.source_review_id,
                "finding_id": example.finding_id,
                "document_set_id": example.document_set_id,
                "status": example.status,
                "feedback_outcome": example.feedback_outcome,
                "active_for_prompting": False,
            },
        )
        return example

    def approve_example(
        self,
        calibration_example_id: str,
        *,
        approved_by: ReviewerId,
        activate: bool = False,
        regression_gate_passed: bool = False,
        regression_gate_report_id: str | None = None,
    ) -> CalibrationExample:
        example = self.repository.get_calibration_example(calibration_example_id)
        if example is None:
            raise CalibrationExampleNotFoundError(
                f"CalibrationExample {calibration_example_id} not found"
            )

        now = datetime.now(UTC)
        update: dict[str, Any] = {
            "status": CalibrationExampleStatus.APPROVED_GOLD,
            "approved_by": example.approved_by or approved_by,
            "approved_at": example.approved_at or now,
        }
        event_type = "review_calibration_example_approved"

        if activate:
            if not regression_gate_passed or not regression_gate_report_id:
                raise CalibrationActivationGateError(
                    "Activation requires a passed regression gate report"
                )
            update.update(
                {
                    "status": CalibrationExampleStatus.ACTIVE,
                    "activated_by": approved_by,
                    "activated_at": now,
                    "regression_gate_report_id": regression_gate_report_id,
                }
            )
            event_type = "review_calibration_example_activated"

        updated = example.model_copy(update=update)
        self.repository.update_calibration_example(updated)
        self.audit_log.append(
            event_type=event_type,
            actor_id=approved_by,
            actor_type="user",
            entity_type="CalibrationExample",
            entity_id=updated.calibration_example_id,
            tenant_id=updated.tenant_id,
            payload={
                "status": updated.status,
                "source_review_id": updated.source_review_id,
                "regression_gate_report_id": updated.regression_gate_report_id,
                "active_for_prompting": updated.status == CalibrationExampleStatus.ACTIVE,
            },
        )
        return updated

    def build_pack(
        self,
        *,
        document_set: DocumentSet,
        agent_role: str,
        requirements: Sequence[Requirement],
        case_signals: Sequence[str],
        max_examples: int = 4,
    ) -> CalibrationPack:
        active_examples = self.repository.list_calibration_examples(
            tenant_id=document_set.tenant_id,
            status=CalibrationExampleStatus.ACTIVE,
            agent_role=agent_role,
        )
        scored_examples = [
            (score, example)
            for example in active_examples
            if (score := _score_example(example, document_set, requirements, case_signals)) > 0
        ]
        scored_examples.sort(
            key=lambda item: (
                -item[0],
                item[1].activated_at or item[1].approved_at or item[1].created_at,
                item[1].calibration_example_id,
            ),
            reverse=False,
        )
        selected = [example for _score, example in scored_examples[:max_examples]]
        prompt_examples = [_prompt_example(example) for example in selected]
        prompt_block = _render_prompt_block(prompt_examples)
        pack_hash = _hash_json(
            {
                "document_set_id": document_set.document_set_id,
                "agent_role": agent_role,
                "example_ids": [
                    example.calibration_example_id for example in prompt_examples
                ],
                "prompt_block": prompt_block,
            }
        )
        return CalibrationPack(
            tenant_id=document_set.tenant_id,
            document_set_id=document_set.document_set_id,
            agent_role=agent_role,
            example_ids=[example.calibration_example_id for example in prompt_examples],
            examples=prompt_examples,
            prompt_block=prompt_block,
            pack_hash=pack_hash,
        )

    def report(self, *, tenant_id: str | None = None) -> ReviewCalibrationReport:
        examples = self.repository.list_calibration_examples(tenant_id=tenant_id)
        report = ReviewCalibrationReport(
            generated_at=datetime.now(UTC),
            total_examples=len(examples),
            raw_feedback_count=_count_status(examples, CalibrationExampleStatus.RAW_FEEDBACK),
            approved_gold_count=_count_status(
                examples,
                CalibrationExampleStatus.APPROVED_GOLD,
            ),
            active_count=_count_status(examples, CalibrationExampleStatus.ACTIVE),
            examples=examples,
            limitations=[
                "Raw reviewer feedback is captured but not injected into model prompts.",
                (
                    "Only active calibration examples are eligible for few-shot prompt "
                    "injection."
                ),
                (
                    "Activation requires an explicit passed regression gate report and "
                    "does not change model weights."
                ),
                (
                    "High and Critical findings remain protected by recall guards; "
                    "calibration is not an auto-clearance rule."
                ),
            ],
        )
        self.audit_log.append(
            event_type="review_calibration_report_viewed",
            actor_id="service_review_calibration",
            actor_type="service",
            entity_type="Analytics",
            entity_id="review_calibration",
            tenant_id=tenant_id,
            payload={
                "total_examples": report.total_examples,
                "raw_feedback_count": report.raw_feedback_count,
                "approved_gold_count": report.approved_gold_count,
                "active_count": report.active_count,
            },
        )
        return report


@dataclass(frozen=True)
class _FindingAuditContext:
    agent_role: str
    prompt_version: str


def _score_example(
    example: CalibrationExample,
    document_set: DocumentSet,
    requirements: Sequence[Requirement],
    case_signals: Sequence[str],
) -> int:
    if example.document_type != document_set.declared_document_type:
        return 0

    requirement_ids = {requirement.requirement_id for requirement in requirements}
    overlap_count = len(requirement_ids.intersection(example.requirement_references))
    same_process_area = example.process_area == document_set.declared_process_area
    signal_text = " ".join(case_signals).lower()
    risk_signal_match = bool(
        example.risk_category and example.risk_category.lower() in signal_text
    )

    if overlap_count == 0 and not same_process_area and not risk_signal_match:
        return 0

    score = 10
    score += overlap_count * 5
    if same_process_area:
        score += 3
    if risk_signal_match:
        score += 1
    if example.high_critical_recall_guard:
        score += 1
    return score


def _prompt_example(example: CalibrationExample) -> CalibrationPromptExample:
    return CalibrationPromptExample(
        calibration_example_id=example.calibration_example_id,
        human_decision=example.human_decision,
        feedback_outcome=example.feedback_outcome,
        risk_category=example.risk_category,
        original_severity=example.original_severity,
        requirement_references=example.requirement_references,
        risk_statement=example.risk_statement,
        reviewer_rationale=example.reviewer_rationale,
        evidence_quotes=example.evidence_quotes,
    )


def _render_prompt_block(examples: Sequence[CalibrationPromptExample]) -> str:
    if not examples:
        return ""

    lines = [
        "Kontrollierte Kalibrierungsbeispiele aus menschlicher QA-Pruefung:",
        (
            "Diese Beispiele sind kein Fine-Tuning und keine neue SOP. Uebertrage sie "
            "nur, wenn Evidenz, Requirement und Kontext der aktuellen Pruefung "
            "vergleichbar sind."
        ),
        (
            "High- und Critical-Recall-Grenzen bleiben aktiv. Bei Unsicherheit melde "
            "den Punkt fuer menschliche Pruefung statt ihn still zu unterdruecken."
        ),
    ]
    for index, example in enumerate(examples, start=1):
        evidence = " | ".join(example.evidence_quotes[:2]) or "keine Evidenzquote gespeichert"
        requirements = ", ".join(example.requirement_references) or "keine Requirement-ID"
        lines.extend(
            [
                f"Beispiel {index} ({example.calibration_example_id}):",
                f"- Menschliche Entscheidung: {example.human_decision}",
                f"- Feedback-Ergebnis: {example.feedback_outcome}",
                f"- Risikokategorie/Severity: {example.risk_category}/{example.original_severity}",
                f"- Requirements: {requirements}",
                f"- Urspruenglicher KI-Claim: {example.risk_statement}",
                f"- Expertenbegruendung: {example.reviewer_rationale}",
                f"- Evidenz: {evidence}",
            ]
        )
    return "\n".join(lines)


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


def _count_status(
    examples: Sequence[CalibrationExample],
    status: CalibrationExampleStatus,
) -> int:
    return sum(1 for example in examples if example.status == status)


def _calibration_example_id(review_id: str) -> str:
    return f"cal_{sha256(review_id.encode()).hexdigest()[:20]}"


def _hash_json(payload: dict[str, object]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()
