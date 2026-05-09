from __future__ import annotations

from datetime import UTC, datetime
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

from app.audit.events import AuditService, audit_log
from app.db.in_memory import repository
from app.main import app
from app.schemas.domain import RequirementSet


@pytest.fixture(autouse=True)
def reset_state() -> None:
    repository.reset()
    audit_log.clear()
    repository.create_requirement_set(_requirement_set())


def test_audit_service_appends_hash_chain_and_detects_tampering() -> None:
    service = AuditService()

    first = service.append_event(
        tenant_id="tenant_demo_pharma",
        actor_type="user",
        actor_id="user_qrm_author",
        event_type="document_uploaded",
        entity_type="Document",
        entity_id="doc_audit_1",
        metadata={
            "document_id": "doc_audit_1",
            "document_text": "This is sensitive full document text that must not be stored.",
            "api_key": "secret-value",
        },
    )
    second = service.append_event(
        tenant_id="tenant_demo_pharma",
        actor_type="service",
        actor_id="service_parser",
        event_type="document_parsed",
        entity_type="Document",
        entity_id="doc_audit_1",
        metadata={"document_id": "doc_audit_1", "page_count": 1},
    )

    assert first.audit_event_id == "audit_1"
    assert second.previous_event_hash == first.event_hash
    assert service.verify_hash_chain() is True
    assert service.get_events_for_entity("Document", "doc_audit_1") == [first, second]
    assert first.metadata["document_text"]["redacted"] is True
    assert first.metadata["api_key"]["redacted"] is True

    first.metadata["document_id"] = "doc_tampered"

    assert service.verify_hash_chain() is False


def test_pipeline_writes_required_audit_events_with_verifiable_chain() -> None:
    client = TestClient(app)
    create_response = client.post(
        "/document-sets",
        json={
            "tenant_id": "tenant_demo_pharma",
            "requirement_set_id": "rset_audit_demo_2026",
            "declared_document_type": "deviation",
            "declared_process_area": "aseptic_filling",
            "uploaded_by": "user_qrm_author",
        },
    )
    assert create_response.status_code == 201
    document_set_id = create_response.json()["document_set_id"]

    upload_response = client.post(
        f"/document-sets/{document_set_id}/documents",
        files={
            "file": (
                "deviation.pdf",
                _pdf_with_text(
                    "Deviation DEV-AUDIT-001 for Batch BATCH-001. "
                    "Impact assessment: batch impact is not documented."
                ),
                "application/pdf",
            )
        },
        data={"uploaded_by": "user_qrm_author"},
    )
    assert upload_response.status_code == 201
    claims_response = client.get(f"/document-sets/{document_set_id}/claims")
    assert claims_response.status_code == 200
    search_response = client.get(
        "/requirements/search?document_type=deviation&process_area=aseptic_filling"
    )
    assert search_response.status_code == 200
    primary_response = client.post(f"/document-sets/{document_set_id}/run-primary-review")
    assert primary_response.status_code == 200
    fusion_response = client.post(f"/document-sets/{document_set_id}/run-risk-fusion")
    assert fusion_response.status_code == 200
    review_pack_response = client.get(f"/document-sets/{document_set_id}/review-pack")
    assert review_pack_response.status_code == 200
    finding_id = primary_response.json()["findings"][0]["finding_id"]
    review_decision_response = client.post(
        f"/findings/{finding_id}/review-decision",
        json={
            "reviewer_id": "reviewer_qa_1",
            "decision": "request_more_information",
            "rationale": "Batch impact evidence must be supplied.",
        },
    )
    assert review_decision_response.status_code == 200
    eval_response = client.post(
        "/evals/run",
        json={"dataset_id": "evalds_deviation_missing_batch_impact"},
    )
    assert eval_response.status_code == 200

    event_types = {event.event_type for event in audit_log.list_events()}

    assert {
        "document_uploaded",
        "document_parsed",
        "chunks_created",
        "claims_extracted",
        "requirements_retrieved",
        "model_run_started",
        "model_run_completed",
        "finding_created",
        "finding_verified",
        "risk_fusion_completed",
        "review_pack_created",
        "human_review_decision_created",
        "eval_run_completed",
    }.issubset(event_types)
    assert audit_log.verify_hash_chain() is True
    assert all("document_text" not in event.metadata for event in audit_log.list_events())


def _requirement_set() -> RequirementSet:
    return RequirementSet(
        requirement_set_id="rset_audit_demo_2026",
        tenant_id="tenant_demo_pharma",
        name="Audit Demo Requirements",
        version="2026.1",
        imported_at=datetime.now(UTC),
        imported_by="user_quality_admin",
        active=True,
        requirements=[
            {
                "requirement_id": "req_audit_batch_impact",
                "source_type": "internal_sop",
                "source_name": "SOP-DEV-AUDIT",
                "source_version": "1.0",
                "section": "3.1",
                "requirement_text": "Deviation batch impact must be documented.",
                "applies_to_document_types": ["deviation"],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": "high",
                "required_evidence": ["batch impact assessment"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            }
        ],
    )


def _pdf_with_text(text: str) -> bytes:
    buffer = BytesIO()
    pdf_canvas = canvas.Canvas(buffer)
    pdf_canvas.drawString(72, 720, text)
    pdf_canvas.save()
    return buffer.getvalue()
