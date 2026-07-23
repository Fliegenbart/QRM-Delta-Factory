from __future__ import annotations

from datetime import UTC, datetime, timedelta
from hashlib import sha256
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.agents.providers import BaseModelProvider
from app.audit.events import audit_log
from app.db.in_memory import repository
from app.main import app
from app.schemas.domain import Document, DocumentChunk, DocumentSet, RequirementSet
from app.schemas.pipeline import PipelineRun, PipelineRunStatus
from app.services import pipeline as pipeline_module
from app.services.pipeline import PipelineService
from app.services.review_orchestrator import (
    MockModelProvider,
    PrimaryReviewOrchestrator,
    ReviewerAgent,
)
from app.services.review_pack import ReviewPackService


@pytest.fixture(autouse=True)
def reset_state() -> None:
    repository.reset()
    audit_log.clear()


def test_pipeline_endpoint_runs_end_to_end_after_document_upload() -> None:
    repository.create_requirement_set(_requirement_set())
    client = TestClient(app)
    create_response = client.post(
        "/document-sets",
        json={
            "tenant_id": "tenant_demo_pharma",
            "requirement_set_id": "rset_pipeline_demo",
            "declared_document_type": "change_control",
            "declared_process_area": "aseptic_filling",
            "uploaded_by": "user_qrm_author",
        },
    )
    document_set_id = create_response.json()["document_set_id"]
    upload_response = client.post(
        f"/document-sets/{document_set_id}/documents",
        files={
            "file": (
                "change-control.txt",
                b"Acceptance criterion: AVI threshold review record present. 2026-05-09.",
                "text/plain",
            )
        },
        data={"uploaded_by": "user_qrm_author"},
    )

    response = client.post(f"/document-sets/{document_set_id}/pipeline-runs")

    assert create_response.status_code == 201
    assert upload_response.status_code == 201
    assert response.status_code == 202
    payload = response.json()
    assert payload["document_set_id"] == document_set_id
    assert payload["status"] == "running"
    get_response = client.get(f"/pipeline-runs/{payload['pipeline_run_id']}")
    assert get_response.status_code == 200
    completed_payload = get_response.json()
    assert completed_payload["status"] == "completed"
    assert completed_payload["failed_step"] is None
    assert completed_payload["completed_at"] is not None
    assert completed_payload["model_manifest"]
    assert {
        entry["agent_role"]: entry["configured_model_id"]
        for entry in completed_payload["model_manifest"]
    }["ContradictionHunter"]
    assert all("knowledge_pack_ids" in entry for entry in completed_payload["model_manifest"])
    assert all("case_signals" in entry for entry in completed_payload["model_manifest"])
    assert repository.get_latest_risk_decision(document_set_id) is not None

    review_pack = ReviewPackService(repository=repository, audit_log=audit_log).get_review_pack(
        document_set_id
    )
    assert review_pack.document_set_id == document_set_id
    assert any(
        event.event_type == "pipeline_run_completed"
        and event.payload["document_set_id"] == document_set_id
        for event in audit_log.list_events()
    )

    assert completed_payload["pipeline_run_id"] == payload["pipeline_run_id"]


def test_model_run_failure_in_pipeline_does_not_allow_auto_clear() -> None:
    _setup_document_set_for_model_failure()
    orchestrator = PrimaryReviewOrchestrator(
        repository=repository,
        audit_log=audit_log,
        agents=[
            ReviewerAgent(
                agent_id="agent_gmp_data_integrity",
                role="GMPDataIntegrityReviewer",
                prompt_version="pipeline-test-v0.1",
                applicable_risk_categories=["data_integrity"],
                provider=MockModelProvider(),
            ),
            ReviewerAgent(
                agent_id="agent_deviation_failed",
                role="DeviationReviewer",
                prompt_version="pipeline-test-v0.1",
                applicable_risk_categories=["deviation_management"],
                provider=FailingProvider(),
            ),
        ],
    )
    service = PipelineService(
        repository=repository,
        audit_log=audit_log,
        primary_review_orchestrator=orchestrator,
    )

    pipeline_run = service.run_pipeline("ds_pipeline_failure")

    decision = repository.get_latest_risk_decision("ds_pipeline_failure")
    assert pipeline_run.status == "needs_human_review"
    assert pipeline_run.failed_step is None
    assert {
        item.agent_role: item.configured_model_id
        for item in pipeline_run.model_manifest
    }["DeviationReviewer"] == "failing-reviewer-v0.1"
    assert all(item.knowledge_pack_ids for item in pipeline_run.model_manifest)
    assert decision is not None
    assert decision.auto_clear_allowed is False
    assert decision.decision == "blocked_due_to_model_failure"
    assert "failed model run affects review coverage" in decision.auto_clear_blockers
    document_set = repository.get_document_set("ds_pipeline_failure")
    assert document_set is not None
    assert document_set.status == "needs_human_review"
    assert ReviewPackService(repository=repository, audit_log=audit_log).get_review_pack(
        "ds_pipeline_failure"
    )


