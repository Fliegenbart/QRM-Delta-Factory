"""Read access to the requirement coverage report.

Deliberately its own endpoint rather than a variant of the review pack: the
pack is built around a RiskDecision and its rows are findings, while this
report is built around obligations and its rows are requirements. Forcing one
schema to carry both would blur exactly the distinction that makes the
coverage report worth having.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from app.core.security import require_document_set_for_tenant
from app.db.in_memory import repository
from app.schemas.requirement_review import RequirementCoverageReport

router = APIRouter(prefix="/document-sets", tags=["requirement-report"])


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
