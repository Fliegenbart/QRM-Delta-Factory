from __future__ import annotations

from typing import Any

from app.schemas.structured_evidence import (
    EvidenceLocation,
    ExtractedActionItem,
    ExtractedEvent,
    ExtractedMeasurement,
    ExtractedSignature,
    ExtractedSpecification,
    StructuredEvidence,
)
from app.services.deterministic_validators import run_validators


def _location(**overrides: Any) -> EvidenceLocation:
    values: dict[str, Any] = {
        "document_id": "doc_val_demo",
        "chunk_id": "chunk_val_demo_p1",
        "page": 1,
        "quote": "Beleg aus dem Dokument.",
    }
    values.update(overrides)
    return EvidenceLocation(**values)


def test_empty_signature_field_is_flagged() -> None:
    findings = run_validators(
        StructuredEvidence(
            signatures=[
                ExtractedSignature(
                    field_label="Abteilungsleitung Produktion",
                    role="Produktionsleitung",
                    is_empty=True,
                    requirement_ids=["req_qa_approval_documented"],
                    location=_location(quote="Abteilungsleitung Produktion: ____"),
                ),
                ExtractedSignature(
                    field_label="QA-Freigabe",
                    role="QA",
                    signer="Dr. M. Feld",
                    date="2026-05-02",
                    is_empty=False,
                    location=_location(),
                ),
            ]
        )
    )
    assert [f.validator_id for f in findings] == ["empty_required_field"]
    assert findings[0].requirement_ids == ["req_qa_approval_documented"]
    assert "Abteilungsleitung Produktion" in findings[0].statement


def test_action_item_without_responsible_is_flagged_per_item() -> None:
    """One of several items missing its owner is the shape a prose read missed."""
    items = [
        ExtractedActionItem(
            list_label="CAPA-Plan CAPA-9911",
            item_label=f"Maßnahme {index}",
            responsible=None if index == 3 else f"Person {index}",
            location=_location(),
        )
        for index in (1, 2, 3, 4)
    ]
    findings = run_validators(StructuredEvidence(action_items=items))
    # A CAPA plan with no effectiveness check also trips the CAPA rule; this
    # test is about the responsible field, so look at that rule alone.
    findings = [f for f in findings if f.validator_id == "action_item_without_responsible"]
    assert len(findings) == 1
    assert "Maßnahme 3" in findings[0].statement


def test_measurement_over_nmt_limit_is_flagged_across_notations() -> None:
    """Comma decimals and split documents must not defeat the comparison."""
    findings = run_validators(
        StructuredEvidence(
            measurements=[
                ExtractedMeasurement(
                    parameter="Restfeuchte",
                    value="2,7",
                    unit="%",
                    requirement_ids=["req_spec_acceptance_limits"],
                    location=_location(document_id="doc_batch_record"),
                )
            ],
            specifications=[
                ExtractedSpecification(
                    parameter="Restfeuchte",
                    operator="NMT",
                    limit_high="2.5",
                    unit="Prozent",
                    location=_location(document_id="doc_specification"),
                )
            ],
        )
    )
    assert [f.validator_id for f in findings] == ["measurement_outside_specification"]
    assert "2,7" in findings[0].statement
    assert len(findings[0].locations) == 2


def test_measurement_within_range_is_not_flagged() -> None:
    findings = run_validators(
        StructuredEvidence(
            measurements=[
                ExtractedMeasurement(
                    parameter="Temperatur", value="41.3", unit="°C", location=_location()
                )
            ],
            specifications=[
                ExtractedSpecification(
                    parameter="Temperatur",
                    operator="Bereich",
                    limit_low="40",
                    limit_high="45",
                    unit="°C",
                    location=_location(),
                )
            ],
        )
    )
    assert findings == []


def test_incompatible_units_are_never_compared() -> None:
    """A validator that guesses across units is worse than no validator."""
    findings = run_validators(
        StructuredEvidence(
            measurements=[
                ExtractedMeasurement(
                    parameter="Konzentration", value="30", unit="mg/ml", location=_location()
                )
            ],
            specifications=[
                ExtractedSpecification(
                    parameter="Konzentration",
                    operator="NMT",
                    limit_high="5",
                    unit="%",
                    location=_location(),
                )
            ],
        )
    )
    assert findings == []