def test_pipeline_marks_run_failed_when_parse_step_has_no_uploaded_documents() -> None:
    repository.create_requirement_set(_requirement_set())
    repository.create_document_set(_document_set(document_set_id="ds_pipeline_empty"))

    pipeline_run = PipelineService(repository=repository, audit_log=audit_log).run_pipeline(
        "ds_pipeline_empty"
    )

    assert pipeline_run.status == "failed"
    assert pipeline_run.failed_step == "parse_document_set"
    assert "No uploaded documents" in str(pipeline_run.error_summary)
    assert any(event.event_type == "pipeline_run_failed" for event in audit_log.list_events())


def test_pipeline_keeps_no_text_document_as_human_review_instead_of_failed() -> None:
    repository.create_requirement_set(_requirement_set())
    repository.create_document_set(_document_set(document_set_id="ds_pipeline_no_text"))
    repository.add_document(
        document=_document(document_set_id="ds_pipeline_no_text", parsing_quality_score=0),
        chunks=[],
    )

    pipeline_run = PipelineService(repository=repository, audit_log=audit_log).run_pipeline(
        "ds_pipeline_no_text"
    )

    assert pipeline_run.status == "needs_human_review"
    assert pipeline_run.failed_step is None
    assert pipeline_run.error_summary is None
    document_set = repository.get_document_set("ds_pipeline_no_text")
    assert document_set is not None
    assert document_set.status == "needs_human_review"


def test_pipeline_service_exposes_an_idempotent_start_contract() -> None:
    assert hasattr(PipelineService, "start_or_get_pipeline_run")
    assert hasattr(pipeline_module, "PipelineRunRetryRequiredError")


def test_pipeline_start_returns_the_existing_active_run_without_executing_again() -> None:
    repository.create_requirement_set(_requirement_set())
    repository.create_document_set(_document_set(document_set_id="ds_pipeline_active"))
    service = PipelineService(repository=repository, audit_log=audit_log)

    first_run = service.start_or_get_pipeline_run("ds_pipeline_active")
    duplicate_run = service.start_or_get_pipeline_run("ds_pipeline_active")

    assert first_run.status == PipelineRunStatus.RUNNING
    assert duplicate_run.pipeline_run_id == first_run.pipeline_run_id
    assert len(repository.pipeline_runs) == 1


def test_pipeline_start_marks_an_expired_running_run_failed_before_explicit_retry() -> None:
    repository.create_requirement_set(_requirement_set())
    repository.create_document_set(_document_set(document_set_id="ds_pipeline_stale"))
    expired_run = PipelineRun(
        pipeline_run_id="prun_expired",
        document_set_id="ds_pipeline_stale",
        status=PipelineRunStatus.RUNNING,
        started_at=datetime.now(UTC) - timedelta(seconds=61),
        config_version="pipeline-config-v0.1",
    )
    repository.add_pipeline_run(expired_run)
    service = PipelineService(
        repository=repository,
        audit_log=audit_log,
        pipeline_lease_seconds=60,
    )

    with pytest.raises(pipeline_module.PipelineRunRetryRequiredError):
        service.start_or_get_pipeline_run("ds_pipeline_stale")

    replacement_run = service.start_or_get_pipeline_run("ds_pipeline_stale", retry=True)

    recovered_run = repository.get_pipeline_run("prun_expired")
    document_set = repository.get_document_set("ds_pipeline_stale")
    assert recovered_run is not None
    assert recovered_run.status == PipelineRunStatus.FAILED
    assert recovered_run.failed_step == "lease_expired"
    assert recovered_run.completed_at is not None
    assert replacement_run.status == PipelineRunStatus.RUNNING
    assert replacement_run.pipeline_run_id != expired_run.pipeline_run_id
    assert document_set is not None
    assert document_set.status == "needs_human_review"


def test_pipeline_requires_explicit_retry_after_a_terminal_run() -> None:
    repository.create_requirement_set(_requirement_set())
    repository.create_document_set(_document_set(document_set_id="ds_pipeline_terminal"))
    terminal_run = PipelineRun(
        pipeline_run_id="prun_terminal",
        document_set_id="ds_pipeline_terminal",
        status=PipelineRunStatus.COMPLETED,
        started_at=datetime.now(UTC) - timedelta(minutes=1),
        completed_at=datetime.now(UTC),
        config_version="pipeline-config-v0.1",
    )
    repository.add_pipeline_run(terminal_run)
    service = PipelineService(repository=repository, audit_log=audit_log)

    with pytest.raises(pipeline_module.PipelineRunRetryRequiredError):
        service.start_or_get_pipeline_run("ds_pipeline_terminal")

    retry_run = service.start_or_get_pipeline_run("ds_pipeline_terminal", retry=True)

    assert retry_run.status == PipelineRunStatus.RUNNING
    assert retry_run.pipeline_run_id != terminal_run.pipeline_run_id


