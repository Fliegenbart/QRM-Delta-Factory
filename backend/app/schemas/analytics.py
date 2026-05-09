from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field

from app.schemas.domain import FindingId, RequirementId, Severity, StrictSchema


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
