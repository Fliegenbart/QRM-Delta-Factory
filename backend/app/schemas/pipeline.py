from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field

from app.schemas.domain import DocumentSetId, PipelineRunId, StrictSchema


class PipelineRunStatus(StrEnum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_HUMAN_REVIEW = "needs_human_review"


class PipelineModelManifestItem(StrictSchema):
    agent_id: str
    agent_role: str
    provider: str
    model_name: str
    model_version: str
    configured_model_id: str
    prompt_version: str
    requirement_ids: list[str] = Field(default_factory=list)
    requirement_package_hash: str | None = None
    knowledge_pack_ids: list[str] = Field(default_factory=list)
    missing_knowledge_pack_ids: list[str] = Field(default_factory=list)
    case_signals: list[str] = Field(default_factory=list)
    calibration_example_ids: list[str] = Field(default_factory=list)
    calibration_pack_hash: str | None = None
    status: str
    model_run_id: str | None = None


class PipelineRun(StrictSchema):
    pipeline_run_id: PipelineRunId
    document_set_id: DocumentSetId
    status: PipelineRunStatus
    started_at: datetime
    completed_at: datetime | None = None
    failed_step: str | None = Field(default=None)
    error_summary: str | None = Field(default=None)
    config_version: str = Field(min_length=1)
    model_manifest: list[PipelineModelManifestItem] = Field(default_factory=list)
