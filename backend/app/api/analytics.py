from __future__ import annotations

from fastapi import APIRouter, Request

from app.audit.events import audit_log
from app.core.security import current_tenant_id
from app.db.in_memory import repository
from app.schemas.analytics import FalsePositiveAnalyticsReport
from app.services.false_positive_analytics import HumanOverrideAnalyzer

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/false-positives", response_model=FalsePositiveAnalyticsReport)
def get_false_positive_analytics(request: Request) -> FalsePositiveAnalyticsReport:
    analyzer = HumanOverrideAnalyzer(repository=repository, audit_log=audit_log)
    return analyzer.analyze(tenant_id=current_tenant_id(request))
