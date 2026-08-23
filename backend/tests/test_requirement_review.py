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
    CHALLENGE_PROMPT,
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


def _entailment(support: str, *, challenge_sustained: bool = False) -> MockProvider:
    """Second-look provider serving both verifier schemas by output type."""

    def _factory(prompt: str, input_schema: Any, output_schema: Any) -> dict[str, Any]:
        if getattr(output_schema, "__name__", "") == "FulfilledChallenge":
            return {
                "challenge_sustained": challenge_sustained,
                "missing_or_asserted_evidence": (
                    ["Audit-Trail-Auszug"] if challenge_sustained else []
                ),
                "reason": "Testzweitprüfung.",
            }
        return {"support": support, "reason": "Testurteil."}

    return MockProvider(output_factory=_factory)


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

    # Two assessor samples see the group (the second in reverse order); the
    # inapplicable requirement reaches neither.
    assert set(seen_requirement_ids) == {"req_threshold_validation"}
    assert len(seen_requirement_ids) == 2
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
    # Both samples died; both are on the record.
    assert report.failed_model_call_count == 2
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


def _fulfilled_verdict(quote: str, **overrides: Any) -> dict[str, Any]:
    verdict: dict[str, Any] = {
        "requirement_id": "req_threshold_validation",
        "status": "fulfilled",
        "severity": None,
        "rationale": "Die Validierung ist laut Freigabevermerk abgeschlossen.",
        "evidence": [
            {
                "document_id": "doc_req_change",
                "chunk_id": "chunk_req_change_p1",
                "page": 1,
                "quote": quote,
            }
        ],
        "evidence_type": "Freigabevermerk",
        "evidence_reference": "change-control.md Abschnitt QA",
        "evidence_sufficiency": "sufficient",
        "independent_support": False,
    }
    verdict.update(overrides)
    return verdict


def test_sustained_challenge_demotes_a_critical_fulfilled_to_unclear() -> None:
    """A fulfilled earned by self-attestation must not publish as settled.

    All five misses of the held-out run were this exact shape: the document
    vouching for itself and the assessor believing it.
    """
    _setup()
    report = _engine(
        _assessor([_fulfilled_verdict("Die QA-Freigabe ist als pending markiert.")]),
        _entailment("supports", challenge_sustained=True),
    ).run("ds_req_review_demo")

    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.model_status == RequirementVerdictStatus.FULFILLED
    assert verdict.published_status == RequirementVerdictStatus.UNCLEAR
    assert verdict.challenge_sustained is True
    assert "Audit-Trail-Auszug" in (verdict.challenge_reason or "")


def test_unsustained_challenge_keeps_fulfilled_published() -> None:
    _setup()
    report = _engine(
        _assessor([_fulfilled_verdict("Die QA-Freigabe ist als pending markiert.")]),
        _entailment("supports", challenge_sustained=False),
    ).run("ds_req_review_demo")

    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.published_status == RequirementVerdictStatus.FULFILLED
    assert verdict.challenge_sustained is False
    assert verdict.evidence_type == "Freigabevermerk"
    assert verdict.independent_support is False


def test_medium_criticality_fulfilled_skips_the_challenge() -> None:
    """The second look is bought only where a wrong all-clear is expensive."""
    _setup()
    calls: list[str] = []

    def _tracking_factory(prompt: str, input_schema: Any, output_schema: Any) -> dict:
        calls.append(getattr(output_schema, "__name__", ""))
        return {
            "challenge_sustained": True,
            "missing_or_asserted_evidence": [],
            "reason": "Sollte nie gefragt werden.",
        }

    report = _engine(
        _assessor(
            [
                _fulfilled_verdict(
                    "Die QA-Freigabe ist als pending markiert.",
                    requirement_id="req_warehouse_only",
                )
            ]
        ),
        MockProvider(output_factory=_tracking_factory),
    ).run("ds_req_review_demo", )

    assert "FulfilledChallenge" not in calls
    # req_warehouse_only is inapplicable for this set, so the verdict from the
    # model is ignored anyway -- the point is that no challenge call happened.
    assert report.failed_model_call_count == 0


def test_self_rated_insufficient_evidence_cannot_publish_fulfilled() -> None:
    _setup()
    report = _engine(
        _assessor(
            [
                _fulfilled_verdict(
                    "Die QA-Freigabe ist als pending markiert.",
                    evidence_sufficiency="insufficient",
                )
            ]
        ),
        _entailment("supports"),
    ).run("ds_req_review_demo")

    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.model_status == RequirementVerdictStatus.FULFILLED
    assert verdict.published_status == RequirementVerdictStatus.UNCLEAR


def test_failed_challenge_call_fails_secure_to_unclear() -> None:
    _setup()

    def _factory(prompt: str, input_schema: Any, output_schema: Any) -> dict:
        if getattr(output_schema, "__name__", "") == "FulfilledChallenge":
            raise ProviderCallError("provider unavailable")
        return {"support": "supports", "reason": "Testurteil."}

    report = _engine(
        _assessor([_fulfilled_verdict("Die QA-Freigabe ist als pending markiert.")]),
        MockProvider(output_factory=_factory),
    ).run("ds_req_review_demo")

    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.published_status == RequirementVerdictStatus.UNCLEAR
    assert report.failed_model_call_count == 1


def test_assessor_prompt_encodes_differentiated_evidence_scepticism() -> None:
    """The rule must distinguish execution proof from documented declarations.

    A blanket "self-attestation never counts" would flood the report with
    precautionary unclear verdicts on perfectly documented declarations.
    """
    assert "DURCHFÜHRUNG" in ASSESSOR_PROMPT
    assert "Primärevidenz" in ASSESSOR_PROMPT
    assert "ERKLÄRUNG" in ASSESSOR_PROMPT
    assert "kann die signierte Erklärung selbst die" in ASSESSOR_PROMPT
    assert "evidence_sufficiency" in ASSESSOR_PROMPT
    assert "independent_support" in ASSESSOR_PROMPT
    assert "leeres Pflichtfeld" in ASSESSOR_PROMPT


def test_prompts_follow_the_umlaut_rule() -> None:
    for prompt in (ASSESSOR_PROMPT, ENTAILMENT_PROMPT, CHALLENGE_PROMPT):
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


