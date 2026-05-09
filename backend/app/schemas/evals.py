from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Any

from pydantic import Field, StringConstraints

from app.schemas.domain import (
    DocumentId,
    EvidenceSupport,
    RequirementId,
    Severity,
    StrictSchema,
)
from app.schemas.risk import RiskDecision

EvalDatasetId = Annotated[str, StringConstraints(pattern=r"^evalds_[A-Za-z0-9_-]+$")]
GoldFindingId = Annotated[str, StringConstraints(pattern=r"^gold_[A-Za-z0-9_-]+$")]
ConfigVersionId = Annotated[str, StringConstraints(pattern=r"^cfg_[A-Za-z0-9_-]+$")]
RegressionRunId = Annotated[str, StringConstraints(pattern=r"^regrun_[A-Za-z0-9_-]+$")]


class RegressionGateCriterionType(StrEnum):
    MISSED_CRITICAL_MUST_DETECT = "MISSED_CRITICAL_MUST_DETECT"
    AUTO_CLEAR_HIGH_CRITICAL_GOLD = "AUTO_CLEAR_HIGH_CRITICAL_GOLD"
    CITATION_PRECISION_BELOW_THRESHOLD = "CITATION_PRECISION_BELOW_THRESHOLD"
    REQUIREMENT_MATCH_ACCURACY_BELOW_THRESHOLD = (
        "REQUIREMENT_MATCH_ACCURACY_BELOW_THRESHOLD"
    )
    HUMAN_REVIEW_RATE_INCREASE_WITHOUT_RECALL_GAIN = (
        "HUMAN_REVIEW_RATE_INCREASE_WITHOUT_RECALL_GAIN"
    )


class ExpectedEvidenceRef(StrictSchema):
    document_id: DocumentId
    chunk_id: str = Field(min_length=1)
    page: int = Field(ge=1)
    quote: str = Field(min_length=1)


class GoldFinding(StrictSchema):
    gold_finding_id: GoldFindingId
    expected_risk_category: str = Field(min_length=1)
    expected_severity: Severity
    expected_requirement_ids: list[RequirementId] = Field(default_factory=list)
    expected_evidence_refs: list[ExpectedEvidenceRef] = Field(default_factory=list)
    must_detect: bool


class EvalDataset(StrictSchema):
    dataset_id: EvalDatasetId
    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    document_type: str = Field(min_length=1)
    process_area: str = Field(min_length=1)
    gold_findings: list[GoldFinding] = Field(default_factory=list)
    seeded_defects: list[str] = Field(default_factory=list)


class EvalMetrics(StrictSchema):
    recall_by_severity: dict[str, float] = Field(default_factory=dict)
    false_omission_rate: float = Field(ge=0, le=1)
    false_positive_rate: float = Field(ge=0, le=1)
    citation_precision: float = Field(ge=0, le=1)
    requirement_match_accuracy: float = Field(ge=0, le=1)
    auto_clear_false_negative_count: int = Field(ge=0)
    human_review_rate: float = Field(ge=0, le=1)


class EvalFixture(StrictSchema):
    dataset: EvalDataset
    system_findings: list[dict[str, object]] = Field(default_factory=list)
    risk_decision: RiskDecision


class EvalReport(StrictSchema):
    dataset: EvalDataset
    metrics: EvalMetrics
    passed: bool
    failures: list[str] = Field(default_factory=list)
    matched_gold_finding_ids: list[GoldFindingId] = Field(default_factory=list)
    unmatched_gold_finding_ids: list[GoldFindingId] = Field(default_factory=list)
    false_positive_finding_ids: list[str] = Field(default_factory=list)
    markdown_report: str
    generated_at: datetime
    runner_version: str


class EvalRunRequest(StrictSchema):
    dataset_id: EvalDatasetId
    provider_mode: str = Field(default="mock", min_length=1)


class EvalFindingMatch(StrictSchema):
    gold_finding_id: GoldFindingId
    finding_id: str = Field(min_length=1)
    evidence_support: EvidenceSupport | None = None


class ConfigVersion(StrictSchema):
    config_version_id: ConfigVersionId
    model_provider: str = Field(min_length=1)
    model_name: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    prompt_versions: dict[str, str] = Field(min_length=1)
    requirement_set_id: str = Field(min_length=1)
    requirement_set_version: str = Field(min_length=1)
    risk_fusion_policy_version: str = Field(min_length=1)
    orchestration_version: str = Field(min_length=1)
    created_at: datetime


class RegressionRun(StrictSchema):
    regression_run_id: RegressionRunId
    config_version: ConfigVersion
    eval_reports: list[EvalReport] = Field(min_length=1)
    generated_at: datetime
    runner_version: str = Field(min_length=1)


class RegressionBlockingCriterion(StrictSchema):
    criterion: RegressionGateCriterionType
    dataset_id: EvalDatasetId | None = None
    reason: str = Field(min_length=1)
    baseline_value: float | str | None = None
    candidate_value: float | str | None = None
    threshold: float | str | None = None


class RegressionGateReport(StrictSchema):
    baseline_run_id: RegressionRunId
    candidate_run_id: RegressionRunId
    baseline_config_version_id: ConfigVersionId
    candidate_config_version_id: ConfigVersionId
    passed: bool
    blocking_criteria: list[RegressionBlockingCriterion] = Field(default_factory=list)
    baseline_summary: dict[str, float] = Field(default_factory=dict)
    candidate_summary: dict[str, float] = Field(default_factory=dict)
    markdown_report: str = Field(min_length=1)
    json_report: dict[str, Any] = Field(default_factory=dict)
    generated_at: datetime
    gate_policy_version: str = Field(min_length=1)
