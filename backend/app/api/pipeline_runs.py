from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status

from app.audit.events import audit_log
from app.core.security import require_document_set_for_tenant
from app.db.in_memory import repository
from app.schemas.pipeline import PipelineRun
from app.services.pipeline import (
    PipelineDocumentSetNotFoundError,
    PipelineRunNotFoundError,
    PipelineRunRetryRequiredError,
    PipelineService,
)

document_set_router = APIRouter(prefix="/document-sets", tags=["pipeline-runs"])
pipeline_run_router = APIRouter(prefix="/pipeline-runs", tags=["pipeline-runs"])


def get_pipeline_service() -> PipelineService:
    return PipelineService(repository=repository, audit_log=audit_log)


@document_set_router.post(
    "/{document_set_id}/pipeline-runs",
    response_model=PipelineRun,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_pipeline_run(
    document_set_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
) -> PipelineRun:
    require_document_set_for_tenant(
        repository=repository,
        document_set_id=document_set_id,
        request=request,
    )
    try:
        service = get_pipeline_service()
        pipeline_run, created = service.enqueue_pipeline_run(document_set_id)
        if created:
            background_tasks.add_task(
                service.execute_pipeline,
                document_set_id,
                pipeline_run,
            )
        return pipeline_run
    except PipelineDocumentSetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PipelineRunRetryRequiredError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@document_set_router.post(
    "/{document_set_id}/pipeline-runs/retry",
    response_model=PipelineRun,
    status_code=status.HTTP_202_ACCEPTED,
)
def retry_pipeline_run(
    document_set_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
) -> PipelineRun:
    require_document_set_for_tenant(
        repository=repository,
        document_set_id=document_set_id,
        request=request,
    )
    try:
        service = get_pipeline_service()
        pipeline_run, created = service.enqueue_pipeline_run(document_set_id, retry=True)
        if created:
            background_tasks.add_task(
                service.execute_pipeline,
                document_set_id,
                pipeline_run,
            )
        return pipeline_run
    except PipelineDocumentSetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@pipeline_run_router.get("/{pipeline_run_id}", response_model=PipelineRun)
def get_pipeline_run(pipeline_run_id: str, request: Request) -> PipelineRun:
    try:
        pipeline_run = get_pipeline_service().get_pipeline_run(pipeline_run_id)
    except PipelineRunNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    require_document_set_for_tenant(
        repository=repository,
        document_set_id=pipeline_run.document_set_id,
        request=request,
    )
    return pipeline_run