def test_presentation_variant_quote_is_repaired_not_dropped() -> None:
    """Markdown and typographic drift must not cost a verdict its evidence.

    One in ten evidence-bearing verdicts lost all quotes to exactly this in
    the regression runs, demoting found violations to unclear.
    """
    _setup()
    # Chunk text says "senkt den AVI-Schwellwert" -- the model quotes it with
    # markdown emphasis that does not exist in the source.
    report = _engine(
        _assessor([_violated_verdict("Change Control CC-2026-014 senkt den **AVI-Schwellwert**.")]),
        _entailment("supports"),
    ).run("ds_req_review_demo")

    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.published_status == RequirementVerdictStatus.VIOLATED
    assert verdict.dropped_evidence_count == 0
    assert verdict.evidence[0].quote == "Change Control CC-2026-014 senkt den AVI-Schwellwert."


def test_ellipsis_quote_grounds_as_one_item_per_fragment() -> None:
    _setup()
    report = _engine(
        _assessor(
            [
                _violated_verdict(
                    "Change Control CC-2026-014 senkt den AVI-Schwellwert. [...] "
                    "Die QA-Freigabe ist als pending markiert."
                )
            ]
        ),
        _entailment("supports"),
    ).run("ds_req_review_demo")

    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.published_status == RequirementVerdictStatus.VIOLATED
    quotes = [item.quote for item in verdict.evidence]
    assert quotes == [
        "Change Control CC-2026-014 senkt den AVI-Schwellwert.",
        "Die QA-Freigabe ist als pending markiert.",
    ]


def test_unrepairable_quote_is_dropped_with_a_recorded_reason() -> None:
    _setup()
    report = _engine(
        _assessor([_violated_verdict("Dieses Zitat steht nirgends im Dokument.")]),
        _entailment("supports"),
    ).run("ds_req_review_demo")

    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.published_status == RequirementVerdictStatus.UNCLEAR
    assert verdict.dropped_evidence_count == 1
    assert len(verdict.dropped_evidence_reasons) == 1
    assert "nicht im Chunk auffindbar" in verdict.dropped_evidence_reasons[0]
    assert "Dieses Zitat steht nirgends" in verdict.dropped_evidence_reasons[0]


def test_challenge_skips_fulfilled_with_independent_support() -> None:
    """The second look targets self-attestation, not independently backed rows."""
    _setup()
    calls: list[str] = []

    def _tracking(prompt: str, input_schema: Any, output_schema: Any) -> dict:
        calls.append(getattr(output_schema, "__name__", ""))
        return {
            "challenge_sustained": True,
            "missing_or_asserted_evidence": [],
            "reason": "Sollte nie gefragt werden.",
        }

    report = _engine(
        _assessor(
            [
                _fulfilled_verdict(
                    "Die QA-Freigabe ist als pending markiert.",
                    independent_support=True,
                )
            ]
        ),
        MockProvider(output_factory=_tracking),
    ).run("ds_req_review_demo")

    assert "FulfilledChallenge" not in calls
    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.published_status == RequirementVerdictStatus.FULFILLED


def _extraction(payload: dict[str, Any]) -> MockProvider:
    base: dict[str, Any] = {
        "signatures": [],
        "measurements": [],
        "specifications": [],
        "action_items": [],
        "events": [],
    }
    base.update(payload)
    return MockProvider(output_factory=lambda *_: base)


def test_validator_breach_overrides_a_fulfilled_verdict() -> None:
    """Deterministic evidence of a breach must beat a model all-clear."""
    _setup()
    engine = RequirementReviewEngine(
        repository=repository,
        audit_log=audit_log,
        assessor_provider=_assessor(
            [_fulfilled_verdict("Die QA-Freigabe ist als pending markiert.")]
        ),
        entailment_provider=_entailment("supports", challenge_sustained=False),
        extraction_provider=_extraction(
            {
                "signatures": [
                    {
                        "field_label": "Freigabe Produktionsleitung",
                        "role": "Produktionsleitung",
                        "signer": None,
                        "date": None,
                        "is_empty": True,
                        "requirement_ids": ["req_threshold_validation"],
                        "location": {
                            "document_id": "doc_req_change",
                            "chunk_id": "chunk_req_change_p1",
                            "page": 1,
                            "quote": "Die QA-Freigabe ist als pending markiert.",
                        },
                    }
                ]
            }
        ),
    )
    report = engine.run("ds_req_review_demo")

    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.published_status == RequirementVerdictStatus.VIOLATED
    assert verdict.validator_flags == ["empty_required_field"]
    assert any("Freigabe Produktionsleitung" in s for s in verdict.validator_statements)
    assert len(report.validator_findings) == 1


def test_ungrounded_extraction_rows_never_reach_the_validators() -> None:
    """A fabricated quote must not become deterministic 'evidence'."""
    _setup()
    engine = RequirementReviewEngine(
        repository=repository,
        audit_log=audit_log,
        assessor_provider=_assessor([]),
        entailment_provider=_entailment("supports"),
        extraction_provider=_extraction(
            {
                "signatures": [
                    {
                        "field_label": "Erfundenes Feld",
                        "is_empty": True,
                        "requirement_ids": ["req_threshold_validation"],
                        "location": {
                            "document_id": "doc_req_change",
                            "chunk_id": "chunk_req_change_p1",
                            "page": 1,
                            "quote": "Dieses Zitat existiert nirgends.",
                        },
                    }
                ]
            }
        ),
    )
    report = engine.run("ds_req_review_demo")

    assert report.validator_findings == []
    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.published_status == RequirementVerdictStatus.UNCLEAR


def test_failed_extraction_keeps_assessed_verdicts_intact() -> None:
    """The validator layer is additive; its death must not sink the run."""
    _setup()

    def _raise(*_: Any) -> dict:
        raise ProviderCallError("extraction unavailable")

    engine = RequirementReviewEngine(
        repository=repository,
        audit_log=audit_log,
        assessor_provider=_assessor(
            [_violated_verdict("Die QA-Freigabe ist als pending markiert.")]
        ),
        entailment_provider=_entailment("supports"),
        extraction_provider=MockProvider(output_factory=_raise),
    )
    report = engine.run("ds_req_review_demo")

    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.published_status == RequirementVerdictStatus.VIOLATED
    failed = [c for c in report.model_calls if c.status == "failed"]
    # Both category passes of the document die with the same transport error.
    assert [c.purpose for c in failed] == [
        "extract[doc_req_change:felder]",
        "extract[doc_req_change:werte]",
    ]


