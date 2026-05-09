from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field

from app.schemas.domain import DocumentSetId, FindingId, RequirementId, Severity, StrictSchema


class RiskDecisionClass(StrEnum):
    HUMAN_REVIEW_REQUIRED = "human_review_required"
    AUTO_CLEAR_CANDIDATE = "auto_clear_candidate"
    INSUFFICIENT_DOCUMENT_QUALITY = "insufficient_document_quality"
    OUT_OF_SCOPE = "out_of_scope"
    BLOCKED_DUE_TO_MODEL_FAILURE = "blocked_due_to_model_failure"
    BLOCKED_DUE_TO_UNVERIFIED_HIGH_RISK = "blocked_due_to_unverified_high_risk"
    NEEDS_MORE_INFORMATION = "needs_more_information"


class FindingCluster(StrictSchema):
    cluster_id: str = Field(min_length=1)
    risk_category: str = Field(min_length=1)
    requirement_references: list[RequirementId] = Field(default_factory=list)
    finding_ids: list[FindingId] = Field(min_length=1)
    max_severity: Severity
    evidence_overlap_score: float = Field(ge=0, le=1)
    similarity_basis: list[str] = Field(default_factory=list)


class RiskDecision(StrictSchema):
    document_set_id: DocumentSetId
    decision: RiskDecisionClass
    max_severity: Severity
    credible_high_or_critical_exists: bool
    model_disagreement_score: float = Field(ge=0, le=1)
    document_quality_score: float = Field(ge=0, le=1)
    ood_score: float = Field(ge=0, le=1)
    coverage_score: float = Field(default=1.0, ge=0, le=1)
    ood_reasons: list[str] = Field(default_factory=list)
    coverage_gap_reasons: list[str] = Field(default_factory=list)
    auto_clear_allowed: bool
    auto_clear_blockers: list[str] = Field(default_factory=list)
    required_human_review_reasons: list[str] = Field(default_factory=list)
    finding_clusters: list[FindingCluster] = Field(default_factory=list)
    generated_at: datetime
    policy_version: str = Field(min_length=1)
