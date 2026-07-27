from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
from typing import Any

from app.agents.providers import MockProvider, ProviderCallError
from app.audit.events import audit_log
from app.db.in_memory import repository
from app.schemas.domain import Document, DocumentChunk, DocumentSet, RequirementSet
from app.schemas.requirement_review import (
    EntailmentSupport,
    RequirementVerdictStatus,
)
from app.services.requirement_review import (
    ASSESSOR_PROMPT,
    ENTAILMENT_PROMPT,
    RequirementReviewEngine,
)

CHUNK_TEXT = (
    "Change Control CC-2026-014 senkt den AVI-Schwellwert. "
    "Ein Validierungsnachweis für den neuen Schwellwert liegt nicht bei. "
    "Die QA-Freigabe ist als pending markiert."
)


def _setup(*, process_area: str = "aseptic_filling") -> None:
    repository.reset()
    audit_log.clear()
    repository.create_requirement_set(
        RequirementSet(
            requirement_set_id="rset_req_review_2026",
            tenant_id="tenant_demo_pharma",
            name="Requirement Review Demo",
            version="2026.1",
            imported_at=datetime.now(UTC),
            imported_by="user_quality_admin",
            active=True,
            requirements=[
                {
                    "requirement_id": "req_threshold_validation",
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
                    "requirement_id": "req_warehouse_only",
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
    )
    repository.create_document_set(
        DocumentSet(
            document_set_id="ds_req_review_demo",
            tenant_id="tenant_demo_pharma",
            requirement_set_id="rset_req_review_2026",
            upload_timestamp=datetime.now(UTC),
            document_ids=[],
            declared_document_type="change_control",
            declared_process_area=process_area,
            uploaded_by="user_qrm_author",
            status="ready_for_orchestration",
        )
    )
    repository.add_document(
        document=Document(
            document_id="doc_req_change",
            document_set_id="ds_req_review_demo",
            filename="change-control.md",
            file_hash_sha256=sha256(b"change-control.md").hexdigest(),
            mime_type="text/markdown",
            page_count=1,
            storage_uri="local://req/change-control.md",
            parser_version="test-parser",
            parsing_status="parsed",
            parsing_quality_score=0.95,
            language="de",
            metadata={},
        ),
        chunks=[
            DocumentChunk(
                chunk_id="chunk_req_change_p1",
                document_id="doc_req_change",
                page_start=1,
                page_end=1,
                text=CHUNK_TEXT,
                token_count=len(CHUNK_TEXT.split()),
                extraction_confidence=0.95,
                bbox=None,
                source_hash=sha256(CHUNK_TEXT.encode()).hexdigest(),
            )
        ],
    )


def _assessor(verdicts: list[dict[str, Any]]) -> MockProvider:
    return MockProvider(output_factory=lambda *_: {"verdicts": verdicts})


def _entailment(support: str) -> MockProvider:
    return MockProvider(
        output_factory=lambda *_: {"support": support, "reason": "Testurteil."}
    )


def _violated_verdict(quote: str) -> dict[str, Any]:
    return {
        "requirement_id": "req_threshold_validation",
        "status": "violated",
        "severity": "high",
        "rationale": (
            "Der Schwellwert wird geändert, ohne dass ein Validierungsnachweis "
            "beiliegt."
        ),
        "evidence": [
            {
                "document_id": "doc_req_change",
                "chunk_id": "chunk_req_change_p1",
                "page": 1,
                "quote": quote,
            }
        ],
    }


def _engine(assessor: MockProvider, entailment: MockProvider) -> RequirementReviewEngine:
    return RequirementReviewEngine(
        repository=repository,
        audit_log=audit_log,
        assessor_provider=assessor,
        entailment_provider=entailment,
    )


def test_inapplicable_requirement_is_answered_by_the_server() -> None:
    """A warehouse-only requirement never reaches the model for a filling case."""
    _setup()
    seen_requirement_ids: list[str] = []

    def _capture(prompt: str, input_schema: dict[str, Any], output_schema: Any) -> dict:
        seen_requirement_ids.extend(
            entry["requirement_id"] for entry in input_schema["requirements"]
        )
        quote = "Ein Validierungsnachweis für den neuen Schwellwert liegt nicht bei."
        return {"verdicts": [_violated_verdict(quote)]}

    report = _engine(
        MockProvider(output_factory=_capture), _entailment("supports")
    ).run("ds_req_review_demo")

    assert seen_requirement_ids == ["req_threshold_validation"]
    warehouse = next(
        v for v in report.verdicts if v.requirement_id == "req_warehouse_only"
    )
    assert warehouse.published_status == RequirementVerdictStatus.NOT_APPLICABLE
    assert warehouse.server_authored is True


def test_fabricated_quote_is_dropped_and_verdict_downgraded_to_unclear() -> None:
    """A violation the pack cannot ground in a checkable quote must not read settled."""
    _setup()
    report = _engine(
        _assessor([_violated_verdict("Dieses Zitat steht nirgends im Dokument.")]),
        _entailment("supports"),
    ).run("ds_req_review_demo")

    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.model_status == RequirementVerdictStatus.VIOLATED
    assert verdict.published_status == RequirementVerdictStatus.UNCLEAR
    assert verdict.dropped_evidence_count == 1
    assert verdict.evidence == []
    assert verdict.provenance_ok is False


def test_entailment_none_downgrades_a_violation() -> None:
    _setup()
    report = _engine(
        _assessor(
            [_violated_verdict("Die QA-Freigabe ist als pending markiert.")]
        ),
        _entailment("none"),
    ).run("ds_req_review_demo")

    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.model_status == RequirementVerdictStatus.VIOLATED
    assert verdict.published_status == RequirementVerdictStatus.UNCLEAR
    assert verdict.entailment == EntailmentSupport.NONE


def test_entailment_supports_keeps_the_violation_published() -> None:
    _setup()
    report = _engine(
        _assessor(
            [_violated_verdict("Die QA-Freigabe ist als pending markiert.")]
        ),
        _entailment("supports"),
    ).run("ds_req_review_demo")

    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.published_status == RequirementVerdictStatus.VIOLATED
    assert verdict.entailment == EntailmentSupport.SUPPORTS
    assert verdict.provenance_ok is True


def test_failed_assessor_group_fails_secure_to_unclear() -> None:
    """A dead model call must surface as human-review work, not as a clean sheet."""
    _setup()

    def _raise(*_: Any) -> dict:
        raise ProviderCallError("provider unavailable")

    report = _engine(
        MockProvider(output_factory=_raise), _entailment("supports")
    ).run("ds_req_review_demo")

    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.published_status == RequirementVerdictStatus.UNCLEAR
    assert verdict.server_authored is True
    assert report.failed_model_call_count == 1
    failed = [call for call in report.model_calls if call.status == "failed"]
    assert failed and failed[0].error_type == "ProviderCallError"


def test_missing_verdict_for_a_requirement_becomes_unclear() -> None:
    """The model answering only half the group must not silently clear the rest."""
    _setup()
    report = _engine(_assessor([]), _entailment("supports")).run("ds_req_review_demo")

    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.published_status == RequirementVerdictStatus.UNCLEAR
    assert verdict.server_authored is True


def test_prompts_follow_the_umlaut_rule() -> None:
    for prompt in (ASSESSOR_PROMPT, ENTAILMENT_PROMPT):
        assert "ä" in prompt or "ü" in prompt
        for substitute in ("fuer", "pruef", "ausschliessl", "woertlich"):
            assert substitute not in prompt.lower()


def test_report_counts_and_audit_event() -> None:
    _setup()
    report = _engine(
        _assessor(
            [_violated_verdict("Die QA-Freigabe ist als pending markiert.")]
        ),
        _entailment("supports"),
    ).run("ds_req_review_demo")

    assert report.status_counts["violated"] == 1
    assert report.status_counts["not_applicable"] == 1
    events = [
        event
        for event in audit_log.list_events()
        if event.event_type == "requirement_review_completed"
    ]
    assert events and events[-1].payload["verdict_count"] == 2