def test_mojibake_umlauts_in_a_quote_are_repaired_before_provenance() -> None:
    """A correct detection was scored as a miss over a broken encoding.

    The quote came back with U+000E followed by "4" where "ä" belonged. It
    grounded nowhere, the verdict lost its only evidence and demoted, and the
    blind corpus counted an error the engine had described almost verbatim.
    """
    _setup()
    corrupted = CHUNK_TEXT[: CHUNK_TEXT.index("Validierungsnachweis")] + (
        "Validierungsnachweis f\x0fcr den neuen Schwellwert liegt nicht bei."
    )
    report = _engine(
        _assessor([_violated_verdict(corrupted[corrupted.index("Ein Valid") :])]
                  if "Ein Valid" in corrupted
                  else [_violated_verdict("Ein Validierungsnachweis f\x0fcr den "
                                          "neuen Schwellwert liegt nicht bei.")]),
        _entailment("supports"),
    ).run("ds_req_review_demo")

    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.published_status == RequirementVerdictStatus.VIOLATED
    assert verdict.dropped_evidence_count == 0
    assert verdict.evidence[0].quote == (
        "Ein Validierungsnachweis für den neuen Schwellwert liegt nicht bei."
    )


def test_hallucinated_chunk_id_is_relocated_within_the_cited_document() -> None:
    """The chunk id is bookkeeping; the document is the claim.

    A verdict naming the right document with an invented chunk id lost both
    quotes and demoted to unclear, although it had found its planted error.
    """
    _setup()
    verdict_payload = _violated_verdict("Die QA-Freigabe ist als pending markiert.")
    verdict_payload["evidence"][0]["chunk_id"] = "chunk_erfunden_p9"
    report = _engine(
        _assessor([verdict_payload]), _entailment("supports")
    ).run("ds_req_review_demo")

    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.published_status == RequirementVerdictStatus.VIOLATED
    assert verdict.dropped_evidence_count == 0
    assert verdict.evidence[0].chunk_id == "chunk_req_change_p1"
    assert verdict.provenance_ok is True


def test_existing_chunk_id_with_a_different_document_is_never_relocated() -> None:
    """A real chunk paired with the wrong document is the hallucination signal.

    Relocating would search the claimed document for the same words and, on
    boilerplate, find them -- publishing a citation into a document the
    finding was never about, with provenance_ok intact.
    """
    _setup()
    boilerplate = "Die QA-Freigabe ist als pending markiert."
    repository.add_document(
        document=Document(
            document_id="doc_req_other",
            document_set_id="ds_req_review_demo",
            filename="sop.md",
            file_hash_sha256=sha256(b"sop.md").hexdigest(),
            mime_type="text/markdown",
            page_count=1,
            storage_uri="local://req/sop.md",
            parser_version="test-parser",
            parsing_status="parsed",
            parsing_quality_score=0.95,
            language="de",
            metadata={},
        ),
        chunks=[
            DocumentChunk(
                chunk_id="chunk_req_other_p1",
                document_id="doc_req_other",
                page_start=1,
                page_end=1,
                text=boilerplate,
                token_count=len(boilerplate.split()),
                extraction_confidence=0.95,
                bbox=None,
                source_hash=sha256(boilerplate.encode()).hexdigest(),
            )
        ],
    )
    verdict_payload = _violated_verdict(boilerplate)
    # Real chunk from the change-control document, claimed for the SOP.
    verdict_payload["evidence"][0]["document_id"] = "doc_req_other"
    verdict_payload["evidence"][0]["chunk_id"] = "chunk_req_change_p1"
    report = _engine(
        _assessor([verdict_payload]), _entailment("supports")
    ).run("ds_req_review_demo")

    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.published_status == RequirementVerdictStatus.UNCLEAR
    assert verdict.dropped_evidence_count == 1
    assert "anderen Dokument" in verdict.dropped_evidence_reasons[0]


def test_repair_leaves_legitimate_control_characters_alone() -> None:
    """U+000C is the page break of PDF text, not a broken umlaut.

    Accepting every C0 lead turned "\\x0c4. Quartal" into "Ä. Quartal" and, by
    overwriting the quote unconditionally, destroyed text that would have
    grounded through reconciliation on its own.
    """
    from app.services.requirement_review import _repair_mojibake

    assert _repair_mojibake("\x0c4. Quartal") == "\x0c4. Quartal"
    assert _repair_mojibake("Abschnitt\r6.2") == "Abschnitt\r6.2"
    assert _repair_mojibake("Integrit\x0e4t") == "Integrität"
    assert _repair_mojibake("f\x0fcr") == "für"


def test_relocation_refuses_an_ambiguous_passage_without_a_page_anchor() -> None:
    """A sentence appearing twice may not be relocated by document order.

    Taking the first match published a precise-looking page the model never
    named, pointing the reviewer at a different occurrence than the rationale
    describes.
    """
    _setup()
    repeated = "Der Nachweis liegt nicht vor."
    for index in (1, 2):
        repository.add_document(
            document=Document(
                document_id=f"doc_req_rep{index}",
                document_set_id="ds_req_review_demo",
                filename=f"bericht{index}.md",
                file_hash_sha256=sha256(f"bericht{index}".encode()).hexdigest(),
                mime_type="text/markdown",
                page_count=1,
                storage_uri=f"local://req/bericht{index}.md",
                parser_version="test-parser",
                parsing_status="parsed",
                parsing_quality_score=0.95,
                language="de",
                metadata={},
            ),
            chunks=[],
        )
    # Two chunks of one document, both carrying the sentence, neither on the
    # page the model named.
    repository.chunks_by_document["doc_req_rep1"] = [
        DocumentChunk(
            chunk_id=f"chunk_req_rep_p{page}",
            document_id="doc_req_rep1",
            page_start=page,
            page_end=page,
            text=repeated,
            token_count=len(repeated.split()),
            extraction_confidence=0.95,
            bbox=None,
            source_hash=sha256(f"{repeated}{page}".encode()).hexdigest(),
        )
        for page in (4, 9)
    ]
    verdict_payload = _violated_verdict(repeated)
    verdict_payload["evidence"][0]["document_id"] = "doc_req_rep1"
    verdict_payload["evidence"][0]["chunk_id"] = "chunk_erfunden_p31"
    verdict_payload["evidence"][0]["page"] = 31
    report = _engine(
        _assessor([verdict_payload]), _entailment("supports")
    ).run("ds_req_review_demo")

    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.published_status == RequirementVerdictStatus.UNCLEAR
    assert verdict.dropped_evidence_count == 1