def test_same_activity_signed_by_two_hands_is_flagged() -> None:
    findings = run_validators(
        StructuredEvidence(
            events=[
                ExtractedEvent(
                    description="Line Clearance geprüft",
                    actor="QC-KM",
                    activity_key="line_clearance_b445",
                    location=_location(quote="geprüft: QC-KM"),
                ),
                ExtractedEvent(
                    description="Line Clearance geprüft",
                    actor="QC-LT",
                    activity_key="line_clearance_b445",
                    location=_location(quote="Prüfung durch QC-LT"),
                ),
            ]
        )
    )
    assert [f.validator_id for f in findings] == [
        "conflicting_actors_for_one_activity"
    ]
    assert "QC-KM" in findings[0].statement and "QC-LT" in findings[0].statement


def test_events_with_distinct_activity_keys_are_never_compared() -> None:
    """Two authorised people doing two different things is not a conflict."""
    findings = run_validators(
        StructuredEvidence(
            events=[
                ExtractedEvent(
                    description="Wiegung",
                    actor="MP",
                    activity_key="weighing_1",
                    location=_location(),
                ),
                ExtractedEvent(
                    description="Sichtprüfung",
                    actor="TK",
                    activity_key="visual_1",
                    location=_location(),
                ),
            ]
        )
    )
    assert findings == []


def test_conflicting_timestamps_for_one_activity_are_flagged() -> None:
    findings = run_validators(
        StructuredEvidence(
            events=[
                ExtractedEvent(
                    description="QA-Review",
                    timestamp="2026-05-02 10:30",
                    activity_key="qa_review_dev_812",
                    location=_location(),
                ),
                ExtractedEvent(
                    description="QA-Review",
                    timestamp="2026-05-01 09:00",
                    activity_key="qa_review_dev_812",
                    location=_location(quote="Review abgeschlossen am 01.05."),
                ),
            ]
        )
    )
    assert [f.validator_id for f in findings] == [
        "conflicting_timestamps_for_one_activity"
    ]


def test_statements_use_correct_umlauts() -> None:
    findings = run_validators(
        StructuredEvidence(
            action_items=[
                ExtractedActionItem(
                    list_label="CAPA", item_label="Maßnahme 1", location=_location()
                )
            ]
        )
    )
    text = " ".join(f.statement for f in findings)
    for substitute in ("Massnahme", "fuer", "pruef"):
        assert substitute not in text


def _loc(quote: str = "x") -> "EvidenceLocation":
    from app.schemas.structured_evidence import EvidenceLocation

    return EvidenceLocation(document_id="doc", chunk_id="c1", page=1, quote=quote)


def _event(description: str, timestamp: str, role: str, refers_to: str | None = "DEV-1", actor: str | None = None):
    from app.schemas.structured_evidence import ExtractedEvent

    return ExtractedEvent(
        description=description, timestamp=timestamp, role=role, refers_to=refers_to,
        actor=actor, activity_key=f"{role}_{description}", location=_loc(description),
    )


def test_ordering_validator_flags_steps_dated_before_their_event_and_release_before_assessment() -> None:
    """Two of the five persistent blind-corpus misses: a review dated before
    the event it reviews, a release referencing an assessment finished later.
    Steps are only compared within the same record."""
    from app.schemas.structured_evidence import StructuredEvidence
    from app.services.deterministic_validators import run_validators

    evidence = StructuredEvidence(
        events=[
            _event("Abweichung festgestellt", "12.05.2026", "event"),
            _event("QA-Review", "10.05.2026", "review"),                 # before the event
            _event("Chargenfreigabe", "14.05.2026", "release"),
            _event("Risikobewertung abgeschlossen", "16. Mai 2026", "assessment"),  # after release
            # a different record: ordered, must not cross-fire
            _event("Abweichung festgestellt", "01.06.2026", "event", refers_to="DEV-2"),
            _event("QA-Review", "03.06.2026", "review", refers_to="DEV-2"),
            # no record: skipped
            _event("Review ohne Bezug", "01.01.2020", "review", refers_to=None),
        ]
    )

    ids = [f.validator_id for f in run_validators(evidence)]

    assert ids.count("step_predates_its_event") == 1
    assert ids.count("release_before_assessment") == 1
    found = {f.validator_id: f for f in run_validators(evidence)}
    assert "req_di_signature_plausibility" in found["step_predates_its_event"].requirement_ids
    assert "req_batch_no_release_before_assessment" in found["release_before_assessment"].requirement_ids
    assert found["release_before_assessment"].severity == "critical"
    assert len(found["release_before_assessment"].locations) == 2


