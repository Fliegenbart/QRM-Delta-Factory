from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.audit.events import audit_log
from app.db.in_memory import repository
from app.main import app
from app.schemas.domain import (
    Claim,
    Document,
    DocumentChunk,
    DocumentSet,
    RequirementSet,
    RiskFinding,
)
from app.services.review_calibration import (
    CalibrationActivationGateError,
    ReviewCalibrationService,
)
from app.services.review_orchestrator import PrimaryReviewOrchestrator, ReviewerAgent
from app.services.review_pack import ReviewPackService


@pytest.fixture(autouse=True)
def reset_state() -> None:
    repository.reset()
    audit_log.clear()
    _setup_calibration_context()


def test_review_decision_creates_raw_calibration_example_only() -> None:
    raw_example = _record_reviewer_feedback()

    examples = repository.list_calibration_examples()
    assert len(examples) == 1
    assert examples[0].calibration_example_id == raw_example.calibration_example_id
    assert examples[0].status == "raw_feedback"
    assert examples[0].feedback_outcome == "false_positive"
    assert examples[0].agent_role == "DeviationReviewer"
    assert examples[0].high_critical_recall_guard is True

    pack = ReviewCalibrationService(repository=repository, audit_log=audit_log).build_pack(
        document_set=_target_document_set(),
        agent_role="DeviationReviewer",
        requirements=_requirements(),
        case_signals=["deviation"],
    )
    assert pack.example_ids == []
    assert pack.prompt_block == ""

    response = TestClient(app).get("/analytics/review-calibration")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_examples"] == 1
    assert payload["raw_feedback_count"] == 1
    assert payload["active_count"] == 0


def test_calibration_activation_requires_regression_gate_then_builds_prompt_pack() -> None:
    raw_example = _record_reviewer_feedback()
    calibration = ReviewCalibrationService(repository=repository, audit_log=audit_log)

    with pytest.raises(CalibrationActivationGateError):
        calibration.approve_example(
            raw_example.calibration_example_id,
            approved_by="reviewer_qa_lead",
            activate=True,
        )

    approved = calibration.approve_example(
        raw_example.calibration_example_id,
        approved_by="reviewer_qa_lead",
    )
    assert approved.status == "approved_gold"
    assert calibration.build_pack(
        document_set=_target_document_set(),
        agent_role="DeviationReviewer",
        requirements=_requirements(),
        case_signals=["deviation"],
    ).example_ids == []

    gate_report = calibration.run_regression_gate()
    assert gate_report.passed is True
    assert gate_report.regression_gate_report_id.startswith("calgate_")

    active = calibration.approve_example(
        raw_example.calibration_example_id,
        approved_by="reviewer_qa_lead",
        activate=True,
        regression_gate_passed=True,
        regression_gate_report_id=gate_report.regression_gate_report_id,
    )

    pack = calibration.build_pack(
        document_set=_target_document_set(),
        agent_role="DeviationReviewer",
        requirements=_requirements(),
        case_signals=["deviation"],
    )

    assert active.status == "active"
    assert pack.example_ids == [active.calibration_example_id]
    assert "Kontrollierte Kalibrierungsbeispiele" in pack.prompt_block
    assert "kein Fine-Tuning" in pack.prompt_block
    assert "false_positive" in pack.prompt_block
    assert "still zu unterdruecken" in pack.prompt_block


def test_review_calibration_api_activates_only_with_gate_report() -> None:
    raw_example = _record_reviewer_feedback()
    client = TestClient(app)

    rejected = client.post(
        f"/analytics/review-calibration/{raw_example.calibration_example_id}/approve",
        json={
            "approved_by": "reviewer_qa_lead",
            "activate": True,
            "regression_gate_passed": False,
        },
    )
    assert rejected.status_code == 409

    gate_response = client.post("/analytics/review-calibration/run-regression-gate")
    assert gate_response.status_code == 200
    gate_payload = gate_response.json()
    assert gate_payload["passed"] is True
    assert gate_payload["regression_gate_report_id"].startswith("calgate_")

    activated = client.post(
        f"/analytics/review-calibration/{raw_example.calibration_example_id}/approve",
        json={
            "approved_by": "reviewer_qa_lead",
            "activate": True,
            "regression_gate_passed": True,
            "regression_gate_report_id": gate_payload["regression_gate_report_id"],
        },
    )
    assert activated.status_code == 200
    assert activated.json()["status"] == "active"

    report = client.get("/analytics/review-calibration")
    assert report.status_code == 200
    assert report.json()["active_count"] == 1