def test_relocation_refuses_a_quote_absent_from_the_cited_document() -> None:
    """Relocation moves the index, never the standard of proof."""
    _setup()
    verdict_payload = _violated_verdict("Diesen Satz enthält kein Dokument.")
    verdict_payload["evidence"][0]["chunk_id"] = "chunk_erfunden_p9"
    report = _engine(
        _assessor([verdict_payload]), _entailment("supports")
    ).run("ds_req_review_demo")

    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.published_status == RequirementVerdictStatus.UNCLEAR
    assert verdict.dropped_evidence_count == 1
    assert verdict.evidence == []


def test_arithmetic_contradiction_publishes_without_escalating_a_verdict() -> None:
    """The check reports a fact about the document, not a requirement breach.

    Escalating someone else's verdict would risk the decoy specificity that is
    the engine's strongest measured result, and the check cannot know which
    obligation a miscalculation breaches.
    """
    _setup()
    text = "An 14 von 320 Ampullen (2,8 %) wurden Eintritte festgestellt."
    repository.add_document(
        document=Document(
            document_id="doc_req_numbers",
            document_set_id="ds_req_review_demo",
            filename="pruefprotokoll.md",
            file_hash_sha256=sha256(b"pruefprotokoll.md").hexdigest(),
            mime_type="text/markdown",
            page_count=1,
            storage_uri="local://req/pruefprotokoll.md",
            parser_version="test-parser",
            parsing_status="parsed",
            parsing_quality_score=0.95,
            language="de",
            metadata={},
        ),
        chunks=[
            DocumentChunk(
                chunk_id="chunk_req_numbers_p1",
                document_id="doc_req_numbers",
                page_start=1,
                page_end=1,
                text=text,
                token_count=len(text.split()),
                extraction_confidence=0.95,
                bbox=None,
                source_hash=sha256(text.encode()).hexdigest(),
            )
        ],
    )
    fulfilled = _fulfilled_verdict("Die QA-Freigabe ist als pending markiert.")
    fulfilled["evidence"].append(
        {
            "document_id": "doc_req_numbers",
            "chunk_id": "chunk_req_numbers_p1",
            "page": 1,
            "quote": text,
        }
    )
    report = _engine(
        _assessor([fulfilled]), _entailment("supports", challenge_sustained=False)
    ).run("ds_req_review_demo")

    arithmetic = [
        f
        for f in report.validator_findings
        if f["validator_id"] == "share_contradicts_fraction"
    ]
    assert len(arithmetic) == 1
    assert arithmetic[0]["requirement_ids"] == []

    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    # Annotated, because it cites the same chunk -- but not escalated.
    assert verdict.published_status == RequirementVerdictStatus.FULFILLED
    assert "share_contradicts_fraction" in verdict.validator_flags


def test_pass_scope_is_enforced_server_side_against_scope_ignoring_models() -> None:
    """A model returning every category in every pass must not double the rows.

    The category split only bounds output size if each pass's result is
    filtered to its categories on the server -- trusting the model to honour
    the scope instruction would turn scope drift into duplicated evidence.
    """
    from app.services.evidence_extraction import EvidenceExtractor

    full_payload = {
        "signatures": [
            {
                "field_label": "Freigabe QA",
                "is_empty": True,
                "requirement_ids": ["req_threshold_validation"],
                "location": {
                    "document_id": "doc_req_change",
                    "chunk_id": "chunk_req_change_p1",
                    "page": 1,
                    "quote": "Die QA-Freigabe ist als pending markiert.",
                },
            }
        ],
        "measurements": [
            {
                "parameter": "Schwellwert",
                "value": "42",
                "unit": "N",
                "requirement_ids": [],
                "location": {
                    "document_id": "doc_req_change",
                    "chunk_id": "chunk_req_change_p1",
                    "page": 1,
                    "quote": "Change Control CC-2026-014 senkt den AVI-Schwellwert.",
                },
            }
        ],
        "specifications": [],
        "action_items": [],
        "events": [],
    }
    _setup()
    chunks = repository.list_chunks_for_document_set("ds_req_review_demo")
    outcome = EvidenceExtractor(
        provider=MockProvider(output_factory=lambda *_: full_payload)
    ).extract(
        chunk_payload=[
            {
                "document_id": "doc_req_change",
                "document_name": "change-control.md",
                "chunk_id": "chunk_req_change_p1",
                "page": 1,
                "text": CHUNK_TEXT,
            }
        ],
        requirement_index=[],
        chunks=chunks,
    )

    # Both passes returned both categories; the scope filter keeps each row once.
    assert len(outcome.evidence.signatures) == 1
    assert len(outcome.evidence.measurements) == 1
    assert outcome.succeeded_document_ids == [
        "doc_req_change:felder",
        "doc_req_change:werte",
    ]


