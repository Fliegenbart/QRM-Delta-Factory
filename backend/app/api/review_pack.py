from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from app.audit.events import audit_log
from app.core.security import require_document_set_for_tenant, require_finding_for_tenant
from app.db.in_memory import repository
from app.schemas.domain import ReviewDecision
from app.schemas.review_pack import ReviewDecisionRequest, ReviewPack
from app.services.review_pack import (
    ReviewDecisionFindingNotFoundError,
    ReviewPackDocumentSetNotFoundError,
    ReviewPackRiskDecisionNotFoundError,
    ReviewPackService,
)

document_set_router = APIRouter(prefix="/document-sets", tags=["review-pack"])
finding_router = APIRouter(prefix="/findings", tags=["review-decisions"])


def get_review_pack_service() -> ReviewPackService:
    return ReviewPackService(repository=repository, audit_log=audit_log)


@document_set_router.get("/{document_set_id}/review-pack", response_model=ReviewPack)
def get_review_pack(document_set_id: str, request: Request) -> ReviewPack:
    require_document_set_for_tenant(
        repository=repository,
        document_set_id=document_set_id,
        request=request,
    )
    try:
        return get_review_pack_service().get_review_pack(document_set_id)
    except ReviewPackDocumentSetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ReviewPackRiskDecisionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@finding_router.post("/{finding_id}/review-decision", response_model=ReviewDecision)
def record_review_decision(
    finding_id: str,
    request: ReviewDecisionRequest,
    http_request: Request,
) -> ReviewDecision:
    require_finding_for_tenant(
        repository=repository,
        finding_id=finding_id,
        request=http_request,
    )
    try:
        return get_review_pack_service().record_review_decision(
            finding_id=finding_id,
            reviewer_id=request.reviewer_id,
            decision=request.decision,
            rationale=request.rationale,
        )
    except ReviewDecisionFindingNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
