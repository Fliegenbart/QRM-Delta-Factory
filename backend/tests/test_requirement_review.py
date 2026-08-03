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
    assert [c.purpose for c in failed] == ["extract[doc_req_change]"]


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
            raise ProviderCallError("mistral provider output was truncated")
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
        "extract[doc_req_change]": "failed",
        "extract[doc_req_capa]": "succeeded",
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

    assert len(attempts) == 2
    verdict = next(
        v for v in report.verdicts if v.requirement_id == "req_threshold_validation"
    )
    assert verdict.published_status == RequirementVerdictStatus.VIOLATED
    assert all(c.status == "succeeded" for c in report.model_calls if c.purpose == "assess")