def test_extraction_failure_is_contained_to_its_document() -> None:
    """One truncated document must not silence the validators for the case.

    The blind run's two zero-detection cases were exactly this: a single
    whole-case extraction call hit the output cap, and with it every
    mechanical check died. Per-document calls make the failure a named gap.
    """
    _setup()
    second_text = "Freigabefeld Produktionsleitung: ________ (Unterschrift ausstehend)"
    repository.add_document(
        document=Document(
            document_id="doc_req_capa",
            document_set_id="ds_req_review_demo",
            filename="capa-plan.md",
            file_hash_sha256=sha256(b"capa-plan.md").hexdigest(),
            mime_type="text/markdown",
            page_count=1,
            storage_uri="local://req/capa-plan.md",
            parser_version="test-parser",
            parsing_status="parsed",
            parsing_quality_score=0.95,
            language="de",
            metadata={},
        ),
        chunks=[
            DocumentChunk(
                chunk_id="chunk_req_capa_p1",
                document_id="doc_req_capa",
                page_start=1,
                page_end=1,
                text=second_text,
                token_count=len(second_text.split()),
                extraction_confidence=0.95,
                bbox=None,
                source_hash=sha256(second_text.encode()).hexdigest(),
            )
        ],
    )

    def _per_document_factory(
        prompt: str, input_schema: dict[str, Any], output_schema: Any
    ) -> dict[str, Any]:
        chunks = input_schema.get("chunks", [])
        document_id = chunks[0]["document_id"] if chunks else ""
        if document_id == "doc_req_change":
            raise ProviderCallError("anthropic provider output was truncated")
        return {
            "signatures": [
                {
                    "field_label": "Freigabefeld Produktionsleitung",
                    "is_empty": True,
                    "requirement_ids": ["req_threshold_validation"],
                    "location": {
                        "document_id": "doc_req_capa",
                        "chunk_id": "chunk_req_capa_p1",
                        "page": 1,
                        "quote": "Freigabefeld Produktionsleitung: ________",
                    },
                }
            ],
            "measurements": [],
            "specifications": [],
            "action_items": [],
            "events": [],
        }

    engine = RequirementReviewEngine(
        repository=repository,
        audit_log=audit_log,
        assessor_provider=_assessor([]),
        entailment_provider=_entailment("supports"),
        extraction_provider=MockProvider(output_factory=_per_document_factory),
    )
    report = engine.run("ds_req_review_demo")

    assert len(report.validator_findings) == 1
    statuses = {c.purpose: c.status for c in report.model_calls if "extract" in c.purpose}
    assert statuses == {
        "extract[doc_req_change:felder]": "failed",
        "extract[doc_req_change:werte]": "failed",
        "extract[doc_req_capa:felder]": "succeeded",
        "extract[doc_req_capa:werte]": "succeeded",
    }


def test_group_payload_normalization_repairs_shape_drift() -> None:
    """Extra keys and enum-adjacent spellings must not kill a verdict group.

    The blind run lost one group to extra keys in verdict objects and another
    to a status value outside the enum -- both mechanically recoverable, and
    both now repaired at the provider's normalization hook.
    """
    from app.schemas.requirement_review import RequirementGroupOutput

    messy = {
        "verdicts": [
            {
                "requirement_id": "req_threshold_validation",
                "status": "Nicht anwendbar",
                "severity": "hoch",
                "rationale": "Begründung.",
                "evidence": [
                    {
                        "document_id": "doc_req_change",
                        "chunk_id": "chunk_req_change_p1",
                        "page": 1,
                        "quote": "Zitat.",
                        "confidence": 0.9,
                    }
                ],
                "evidence_sufficiency": "ausreichend",
                "independent_support": "ja",
                "assessment_notes": "extra key the schema forbids",
            }
        ]
    }
    provider = MockProvider(output_factory=lambda *_: messy)
    result = provider.run_structured("prompt", {}, RequirementGroupOutput)

    verdict = result["verdicts"][0]
    assert verdict["status"] == "not_applicable"
    assert verdict["severity"] == "high"
    assert verdict["evidence_sufficiency"] == "sufficient"
    assert verdict["independent_support"] is True
    assert "assessment_notes" not in verdict
    assert "confidence" not in verdict["evidence"][0]


def test_challenge_payload_normalization_repairs_string_list() -> None:
    """The blind regression lost one challenge to a string where a list belongs."""
    from app.schemas.requirement_review import FulfilledChallenge

    messy = {
        "challenge_sustained": "ja",
        "missing_or_asserted_evidence": "Audit-Trail-Auszug fehlt",
        "reason": "Nur behauptet.",
        "confidence": "hoch",
    }
    provider = MockProvider(output_factory=lambda *_: messy)
    result = provider.run_structured("prompt", {}, FulfilledChallenge)

    assert result["challenge_sustained"] is True
    assert result["missing_or_asserted_evidence"] == ["Audit-Trail-Auszug fehlt"]
    assert "confidence" not in result


def test_extraction_prompt_types_lists_and_binds_activities_to_objects() -> None:
    """The two decoy-hit classes of the blind regression, pinned as prompt rules.

    A document inventory typed as an action list turned two correct fulfilled
    verdicts into violations; an activity_key spanning two batches turned two
    rightful signers into a contradiction.
    """
    from app.services.evidence_extraction import EXTRACTION_PROMPT

    assert "KEINE action_items" in EXTRACTION_PROMPT
    assert "Dokumentlisten" in EXTRACTION_PROMPT
    assert "Verteilerlisten" in EXTRACTION_PROMPT
    assert "SELBEN Objekt" in EXTRACTION_PROMPT
    assert "gleiche Charge" in EXTRACTION_PROMPT
    assert "zwei Aktivitäten" in EXTRACTION_PROMPT
    assert "Ein Datum ist kein Unterzeichner" in EXTRACTION_PROMPT


def test_ambiguous_challenge_sustained_string_fails_validation_not_false() -> None:
    """A sentence-form sustained challenge must never silently become False.

    Mapping the unknown to False would keep a FULFILLED published although the
    second look confirmed the objection -- the one direction the challenge is
    forbidden to take. Ambiguity has to fail validation so the call is
    re-asked and, failing twice, the verdict drops to UNCLEAR.
    """
    from app.agents.providers import ProviderStructuredOutputError as SchemaError
    from app.schemas.requirement_review import FulfilledChallenge

    ambiguous = {
        "challenge_sustained": "Ja, der Audit-Trail-Nachweis ist nur behauptet",
        "missing_or_asserted_evidence": [],
        "reason": "Begründung.",
    }
    provider = MockProvider(output_factory=lambda *_: ambiguous)
    try:
        provider.run_structured("prompt", {}, FulfilledChallenge)
        raise AssertionError("ambiguous string must not validate")
    except SchemaError:
        pass

    # Unambiguous German forms map in both directions.
    for text, expected in (("wahr", True), ("Ja.", True), ("nein", False)):
        payload = {**ambiguous, "challenge_sustained": text}
        provider = MockProvider(output_factory=lambda *_, p=payload: p)
        result = provider.run_structured("prompt", {}, FulfilledChallenge)
        assert result["challenge_sustained"] is expected, text


