from __future__ import annotations

from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from pytest import MonkeyPatch
from reportlab.pdfgen import canvas

from app.audit.events import audit_log
from app.core.config import get_settings
from app.db.in_memory import repository
from app.main import app
from app.schemas.domain import RequirementSet
from app.services.document_parser import ParserError, ParserRegistry


@pytest.fixture(autouse=True)
def reset_state(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    repository.reset()
    audit_log.clear()
    repository.create_requirement_set(_active_requirement_set())
    monkeypatch.setenv("QRM_LOCAL_STORAGE_ROOT", str(tmp_path / "storage"))
    get_settings.cache_clear()


def test_create_document_set() -> None:
    client = TestClient(app)

    response = client.post("/document-sets", json=_document_set_payload())

    assert response.status_code == 201
    payload = response.json()
    assert payload["document_set_id"].startswith("ds_")
    assert payload["document_ids"] == []
    assert payload["status"] == "uploaded"


def test_upload_txt_document_creates_chunks_and_audit_events() -> None:
    client = TestClient(app)
    document_set_id = _create_document_set(client)

    response = client.post(
        f"/document-sets/{document_set_id}/documents",
        files={
            "file": (
                "process.txt",
                b"This is a meaningful process control document.",
                "text/plain",
            )
        },
        data={"uploaded_by": "user_qrm_author"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["document"]["file_hash_sha256"]
    assert payload["document"]["parsing_status"] == "parsed"
    assert payload["document_set"]["status"] == "ready_for_orchestration"
    assert len(payload["chunks"]) == 1
    assert payload["chunks"][0]["token_count"] >= 6
    assert [event.event_type for event in audit_log.list_events()] == [
        "document_set_created",
        "document_uploaded",
        "document_parsed",
        "chunks_created",
        "document_parser_run",
    ]


def test_delete_document_set_removes_case_and_uploaded_documents() -> None:
    client = TestClient(app)
    document_set_id = _create_document_set(client)
    upload_response = client.post(
        f"/document-sets/{document_set_id}/documents",
        files={
            "file": (
                "process.txt",
                b"This is a meaningful process control document.",
                "text/plain",
            )
        },
        data={"uploaded_by": "user_qrm_author"},
    )
    assert upload_response.status_code == 201
    document_id = upload_response.json()["document"]["document_id"]

    response = client.delete(f"/document-sets/{document_set_id}")

    assert response.status_code == 204
    assert client.get(f"/document-sets/{document_set_id}").status_code == 404
    assert repository.get_document(document_id) is None


def test_upload_normal_pdf_creates_chunks() -> None:
    client = TestClient(app)
    document_set_id = _create_document_set(client)

    response = client.post(
        f"/document-sets/{document_set_id}/documents",
        files={
            "file": (
                "validation.pdf",
                _pdf_with_text("Validation evidence supports the current threshold setting."),
                "application/pdf",
            )
        },
        data={"uploaded_by": "user_qrm_author"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["document"]["page_count"] == 1
    assert payload["document"]["parsing_quality_score"] >= 0.65
    assert payload["document_set"]["status"] == "ready_for_orchestration"
    assert payload["chunks"][0]["text"]


def test_empty_txt_escalates_to_human_review() -> None:
    client = TestClient(app)
    document_set_id = _create_document_set(client)

    response = client.post(
        f"/document-sets/{document_set_id}/documents",
        files={"file": ("empty.txt", b"", "text/plain")},
        data={"uploaded_by": "user_qrm_author"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["document"]["parsing_quality_score"] < 0.65
    assert payload["document_set"]["status"] == "needs_human_review"
    assert payload["chunks"] == []


def test_empty_pdf_escalates_to_human_review() -> None:
    client = TestClient(app)
    document_set_id = _create_document_set(client)

    response = client.post(
        f"/document-sets/{document_set_id}/documents",
        files={"file": ("blank.pdf", _blank_pdf(), "application/pdf")},
        data={"uploaded_by": "user_qrm_author"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["document"]["parsing_quality_score"] < 0.65
    assert payload["document_set"]["status"] == "needs_human_review"
    assert payload["chunks"] == []


def test_parser_error_is_audited_and_escalates(monkeypatch: MonkeyPatch) -> None:
    client = TestClient(app)
    document_set_id = _create_document_set(client)

    def raise_error(self, filename: str, mime_type: str):  # type: ignore[no-untyped-def]
        raise ParserError("forced parser failure")

    monkeypatch.setattr(ParserRegistry, "for_filename", raise_error)
    response = client.post(
        f"/document-sets/{document_set_id}/documents",
        files={"file": ("broken.pdf", b"%PDF broken", "application/pdf")},
        data={"uploaded_by": "user_qrm_author"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["document"]["parsing_status"] == "failed"
    assert payload["document"]["parsing_quality_score"] == 0
    assert payload["document_set"]["status"] == "needs_human_review"
    assert audit_log.list_events()[-1].event_type == "document_parser_run"
    assert audit_log.list_events()[-1].payload["parser_error"] == "forced parser failure"


def _create_document_set(client: TestClient) -> str:
    response = client.post("/document-sets", json=_document_set_payload())
    assert response.status_code == 201
    return str(response.json()["document_set_id"])


def _document_set_payload() -> dict[str, str]:
    return {
        "tenant_id": "tenant_demo_pharma",
        "requirement_set_id": "rset_demo_active_2026",
        "declared_document_type": "change_control_package",
        "declared_process_area": "automated_visual_inspection",
        "uploaded_by": "user_qrm_author",
    }


def _active_requirement_set() -> RequirementSet:
    return RequirementSet(
        requirement_set_id="rset_demo_active_2026",
        tenant_id="tenant_demo_pharma",
        name="Demo Active Requirements",
        version="2026.1",
        imported_at=datetime.now(UTC),
        imported_by="user_quality_admin",
        active=True,
        requirements=[
            {
                "requirement_id": "req_demo_source_required",
                "source_type": "internal_sop",
                "source_name": "SOP-QRM-DEMO",
                "source_version": "1.0",
                "section": "1.0",
                "requirement_text": "Uploaded documents must be source traceable.",
                "applies_to_document_types": ["change_control_package"],
                "applies_to_process_areas": ["automated_visual_inspection"],
                "criticality": "medium",
                "required_evidence": ["source document"],
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


def _blank_pdf() -> bytes:
    buffer = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.write(buffer)
    return buffer.getvalue()
