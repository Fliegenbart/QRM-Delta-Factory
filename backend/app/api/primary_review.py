from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from app.audit.events import audit_log
from app.core.security import require_document_set_for_tenant
from app.db.in_memory import repository
from app.schemas.review import PrimaryReviewResponse
from app.services.claim_ledger import (
    ClaimLedgerDocumentSetNotFoundError,
    ClaimLedgerService,
    ClaimLedgerValidationError,
    MockClaimExtractor,
)
from app.services.review_orchestrator import (
    PrimaryReviewDocumentSetNotFoundError,
    PrimaryReviewOrchestrator,
)

router = APIRouter(prefix="/document-sets", tags=["primary-review"])


def get_primary_review_orchestrator() -> PrimaryReviewOrchestrator:
    return PrimaryReviewOrchestrator(repository=repository, audit_log=audit_log)


def get_claim_ledger_service() -> ClaimLedgerService:
    return ClaimLedgerService(
        repository=repository,
        audit_log=audit_log,
        extractor=MockClaimExtractor(),
    )


@router.post("/{document_set_id}/run-primary-review", response_model=PrimaryReviewResponse)
def run_primary_review(document_set_id: str, request: Request) -> PrimaryReviewResponse:
    require_document_set_for_tenant(
        repository=repository,
        document_set_id=document_set_id,
        request=request,
    )
    try:
        get_claim_ledger_service().get_or_build_claim_ledger(document_set_id)
        return get_primary_review_orchestrator().run_primary_review(document_set_id)
    except (PrimaryReviewDocumentSetNotFoundError, ClaimLedgerDocumentSetNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ClaimLedgerValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
