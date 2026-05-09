from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from app.audit.events import audit_log
from app.core.security import require_document_set_for_tenant
from app.db.in_memory import repository
from app.schemas.risk import RiskDecision
from app.services.risk_fusion import (
    RiskFusionDocumentSetNotFoundError,
    RiskFusionService,
)

router = APIRouter(prefix="/document-sets", tags=["risk-fusion"])


def get_risk_fusion_service() -> RiskFusionService:
    return RiskFusionService(repository=repository, audit_log=audit_log)


@router.post("/{document_set_id}/run-risk-fusion", response_model=RiskDecision)
def run_risk_fusion(document_set_id: str, request: Request) -> RiskDecision:
    require_document_set_for_tenant(
        repository=repository,
        document_set_id=document_set_id,
        request=request,
    )
    try:
        return get_risk_fusion_service().run_risk_fusion(document_set_id)
    except RiskFusionDocumentSetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
