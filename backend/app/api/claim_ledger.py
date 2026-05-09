from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from app.audit.events import audit_log
from app.core.security import require_document_set_for_tenant
from app.db.in_memory import repository
from app.schemas.domain import Claim
from app.services.claim_ledger import (
    ClaimLedgerDocumentSetNotFoundError,
    ClaimLedgerService,
    ClaimLedgerValidationError,
    MockClaimExtractor,
)

router = APIRouter(prefix="/document-sets", tags=["claim-ledger"])


def get_claim_ledger_service() -> ClaimLedgerService:
    return ClaimLedgerService(
        repository=repository,
        audit_log=audit_log,
        extractor=MockClaimExtractor(),
    )


@router.get("/{document_set_id}/claims", response_model=list[Claim])
def get_document_set_claims(document_set_id: str, request: Request) -> list[Claim]:
    require_document_set_for_tenant(
        repository=repository,
        document_set_id=document_set_id,
        request=request,
    )
    try:
        return get_claim_ledger_service().get_or_build_claim_ledger(document_set_id)
    except ClaimLedgerDocumentSetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ClaimLedgerValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
