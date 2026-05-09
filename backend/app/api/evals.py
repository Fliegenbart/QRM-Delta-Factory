from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.audit.events import audit_log
from app.schemas.evals import EvalReport, EvalRunRequest
from app.services.eval_runner import EvalFixtureNotFoundError, EvalRunner

router = APIRouter(prefix="/evals", tags=["evals"])


@router.post("/run", response_model=EvalReport)
def run_eval(request: EvalRunRequest) -> EvalReport:
    if request.provider_mode != "mock":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Only provider_mode=mock is implemented in the MVP eval harness",
        )
    try:
        report = EvalRunner().run_fixture(request.dataset_id)
        audit_log.append(
            event_type="eval_run_completed",
            actor_id="service_eval_runner",
            actor_type="service",
            entity_type="EvalDataset",
            entity_id=report.dataset.dataset_id,
            payload={
                "dataset_id": report.dataset.dataset_id,
                "dataset_version": report.dataset.version,
                "provider_mode": request.provider_mode,
                "passed": report.passed,
                "runner_version": report.runner_version,
                "failure_count": len(report.failures),
                "metric_keys": sorted(report.metrics.model_dump()),
            },
        )
        return report
    except EvalFixtureNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
