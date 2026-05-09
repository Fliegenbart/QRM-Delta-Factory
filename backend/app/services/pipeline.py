from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from hashlib import sha256
from typing import Any, Protocol

from app.audit.events import InMemoryAuditLog
from app.core.config import get_settings
from app.db.in_memory import InMemoryDocumentRepository
from app.schemas.domain import DocumentSet, DocumentSetStatus, ModelRunStatus, ParsingStatus
from app.schemas.pipeline import PipelineRun, PipelineRunStatus
from app.schemas.risk import RiskDecision, RiskDecisionClass
from app.services.adversarial_review import AdversarialReviewService
from app.services.claim_ledger import ClaimLedgerService, MockClaimExtractor
from app.services.review_orchestrator import PrimaryReviewOrchestrator
from app.services.review_pack import ReviewPackService
from app.services.risk_fusion import RiskFusionService
from app.verifiers.evidence import EvidenceVerifierService

PIPELINE_CONFIG_VERSION = "pipeline-config-v0.1"


class PipelineDocumentSetNotFoundError(Exception):
    pass


class PipelineRunNotFoundError(Exception):
    pass


class PipelineJobQueue(Protocol):
    """Future async boundary for Celery/RQ-backed dispatch."""

    def enqueue(self, document_set_id: str) -> PipelineRun:
        ...


