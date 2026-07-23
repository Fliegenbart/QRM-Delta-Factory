from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.audit.events import audit_log
from app.core.config import get_settings
from app.db.in_memory import repository
from app.main import app
from app.schemas.domain import RequirementSet
from app.storage.local import LocalFilesystemStorage


@pytest.fixture(autouse=True)
def reset_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QRM_LOCAL_STORAGE_ROOT", str(tmp_path / "storage"))
    get_settings.cache_clear()
    repository.reset()
    audit_log.clear()
    repository.create_requirement_set(
        RequirementSet.model_validate(
            {
                "requirement_set_id": "rset_delete_demo",
                "tenant_id": "tenant_demo_pharma",
                "name": "Delete demo",
                "version": "1",
                "imported_at": "2026-01-01T00:00:00Z",
                "imported_by": "user_quality_admin",
                "active": True,
                "requirements": [
                    {
                        "requirement_id": "req_delete_demo",
                        "source_type": "internal_sop",
                        "source_name": "SOP-DELETE",
                        "source_version": "1",
                        "section": "1",
                        "requirement_text": "Keep a deletion record.",
                        "applies_to_document_types": ["deviation"],
                        "applies_to_process_areas": ["quality_control"],
                        "criticality": "low",
                        "required_evidence": ["record"],
                        "auto_close_allowed": False,
                        "effective_from": "2026-01-01T00:00:00Z",
                        "effective_to": None,
                    }
                ],
            }
        )
    )


def _document_set(client: TestClient) -> str:
    response = client.post(
        "/document-sets",
        json={
            "tenant_id": "tenant_demo_pharma",
            "requirement_set_id": "rset_delete_demo",
            "declared_document_type": "deviation",
            "declared_process_area": "quality_control",
            "uploaded_by": "user_qrm_author",
        },
    )
    assert response.status_code == 201
    return response.json()["document_set_id"]


def test_delete_document_set_removes_document_bytes() -> None:
    client = TestClient(app)
    document_set_id = _document_set(client)
    upload = client.post(
        f"/document-sets/{document_set_id}/documents",
        files={"file": ("source.txt", b"confidential", "text/plain")},
        data={"uploaded_by": "user_qrm_author"},
    )
    assert upload.status_code == 201
    uri = upload.json()["document"]["storage_uri"]

    response = client.delete(f"/document-sets/{document_set_id}")

    assert response.status_code == 204
    with pytest.raises(FileNotFoundError):
        LocalFilesystemStorage(Path(get_settings().local_storage_root)).read_object(uri=uri)


def test_delete_preserves_metadata_when_storage_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    client = TestClient(app, raise_server_exceptions=False)
    document_set_id = _document_set(client)
    upload = client.post(
        f"/document-sets/{document_set_id}/documents",
        files={"file": ("source.txt", b"confidential", "text/plain")},
        data={"uploaded_by": "user_qrm_author"},
    )
    assert upload.status_code == 201

    def fail_delete(self: LocalFilesystemStorage, *, uri: str) -> None:
        raise OSError("offline")

    monkeypatch.setattr(LocalFilesystemStorage, "delete_object", fail_delete)
    response = client.delete(f"/document-sets/{document_set_id}")

    assert response.status_code == 500
    assert repository.get_document_set(document_set_id) is not None
