from __future__ import annotations

from app.schemas.domain import DocumentSet, StrictSchema
from app.schemas.pipeline import PipelineRun
from app.schemas.review_pack import ReviewPack


class DemoSeedResponse(StrictSchema):
    created: bool
    document_set: DocumentSet
    pipeline_run: PipelineRun
    review_pack: ReviewPack
