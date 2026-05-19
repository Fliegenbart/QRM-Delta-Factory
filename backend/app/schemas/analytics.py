from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field

from app.schemas.domain import (
    DocumentSetId,
    FindingId,
    RequirementId,
    ReviewDecisionValue,
    ReviewerId,
    ReviewId,
    Severity,
    StrictSchema,
    TenantId,
)


class FalsePositiveRecommendationType(StrEnum):
    PROMPT_CLARIFICATION_CANDIDATE = "PROMPT_CLARIFICATION_CANDIDATE"
    REQUIREMENT_RULE_CLARIFICATION_CANDIDATE = "REQUIREMENT_RULE_CLARIFICATION_CANDIDATE"
    DETERMINISTIC_VERIFIER_RULE_CANDIDATE = "DETERMINISTIC_VERIFIER_RULE_CANDIDATE"
    DO_NOT_AUTO_ESCALATE_PATTERN_CANDIDATE = "DO_NOT_AUTO_ESCALATE_PATTERN_CANDIDATE"


class FalsePositiveClusterGroup(StrictSchema):
    requirement_id: RequirementId | str
    risk_category: str = Field(min_length=1)
    agent_role: str = Field(min_length=1)
    prompt_version: str = Field(min_length=1)
    evidence_support: str = Field(min_length=1)
    document_type: str = Field(min_length=1)


class FalsePositiveRecommendation(StrictSchema):
    recommendation_type: FalsePositiveRecommendationType
    rationale: str = Field(min_length=1)
    required_follow_up: list[str] = Field(min_length=1)


class FalsePositiveCluster(StrictSchema):
    cluster_id: str = Field(min_length=1)
    group: FalsePositiveClusterGroup
    finding_ids: list[FindingId] = Field(min_length=1)
    override_decision_count: int = Field(ge=1)
    reject_false_positive_count: int = Field(ge=0)
    downgrade_count: int = Field(ge=0)
    max_severity: Severity
    high_critical_recall_guard: bool
    auto_rule_change_allowed: bool
    recommendations: list[FalsePositiveRecommendation] = Field(default_factory=list)


class FalsePositiveAnalyticsReport(StrictSchema):
    generated_at: datetime
    total_override_decisions: int = Field(ge=0)
    cluster_count: int = Field(ge=0)
    clusters: list[FalsePositiveCluster] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class HumanFeedbackRecord(StrictSchema):
    feedback_id: str = Field(min_length=1)
    review_id: ReviewId
    document_set_id: DocumentSetId
    finding_id: FindingId
    tenant_id: TenantId
    document_type: str = Field(min_length=1)
    process_area: str = Field(min_length=1)
    agent_role: str = Field(min_length=1)
    model_provider: str = Field(min_length=1)
    model_name: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    prompt_version: str = Field(min_length=1)
    requirement_references: list[RequirementId] = Field(default_factory=list)
    risk_category: str = Field(min_length=1)
    original_severity: Severity
    original_evidence_support: str = Field(min_length=1)
    verifier_evidence_support: str | None = None
    human_decision: ReviewDecisionValue
    feedback_outcome: str = Field(min_length=1)
    reviewer_id: ReviewerId
    rationale: str = Field(min_length=1)
    created_at: datetime
    high_critical_recall_guard: bool


class HumanFeedbackModelCard(StrictSchema):
    model_provider: str = Field(min_length=1)
    model_name: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    prompt_version: str = Field(min_length=1)
    agent_role: str = Field(min_length=1)
    total_human_decisions: int = Field(ge=0)
    confirmed_count: int = Field(ge=0)
    downgrade_count: int = Field(ge=0)
    false_positive_count: int = Field(ge=0)
    severity_issue_count: int = Field(ge=0)
    evidence_issue_count: int = Field(ge=0)
    requirement_issue_count: int = Field(ge=0)
    missed_finding_count: int = Field(ge=0)
    more_information_count: int = Field(ge=0)
    escalation_count: int = Field(ge=0)
    confirmation_rate: float = Field(ge=0, le=1)
    downgrade_rate: float = Field(ge=0, le=1)
    false_positive_rate: float = Field(ge=0, le=1)


class HumanFeedbackRegistryReport(StrictSchema):
    generated_at: datetime
    total_feedback_records: int = Field(ge=0)
    model_card_count: int = Field(ge=0)
    records: list[HumanFeedbackRecord] = Field(default_factory=list)
    model_cards: list[HumanFeedbackModelCard] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
