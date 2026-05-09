from __future__ import annotations

from pydantic import Field

from app.schemas.domain import (
    DocumentId,
    DocumentSetId,
    FindingId,
    FindingVerificationResult,
    RequirementId,
    ReviewDecisionValue,
    ReviewerId,
    ReviewPackId,
    Severity,
    StrictSchema,
)
from app.schemas.risk import FindingCluster, RiskDecision


class ReviewPackEvidenceQuote(StrictSchema):
    document_id: DocumentId
    chunk_id: str = Field(min_length=1)
    page: int = Field(ge=1)
    quote: str = Field(min_length=1)
    support_type: str = Field(min_length=1)


class ReviewPackTopRisk(StrictSchema):
    finding_id: FindingId
    risk_statement: str = Field(min_length=1)
    severity: Severity
    risk_category: str = Field(min_length=1)
    requirement_references: list[RequirementId] = Field(default_factory=list)
    evidence_quotes: list[ReviewPackEvidenceQuote] = Field(default_factory=list)
    found_by_agents: list[str] = Field(default_factory=list)
    contradicted_by_agents: list[str] = Field(default_factory=list)
    no_issue_agents: list[str] = Field(default_factory=list)
    verifier_status: str = Field(min_length=1)
    human_review_reason: str = Field(min_length=1)


class ReviewPackEvidenceRow(StrictSchema):
    finding_id: FindingId
    risk_statement: str = Field(min_length=1)
    document_id: DocumentId
    page: int = Field(ge=1)
    chunk_id: str = Field(min_length=1)
    quote: str = Field(min_length=1)
    requirement_references: list[RequirementId] = Field(default_factory=list)
    verifier_status: str = Field(min_length=1)


class ModelPosition(StrictSchema):
    finding_id: FindingId
    found_by_agents: list[str] = Field(default_factory=list)
    contradicted_by_agents: list[str] = Field(default_factory=list)
    no_issue_agents: list[str] = Field(default_factory=list)


class ReviewerActionRecommendation(StrictSchema):
    action: ReviewDecisionValue
    rationale: str = Field(min_length=1)
    finding_id: FindingId | None = None


class ReviewPack(StrictSchema):
    review_pack_id: ReviewPackId
    document_set_id: DocumentSetId
    decision: RiskDecision
    summary: str = Field(min_length=1)
    top_risks: list[ReviewPackTopRisk] = Field(default_factory=list)
    finding_clusters: list[FindingCluster] = Field(default_factory=list)
    evidence_table: list[ReviewPackEvidenceRow] = Field(default_factory=list)
    model_positions: list[ModelPosition] = Field(default_factory=list)
    verifier_results: list[FindingVerificationResult] = Field(default_factory=list)
    ood_reasons: list[str] = Field(default_factory=list)
    coverage_gap_reasons: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    recommended_reviewer_actions: list[ReviewerActionRecommendation] = Field(
        default_factory=list
    )
    audit_references: list[str] = Field(default_factory=list)


class ReviewDecisionRequest(StrictSchema):
    reviewer_id: ReviewerId
    decision: ReviewDecisionValue
    rationale: str = Field(min_length=1)
