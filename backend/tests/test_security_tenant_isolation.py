from __future__ import annotations

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.agents.providers import ExternalModelCallsDisabledError, ExternalModelProviderStub
from app.audit.events import audit_log
from app.core.config import get_settings
from app.db.in_memory import repository
from app.main import app
from app.schemas.domain import DocumentSet, RequirementSet


@pytest.fixture(autouse=True)
def reset_state(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QRM_API_KEYS", "tenant_a=key-a,tenant_b=key-b")
    monkeypatch.setenv("QRM_EXTERNAL_MODEL_CALLS_ENABLED", "false")
    get_settings.cache_clear()
    repository.reset()
    audit_log.clear()
    repository.create_requirement_set(_requirement_set("tenant_a", "rset_tenant_a"))
    repository.create_requirement_set(_requirement_set("tenant_b", "rset_tenant_b"))
    repository.create_document_set(_document_set("tenant_a", "ds_tenant_a", "rset_tenant_a"))
    repository.create_document_set(_document_set("tenant_b", "ds_tenant_b", "rset_tenant_b"))
    yield
    get_settings.cache_clear()


def test_missing_api_key_returns_401() -> None:
    client = TestClient(app)

    response = client.get("/document-sets/ds_tenant_a")

    assert response.status_code == 401


def test_wrong_api_key_returns_401() -> None:
    client = TestClient(app)

    response = client.get("/document-sets/ds_tenant_a", headers={"X-API-Key": "wrong"})

    assert response.status_code == 401


def test_tenant_a_cannot_read_tenant_b_document_set() -> None:
    client = TestClient(app)

    blocked = client.get("/document-sets/ds_tenant_b", headers={"X-API-Key": "key-a"})
    allowed = client.get("/document-sets/ds_tenant_a", headers={"X-API-Key": "key-a"})

    assert blocked.status_code == 404
    assert allowed.status_code == 200
    assert allowed.json()["tenant_id"] == "tenant_a"


def test_document_set_list_is_scoped_to_authenticated_tenant() -> None:
    client = TestClient(app)

    response = client.get("/document-sets", headers={"X-API-Key": "key-a"})

    assert response.status_code == 200
    assert [item["document_set_id"] for item in response.json()] == ["ds_tenant_a"]


def test_create_document_set_for_other_tenant_is_forbidden() -> None:
    client = TestClient(app)

    response = client.post(
        "/document-sets",
        headers={"X-API-Key": "key-a"},
        json={
            "tenant_id": "tenant_b",
            "requirement_set_id": "rset_tenant_b",
            "declared_document_type": "deviation",
            "declared_process_area": "aseptic_filling",
            "uploaded_by": "user_qrm_author",
        },
    )

    assert response.status_code == 403


def test_external_model_calls_disabled_provider_stub_fails_cleanly() -> None:
    provider = ExternalModelProviderStub(
        provider_name="openai",
        model_name="gpt-test",
        model_version="2026-01",
    )

    with pytest.raises(ExternalModelCallsDisabledError):
        provider.run_structured(
            prompt="Do not call external systems",
            input_schema={},
            output_schema=DummyOutput,
        )


class DummyOutput(BaseModel):
    value: str


def _document_set(tenant_id: str, document_set_id: str, requirement_set_id: str) -> DocumentSet:
    return DocumentSet(
        document_set_id=document_set_id,
        tenant_id=tenant_id,
        requirement_set_id=requirement_set_id,
        upload_timestamp=datetime.now(UTC),
        document_ids=[],
        declared_document_type="deviation",
        declared_process_area="aseptic_filling",
        uploaded_by="user_qrm_author",
        status="uploaded",
    )


def _requirement_set(tenant_id: str, requirement_set_id: str) -> RequirementSet:
    return RequirementSet(
        requirement_set_id=requirement_set_id,
        tenant_id=tenant_id,
        name=f"{tenant_id} requirements",
        version="2026.1",
        imported_at=datetime.now(UTC),
        imported_by="user_quality_admin",
        active=True,
        requirements=[
            {
                "requirement_id": f"req_{tenant_id}_deviation_review",
                "source_type": "internal_sop",
                "source_name": "SOP-SECURITY-DEMO",
                "source_version": "1.0",
                "section": "1.0",
                "requirement_text": "Deviation records must be reviewed.",
                "applies_to_document_types": ["deviation"],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": "medium",
                "required_evidence": ["deviation record"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            }
        ],
    )
