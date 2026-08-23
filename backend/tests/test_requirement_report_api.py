"""The coverage report as a product surface, not an eval artifact.

The requirement engine measured better than the finding path on a blind
corpus -- 79% sensitivity at 98% decoy specificity and half the list length --
while being reachable only from the eval harness: no pipeline step, no
persistence, no endpoint. These tests pin the path from upload to report.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.audit.events import audit_log
from app.core.config import get_settings
from app.db.in_memory import repository
from app.main import app
from app.schemas.domain import RequirementSet


@pytest.fixture(autouse=True)
def reset_state() -> None:
    repository.reset()
    audit_log.clear()
    get_settings.cache_clear()


def _requirement_set() -> RequirementSet:
    return RequirementSet(
        requirement_set_id="rset_report_demo",
        tenant_id="tenant_demo_pharma",
        name="Coverage Report Demo",
        version="2026.1",
        imported_at=datetime.now(UTC),
        imported_by="user_quality_admin",
        active=True,
        requirements=[
            {
                "requirement_id": "req_report_threshold",
                "source_type": "internal_sop",
                "source_name": "SOP-CC-AVI-001",
                "source_version": "3.0",
                "section": "8.4",
                "requirement_text": (
                    "Schwellwertänderungen erfordern aktuelle Validierungsevidenz."
                ),
                "applies_to_document_types": ["change_control"],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": "high",
                "required_evidence": ["Validierungsnachweis"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            },
            {
                "requirement_id": "req_report_warehouse",
                "source_type": "internal_sop",
                "source_name": "SOP-WH-002",
                "source_version": "1.0",
                "section": "2.1",
                "requirement_text": "Lagertemperatur ist zu dokumentieren.",
                "applies_to_document_types": ["change_control"],
                "applies_to_process_areas": ["warehouse"],
                "criticality": "medium",
                "required_evidence": ["Temperaturlog"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            },
        ],
    )


def _run_pipeline(client: TestClient) -> str:
    repository.create_requirement_set(_requirement_set())
    created = client.post(
        "/document-sets",
        json={
            "tenant_id": "tenant_demo_pharma",
            "requirement_set_id": "rset_report_demo",
            "declared_document_type": "change_control",
            "declared_process_area": "aseptic_filling",
            "uploaded_by": "user_qrm_author",
        },
    )
    document_set_id = created.json()["document_set_id"]
    client.post(
        f"/document-sets/{document_set_id}/documents",
        files={
            "file": (
                "change-control.txt",
                b"Change Control CC-2026-014 senkt den AVI-Schwellwert. "
                b"Ein Validierungsnachweis liegt nicht bei.",
                "text/plain",
            )
        },
        data={"uploaded_by": "user_qrm_author"},
    )
    client.post(f"/document-sets/{document_set_id}/pipeline-runs")
    return document_set_id


def test_pipeline_publishes_a_coverage_report_reachable_over_the_api() -> None:
    client = TestClient(app)
    document_set_id = _run_pipeline(client)

    response = client.get(f"/document-sets/{document_set_id}/requirement-report")

    assert response.status_code == 200
    report = response.json()
    assert report["document_set_id"] == document_set_id
    # Every requirement of the set is answered exactly once -- the property
    # that makes the report a coverage statement rather than a feed.
    assert len(report["verdicts"]) == 2
    assert {v["requirement_id"] for v in report["verdicts"]} == {
        "req_report_threshold",
        "req_report_warehouse",
    }
    # The out-of-scope requirement is answered by the server, not the model.
    warehouse = next(
        v for v in report["verdicts"] if v["requirement_id"] == "req_report_warehouse"
    )
    assert warehouse["published_status"] == "not_applicable"
    assert warehouse["server_authored"] is True
    # Each row carries its obligation's provenance, not just a model sentence.
    threshold = next(
        v for v in report["verdicts"] if v["requirement_id"] == "req_report_threshold"
    )
    assert threshold["source_name"] == "SOP-CC-AVI-001"
    assert threshold["section"] == "8.4"
    assert threshold["requirement_text"]


def test_report_is_absent_with_a_clear_conflict_before_the_run() -> None:
    client = TestClient(app)
    repository.create_requirement_set(_requirement_set())
    created = client.post(
        "/document-sets",
        json={
            "tenant_id": "tenant_demo_pharma",
            "requirement_set_id": "rset_report_demo",
            "declared_document_type": "change_control",
            "declared_process_area": "aseptic_filling",
            "uploaded_by": "user_qrm_author",
        },
    )
    document_set_id = created.json()["document_set_id"]

    response = client.get(f"/document-sets/{document_set_id}/requirement-report")

    assert response.status_code == 409
    assert "Anforderungsbericht" in response.json()["detail"]


def test_unknown_document_set_is_not_found() -> None:
    client = TestClient(app)

    response = client.get("/document-sets/ds_gibt_es_nicht/requirement-report")

    assert response.status_code in {401, 403, 404}


def test_coverage_review_failure_never_fails_the_pipeline_run(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The finding pack is a complete result; an additive report may not sink it."""
    from app.services import pipeline as pipeline_module

    def _explode(**_: object) -> object:
        raise RuntimeError("coverage engine unavailable")

    monkeypatch.setattr(
        "app.services.requirement_review.default_requirement_review_engine",
        _explode,
    )
    client = TestClient(app)
    document_set_id = _run_pipeline(client)

    latest = client.get(f"/document-sets/{document_set_id}/pipeline-runs/latest")
    assert latest.status_code == 200
    assert latest.json()["status"] in {"completed", "needs_human_review"}
    assert latest.json()["failed_step"] is None
    assert any(
        event.event_type == "requirement_review_failed"
        and event.entity_id == document_set_id
        for event in audit_log.list_events()
    )
    assert pipeline_module is not None