def test_unmappable_enum_values_fail_validation_instead_of_becoming_none() -> None:
    """"nicht ausreichend" must not vanish into None and bypass the downgrade."""
    from app.agents.providers import ProviderStructuredOutputError as SchemaError
    from app.schemas.requirement_review import RequirementGroupOutput

    def _verdict_with(**fields: Any) -> dict[str, Any]:
        return {
            "verdicts": [
                {
                    "requirement_id": "req_x",
                    "status": "fulfilled",
                    "rationale": "Begründung.",
                    # A decided verdict needs a quote; this test is about the
                    # enum fields, so give it one that is not under test.
                    "evidence": [
                        {
                            "document_id": "doc_x",
                            "chunk_id": "chunk_x",
                            "page": 1,
                            "quote": "Die QA-Freigabe ist dokumentiert.",
                        }
                    ],
                    **fields,
                }
            ]
        }

    for bad in (
        _verdict_with(evidence_sufficiency="nicht ausreichend"),
        _verdict_with(severity="schwerwiegend"),
    ):
        provider = MockProvider(output_factory=lambda *_, p=bad: p)
        try:
            provider.run_structured("prompt", {}, RequirementGroupOutput)
            raise AssertionError("unmappable enum value must not validate")
        except SchemaError:
            pass

    # Punctuation variants of known values still repair.
    ok = _verdict_with(evidence_sufficiency="unzureichend.", severity="kritisch")
    provider = MockProvider(output_factory=lambda *_: ok)
    result = provider.run_structured("prompt", {}, RequirementGroupOutput)
    assert result["verdicts"][0]["evidence_sufficiency"] == "insufficient"
    assert result["verdicts"][0]["severity"] == "critical"


def test_decided_verdict_without_quote_gets_one_explicit_second_chance() -> None:
    """A violated verdict with no quote is re-asked once, never lost as a group.

    The 2026-08-22 Hetzner ablation demoted 136 quote-less VIOLATED verdicts to
    UNCLEAR without a second ask. Enforcing the quote in the schema was tried
    and lost whole groups when the model refused twice; the engine rule keeps
    the better of the two answers and leaves demotion to provenance.
    """
    from app.schemas.requirement_review import RequirementGroupOutput
    from app.services.requirement_review import (
        REASK_CONTRACT_NOTE,
        RequirementReviewEngine,
    )

    quote = {"document_id": "doc_x", "chunk_id": "chunk_x", "page": 1, "quote": "R-02."}

    def _group(evidence_for_a: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "verdicts": [
                {"requirement_id": "req_a", "status": "violated", "severity": "high",
                 "rationale": "Chargenliste fehlt.", "evidence": evidence_for_a},
                {"requirement_id": "req_b", "status": "violated", "severity": "high",
                 "rationale": "Belegt.", "evidence": [quote]},
            ]
        }

    prompts: list[str] = []

    # The provider is only called for the second chance; the first answer is
    # handed in directly below, so the learned answer carries the quote.
    def _learns(prompt: str, *_: Any) -> dict[str, Any]:
        prompts.append(prompt)
        return _group([quote])

    engine = RequirementReviewEngine.__new__(RequirementReviewEngine)
    engine.assessor_provider = MockProvider(output_factory=_learns)
    first = RequirementGroupOutput.model_validate(_group([]))
    discarded: list[Any] = []

    kept = engine._insist_on_quotes(first, {}, discarded_usage=discarded)

    assert len(prompts) == 1 and prompts[0].endswith(REASK_CONTRACT_NOTE)
    assert "ohne Zitat" in REASK_CONTRACT_NOTE
    assert kept.verdicts[0].evidence[0].quote == "R-02."

    # A model that refuses twice keeps the first answer -- req_b's quote is
    # not thrown away with req_a's missing one.
    engine.assessor_provider = MockProvider(output_factory=lambda *_: _group([]))
    kept = engine._insist_on_quotes(first, {}, discarded_usage=[])
    assert [v.requirement_id for v in kept.verdicts] == ["req_a", "req_b"]
    assert kept.verdicts[1].evidence[0].quote == "R-02."

    # Nothing to insist on: no extra call.
    calls: list[int] = []
    engine.assessor_provider = MockProvider(output_factory=lambda *_: calls.append(1) or _group([quote]))
    complete = RequirementGroupOutput.model_validate(_group([quote]))
    assert engine._insist_on_quotes(complete, {}, discarded_usage=[]) is complete
    assert calls == []


def test_reasked_call_accounts_for_the_discarded_sample() -> None:
    """The first, malformed sample was billed; the call record must carry it."""
    _setup()
    attempts: list[int] = []

    def _flaky(prompt: str, input_schema: Any, output_schema: Any) -> dict[str, Any]:
        attempts.append(1)
        if len(attempts) == 1:
            return {
                "verdicts": [
                    {
                        "requirement_id": "req_threshold_validation",
                        "status": "banana",
                        "rationale": "kaputt",
                        "evidence": [],
                    }
                ],
                "token_usage": {
                    "input_tokens": 1000,
                    "output_tokens": 50,
                    "total_tokens": 1050,
                },
            }
        return {
            "verdicts": [
                _violated_verdict("Die QA-Freigabe ist als pending markiert.")
            ],
            "token_usage": {
                "input_tokens": 1000,
                "output_tokens": 400,
                "total_tokens": 1400,
            },
        }

    report = _engine(
        MockProvider(output_factory=_flaky), _entailment("supports")
    ).run("ds_req_review_demo")

    assess = next(c for c in report.model_calls if c.purpose == "assess")
    assert assess.status == "succeeded"
    assert assess.input_tokens == 2000
    assert assess.output_tokens == 450


def _two_sample_assessor(
    first: list[dict[str, Any]], second: list[dict[str, Any]]
) -> MockProvider:
    calls: list[int] = []

    def _factory(prompt: str, input_schema: Any, output_schema: Any) -> dict[str, Any]:
        calls.append(1)
        return {"verdicts": first if len(calls) == 1 else second}

    return MockProvider(output_factory=_factory)


