from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, Response, status

from app.audit.events import audit_log
from app.core.security import current_tenant_id
from app.db.in_memory import repository
from app.schemas.demo import DemoSeedResponse
from app.services.demo_seed import DemoSeedService, DemoSeedTenantMismatchError

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/seed", response_model=DemoSeedResponse, status_code=status.HTTP_201_CREATED)
def seed_demo_data(request: Request, response: Response) -> DemoSeedResponse:
    tenant_id = current_tenant_id(request) or "tenant_demo_pharma"
    try:
        result = DemoSeedService(repository=repository, audit_log=audit_log).seed(
            tenant_id=tenant_id
        )
    except DemoSeedTenantMismatchError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if not result.created:
        response.status_code = status.HTTP_200_OK
    return result