def test_pipeline_manifest_uses_latest_attempt_per_reviewer() -> None:
    _setup_document_set_for_model_failure()
    service = PipelineService(repository=repository, audit_log=audit_log)
    service.run_pipeline("ds_pipeline_failure")

    original = repository.list_model_runs("ds_pipeline_failure")[0]
    repository.add_model_run(
        document_set_id="ds_pipeline_failure",
        model_run=original.model_copy(
            update={
                "status": "failed",
                "completed_at": original.completed_at + timedelta(seconds=1),
            }
        ),
    )
    repository.add_model_run(
        document_set_id="ds_pipeline_failure",
        model_run=original.model_copy(
            update={
                "status": "succeeded",
                "completed_at": original.completed_at + timedelta(seconds=2),
            }
        ),
    )

    manifest = service._model_manifest("ds_pipeline_failure")

    assert len(manifest) == 7
    assert all(item.status == "succeeded" for item in manifest)


class FailingProvider(BaseModelProvider):
    def __init__(self) -> None:
        super().__init__(
            provider_name="mock",
            model_name="failing-reviewer",
            model_version="0.1.0",
            configured_model_id="failing-reviewer-v0.1",
            prompt_version="pipeline-test-v0.1",
            external_calls_required=False,
        )

    def _run_structured_once(
        self,
        *,
        prompt: str,
        input_schema: dict[str, Any],
        output_schema: type[Any],
    ) -> dict[str, Any]:
        raise RuntimeError("simulated model failure")


def _setup_document_set_for_model_failure() -> None:
    repository.create_requirement_set(
        _requirement_set(document_type="deviation", criticality="medium")
    )
    repository.create_document_set(
        _document_set(
            document_set_id="ds_pipeline_failure",
            document_type="deviation",
            process_area="aseptic_filling",
        )
    )
    repository.add_document(document=_document(), chunks=[_chunk()])


def _document_set(
    *,
    document_set_id: str,
    document_type: str = "change_control",
    process_area: str = "aseptic_filling",
) -> DocumentSet:
    return DocumentSet(
        document_set_id=document_set_id,
        tenant_id="tenant_demo_pharma",
        requirement_set_id="rset_pipeline_demo",
        upload_timestamp=datetime.now(UTC),
        document_ids=[],
        declared_document_type=document_type,
        declared_process_area=process_area,
        uploaded_by="user_qrm_author",
        status="ready_for_orchestration",
    )


def _requirement_set(
    *,
    document_type: str = "change_control",
    criticality: str = "low",
) -> RequirementSet:
    return RequirementSet(
        requirement_set_id="rset_pipeline_demo",
        tenant_id="tenant_demo_pharma",
        name="Pipeline Demo Requirements",
        version="2026.1",
        imported_at=datetime.now(UTC),
        imported_by="user_quality_admin",
        active=True,
        requirements=[
            {
                "requirement_id": "req_pipeline_review_record",
                "source_type": "internal_sop",
                "source_name": "SOP-PIPE-001",
                "source_version": "1.0",
                "section": "4.1",
                "requirement_text": "Pipeline demo packages require a review record.",
                "applies_to_document_types": [document_type],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": criticality,
                "required_evidence": ["review record"],
                "auto_close_allowed": True,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            }
        ],
    )


def _document(
    *,
    document_id: str = "doc_pipeline_failure",
    document_set_id: str = "ds_pipeline_failure",
    parsing_quality_score: float = 0.95,
) -> Document:
    return Document(
        document_id=document_id,
        document_set_id=document_set_id,
        filename="deviation.txt",
        file_hash_sha256=sha256(b"deviation.txt").hexdigest(),
        mime_type="text/plain",
        page_count=1,
        storage_uri="local://pipeline/deviation.txt",
        parser_version="test-parser",
        parsing_status="parsed",
        parsing_quality_score=parsing_quality_score,
        language="en",
        metadata={},
    )


def _chunk() -> DocumentChunk:
    text = "DEV-2026-014. Acceptance criterion: deviation review record present."
    return DocumentChunk(
        chunk_id="chunk_pipeline_failure_p1",
        document_id="doc_pipeline_failure",
        page_start=1,
        page_end=1,
        text=text,
        token_count=len(text.split()),
        extraction_confidence=0.95,
        bbox=None,
        source_hash=sha256(text.encode()).hexdigest(),
    )
