"""Structured evidence: the typed layer between prose and deterministic checks.

Mismatched initials or contradictory timestamps only become deterministically
checkable after something has decided which values and events belong together
-- that association is semantic work and stays with a model. This schema is
the contract for that hand-off: one extraction pass reads the chunks into
typed rows with verbatim quotes, the server verifies every quote against the
stored chunks, and the validators then do arithmetic and set comparisons on
rows whose provenance is already established. The model associates; it never
judges. The validators judge; they never interpret prose.
"""

from __future__ import annotations

from pydantic import Field

from app.schemas.domain import StrictSchema


class EvidenceLocation(StrictSchema):
    document_id: str = Field(min_length=1)
    chunk_id: str = Field(min_length=1)
    page: int = Field(ge=1)
    quote: str = Field(min_length=1)


class ExtractedSignature(StrictSchema):
    """One signature or approval field, present or conspicuously empty."""

    field_label: str = Field(min_length=1)
    role: str | None = None
    signer: str | None = None
    date: str | None = None
    #: True when the field exists but carries no signer -- an empty mandatory
    #: field is a first-class observation, not an absence of data.
    is_empty: bool = False
    requirement_ids: list[str] = Field(default_factory=list)
    location: EvidenceLocation


class ExtractedMeasurement(StrictSchema):
    parameter: str = Field(min_length=1)
    value: str = Field(min_length=1)
    unit: str | None = None
    requirement_ids: list[str] = Field(default_factory=list)
    location: EvidenceLocation


class ExtractedSpecification(StrictSchema):
    """A declared limit: NMT/NLT/range, with the same parameter naming the
    extraction used for measurements, so the join is a string match."""

    parameter: str = Field(min_length=1)
    operator: str = Field(min_length=1)
    limit_low: str | None = None
    limit_high: str | None = None
    unit: str | None = None
    requirement_ids: list[str] = Field(default_factory=list)
    location: EvidenceLocation


class ExtractedActionItem(StrictSchema):
    """One row of an action list (CAPA measures, tasks), checked per item."""

    list_label: str = Field(min_length=1)
    item_label: str = Field(min_length=1)
    responsible: str | None = None
    due_date: str | None = None
    requirement_ids: list[str] = Field(default_factory=list)
    location: EvidenceLocation


#: What kind of step an event is in the life of a GMP record. The ordering
#: validator reasons over these, never over prose: a release dated before the
#: assessment it rests on, a review dated before the event it reviews.
EVENT_ROLES = (
    "event",  # the deviation, OOS, change or incident itself
    "investigation",
    "assessment",
    "review",
    "approval",
    "release",
    "training",
    "implementation",
    "effectiveness_check",
    "first_use",
    "other",
)


class ExtractedEvent(StrictSchema):
    description: str = Field(min_length=1)
    timestamp: str | None = None
    actor: str | None = None
    #: One of EVENT_ROLES, as classified by the extractor; None when unknown.
    role: str | None = None
    #: The record this step belongs to -- batch, deviation, change or sample
    #: identifier -- so steps of different records are never ordered against
    #: each other.
    refers_to: str | None = None
    #: Extraction groups rows that describe the same real-world activity under
    #: one key; the consistency validator only ever compares within a group.
    activity_key: str | None = None
    requirement_ids: list[str] = Field(default_factory=list)
    location: EvidenceLocation


class StructuredEvidence(StrictSchema):
    signatures: list[ExtractedSignature] = Field(default_factory=list)
    measurements: list[ExtractedMeasurement] = Field(default_factory=list)
    specifications: list[ExtractedSpecification] = Field(default_factory=list)
    action_items: list[ExtractedActionItem] = Field(default_factory=list)
    events: list[ExtractedEvent] = Field(default_factory=list)


class ValidatorFinding(StrictSchema):
    """A deterministic verdict contribution, traceable to its rule and rows."""

    validator_id: str = Field(min_length=1)
    requirement_ids: list[str] = Field(default_factory=list)
    severity: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    locations: list[EvidenceLocation] = Field(default_factory=list)
