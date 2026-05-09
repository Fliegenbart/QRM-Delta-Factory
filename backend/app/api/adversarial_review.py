from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from app.audit.events import audit_log
from app.core.security import require_document_set_for_tenant
from app.db.in_memory import repository
from app.schemas.review import AdversarialReviewResponse
from app.services.adversarial_review import (
    AdversarialReviewDocumentSetNotFoundError,
    AdversarialReviewMissingPrimaryReviewError,
    AdversarialReviewService,
)

router = APIRouter(prefix="/document-sets", tags=["adversarial-review"])


def get_adversarial_review_service() -> AdversarialReviewService:
    return AdversarialReviewService(repository=repository, audit_log=audit_log)


@router.post(
    "/{document_set_id}/run-adversarial-review",
    response_model=AdversarialReviewResponse,
)
def run_adversarial_review(
    document_set_id: str,
    request: Request,
) -> AdversarialReviewResponse:
    require_document_set_for_tenant(
        repository=repository,
        document_set_id=document_set_id,
        request=request,
    )
    try:
        return get_adversarial_review_service().run_adversarial_review(document_set_id)
    except AdversarialReviewDocumentSetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AdversarialReviewMissingPrimaryReviewError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
