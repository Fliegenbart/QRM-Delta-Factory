from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated

from pydantic import Field, StringConstraints, model_validator

from app.schemas.domain import (
    DocumentSetId,
    FindingId,
    RequirementId,
    ReviewDecisionValue,
    ReviewerId,
    ReviewId,
    Severity,
    Sha256Hash,
    StrictSchema,
    TenantId,
)
from app.schemas.evals import EvalReport

CalibrationExampleId = Annotated[str, StringConstraints(pattern=r"^cal_[A-Za-z0-9_-]+$")]
CalibrationGateReportId = Annotated[str, StringConstraints(pattern=r"^calgate_[A-Za-z0-9_-]+$")]


class CalibrationExampleStatus(StrEnum):
    RAW_FEEDBACK = "raw_feedback"
    APPROVED_GOLD = "approved_gold"
    ACTIVE = "active"


class CalibrationExample(StrictSchema):
    calibration_example_id: CalibrationExampleId
    source_review_id: ReviewId
    source_feedback_id: str = Field(min_length=1)
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
    human_decision: ReviewDecisionValue
    feedback_outcome: str = Field(min_length=1)
    reviewer_id: ReviewerId
    reviewer_rationale: str = Field(min_length=1)
    risk_statement: str = Field(min_length=1)
    evidence_quotes: list[str] = Field(default_factory=list)
    high_critical_recall_guard: bool
    status: CalibrationExampleStatus
    created_at: datetime
    approved_by: ReviewerId | None = None
    approved_at: datetime | None = None
    activated_by: ReviewerId | None = None
    activated_at: datetime | None = None
    regression_gate_report_id: CalibrationGateReportId | None = None

    @model_validator(mode="after")
    def active_examples_require_audit_trail(self) -> CalibrationExample:
        if self.status in {
            CalibrationExampleStatus.APPROVED_GOLD,
            CalibrationExampleStatus.ACTIVE,
        } and (self.approved_by is None or self.approved_at is None):
            raise ValueError("approved calibration examples require approved_by and approved_at")
        if self.status == CalibrationExampleStatus.ACTIVE and (
            self.activated_by is None
            or self.activated_at is None
            or self.regression_gate_report_id is None
        ):
            raise ValueError(
                "active calibration examples require activation and regression gate metadata"
            )
        return self


class CalibrationPromptExample(StrictSchema):
    calibration_example_id: CalibrationExampleId
    human_decision: ReviewDecisionValue
    feedback_outcome: str = Field(min_length=1)
    risk_category: str = Field(min_length=1)
    original_severity: Severity
    requirement_references: list[RequirementId] = Field(default_factory=list)
    risk_statement: str = Field(min_length=1)
    reviewer_rationale: str = Field(min_length=1)
    evidence_quotes: list[str] = Field(default_factory=list)


class CalibrationPack(StrictSchema):
    tenant_id: TenantId
    document_set_id: DocumentSetId
    agent_role: str = Field(min_length=1)
    example_ids: list[CalibrationExampleId] = Field(default_factory=list)
    examples: list[CalibrationPromptExample] = Field(default_factory=list)
    prompt_block: str = ""
    pack_hash: Sha256Hash


class CalibrationExampleApprovalRequest(StrictSchema):
    approved_by: ReviewerId
    activate: bool = False
    regression_gate_passed: bool = False
    regression_gate_report_id: CalibrationGateReportId | None = None


class ReviewCalibrationReport(StrictSchema):
    generated_at: datetime
    total_examples: int = Field(ge=0)
    raw_feedback_count: int = Field(ge=0)
    approved_gold_count: int = Field(ge=0)
    active_count: int = Field(ge=0)
    examples: list[CalibrationExample] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class CalibrationRegressionGateReport(StrictSchema):
    regression_gate_report_id: CalibrationGateReportId
    generated_at: datetime
    passed: bool
    eval_dataset_count: int = Field(ge=0)
    failed_dataset_ids: list[str] = Field(default_factory=list)
    eval_reports: list[EvalReport] = Field(default_factory=list)
