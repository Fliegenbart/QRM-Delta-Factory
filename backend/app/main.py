from fastapi import FastAPI

from app.api.adversarial_review import router as adversarial_review_router
from app.api.analytics import router as analytics_router
from app.api.claim_ledger import router as claim_ledger_router
from app.api.document_sets import router as document_sets_router
from app.api.evals import router as evals_router
from app.api.health import router as health_router
from app.api.pipeline_runs import document_set_router as pipeline_document_set_router
from app.api.pipeline_runs import pipeline_run_router
from app.api.primary_review import router as primary_review_router
from app.api.requirement_sets import router as requirement_sets_router
from app.api.review_pack import document_set_router as review_pack_document_set_router
from app.api.review_pack import finding_router as review_pack_finding_router
from app.api.risk_fusion import router as risk_fusion_router
from app.core.config import get_settings
from app.core.security import api_key_auth_middleware


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Backend skeleton for evidence-first pharma AI risk orchestration. "
            "This system supports human review and does not make autonomous "
            "regulatory decisions."
        ),
    )
    application.middleware("http")(api_key_auth_middleware)
    application.include_router(analytics_router)
    application.include_router(requirement_sets_router)
    application.include_router(document_sets_router)
    application.include_router(claim_ledger_router)
    application.include_router(primary_review_router)
    application.include_router(adversarial_review_router)
    application.include_router(risk_fusion_router)
    application.include_router(review_pack_document_set_router)
    application.include_router(review_pack_finding_router)
    application.include_router(pipeline_document_set_router)
    application.include_router(pipeline_run_router)
    application.include_router(evals_router)
    application.include_router(health_router)
    return application


app = create_app()
