from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import BaseModel

from app.agents.providers import (
    AnthropicProvider,
    ExternalModelCallsDisabledError,
    GeminiProvider,
    MockProvider,
    ModelProviderNotAllowedError,
    OpenAIProvider,
    ProviderConfigurationError,
    ProviderStructuredOutputError,
)
from app.audit.events import audit_log
from app.core.config import get_settings
from app.db.in_memory import repository
from app.schemas.domain import DocumentSet, RequirementSet
from app.services.review_orchestrator import PrimaryReviewOrchestrator, ReviewerAgent
from app.services.risk_fusion import RiskFusionService


@pytest.fixture(autouse=True)
def reset_state(monkeypatch: pytest.MonkeyPatch) -> None:
    repository.reset()
    audit_log.clear()
    monkeypatch.setenv("QRM_EXTERNAL_MODEL_CALLS_ENABLED", "false")
    monkeypatch.setenv("QRM_ALLOWED_MODEL_PROVIDERS", "mock")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_mock_provider_validates_structured_output_and_records_metadata() -> None:
    provider = MockProvider(
        model_name="mock-reviewer",
        model_version="0.1.0",
        configured_model_id="mock-local",
        structured_output={"value": "ok"},
        prompt_version="prompt-v1",
    )

    output = provider.run_structured(
        prompt="Return a small object.",
        input_schema={"document_set_id": "ds_provider_demo"},
        output_schema=SimpleOutput,
    )

    assert output == {"value": "ok"}
    assert provider.last_run_metadata is not None
    assert provider.last_run_metadata.provider == "mock"
    assert provider.last_run_metadata.model_name == "mock-reviewer"
    assert provider.last_run_metadata.configured_model_id == "mock-local"
    assert provider.last_run_metadata.prompt_version == "prompt-v1"
    assert len(provider.last_run_metadata.request_hash) == 64
    assert len(provider.last_run_metadata.response_hash) == 64
    assert provider.last_run_metadata.latency_ms >= 0


def test_mock_provider_rejects_invalid_structured_output() -> None:
    provider = MockProvider(
        model_name="mock-reviewer",
        model_version="0.1.0",
        configured_model_id="mock-local",
        structured_output={"wrong": "shape"},
    )

    with pytest.raises(ProviderStructuredOutputError):
        provider.run_structured(
            prompt="Return bad object.",
            input_schema={},
            output_schema=SimpleOutput,
        )


@pytest.mark.parametrize(
    "provider",
    [
        OpenAIProvider(configured_model_id="gpt-test"),
        AnthropicProvider(configured_model_id="claude-test"),
        GeminiProvider(configured_model_id="gemini-test"),
    ],
)
def test_external_providers_fail_closed_when_disabled(provider: Any) -> None:
    with pytest.raises(ExternalModelCallsDisabledError):
        provider.run_structured(
            prompt="No external call should happen.",
            input_schema={},
            output_schema=SimpleOutput,
        )


def test_external_provider_requires_explicit_configured_model_id() -> None:
    with pytest.raises(ProviderConfigurationError):
        OpenAIProvider()


def test_external_provider_does_not_fallback_to_disallowed_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QRM_EXTERNAL_MODEL_CALLS_ENABLED", "true")
    monkeypatch.setenv("QRM_ALLOWED_MODEL_PROVIDERS", "anthropic")
    monkeypatch.setenv("QRM_OPENAI_API_KEY", "test-key-from-env")
    get_settings.cache_clear()
    provider = OpenAIProvider(configured_model_id="gpt-test")

    with pytest.raises(ModelProviderNotAllowedError):
        provider.run_structured(
            prompt="Provider is intentionally disallowed.",
            input_schema={},
            output_schema=SimpleOutput,
        )


def test_provider_error_reaches_risk_fusion_as_coverage_risk() -> None:
    repository.create_requirement_set(_requirement_set())
    repository.create_document_set(_document_set())
    failing_provider = OpenAIProvider(configured_model_id="gpt-test")
    agent = ReviewerAgent(
        agent_id="agent_openai_disabled",
        role="DeviationReviewer",
        prompt_version="provider-error-v0.1",
        applicable_risk_categories=["deviation_management"],
        provider=failing_provider,
    )
    result = PrimaryReviewOrchestrator(
        repository=repository,
        audit_log=audit_log,
        agents=[agent],
    ).run_primary_review("ds_provider_demo")

    decision = RiskFusionService(repository=repository, audit_log=audit_log).run_risk_fusion(
        "ds_provider_demo"
    )

    assert len(result.failed_model_runs) == 1
    assert result.failed_model_runs[0].provider == "openai"
    assert decision.decision == "blocked_due_to_model_failure"
    assert "failed model run affects review coverage" in decision.auto_clear_blockers


class SimpleOutput(BaseModel):
    value: str


def _document_set() -> DocumentSet:
    return DocumentSet(
        document_set_id="ds_provider_demo",
        tenant_id="tenant_demo_pharma",
        requirement_set_id="rset_provider_demo",
        upload_timestamp=datetime.now(UTC),
        document_ids=[],
        declared_document_type="deviation",
        declared_process_area="aseptic_filling",
        uploaded_by="user_qrm_author",
        status="ready_for_orchestration",
    )


def _requirement_set() -> RequirementSet:
    return RequirementSet(
        requirement_set_id="rset_provider_demo",
        tenant_id="tenant_demo_pharma",
        name="Provider Demo Requirements",
        version="2026.1",
        imported_at=datetime.now(UTC),
        imported_by="user_quality_admin",
        active=True,
        requirements=[
            {
                "requirement_id": "req_provider_deviation_review",
                "source_type": "internal_sop",
                "source_name": "SOP-PROVIDER-DEMO",
                "source_version": "1.0",
                "section": "1.0",
                "requirement_text": "Deviation package requires reviewer coverage.",
                "applies_to_document_types": ["deviation"],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": "medium",
                "required_evidence": ["deviation record"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            }
        ],
    )