def test_primary_review_injects_active_calibration_examples_into_agent_context() -> None:
    raw_example = _record_reviewer_feedback()
    active = ReviewCalibrationService(
        repository=repository,
        audit_log=audit_log,
    )
    gate_report = active.run_regression_gate()
    activated = active.approve_example(
        raw_example.calibration_example_id,
        approved_by="reviewer_qa_lead",
        activate=True,
        regression_gate_passed=True,
        regression_gate_report_id=gate_report.regression_gate_report_id,
    )
    provider = CapturingProvider()
    orchestrator = PrimaryReviewOrchestrator(
        repository=repository,
        audit_log=audit_log,
        agents=[
            ReviewerAgent(
                agent_id="agent_deviation",
                role="DeviationReviewer",
                prompt_version="deviation_reviewer_v1",
                applicable_risk_categories=["deviation_management"],
                provider=provider,
            )
        ],
    )

    result = orchestrator.run_primary_review("ds_calibration_target")

    assert result.model_runs[0].calibration_example_ids == [activated.calibration_example_id]
    assert result.model_runs[0].calibration_pack_hash is not None
    assert provider.last_input_schema is not None
    assert provider.last_input_schema["calibration_example_ids"] == [
        activated.calibration_example_id
    ]
    assert "Kontrollierte Kalibrierungsbeispiele" in str(provider.last_prompt)
    completed_event = next(
        event for event in audit_log.list_events() if event.event_type == "model_run_completed"
    )
    assert completed_event.payload["calibration_example_ids"] == [
        activated.calibration_example_id
    ]
    assert (
        completed_event.payload["calibration_pack_hash"]
        == result.model_runs[0].calibration_pack_hash
    )


class CapturingProvider:
    provider_name = "mock"
    model_name = "capturing-reviewer"
    model_version = "0.1.0"
    configured_model_id = "capturing-reviewer-v0.1"
    last_run_metadata = None

    def __init__(self) -> None:
        self.last_prompt: str | None = None
        self.last_input_schema: dict[str, Any] | None = None

    def run_structured(
        self,
        prompt: str,
        input_schema: dict[str, Any],
        output_schema: type[Any],
    ) -> dict[str, Any]:
        self.last_prompt = prompt
        self.last_input_schema = input_schema
        return {
            "findings": [],
            "coverage_summary": "No comparable risk found after calibrated review.",
        }


def _record_reviewer_feedback() -> Any:
    return ReviewCalibrationService(
        repository=repository,
        audit_log=audit_log,
    ).record_feedback_decision(
        ReviewPackService(
            repository=repository,
            audit_log=audit_log,
        ).record_review_decision(
            finding_id="finding_calibration_source",
            reviewer_id="reviewer_qa_1",
            decision="reject_false_positive",
            rationale=(
                "The source text says impact was assessed; the model confused "
                "brief wording with a missing assessment."
            ),
        )
    )


def _setup_calibration_context() -> None:
    repository.create_requirement_set(_requirement_set())
    repository.create_document_set(_source_document_set())
    repository.create_document_set(_target_document_set())
    repository.add_document(document=_source_document(), chunks=[_source_chunk()])
    repository.replace_claim_ledger(
        document_set_id="ds_calibration_target",
        claims=[_target_claim()],
    )
    repository.replace_risk_findings(
        document_set_id="ds_calibration_source",
        findings=[_source_finding()],
    )
    audit_log.append(
        event_type="finding_created",
        actor_id="model_capturing-reviewer",
        actor_type="model",
        entity_type="RiskFinding",
        entity_id="finding_calibration_source",
        payload={
            "document_set_id": "ds_calibration_source",
            "agent_role": "DeviationReviewer",
            "prompt_version": "deviation_reviewer_v1",
        },
    )