def test_the_review_can_be_switched_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QRM_REQUIREMENT_REVIEW_ENABLED", "false")
    get_settings.cache_clear()
    client = TestClient(app)
    document_set_id = _run_pipeline(client)

    assert repository.get_requirement_report(document_set_id) is None
    latest = client.get(f"/document-sets/{document_set_id}/pipeline-runs/latest")
    assert latest.json()["failed_step"] is None


def test_failed_rows_can_be_retried_over_the_api() -> None:
    """The retry runs in the background, reports progress, and leaves the
    report standing when there is nothing to retry."""
    client = TestClient(app)
    document_set_id = _run_pipeline(client)

    idle = client.get(f"/document-sets/{document_set_id}/requirement-report/retry")
    assert idle.status_code == 200
    assert idle.json() == {"retryable": 0, "active": False, "detail": None}

    # Nothing failed in the mock run: the POST is a no-op that says so.
    nothing = client.post(f"/document-sets/{document_set_id}/requirement-report/retry")
    assert nothing.status_code == 202
    assert nothing.json()["active"] is False

    # Mark a row as a placeholder the way a dead model call would.
    report = repository.get_requirement_report(document_set_id)
    assert report is not None
    marked = report.model_copy(
        update={
            "verdicts": [
                v.model_copy(update={"needs_retry": True})
                if v.requirement_id == "req_report_threshold"
                else v
                for v in report.verdicts
            ]
        }
    )
    repository.replace_requirement_report(document_set_id=document_set_id, report=marked)

    accepted = client.post(f"/document-sets/{document_set_id}/requirement-report/retry")
    assert accepted.status_code == 202
    assert accepted.json()["retryable"] == 1
    assert accepted.json()["active"] is True

    # TestClient runs background tasks before returning: the retry is done.
    after = client.get(f"/document-sets/{document_set_id}/requirement-report/retry")
    assert after.json() == {"retryable": 0, "active": False, "detail": None}
    refreshed = client.get(f"/document-sets/{document_set_id}/requirement-report").json()
    threshold = next(
        v for v in refreshed["verdicts"] if v["requirement_id"] == "req_report_threshold"
    )
    assert threshold["needs_retry"] is False
    assert any(
        event.event_type == "requirement_review_retried"
        for event in audit_log.list_events()
    )


def test_retry_without_a_report_is_a_conflict() -> None:
    client = TestClient(app)
    repository.create_requirement_set(_requirement_set())
    created = client.post(
        "/document-sets",
        json={
            "tenant_id": "tenant_demo_pharma",
            "requirement_set_id": "rset_report_demo",
            "declared_document_type": "change_control",
            "declared_process_area": "aseptic_filling",
            "uploaded_by": "user_qrm_author",
        },
    )
    document_set_id = created.json()["document_set_id"]

    response = client.post(f"/document-sets/{document_set_id}/requirement-report/retry")

    assert response.status_code == 409


def test_retry_is_refused_while_the_pipeline_is_running() -> None:
    from app.schemas.pipeline import PipelineRunStatus

    client = TestClient(app)
    document_set_id = _run_pipeline(client)
    run = max(repository.pipeline_runs.values(), key=lambda r: r.started_at)
    repository.update_pipeline_run(
        run.model_copy(update={"status": PipelineRunStatus.RUNNING, "completed_at": None})
    )

    response = client.post(f"/document-sets/{document_set_id}/requirement-report/retry")

    assert response.status_code == 409
    assert "läuft gerade" in response.json()["detail"]