class PipelineService:
    def __init__(
        self,
        *,
        repository: InMemoryDocumentRepository,
        audit_log: InMemoryAuditLog,
        claim_ledger_service: ClaimLedgerService | None = None,
        primary_review_orchestrator: PrimaryReviewOrchestrator | None = None,
        adversarial_review_service: AdversarialReviewService | None = None,
        evidence_verifier_service: EvidenceVerifierService | None = None,
        risk_fusion_service: RiskFusionService | None = None,
        review_pack_service: ReviewPackService | None = None,
        config_version: str = PIPELINE_CONFIG_VERSION,
    ) -> None:
        self.repository = repository
        self.audit_log = audit_log
        self.claim_ledger_service = claim_ledger_service or ClaimLedgerService(
            repository=repository,
            audit_log=audit_log,
            extractor=MockClaimExtractor(),
        )
        self.primary_review_orchestrator = primary_review_orchestrator or PrimaryReviewOrchestrator(
            repository=repository,
            audit_log=audit_log,
        )
        self.adversarial_review_service = adversarial_review_service or AdversarialReviewService(
            repository=repository,
            audit_log=audit_log,
        )
        self.evidence_verifier_service = evidence_verifier_service or EvidenceVerifierService(
            repository=repository,
            audit_log=audit_log,
        )
        self.risk_fusion_service = risk_fusion_service or RiskFusionService(
            repository=repository,
            audit_log=audit_log,
        )
        self.review_pack_service = review_pack_service or ReviewPackService(
            repository=repository,
            audit_log=audit_log,
        )
        self.config_version = config_version

    def run_pipeline(self, document_set_id: str) -> PipelineRun:
        document_set = self.repository.get_document_set(document_set_id)
        if document_set is None:
            raise PipelineDocumentSetNotFoundError(f"DocumentSet {document_set_id} not found")

        started_at = datetime.now(UTC)
        pipeline_run = PipelineRun(
            pipeline_run_id=_pipeline_run_id(document_set_id, started_at),
            document_set_id=document_set_id,
            status=PipelineRunStatus.RUNNING,
            started_at=started_at,
            completed_at=None,
            failed_step=None,
            error_summary=None,
            config_version=self.config_version,
        )
        self.repository.add_pipeline_run(pipeline_run)
        self._audit(
            event_type="pipeline_run_started",
            pipeline_run=pipeline_run,
            document_set=document_set,
            payload={"config_version": self.config_version},
        )

        current_step: str | None = None
        risk_decision: RiskDecision | None = None
        try:
            steps: list[tuple[str, Callable[[str], Any]]] = [
                ("parse_document_set", self._parse_document_set),
                ("quality_gate", self._quality_gate),
                ("requirement_retrieval", self._requirement_retrieval),
                ("claim_ledger_extraction", self._claim_ledger_extraction),
                ("primary_multi_agent_review", self._primary_multi_agent_review),
                ("evidence_verification", self._evidence_verification),
                ("adversarial_review", self._adversarial_review),
                ("adversarial_evidence_verification", self._adversarial_evidence_verification),
                ("risk_fusion", self._risk_fusion),
                ("review_pack_generation", self._review_pack_generation),
                ("audit_trail_completion", self._audit_trail_completion),
            ]
            for step_name, step in steps:
                current_step = step_name
                step_result = step(document_set_id)
                if isinstance(step_result, RiskDecision):
                    risk_decision = step_result
                self._audit_step_completed(
                    pipeline_run=pipeline_run,
                    document_set=document_set,
                    step_name=step_name,
                    step_result=step_result,
                )

            completed_status = self._completed_status(
                document_set_id=document_set_id,
                risk_decision=risk_decision,
            )
            completed_run = pipeline_run.model_copy(
                update={
                    "status": completed_status,
                    "completed_at": datetime.now(UTC),
                }
            )
            self.repository.update_pipeline_run(completed_run)
            self._audit(
                event_type="pipeline_run_completed",
                pipeline_run=completed_run,
                document_set=document_set,
                payload={
                    "status": completed_run.status,
                    "risk_decision": risk_decision.decision if risk_decision else None,
                    "auto_clear_allowed": risk_decision.auto_clear_allowed
                    if risk_decision
                    else False,
                },
            )
            return completed_run
        except Exception as exc:
            failed_run = pipeline_run.model_copy(
                update={
                    "status": PipelineRunStatus.FAILED,
                    "completed_at": datetime.now(UTC),
                    "failed_step": current_step,
                    "error_summary": str(exc),
                }
            )
            self.repository.update_pipeline_run(failed_run)
            self._mark_document_set_for_human_review(document_set)
            self._audit(
                event_type="pipeline_run_failed",
                pipeline_run=failed_run,
                document_set=document_set,
                payload={
                    "failed_step": current_step,
                    "error_summary": str(exc),
                    "auto_clear_allowed": False,
                },
            )
            return failed_run

    def get_pipeline_run(self, pipeline_run_id: str) -> PipelineRun:
        pipeline_run = self.repository.get_pipeline_run(pipeline_run_id)
        if pipeline_run is None:
            raise PipelineRunNotFoundError(f"PipelineRun {pipeline_run_id} not found")
        return pipeline_run

    def _parse_document_set(self, document_set_id: str) -> dict[str, Any]:
        document_set = self._document_set(document_set_id)
        if not document_set.document_ids:
            raise ValueError("No uploaded documents found for DocumentSet")
        documents = [
            self.repository.get_document(document_id)
            for document_id in document_set.document_ids
        ]
        if any(document is None for document in documents):
            raise ValueError("DocumentSet references a missing document")
        missing_chunks = [
            document.document_id
            for document in documents
            if document is not None and not self.repository.list_chunks(document.document_id)
        ]
        if missing_chunks:
            raise ValueError(f"Parsed chunks missing for document(s): {', '.join(missing_chunks)}")
        parser_failures = [
            document.document_id
            for document in documents
            if document is not None and document.parsing_status == ParsingStatus.FAILED
        ]
        return {
            "document_count": len(document_set.document_ids),
            "parser_failure_count": len(parser_failures),
        }

    def _quality_gate(self, document_set_id: str) -> dict[str, Any]:
        document_set = self._document_set(document_set_id)
        documents = [
            document
            for document_id in document_set.document_ids
            if (document := self.repository.get_document(document_id)) is not None
        ]
        threshold = get_settings().parsing_quality_threshold
        quality_score = min(
            (document.parsing_quality_score for document in documents),
            default=1.0,
        )
        if quality_score < threshold:
            self._mark_document_set_for_human_review(document_set)
        return {
            "document_quality_score": quality_score,
            "threshold": threshold,
            "passed": quality_score >= threshold,
        }

    def _requirement_retrieval(self, document_set_id: str) -> dict[str, Any]:
        document_set = self._document_set(document_set_id)
        requirement_set = self.repository.get_requirement_set(document_set.requirement_set_id)
        if requirement_set is None:
            raise ValueError(f"RequirementSet {document_set.requirement_set_id} not found")
        self.audit_log.append(
            event_type="requirements_retrieved",
            actor_id="service_pipeline",
            actor_type="service",
            entity_type="RequirementSet",
            entity_id=requirement_set.requirement_set_id,
            tenant_id=document_set.tenant_id,
            payload={
                "document_set_id": document_set_id,
                "requirement_set_id": requirement_set.requirement_set_id,
                "requirement_count": len(requirement_set.requirements),
                "requirement_ids": [
                    requirement.requirement_id for requirement in requirement_set.requirements
                ],
            },
        )
        return {
            "requirement_set_id": requirement_set.requirement_set_id,
            "requirement_count": len(requirement_set.requirements),
        }

    def _claim_ledger_extraction(self, document_set_id: str) -> dict[str, Any]:
        claims = self.claim_ledger_service.get_or_build_claim_ledger(document_set_id)
        return {"claim_count": len(claims)}

    def _primary_multi_agent_review(self, document_set_id: str) -> dict[str, Any]:
        result = self.primary_review_orchestrator.run_primary_review(document_set_id)
        return {
            "finding_count": len(result.findings),
            "model_run_count": len(result.model_runs),
            "failed_model_run_count": len(result.failed_model_runs),
            "coverage_summary_count": len(result.coverage_summaries),
        }

    def _evidence_verification(self, document_set_id: str) -> dict[str, Any]:
        findings = self.repository.list_risk_findings(document_set_id)
        verified_findings = self.evidence_verifier_service.verify_findings(
            document_set_id,
            findings,
        )
        return {"verified_finding_count": len(verified_findings)}

    def _adversarial_review(self, document_set_id: str) -> dict[str, Any]:
        result = self.adversarial_review_service.run_adversarial_review(document_set_id)
        return {
            "additional_finding_count": len(result.additional_findings),
            "challenge_count": len(result.challenged_findings)
            + len(result.challenged_no_issue_claims),
            "unresolved_question_count": len(result.unresolved_questions),
        }

    def _adversarial_evidence_verification(self, document_set_id: str) -> dict[str, Any]:
        findings = self.repository.list_risk_fusion_findings(document_set_id)
        if not findings:
            return {"verified_finding_count": 0}
        verified_findings = self.evidence_verifier_service.verify_findings(
            document_set_id,
            findings,
        )
        self.repository.replace_risk_fusion_findings(
            document_set_id=document_set_id,
            findings=verified_findings,
        )
        return {"verified_finding_count": len(verified_findings)}

    def _risk_fusion(self, document_set_id: str) -> RiskDecision:
        return self.risk_fusion_service.run_risk_fusion(document_set_id)

    def _review_pack_generation(self, document_set_id: str) -> dict[str, Any]:
        review_pack = self.review_pack_service.get_review_pack(document_set_id)
        return {
            "review_pack_id": review_pack.review_pack_id,
            "top_risk_count": len(review_pack.top_risks),
            "evidence_row_count": len(review_pack.evidence_table),
        }

    def _audit_trail_completion(self, document_set_id: str) -> dict[str, Any]:
        document_set = self._document_set(document_set_id)
        matching_events = [
            event
            for event in self.audit_log.list_events()
            if event.payload.get("document_set_id") == document_set_id
            or event.entity_id == document_set_id
        ]
        self.audit_log.append(
            event_type="pipeline_audit_trail_completed",
            actor_id="service_pipeline",
            actor_type="service",
            entity_type="DocumentSet",
            entity_id=document_set_id,
            tenant_id=document_set.tenant_id,
            payload={
                "document_set_id": document_set_id,
                "audit_event_count_before_completion": len(matching_events),
            },
        )
        return {"audit_event_count_before_completion": len(matching_events)}

    def _completed_status(
        self,
        *,
        document_set_id: str,
        risk_decision: RiskDecision | None,
    ) -> PipelineRunStatus:
        document_set = self._document_set(document_set_id)
        failed_model_runs = [
            run
            for run in self.repository.list_model_runs(document_set_id)
            if run.status == ModelRunStatus.FAILED
        ]
        if failed_model_runs:
            return PipelineRunStatus.NEEDS_HUMAN_REVIEW
        if document_set.status == DocumentSetStatus.NEEDS_HUMAN_REVIEW:
            return PipelineRunStatus.NEEDS_HUMAN_REVIEW
        if risk_decision is None:
            return PipelineRunStatus.NEEDS_HUMAN_REVIEW
        if risk_decision.decision in {
            RiskDecisionClass.INSUFFICIENT_DOCUMENT_QUALITY,
            RiskDecisionClass.OUT_OF_SCOPE,
            RiskDecisionClass.BLOCKED_DUE_TO_MODEL_FAILURE,
            RiskDecisionClass.BLOCKED_DUE_TO_UNVERIFIED_HIGH_RISK,
            RiskDecisionClass.NEEDS_MORE_INFORMATION,
        }:
            return PipelineRunStatus.NEEDS_HUMAN_REVIEW
        return PipelineRunStatus.COMPLETED

    def _document_set(self, document_set_id: str) -> DocumentSet:
        document_set = self.repository.get_document_set(document_set_id)
        if document_set is None:
            raise PipelineDocumentSetNotFoundError(f"DocumentSet {document_set_id} not found")
        return document_set

    def _mark_document_set_for_human_review(self, document_set: DocumentSet) -> None:
        self.repository.update_document_set(
            document_set.model_copy(update={"status": DocumentSetStatus.NEEDS_HUMAN_REVIEW})
        )

    def _audit_step_completed(
        self,
        *,
        pipeline_run: PipelineRun,
        document_set: DocumentSet,
        step_name: str,
        step_result: Any,
    ) -> None:
        self._audit(
            event_type="pipeline_step_completed",
            pipeline_run=pipeline_run,
            document_set=document_set,
            payload={
                "step": step_name,
                "step_result": _safe_step_summary(step_result),
            },
        )

    def _audit(
        self,
        *,
        event_type: str,
        pipeline_run: PipelineRun,
        document_set: DocumentSet,
        payload: dict[str, Any],
    ) -> None:
        self.audit_log.append(
            event_type=event_type,
            actor_id="service_pipeline",
            actor_type="service",
            entity_type="PipelineRun",
            entity_id=pipeline_run.pipeline_run_id,
            tenant_id=document_set.tenant_id,
            payload={
                "document_set_id": pipeline_run.document_set_id,
                "pipeline_run_id": pipeline_run.pipeline_run_id,
                **payload,
            },
        )


def _pipeline_run_id(document_set_id: str, started_at: datetime) -> str:
    seed = f"{document_set_id}|{started_at.isoformat()}"
    return f"prun_{sha256(seed.encode()).hexdigest()[:20]}"


def _safe_step_summary(step_result: Any) -> dict[str, Any]:
    if isinstance(step_result, RiskDecision):
        return {
            "decision": step_result.decision,
            "auto_clear_allowed": step_result.auto_clear_allowed,
            "auto_clear_blocker_count": len(step_result.auto_clear_blockers),
        }
    if isinstance(step_result, dict):
        return step_result
    return {"result_type": type(step_result).__name__}
