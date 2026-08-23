"""Schemas for the requirement-centric review path.

This is the second review engine, organised the way a QA reviewer actually
thinks: not "which observations did ten agents produce" but "which requirement
is fulfilled, violated or unclear, and where is the evidence". One requirement
yields exactly one verdict, so the repetition problem of the finding-centric
path (redundancy rate 0.85 on both measured corpora) cannot exist here by
construction -- there is no second row for the same obligation.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import Field
from pydantic.json_schema import SkipJsonSchema

from app.schemas.domain import Severity, StrictSchema


class RequirementVerdictStatus(StrEnum):
    FULFILLED = "fulfilled"
    VIOLATED = "violated"
    UNCLEAR = "unclear"
    NOT_APPLICABLE = "not_applicable"


class EntailmentSupport(StrEnum):
    SUPPORTS = "supports"
    PARTIAL = "partial"
    NONE = "none"


class RequirementReviewEvidence(StrictSchema):
    """A cited passage as the assessor model returns it.

    Deliberately leaner than the domain EvidenceItem: no hash and no verifier
    score, because provenance is established server-side against the stored
    chunks rather than trusted from the model.
    """

    document_id: str = Field(min_length=1)
    chunk_id: str = Field(min_length=1)
    page: int = Field(ge=1)
    quote: str = Field(min_length=1)
    #: Filled server-side when the report is assembled. Kept out of the JSON
    #: schema the assessor sees: a reviewer needs "Abweichungsbericht, Seite 3",
    #: the model only knows document ids, and the prompt must not change for it.
    document_name: SkipJsonSchema[str] = ""


class EvidenceSufficiency(StrEnum):
    SUFFICIENT = "sufficient"
    PARTIAL = "partial"
    INSUFFICIENT = "insufficient"


class RequirementVerdict(StrictSchema):
    requirement_id: str = Field(min_length=1)
    status: RequirementVerdictStatus
    severity: Severity | None = None
    rationale: str = Field(min_length=1)
    evidence: list[RequirementReviewEvidence] = Field(default_factory=list)
    #: Required for FULFILLED verdicts: what kind of proof carries the verdict
    #: (e.g. "Audit-Trail-Auszug", "signierte Freigabeerklärung", "Rohdaten"),
    #: where it lives, whether it suffices, and whether anything beyond the
    #: document's own say-so backs it. These make a credulous "fulfilled"
    #: visible instead of silent.
    evidence_type: str | None = None
    evidence_reference: str | None = None
    evidence_sufficiency: EvidenceSufficiency | None = None
    independent_support: bool | None = None


class RequirementGroupOutput(StrictSchema):
    """Structured output contract for one assessor call over a requirement group."""

    verdicts: list[RequirementVerdict]


class LocatedQuote(StrictSchema):
    """One verbatim passage the locator says bears on a requirement."""

    chunk_id: str = Field(min_length=1)
    quote: str = Field(min_length=1)


class RequirementApplicability(StrEnum):
    APPLIES = "applies"
    DOES_NOT_APPLY = "does_not_apply"
    CANNOT_TELL = "cannot_tell"


class EvidenceLocation(StrictSchema):
    """Output of the narrow assessor's first call: where is the evidence?

    Flat on purpose. A 27B model that left the evidence list empty in 154 of
    280 grouped verdicts quoted verbatim four times out of four when asked one
    question with one flat answer. The judgment is a separate call that only
    ever sees these quotes, so a decided verdict cannot exist without one.
    """

    applicability: RequirementApplicability
    reason: str = Field(min_length=1)
    quotes: list[LocatedQuote] = Field(default_factory=list)


class NarrowVerdict(StrictSchema):
    """Output of the narrow assessor's second call: the judgment over quotes.

    ``supporting_quote_indices`` point into the quotes the judge was given;
    the engine resolves them back to chunks, so the model never has to copy
    document ids or page numbers -- the two fields it got wrong most.
    """

    status: RequirementVerdictStatus
    severity: Severity | None = None
    rationale: str = Field(min_length=1)
    supporting_quote_indices: list[int] = Field(default_factory=list)
    evidence_type: str | None = None
    evidence_reference: str | None = None
    evidence_sufficiency: EvidenceSufficiency | None = None
    independent_support: bool | None = None


class FulfilledChallenge(StrictSchema):
    """Structured output of the adversarial second look at a FULFILLED verdict.

    Asked only one question: which required evidence could be missing,
    incomplete or merely asserted despite the positive wording. A sustained
    challenge demotes to UNCLEAR; it never upgrades anything.
    """

    challenge_sustained: bool
    missing_or_asserted_evidence: list[str] = Field(default_factory=list)
    reason: str = Field(min_length=1)


class EntailmentCheck(StrictSchema):
    """Structured output contract for the semantic verification call.

    This replaces the lexical claim-support check of the finding path, which
    classified 98-100% of all findings as unsupported on every measured corpus
    and therefore carried no information.
    """

    support: EntailmentSupport
    reason: str = Field(min_length=1)


class VerifiedRequirementVerdict(StrictSchema):
    requirement_id: str = Field(min_length=1)
    requirement_title: str | None = None
    requirement_text: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    section: str = Field(min_length=1)
    #: What the assessor model said.
    model_status: RequirementVerdictStatus
    #: What the report publishes after provenance and entailment checks. Only
    #: ever equal to or more cautious than model_status; a verdict is never
    #: upgraded by verification.
    published_status: RequirementVerdictStatus
    severity: Severity | None = None
    rationale: str = Field(min_length=1)
    evidence: list[RequirementReviewEvidence] = Field(default_factory=list)
    dropped_evidence_count: int = Field(default=0, ge=0)
    #: One entry per dropped quote, naming why it was dropped. The 2026-07-27
    #: regression run lost five previously-found errors to dropped quotes and
    #: the report could not say what the quotes had been -- diagnosing it took
    #: a run-to-run diff. Never again.
    dropped_evidence_reasons: list[str] = Field(default_factory=list)
    provenance_ok: bool
    entailment: EntailmentSupport | None = None
    entailment_reason: str | None = None
    evidence_type: str | None = None
    evidence_reference: str | None = None
    evidence_sufficiency: EvidenceSufficiency | None = None
    independent_support: bool | None = None
    #: Set when the adversarial second look ran on a FULFILLED verdict.
    challenge_sustained: bool | None = None
    challenge_reason: str | None = None
    #: True when independent assessor samples returned different statuses for
    #: this requirement -- the merged verdict is the most cautious of them.
    sample_disagreement: bool = False
    #: Validator ids whose deterministic findings escalated or corroborated
    #: this verdict. Deterministic evidence of a breach overrides a model
    #: all-clear -- the one path that raises alarm instead of lowering it,
    #: and it is reserved for checks that do arithmetic, not judgement.
    validator_flags: list[str] = Field(default_factory=list)
    validator_statements: list[str] = Field(default_factory=list)
    #: True when the verdict was authored by the server (inapplicable
    #: requirement, failed model group), not by a model.
    server_authored: bool = False
    #: True when a model call behind this row failed (assessment, evidence
    #: search, entailment or challenge) and the row is a placeholder rather
    #: than a judgement. These rows can be re-run on their own -- on a host
    #: that answers 5xx for an afternoon, that is the difference between a
    #: two-minute fix and a 25-minute rerun.
    needs_retry: bool = False


class RequirementReviewModelCall(StrictSchema):
    purpose: str = Field(min_length=1)
    provider: str = Field(min_length=1)
    model_id: str = Field(default="")
    requirement_ids: list[str] = Field(default_factory=list)
    status: str = Field(min_length=1)
    error_type: str | None = None
    error_summary: str | None = None
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)


class RequirementCoverageReport(StrictSchema):
    document_set_id: str = Field(min_length=1)
    engine_version: str = Field(min_length=1)
    created_at: datetime
    verdicts: list[VerifiedRequirementVerdict]
    status_counts: dict[str, int] = Field(default_factory=dict)
    model_calls: list[RequirementReviewModelCall] = Field(default_factory=list)
    failed_model_call_count: int = Field(default=0, ge=0)
    #: Every deterministic finding of the run, including those no requirement
    #: claimed -- an unattached breach is still a breach and must not vanish
    #: because the mapping was missing.
    validator_findings: list[dict] = Field(default_factory=list)
    #: What the extraction layer actually produced -- row counts, rows the
    #: grounding step dropped, and the rows themselves -- so that a validator
    #: that did not fire can be traced to the input it did not get.
    extracted_evidence: dict | None = None

    def summary(self) -> dict[str, Any]:
        return {
            "document_set_id": self.document_set_id,
            "engine_version": self.engine_version,
            "verdict_count": len(self.verdicts),
            **self.status_counts,
            "failed_model_call_count": self.failed_model_call_count,
        }
