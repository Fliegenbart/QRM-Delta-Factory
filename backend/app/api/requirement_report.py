"""Read access to the requirement coverage report.

Deliberately its own endpoint rather than a variant of the review pack: the
pack is built around a RiskDecision and its rows are findings, while this
report is built around obligations and its rows are requirements. Forcing one
schema to carry both would blur exactly the distinction that makes the
coverage report worth having.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict

from app.audit.events import audit_log
from app.core.security import require_document_set_for_tenant
from app.db.in_memory import repository
from app.schemas.requirement_review import RequirementCoverageReport
from app.services import progress

router = APIRouter(prefix="/document-sets", tags=["requirement-report"])
logger = logging.getLogger("qrm.requirement_report")


class RequirementReportRetry(BaseModel):
    """What a retry of the failed rows is doing right now."""

    model_config = ConfigDict(extra="forbid")

    #: Rows a failed model call left as placeholders in the stored report.
    retryable: int
    #: True while a retry is running in this process.
    active: bool
    detail: str | None = None


def _retry_key(document_set_id: str) -> str:
    # Separate from the pipeline's progress slot: a retry must never be read
    # as a running pipeline, and the two cannot run at the same time anyway.
    return f"retry:{document_set_id}"


def _retry_status(document_set_id: str) -> RequirementReportRetry:
    report = repository.get_requirement_report(document_set_id)
    retryable = sum(1 for v in report.verdicts if v.needs_retry) if report else 0
    detail = progress.detail_for(_retry_key(document_set_id))
    return RequirementReportRetry(
        retryable=retryable, active=detail is not None, detail=detail
    )


def _pipeline_is_running(document_set_id: str) -> bool:
    from app.api.pipeline_runs import get_pipeline_service
    from app.schemas.pipeline import PipelineRunStatus
    from app.services.pipeline import PipelineRunNotFoundError

    try:
        latest = get_pipeline_service().get_latest_pipeline_run(document_set_id)
    except PipelineRunNotFoundError:
        return False
    return latest.status == PipelineRunStatus.RUNNING


def _run_retry(document_set_id: str) -> None:
    from app.services.requirement_review import default_requirement_review_engine

    key = _retry_key(document_set_id)
    try:
        engine = default_requirement_review_engine(
            repository=repository, audit_log=audit_log
        )
        engine.rerun_failed(
            document_set_id, progress=lambda detail: progress.report(key, detail)
        )
    except Exception:  # noqa: BLE001 - a failed retry leaves the old report standing
        logger.exception("requirement report retry failed for %s", document_set_id)
    finally:
        progress.clear(key)


@router.get(
    "/{document_set_id}/requirement-report",
    response_model=RequirementCoverageReport,
)
def get_requirement_report(
    document_set_id: str, request: Request
) -> RequirementCoverageReport:
    require_document_set_for_tenant(
        repository=repository,
        document_set_id=document_set_id,
        request=request,
    )
    report = repository.get_requirement_report(document_set_id)
    if report is None:
        # 409 rather than 404: the document set exists, its coverage review
        # has not produced a report yet (still running, disabled, or failed).
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Für DocumentSet {document_set_id} liegt noch kein "
                "Anforderungsbericht vor."
            ),
        )
    return report


@router.get(
    "/{document_set_id}/requirement-report/retry",
    response_model=RequirementReportRetry,
)
def get_requirement_report_retry(
    document_set_id: str, request: Request
) -> RequirementReportRetry:
    require_document_set_for_tenant(
        repository=repository,
        document_set_id=document_set_id,
        request=request,
    )
    return _retry_status(document_set_id)


@router.post(
    "/{document_set_id}/requirement-report/retry",
    response_model=RequirementReportRetry,
    status_code=status.HTTP_202_ACCEPTED,
)
def retry_failed_requirements(
    document_set_id: str, request: Request, background_tasks: BackgroundTasks
) -> RequirementReportRetry:
    """Re-judge only the rows a failed model call left behind.

    Everything else in the report stays as it is. Runs in the background
    like a pipeline; poll the GET to watch it and reload the report when
    `active` drops back to false.
    """
    require_document_set_for_tenant(
        repository=repository,
        document_set_id=document_set_id,
        request=request,
    )
    current = _retry_status(document_set_id)
    if repository.get_requirement_report(document_set_id) is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Für DocumentSet {document_set_id} liegt noch kein Anforderungsbericht vor.",
        )
    if _pipeline_is_running(document_set_id):
        # The pipeline will replace the whole report when it finishes; a
        # retry merging into the old one in parallel would be lost or, worse,
        # interleave with the new report's write.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Die Analyse läuft gerade; die erneute Prüfung ist erst danach möglich.",
        )
    if current.active:
        return current
    if current.retryable == 0:
        return current
    key = _retry_key(document_set_id)
    progress.report(key, f"Erneute Prüfung von {current.retryable} Anforderungen gestartet")
    background_tasks.add_task(_run_retry, document_set_id)
    return RequirementReportRetry(
        retryable=current.retryable, active=True, detail=progress.detail_for(key)
    )
