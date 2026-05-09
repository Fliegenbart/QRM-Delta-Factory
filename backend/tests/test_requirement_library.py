from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.audit.events import audit_log
from app.db.in_memory import repository
from app.main import app

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples" / "requirements"


@pytest.fixture(autouse=True)
def reset_state() -> None:
    repository.reset()
    audit_log.clear()


def test_import_requirement_set_from_yaml_and_get_by_id() -> None:
    client = TestClient(app)

    imported = _import_yaml(client)

    response = client.get(f"/requirement-sets/{imported['requirement_set_id']}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["requirement_set_id"] == "rset_demo_gmp_qrm_2026_1"
    assert payload["version"] == "2026.1"
    assert len(payload["requirements"]) >= 6
    assert audit_log.list_events()[0].event_type == "requirement_set_imported"


def test_requirement_set_versions_are_preserved() -> None:
    client = TestClient(app)
    first = _import_yaml(client)
    second_payload = _load_yaml_text().replace(
        "rset_demo_gmp_qrm_2026_1",
        "rset_demo_gmp_qrm_2026_2",
    )
    second_payload = second_payload.replace('version: "2026.1"', 'version: "2026.2"')

    response = client.post(
        "/requirement-sets/import",
        files={"file": ("deviation_management_v2.yaml", second_payload, "application/x-yaml")},
        data={"imported_by": "user_quality_admin"},
    )

    assert response.status_code == 201
    assert first["version"] == "2026.1"
    assert response.json()["version"] == "2026.2"
    assert client.get("/requirement-sets/rset_demo_gmp_qrm_2026_1").status_code == 200
    assert client.get("/requirement-sets/rset_demo_gmp_qrm_2026_2").status_code == 200


def test_import_requirement_set_from_json() -> None:
    client = TestClient(app)
    payload = _minimal_requirement_set_payload()

    response = client.post(
        "/requirement-sets/import",
        files={"file": ("requirements.json", json.dumps(payload), "application/json")},
        data={"imported_by": "user_quality_admin"},
    )

    assert response.status_code == 201
    assert response.json()["requirement_set_id"] == "rset_json_import_2026_1"
    assert response.json()["requirements"][0]["requirement_id"] == "req_json_import_demo"


def test_search_filters_active_requirements() -> None:
    client = TestClient(app)
    _import_yaml(client)
    activate_response = client.post("/requirement-sets/rset_demo_gmp_qrm_2026_1/activate")
    assert activate_response.status_code == 200

    response = client.get(
        "/requirements/search",
        params={
            "document_type": "change_control",
            "process_area": "aseptic_filling",
            "criticality": "high",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert [item["requirement_id"] for item in payload] == ["req_change_control_impact_assessment"]


def test_import_rejects_duplicate_requirement_ids() -> None:
    client = TestClient(app)
    duplicate_yaml = _load_yaml_text().replace(
        "req_capa_effectiveness_check",
        "req_deviation_documented_impact_assessment",
    )

    response = client.post(
        "/requirement-sets/import",
        files={"file": ("duplicate.yaml", duplicate_yaml, "application/x-yaml")},
        data={"imported_by": "user_quality_admin"},
    )

    assert response.status_code == 422
    assert "unique" in response.json()["detail"].lower()


def test_import_rejects_high_requirement_without_evidence() -> None:
    client = TestClient(app)
    payload = {
        "requirement_set_id": "rset_invalid_evidence",
        "tenant_id": "tenant_demo_pharma",
        "name": "Invalid Evidence Library",
        "version": "2026.1",
        "active": False,
        "requirements": [
            {
                "requirement_id": "req_missing_high_evidence",
                "source_type": "internal_sop",
                "source_name": "SOP-QA-001",
                "source_version": "1.0",
                "section": "1.0",
                "requirement_text": "High impact changes require objective evidence.",
                "applies_to_document_types": ["change_control"],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": "high",
                "required_evidence": [],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            }
        ],
    }

    response = client.post(
        "/requirement-sets/import",
        files={"file": ("invalid.json", json.dumps(payload), "application/json")},
        data={"imported_by": "user_quality_admin"},
    )

    assert response.status_code == 422
    assert "required_evidence" in response.json()["detail"]


@pytest.mark.parametrize("missing_field", ["source_version", "effective_from", "criticality"])
def test_import_rejects_missing_required_requirement_fields(missing_field: str) -> None:
    client = TestClient(app)
    payload = _minimal_requirement_set_payload()
    del payload["requirements"][0][missing_field]

    response = client.post(
        "/requirement-sets/import",
        files={"file": ("missing-field.json", json.dumps(payload), "application/json")},
        data={"imported_by": "user_quality_admin"},
    )

    assert response.status_code == 422
    assert missing_field in response.json()["detail"]


def test_activation_and_deactivation_are_audited() -> None:
    client = TestClient(app)
    _import_yaml(client)

    activate_response = client.post("/requirement-sets/rset_demo_gmp_qrm_2026_1/activate")
    deactivate_response = client.post("/requirement-sets/rset_demo_gmp_qrm_2026_1/deactivate")

    assert activate_response.status_code == 200
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["active"] is False
    assert [event.event_type for event in audit_log.list_events()] == [
        "requirement_set_imported",
        "requirement_set_activated",
        "requirement_set_deactivated",
    ]


def test_document_set_requires_active_requirement_set() -> None:
    client = TestClient(app)
    _import_yaml(client)

    inactive_response = client.post(
        "/document-sets",
        json={
            "tenant_id": "tenant_demo_pharma",
            "declared_document_type": "change_control",
            "declared_process_area": "aseptic_filling",
            "uploaded_by": "user_qrm_author",
            "requirement_set_id": "rset_demo_gmp_qrm_2026_1",
        },
    )
    assert inactive_response.status_code == 422

    client.post("/requirement-sets/rset_demo_gmp_qrm_2026_1/activate")
    active_response = client.post(
        "/document-sets",
        json={
            "tenant_id": "tenant_demo_pharma",
            "declared_document_type": "change_control",
            "declared_process_area": "aseptic_filling",
            "uploaded_by": "user_qrm_author",
            "requirement_set_id": "rset_demo_gmp_qrm_2026_1",
        },
    )

    assert active_response.status_code == 201
    assert active_response.json()["requirement_set_id"] == "rset_demo_gmp_qrm_2026_1"


def _import_yaml(client: TestClient) -> dict[str, object]:
    response = client.post(
        "/requirement-sets/import",
        files={
            "file": (
                "deviation_management.yaml",
                _load_yaml_text(),
                "application/x-yaml",
            )
        },
        data={"imported_by": "user_quality_admin"},
    )
    assert response.status_code == 201
    return dict(response.json())


def _load_yaml_text() -> str:
    return (EXAMPLES_DIR / "deviation_management.yaml").read_text(encoding="utf-8")


def _minimal_requirement_set_payload() -> dict[str, object]:
    return {
        "requirement_set_id": "rset_json_import_2026_1",
        "tenant_id": "tenant_demo_pharma",
        "name": "JSON Import Library",
        "version": "2026.1",
        "active": False,
        "requirements": [
            {
                "requirement_id": "req_json_import_demo",
                "source_type": "internal_sop",
                "source_name": "SOP-QA-JSON",
                "source_version": "1.0",
                "section": "1.0",
                "requirement_text": "JSON-imported requirements must be validated.",
                "applies_to_document_types": ["change_control"],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": "medium",
                "required_evidence": ["source reference"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            }
        ],
    }
