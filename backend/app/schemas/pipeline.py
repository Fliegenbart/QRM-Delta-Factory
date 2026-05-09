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


class PipelineRun(StrictSchema):
    pipeline_run_id: PipelineRunId
    document_set_id: DocumentSetId
    status: PipelineRunStatus
    started_at: datetime
    completed_at: datetime | None = None
    failed_step: str | None = Field(default=None)
    error_summary: str | None = Field(default=None)
    config_version: str = Field(min_length=1)
