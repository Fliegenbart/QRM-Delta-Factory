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
    #: True when the verdict was authored by the server (inapplicable
    #: requirement, failed model group), not by a model.
    server_authored: bool = False


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

    def summary(self) -> dict[str, Any]:
        return {
            "document_set_id": self.document_set_id,
            "engine_version": self.engine_version,
            "verdict_count": len(self.verdicts),
            **self.status_counts,
            "failed_model_call_count": self.failed_model_call_count,
        }
