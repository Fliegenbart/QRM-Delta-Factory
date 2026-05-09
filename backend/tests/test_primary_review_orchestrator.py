from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.audit.events import audit_log
from app.db.in_memory import repository
from app.main import app
from app.schemas.domain import Claim, DocumentSet, RequirementSet
from app.services.review_orchestrator import (
    MockModelProvider,
    PrimaryReviewOrchestrator,
    ReviewerAgent,
)


@pytest.fixture(autouse=True)
def reset_state() -> None:
    repository.reset()
    audit_log.clear()
    repository.create_requirement_set(_requirement_set())
    repository.create_document_set(_document_set())
    repository.replace_claim_ledger(document_set_id="ds_review_demo", claims=_claims())


def test_primary_review_endpoint_creates_findings_model_runs_and_audit_events() -> None:
    client = TestClient(app)

    response = client.post("/document-sets/ds_review_demo/run-primary-review")

    assert response.status_code == 200
    payload = response.json()
    assert payload["document_set_id"] == "ds_review_demo"
    assert {finding["risk_category"] for finding in payload["findings"]} >= {
        "deviation_management",
        "batch_impact_assessment",
    }
    assert all(finding["evidence_items"] for finding in payload["findings"])
    assert all(finding["verification_result"] is not None for finding in payload["findings"])
    assert len(payload["model_runs"]) == 6
    assert len(repository.list_model_runs("ds_review_demo")) == 6
    assert repository.list_raw_model_outputs()
    assert "primary_review_run_completed" in [event.event_type for event in audit_log.list_events()]
    assert "model_run_recorded" in [event.event_type for event in audit_log.list_events()]


def test_model_run_audit_includes_tenant_provider_model_id_prompt_and_hashes() -> None:
    orchestrator = PrimaryReviewOrchestrator(
        repository=repository,
        audit_log=audit_log,
        agents=[
            ReviewerAgent(
                agent_id="agent_auditability",
                role="DeviationReviewer",
                prompt_version="deviation_reviewer_v1",
                applicable_risk_categories=["deviation_management"],
                provider=MockModelProvider(),
            )
        ],
    )

    result = orchestrator.run_primary_review("ds_review_demo")

    assert result.model_runs[0].configured_model_id == "mock-reviewer-v0.1"
    completed_event = next(
        event for event in audit_log.list_events() if event.event_type == "model_run_completed"
    )
    assert completed_event.tenant_id == "tenant_demo_pharma"
    assert completed_event.input_hash == result.model_runs[0].input_hash
    assert completed_event.output_hash == result.model_runs[0].output_hash
    assert completed_event.payload["provider"] == "mock"
    assert completed_event.payload["model_name"] == "mock-reviewer"
    assert completed_event.payload["model_version"] == "0.1.0"
    assert completed_event.payload["configured_model_id"] == "mock-reviewer-v0.1"
    assert completed_event.payload["prompt_version"] == "deviation_reviewer_v1"


def test_orchestrator_runs_review_agents_in_parallel() -> None:
    agents = [
        ReviewerAgent(
            agent_id=f"agent_parallel_{index}",
            role=f"ParallelReviewer{index}",
            prompt_version="parallel-test-v0.1",
            applicable_risk_categories=["parallel"],
            provider=MockModelProvider(delay_seconds=0.2),
        )
        for index in range(3)
    ]
    orchestrator = PrimaryReviewOrchestrator(
        repository=repository,
        audit_log=audit_log,
        agents=agents,
    )

    started = time.perf_counter()
    result = orchestrator.run_primary_review("ds_review_demo")
    elapsed = time.perf_counter() - started

    assert elapsed < 0.5
    assert len(result.model_runs) == 3


def test_invalid_model_output_is_caught_as_failed_model_run() -> None:
    agents = [
        ReviewerAgent(
            agent_id="agent_bad",
            role="BadReviewer",
            prompt_version="bad-v0.1",
            applicable_risk_categories=["bad"],
            provider=BadOutputProvider(),
        ),
        ReviewerAgent(
            agent_id="agent_good",
            role="DeviationReviewer",
            prompt_version="good-v0.1",
            applicable_risk_categories=["deviation_management"],
            provider=MockModelProvider(),
        ),
    ]
    orchestrator = PrimaryReviewOrchestrator(
        repository=repository,
        audit_log=audit_log,
        agents=agents,
    )

    result = orchestrator.run_primary_review("ds_review_demo")

    assert len(result.failed_model_runs) == 1
    assert result.failed_model_runs[0].status == "failed"
    assert result.findings
    event_types = [event.event_type for event in audit_log.list_events()]
    assert "model_run_failed" in event_types
    assert "failed_model_run" in event_types