def test_violation_seen_by_one_sample_survives_the_merge() -> None:
    """Nine errors flipped between single-sample runs; the union keeps them.

    A violation only one sample saw becomes the merged candidate and still has
    to pass provenance and entailment -- the gates, not the merge, set the
    standard of proof.
    """
    _setup()
    report = _engine(
        _two_sample_assessor(
            [_fulfilled_verdict("Die QA-Freigabe ist als pending markiert.")],
            [_violated_verdict("Die QA-Freigabe ist als pending markiert.")],
        ),
        _entailment("supports"),
    ).run("ds_req_review_demo")

    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.published_status == RequirementVerdictStatus.VIOLATED
    assert verdict.sample_disagreement is True
    assert verdict.entailment == EntailmentSupport.SUPPORTS


def test_agreeing_samples_report_no_disagreement() -> None:
    _setup()
    verdict_payload = _violated_verdict("Die QA-Freigabe ist als pending markiert.")
    report = _engine(
        _two_sample_assessor([verdict_payload], [verdict_payload]),
        _entailment("supports"),
    ).run("ds_req_review_demo")

    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.published_status == RequirementVerdictStatus.VIOLATED
    assert verdict.sample_disagreement is False


def test_unclear_sample_blocks_a_lone_fulfilled() -> None:
    """Disagreement between unclear and fulfilled must not settle as fulfilled."""
    _setup()
    unclear_payload = {
        "requirement_id": "req_threshold_validation",
        "status": "unclear",
        "severity": "medium",
        "rationale": "Die Unterlagen reichen nicht für eine Entscheidung.",
        "evidence": [],
    }
    report = _engine(
        _two_sample_assessor(
            [_fulfilled_verdict("Die QA-Freigabe ist als pending markiert.")],
            [unclear_payload],
        ),
        _entailment("supports", challenge_sustained=False),
    ).run("ds_req_review_demo")

    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.published_status == RequirementVerdictStatus.UNCLEAR
    assert verdict.sample_disagreement is True


def test_second_sample_sees_reversed_input_order() -> None:
    """Temperature-zero providers repeat themselves; the reorder decorrelates."""
    _setup()
    seen_chunk_orders: list[list[str]] = []

    def _capture(prompt: str, input_schema: Any, output_schema: Any) -> dict[str, Any]:
        seen_chunk_orders.append(
            [chunk["chunk_id"] for chunk in input_schema["chunks"]]
        )
        return {"verdicts": []}

    second_text = "Zweiter Chunk für die Reihenfolgeprüfung."
    repository.add_document(
        document=Document(
            document_id="doc_req_order",
            document_set_id="ds_req_review_demo",
            filename="order.md",
            file_hash_sha256=sha256(b"order.md").hexdigest(),
            mime_type="text/markdown",
            page_count=1,
            storage_uri="local://req/order.md",
            parser_version="test-parser",
            parsing_status="parsed",
            parsing_quality_score=0.95,
            language="de",
            metadata={},
        ),
        chunks=[
            DocumentChunk(
                chunk_id="chunk_req_order_p1",
                document_id="doc_req_order",
                page_start=1,
                page_end=1,
                text=second_text,
                token_count=len(second_text.split()),
                extraction_confidence=0.95,
                bbox=None,
                source_hash=sha256(second_text.encode()).hexdigest(),
            )
        ],
    )
    _engine(
        MockProvider(output_factory=_capture), _entailment("supports")
    ).run("ds_req_review_demo")

    assert len(seen_chunk_orders) == 2
    assert seen_chunk_orders[1] == list(reversed(seen_chunk_orders[0]))


def test_assessor_retries_once_on_a_malformed_response() -> None:
    """A single unparseable sample must not publish a whole group as unclear."""
    _setup()
    attempts: list[int] = []

    def _flaky(prompt: str, input_schema: Any, output_schema: Any) -> dict[str, Any]:
        attempts.append(1)
        if len(attempts) == 1:
            return {
                "verdicts": [
                    {
                        "requirement_id": "req_threshold_validation",
                        "status": "banana",
                        "rationale": "kaputt",
                        "evidence": [],
                    }
                ]
            }
        return {
            "verdicts": [
                _violated_verdict("Die QA-Freigabe ist als pending markiert.")
            ]
        }

    report = _engine(
        MockProvider(output_factory=_flaky), _entailment("supports")
    ).run("ds_req_review_demo")

    # Sample 1: malformed then re-asked (2 attempts); sample 2: clean (1).
    assert len(attempts) == 3
    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.published_status == RequirementVerdictStatus.VIOLATED
    assert all(c.status == "succeeded" for c in report.model_calls if c.purpose == "assess")


# --- narrow assessor -------------------------------------------------------


def _narrow_provider(
    *,
    applicability: str = "applies",
    quotes: list[dict[str, str]] | None = None,
    judge: dict[str, Any] | None = None,
    judge_sequence: list[dict[str, Any]] | None = None,
) -> tuple[MockProvider, list[tuple[str, str]]]:
    """Mock that answers EvidenceLocation and NarrowVerdict; records the calls."""
    from app.schemas.requirement_review import EvidenceLocation, NarrowVerdict

    seen: list[tuple[str, str]] = []
    judged: list[int] = []

    def _factory(prompt: str, input_schema: dict[str, Any], output_schema: Any) -> dict:
        if output_schema is EvidenceLocation:
            seen.append(("locate", prompt))
            assert "requirement" in input_schema and "chunks" in input_schema
            return {
                "applicability": applicability,
                "reason": "Belegsuche.",
                "quotes": quotes if quotes is not None else [],
            }
        assert output_schema is NarrowVerdict
        seen.append(("judge", prompt))
        if judge_sequence:
            judged.append(1)
            return judge_sequence[min(len(judged) - 1, len(judge_sequence) - 1)]
        return judge or {"status": "unclear", "severity": "medium", "rationale": "Unklar."}

    return MockProvider(output_factory=_factory), seen


def _narrow_engine(assessor: MockProvider, *, samples: int = 1) -> RequirementReviewEngine:
    return RequirementReviewEngine(
        repository=repository,
        audit_log=audit_log,
        assessor_provider=assessor,
        entailment_provider=_entailment("supports"),
        assessor_samples=samples,
        assessor_mode="narrow",
    )


