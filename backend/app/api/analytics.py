from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from app.audit.events import audit_log
from app.core.security import current_tenant_id
from app.db.in_memory import repository
from app.schemas.analytics import FalsePositiveAnalyticsReport, HumanFeedbackRegistryReport
from app.schemas.calibration import (
    CalibrationExample,
    CalibrationExampleApprovalRequest,
    CalibrationRegressionGateReport,
    ReviewCalibrationReport,
)
from app.services.false_positive_analytics import HumanOverrideAnalyzer
from app.services.human_feedback_registry import HumanFeedbackRegistry
from app.services.review_calibration import (
    CalibrationActivationGateError,
    CalibrationExampleNotFoundError,
    ReviewCalibrationService,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/false-positives", response_model=FalsePositiveAnalyticsReport)
def get_false_positive_analytics(request: Request) -> FalsePositiveAnalyticsReport:
    analyzer = HumanOverrideAnalyzer(repository=repository, audit_log=audit_log)
    return analyzer.analyze(tenant_id=current_tenant_id(request))


@router.get("/human-feedback", response_model=HumanFeedbackRegistryReport)
def get_human_feedback_registry(request: Request) -> HumanFeedbackRegistryReport:
    registry = HumanFeedbackRegistry(repository=repository, audit_log=audit_log)
    return registry.report(tenant_id=current_tenant_id(request))


@router.get("/review-calibration", response_model=ReviewCalibrationReport)
def get_review_calibration_report(request: Request) -> ReviewCalibrationReport:
    calibration = ReviewCalibrationService(repository=repository, audit_log=audit_log)
    return calibration.report(tenant_id=current_tenant_id(request))


@router.post(
    "/review-calibration/run-regression-gate",
    response_model=CalibrationRegressionGateReport,
)
def run_review_calibration_regression_gate() -> CalibrationRegressionGateReport:
    calibration = ReviewCalibrationService(repository=repository, audit_log=audit_log)
    return calibration.run_regression_gate()


@router.post(
    "/review-calibration/{calibration_example_id}/approve",
    response_model=CalibrationExample,
)
def approve_review_calibration_example(
    calibration_example_id: str,
    approval_request: CalibrationExampleApprovalRequest,
    request: Request,
) -> CalibrationExample:
    tenant_id = current_tenant_id(request)
    existing = repository.get_calibration_example(calibration_example_id)
    if existing is None or (tenant_id is not None and existing.tenant_id != tenant_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CalibrationExample {calibration_example_id} not found",
        )

    calibration = ReviewCalibrationService(repository=repository, audit_log=audit_log)
    try:
        return calibration.approve_example(
            calibration_example_id,
            approved_by=approval_request.approved_by,
            activate=approval_request.activate,
            regression_gate_passed=approval_request.regression_gate_passed,
            regression_gate_report_id=approval_request.regression_gate_report_id,
        )
    except CalibrationExampleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except CalibrationActivationGateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