def test_no_findings_requires_coverage_summary() -> None:
    agents = [
        ReviewerAgent(
            agent_id="agent_no_coverage",
            role="NoCoverageReviewer",
            prompt_version="no-coverage-v0.1",
            applicable_risk_categories=["no_coverage"],
            provider=MissingCoverageProvider(),
        )
    ]
    orchestrator = PrimaryReviewOrchestrator(
        repository=repository,
        audit_log=audit_log,
        agents=agents,
    )

    result = orchestrator.run_primary_review("ds_review_demo")

    assert not result.findings
    assert len(result.failed_model_runs) == 1


class BadOutputProvider:
    provider_name = "mock"
    model_name = "bad-output-model"
    model_version = "0.1.0"
    configured_model_id = "bad-output-model-v0.1"

    def run_structured(
        self,
        prompt: str,
        input_schema: dict[str, Any],
        output_schema: type[Any],
    ) -> dict[str, Any]:
        return {
            "findings": [
                {
                    "finding_id": "finding_missing_evidence",
                    "document_set_id": "ds_review_demo",
                    "risk_category": "bad",
                    "severity": "medium",
                    "likelihood": 2,
                    "detectability": 2,
                    "risk_statement": "This finding has no evidence and must fail validation.",
                    "evidence_items": [],
                    "requirement_references": [],
                    "missing_information": [],
                    "model_provider": "mock",
                    "model_name": "bad-output-model",
                    "model_version": "0.1.0",
                    "prompt_version": "bad-v0.1",
                    "evidence_support": "weak",
                    "recommended_action": "Do not auto-clear.",
                    "auto_close_allowed": False,
                    "status": "needs_human_review",
                }
            ],
            "coverage_summary": "Bad output attempted to emit a finding without evidence.",
        }


class MissingCoverageProvider:
    provider_name = "mock"
    model_name = "missing-coverage-model"
    model_version = "0.1.0"
    configured_model_id = "missing-coverage-model-v0.1"

    def run_structured(
        self,
        prompt: str,
        input_schema: dict[str, Any],
        output_schema: type[Any],
    ) -> dict[str, Any]:
        return {"findings": []}


def _document_set() -> DocumentSet:
    return DocumentSet(
        document_set_id="ds_review_demo",
        tenant_id="tenant_demo_pharma",
        requirement_set_id="rset_review_demo_2026",
        upload_timestamp=datetime.now(UTC),
        document_ids=["doc_review_deviation"],
        declared_document_type="deviation",
        declared_process_area="aseptic_filling",
        uploaded_by="user_qrm_author",
        status="ready_for_orchestration",
    )


def _requirement_set() -> RequirementSet:
    return RequirementSet(
        requirement_set_id="rset_review_demo_2026",
        tenant_id="tenant_demo_pharma",
        name="Review Demo Requirements",
        version="2026.1",
        imported_at=datetime.now(UTC),
        imported_by="user_quality_admin",
        active=True,
        requirements=[
            {
                "requirement_id": "req_deviation_documented_impact_assessment",
                "source_type": "internal_sop",
                "source_name": "SOP-DEV-001",
                "source_version": "4.2",
                "section": "6.3",
                "requirement_text": "Deviation records need documented product impact assessment.",
                "applies_to_document_types": ["deviation"],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": "high",
                "required_evidence": ["deviation record", "impact assessment"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            },
            {
                "requirement_id": "req_batch_impact_disposition_trace",
                "source_type": "checklist",
                "source_name": "QRM Batch Impact Checklist",
                "source_version": "2.0",
                "section": "3.2",
                "requirement_text": (
                    "Batch impact must link affected batches to disposition rationale."
                ),
                "applies_to_document_types": ["deviation"],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": "medium",
                "required_evidence": ["batch record excerpt"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            },
        ],
    )


def _claims() -> list[Claim]:
    return [
        _claim(
            "claim_deviation",
            "deviation_description",
            "deviation_id",
            "DEV-2026-014",
            "Deviation DEV-2026-014 for Batch BATCH-001.",
        ),
        _claim(
            "claim_batch",
            "batch_identifier",
            "batch_identifier",
            "BATCH-001",
            "Batch BATCH-001",
        ),
        _claim(
            "claim_impact",
            "impact_assessment",
            "impact_assessment",
            "possible false accept of defective container",
            "Impact assessment: possible false accept of defective container.",
        ),
        _claim(
            "claim_qa_pending",
            "qa_approval",
            "qa_approval",
            "pending",
            "QA approval: pending.",
        ),
    ]


def _claim(
    claim_id: str,
    claim_type: str,
    normalized_subject: str,
    normalized_object: str,
    quote: str,
) -> Claim:
    return Claim(
        claim_id=claim_id,
        document_id="doc_review_deviation",
        chunk_id="chunk_review_deviation_p1",
        page=1,
        claim_type=claim_type,
        normalized_subject=normalized_subject,
        normalized_predicate="states",
        normalized_object=normalized_object,
        raw_text_quote=quote,
        confidence=0.9,
        dependencies=[],
        created_by_model="mock-claim-extractor-v0.1",
        prompt_version="mock-claim-ledger-v0.1",
    )