def test_narrow_assessor_locates_then_judges_and_resolves_quotes_by_index() -> None:
    """The judge points at quotes by index; the engine attaches chunk and page.

    The model never copies a document id or a page number -- the two fields
    the grouped call got wrong most -- and a decided verdict cannot exist
    without a quote because the judge never sees anything else.
    """
    _setup()
    quote = "Ein Validierungsnachweis für den neuen Schwellwert liegt nicht bei."
    provider, seen = _narrow_provider(
        quotes=[{"chunk_id": "chunk_req_change_p1", "quote": quote}],
        judge={
            "status": "violated",
            "severity": "high",
            "rationale": "Der Nachweis fehlt.",
            "supporting_quote_indices": [0, 7],  # 7 is out of range and ignored
        },
    )

    report = _narrow_engine(provider).run("ds_req_review_demo")

    verdict = next(v for v in report.verdicts if v.requirement_id == "req_threshold_validation")
    assert [kind for kind, _ in seen] == ["locate", "judge"]
    assert verdict.model_status == RequirementVerdictStatus.VIOLATED
    assert verdict.published_status == RequirementVerdictStatus.VIOLATED
    assert verdict.provenance_ok is True
    assert [e.quote for e in verdict.evidence] == [quote]
    assert verdict.evidence[0].document_id == "doc_req_change"
    assert verdict.evidence[0].page == 1
    assert [c.purpose for c in report.model_calls if c.status == "succeeded"] == [
        "locate",
        "judge",
        "entailment",
    ]


def test_narrow_assessor_answers_without_quotes_on_the_server() -> None:
    """No located evidence means no judge call: unclear, or not applicable
    when the locator says the requirement does not concern the case."""
    _setup()
    provider, seen = _narrow_provider(applicability="cannot_tell", quotes=[])
    report = _narrow_engine(provider).run("ds_req_review_demo")
    verdict = next(v for v in report.verdicts if v.requirement_id == "req_threshold_validation")
    assert [kind for kind, _ in seen] == ["locate"]
    assert verdict.published_status == RequirementVerdictStatus.UNCLEAR
    assert verdict.server_authored is True

    _setup()
    provider, seen = _narrow_provider(applicability="does_not_apply", quotes=[])
    report = _narrow_engine(provider).run("ds_req_review_demo")
    verdict = next(v for v in report.verdicts if v.requirement_id == "req_threshold_validation")
    assert verdict.published_status == RequirementVerdictStatus.NOT_APPLICABLE
    assert verdict.server_authored is True


def test_narrow_judge_gets_one_second_chance_to_point_at_a_quote() -> None:
    """violated with no indices is re-asked once with the breach named; a
    judge that still points at nothing keeps its answer and is demoted by
    provenance, never lost."""
    from app.services.requirement_review import JUDGE_REASK_NOTE

    _setup()
    quote = "Ein Validierungsnachweis für den neuen Schwellwert liegt nicht bei."
    provider, seen = _narrow_provider(
        quotes=[{"chunk_id": "chunk_req_change_p1", "quote": quote}],
        judge_sequence=[
            {"status": "violated", "severity": "high", "rationale": "Fehlt.", "supporting_quote_indices": []},
            {"status": "violated", "severity": "high", "rationale": "Fehlt.", "supporting_quote_indices": [0]},
        ],
    )
    report = _narrow_engine(provider).run("ds_req_review_demo")
    verdict = next(v for v in report.verdicts if v.requirement_id == "req_threshold_validation")
    judge_prompts = [p for kind, p in seen if kind == "judge"]
    assert len(judge_prompts) == 2
    assert judge_prompts[1].endswith(JUDGE_REASK_NOTE)
    assert verdict.published_status == RequirementVerdictStatus.VIOLATED
    assert verdict.evidence[0].quote == quote

    # Refuses twice: the first answer stands and provenance demotes it.
    _setup()
    provider, seen = _narrow_provider(
        quotes=[{"chunk_id": "chunk_req_change_p1", "quote": quote}],
        judge={"status": "violated", "severity": "high", "rationale": "Fehlt.", "supporting_quote_indices": []},
    )
    report = _narrow_engine(provider).run("ds_req_review_demo")
    verdict = next(v for v in report.verdicts if v.requirement_id == "req_threshold_validation")
    assert verdict.model_status == RequirementVerdictStatus.VIOLATED
    assert verdict.published_status == RequirementVerdictStatus.UNCLEAR
    assert verdict.server_authored is False


def test_narrow_assessor_merges_judge_samples_alarm_side() -> None:
    """Two judge samples over the same quotes merge like grouped samples:
    one violated is enough to make a candidate; the second sees the quotes
    reversed."""
    _setup()
    quotes = [
        {"chunk_id": "chunk_req_change_p1", "quote": "Change Control CC-2026-014 senkt den AVI-Schwellwert."},
        {"chunk_id": "chunk_req_change_p1", "quote": "Ein Validierungsnachweis für den neuen Schwellwert liegt nicht bei."},
    ]
    orders: list[list[str]] = []
    from app.schemas.requirement_review import EvidenceLocation, NarrowVerdict

    def _factory(prompt: str, input_schema: dict[str, Any], output_schema: Any) -> dict:
        if output_schema is EvidenceLocation:
            return {"applicability": "applies", "reason": "ok", "quotes": quotes}
        order = [q["quote"] for q in input_schema["quotes"]]
        orders.append(order)
        if len(orders) == 1:
            return {"status": "fulfilled", "rationale": "Belegt.", "supporting_quote_indices": [0],
                    "evidence_type": "Auszug", "evidence_reference": "p1",
                    "evidence_sufficiency": "sufficient", "independent_support": True}
        # second sample sees the reversed order; index 0 is now the gap quote
        return {"status": "violated", "severity": "high", "rationale": "Nachweis fehlt.", "supporting_quote_indices": [0]}

    report = _narrow_engine(MockProvider(output_factory=_factory), samples=2).run("ds_req_review_demo")
    verdict = next(v for v in report.verdicts if v.requirement_id == "req_threshold_validation")
    assert orders[1] == list(reversed(orders[0]))
    assert verdict.model_status == RequirementVerdictStatus.VIOLATED
    assert verdict.sample_disagreement is True
    assert verdict.evidence[0].quote == quotes[1]["quote"]