def _target_document_set() -> DocumentSet:
    return DocumentSet(
        document_set_id="ds_calibration_target",
        tenant_id="tenant_demo_pharma",
        requirement_set_id="rset_calibration_demo_2026",
        upload_timestamp=datetime.now(UTC),
        document_ids=[],
        declared_document_type="deviation",
        declared_process_area="aseptic_filling",
        uploaded_by="user_qrm_author",
        status="ready_for_orchestration",
    )


def _source_document_set() -> DocumentSet:
    return DocumentSet(
        document_set_id="ds_calibration_source",
        tenant_id="tenant_demo_pharma",
        requirement_set_id="rset_calibration_demo_2026",
        upload_timestamp=datetime.now(UTC),
        document_ids=[],
        declared_document_type="deviation",
        declared_process_area="aseptic_filling",
        uploaded_by="user_qrm_author",
        status="needs_human_review",
    )


def _requirement_set() -> RequirementSet:
    return RequirementSet(
        requirement_set_id="rset_calibration_demo_2026",
        tenant_id="tenant_demo_pharma",
        name="Calibration Demo Requirements",
        version="2026.1",
        imported_at=datetime.now(UTC),
        imported_by="user_quality_admin",
        active=True,
        requirements=[
            {
                "requirement_id": "req_calibration_impact_assessment",
                "source_type": "internal_sop",
                "source_name": "SOP-DEV-CAL-001",
                "source_version": "1.0",
                "section": "5.4",
                "requirement_text": "Deviation records require documented impact assessment.",
                "applies_to_document_types": ["deviation"],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": "high",
                "required_evidence": ["impact assessment"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            }
        ],
    )


def _requirements() -> list[Any]:
    requirement_set = repository.get_requirement_set("rset_calibration_demo_2026")
    assert requirement_set is not None
    return requirement_set.requirements


def _source_document() -> Document:
    return Document(
        document_id="doc_calibration_source",
        document_set_id="ds_calibration_source",
        filename="source-deviation.txt",
        file_hash_sha256=sha256(b"source-deviation").hexdigest(),
        mime_type="text/plain",
        page_count=1,
        storage_uri="local://calibration/source-deviation.txt",
        parser_version="test-parser",
        parsing_status="parsed",
        parsing_quality_score=0.98,
        language="en",
        metadata={},
    )


def _source_chunk() -> DocumentChunk:
    text = "Impact was assessed and no product quality impact was identified."
    return DocumentChunk(
        chunk_id="chunk_calibration_source_p1",
        document_id="doc_calibration_source",
        page_start=1,
        page_end=1,
        text=text,
        token_count=len(text.split()),
        extraction_confidence=0.98,
        bbox=None,
        source_hash=sha256(text.encode()).hexdigest(),
    )


def _target_claim() -> Claim:
    quote = "Deviation DEV-2026-015 includes an impact assessment."
    return Claim(
        claim_id="claim_calibration_target",
        document_id="doc_calibration_target",
        chunk_id="chunk_calibration_target_p1",
        page=1,
        claim_type="deviation_description",
        normalized_subject="deviation",
        normalized_predicate="includes",
        normalized_object="impact assessment",
        raw_text_quote=quote,
        confidence=0.9,
        dependencies=[],
        created_by_model="mock-claim-extractor-v0.1",
        prompt_version="mock-claim-ledger-v0.1",
    )


def _source_finding() -> RiskFinding:
    quote = "Impact was assessed and no product quality impact was identified."
    return RiskFinding(
        finding_id="finding_calibration_source",
        document_set_id="ds_calibration_source",
        risk_category="deviation_management",
        severity="high",
        likelihood=3,
        detectability=3,
        risk_statement="Impact assessment may be missing or incomplete.",
        evidence_items=[
            {
                "document_id": "doc_calibration_source",
                "chunk_id": "chunk_calibration_source_p1",
                "page": 1,
                "quote": quote,
                "quote_hash": sha256(quote.encode()).hexdigest(),
                "support_type": "supports",
                "verifier_score": 0.9,
            }
        ],
        requirement_references=["req_calibration_impact_assessment"],
        missing_information=[],
        model_provider="mock",
        model_name="capturing-reviewer",
        model_version="0.1.0",
        prompt_version="deviation_reviewer_v1",
        evidence_support="partial",
        recommended_action="Route to QA reviewer.",
        auto_close_allowed=False,
        status="needs_human_review",
        verification_result=None,
    )