def test_ordering_validator_is_quiet_on_a_well_ordered_record() -> None:
    from app.schemas.structured_evidence import StructuredEvidence
    from app.services.deterministic_validators import run_validators

    evidence = StructuredEvidence(
        events=[
            _event("Abweichung", "2026-05-12", "event"),
            _event("Untersuchung", "2026-05-13", "investigation"),
            _event("Bewertung", "2026-05-14", "assessment"),
            _event("Freigabe", "2026-05-15", "release"),
            _event("Umsetzung", "2026-05-20", "implementation"),
            _event("Wirksamkeitsprüfung", "2026-06-20", "effectiveness_check"),
            _event("Unparseable", "demnächst", "review"),
        ]
    )
    assert run_validators(evidence) == []


def test_four_eyes_validator_names_a_self_approval() -> None:
    from app.schemas.structured_evidence import ExtractedSignature, StructuredEvidence
    from app.services.deterministic_validators import run_validators

    evidence = StructuredEvidence(
        signatures=[
            ExtractedSignature(field_label="Erstellt von", signer="M. Weber", location=_loc("Erstellt")),
            ExtractedSignature(field_label="Geprüft von (QA)", signer="m. weber", location=_loc("Geprüft")),
            ExtractedSignature(field_label="Freigegeben von", signer="K. Ott", location=_loc("Frei")),
        ]
    )
    findings = run_validators(evidence)
    assert [f.validator_id for f in findings] == ["same_person_performs_and_approves"]
    assert "M. Weber" in findings[0].statement
    assert "req_di_signature_plausibility" in findings[0].requirement_ids

    clean = StructuredEvidence(
        signatures=[
            ExtractedSignature(field_label="Erstellt von", signer="M. Weber", location=_loc()),
            ExtractedSignature(field_label="Geprüft von", signer="K. Ott", location=_loc()),
        ]
    )
    assert run_validators(clean) == []


def test_capa_without_any_effectiveness_check_is_a_finding_only_for_capa_records() -> None:
    """The one miss every stack shared on the goldstandard corpus."""
    from app.schemas.structured_evidence import ExtractedActionItem, StructuredEvidence
    from app.services.deterministic_validators import ValidationContext, run_validators

    measures = StructuredEvidence(
        action_items=[
            ExtractedActionItem(list_label="Maßnahmen", item_label="SOP-123 überarbeiten", responsible="QA", location=_loc("SOP")),
            ExtractedActionItem(list_label="Maßnahmen", item_label="Schulung", responsible="QA", location=_loc("Schulung")),
        ]
    )
    capa = ValidationContext(declared_document_type="capa_package", chunk_texts=("Maßnahmen: SOP-123 überarbeiten; Schulung.",))

    findings = run_validators(measures, capa)
    assert [f.validator_id for f in findings] == ["capa_effectiveness_check_missing"]
    assert "req_capa_effectiveness" in findings[0].requirement_ids
    assert findings[0].locations  # the action list is the trigger

    # Mentioned anywhere in the record: no finding. Not a CAPA: no finding.
    mentioned = ValidationContext(declared_document_type="capa_package", chunk_texts=("Wirksamkeitsprüfung nach 30 Tagen geplant.",))
    assert run_validators(measures, mentioned) == []
    # A deviation package carrying CAPA measures triggers it too; a task list
    # that is not a corrective measure does not.
    deviation = ValidationContext(declared_document_type="deviation_package", chunk_texts=("Maßnahmen.",))
    assert [f.validator_id for f in run_validators(measures, deviation)] == ["capa_effectiveness_check_missing"]
    tasks = StructuredEvidence(
        action_items=[ExtractedActionItem(list_label="Aufgaben", item_label="Kopie an QC senden", responsible="QA", location=_loc())]
    )
    assert run_validators(tasks, deviation) == []
    typed = measures.model_copy(update={"events": [_event("Effectiveness check", "01.07.2026", "effectiveness_check", refers_to="CAPA-1")]})
    assert run_validators(typed, capa) == []
