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
    assert len(findings) == 1
    assert findings[0].validator_id == "action_item_without_responsible"
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
