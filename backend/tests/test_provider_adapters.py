from __future__ import annotations

import json
from datetime import UTC, datetime
from hashlib import sha256
from threading import Thread
from time import sleep
from typing import Any

import httpx
import pytest
from pydantic import BaseModel

from app.agents.providers import (
    AnthropicProvider,
    BaseModelProvider,
    ExternalModelCallsDisabledError,
    GeminiProvider,
    MistralProvider,
    MockProvider,
    ModelProviderNotAllowedError,
    OpenAIProvider,
    ProviderCallError,
    ProviderCircuitOpenError,
    ProviderConfigurationError,
    ProviderRuntimeOptions,
    ProviderStructuredOutputError,
    external_base,
)
from app.agents.providers.external_base import ExternalProviderBase
from app.audit.events import audit_log
from app.core.config import get_settings
from app.db.in_memory import repository
from app.schemas.domain import DocumentSet, RequirementSet
from app.schemas.review import ReviewerAgentOutput
from app.services.review_orchestrator import (
    PrimaryReviewOrchestrator,
    ReviewerAgent,
    default_reviewer_agents,
)
from app.services.risk_fusion import RiskFusionService


@pytest.fixture(autouse=True)
def reset_state(monkeypatch: pytest.MonkeyPatch) -> None:
    repository.reset()
    audit_log.clear()
    monkeypatch.setenv("QRM_EXTERNAL_MODEL_CALLS_ENABLED", "false")
    monkeypatch.setenv("QRM_ALLOWED_MODEL_PROVIDERS", "mock")
    monkeypatch.delenv("QRM_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("QRM_ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("QRM_GEMINI_API_KEY", raising=False)
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


def test_provider_normalizes_model_supplied_quote_hashes_for_reviewer_output() -> None:
    quote = "QA approval remains pending."
    provider = MockProvider(
        model_name="mock-reviewer",
        model_version="0.1.0",
        configured_model_id="mock-local",
        structured_output={
            "coverage_summary": "Reviewed one claim.",
            "findings": [
                {
                    "finding_id": "finding_provider_hash",
                    "document_set_id": "ds_provider_demo",
                    "risk_category": "qa_approval",
                    "severity": "medium",
                    "likelihood": 3,
                    "detectability": 3,
                    "risk_statement": "QA approval appears pending.",
                    "evidence_items": [
                        {
                            "document_id": "doc_provider_demo",
                            "chunk_id": "chunk_provider_demo",
                            "page": 1,
                            "quote": quote,
                            "quote_hash": "not-a-valid-sha256",
                            "support_type": "supports",
                            "verifier_score": 0.7,
                        }
                    ],
                    "requirement_references": ["req_provider_deviation_review"],
                    "missing_information": ["documented QA approval decision"],
                    "model_provider": "mock",
                    "model_name": "mock-reviewer",
                    "model_version": "0.1.0",
                    "prompt_version": "prompt-v1",
                    "evidence_support": "partial",
                    "recommended_action": "Review approval status.",
                    "auto_close_allowed": False,
                    "status": "needs_human_review",
                }
            ],
        },
        prompt_version="prompt-v1",
    )

    output = provider.run_structured(
        prompt="Return reviewer output.",
        input_schema={},
        output_schema=ReviewerAgentOutput,
    )

    assert (
        output["findings"][0]["evidence_items"][0]["quote_hash"]
        == sha256(quote.encode()).hexdigest()
    )


def test_stringified_findings_payload_is_normalized_for_reviewer_output() -> None:
    quote = "QA approval remains pending."
    stringified_findings = (
        "["
        + json.dumps(
            {
                "finding_id": "finding_stringified",
                "document_set_id": "ds_provider_demo",
                "risk_category": "qa_approval",
                "severity": "high",
                "likelihood": 3,
                "detectability": 3,
                "risk_statement": "QA approval appears pending.",
                "evidence_items": [
                    {
                        "document_id": "doc_provider_demo",
                        "chunk_id": "chunk_provider_demo",
                        "page": 1,
                        "quote": quote,
                        "quote_hash": "not-a-valid-sha256",
                        "support_type": "supports",
                        "verifier_score": 0.8,
                    }
                ],
                "requirement_references": ["req_provider_deviation_review"],
                "missing_information": ["documented QA approval decision"],
                "model_provider": "mock",
                "model_name": "mock-reviewer",
                "model_version": "0.1.0",
                "prompt_version": "prompt-v1",
                "evidence_support": "partial",
                "recommended_action": "Review approval status.",
                "auto_close_allowed": False,
                "status": "needs_human_review",
            }
        )
        + "]"
    )
    provider = MockProvider(
        model_name="mock-reviewer",
        model_version="0.1.0",
        configured_model_id="mock-local",
        structured_output={
            "coverage_summary": "Reviewed one stringified finding.",
            "findings": stringified_findings,
        },
        prompt_version="prompt-v1",
    )

    output = provider.run_structured(
        prompt="Return reviewer output.",
        input_schema={},
        output_schema=ReviewerAgentOutput,
    )

    assert isinstance(output["findings"], list)
    assert output["findings"][0]["finding_id"] == "finding_stringified"
    assert (
        output["findings"][0]["evidence_items"][0]["quote_hash"]
        == sha256(quote.encode()).hexdigest()
    )


@pytest.mark.parametrize(
    "provider",
    [
        OpenAIProvider(configured_model_id="gpt-test"),
        AnthropicProvider(configured_model_id="claude-test"),
        GeminiProvider(configured_model_id="gemini-test"),
        MistralProvider(configured_model_id="mistral-test"),
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


def test_openai_provider_runs_structured_call_with_mocked_http(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QRM_EXTERNAL_MODEL_CALLS_ENABLED", "true")
    monkeypatch.setenv("QRM_ALLOWED_MODEL_PROVIDERS", "openai")
    monkeypatch.setenv("QRM_OPENAI_API_KEY", "test-openai-key")
    get_settings.cache_clear()
    provider = OpenAIProvider(configured_model_id="gpt-test")

    def fake_post_json(
        *,
        url: str,
        headers: dict[str, str],
        json_body: dict[str, Any],
    ) -> dict[str, Any]:
        assert url.endswith("/v1/chat/completions")
        assert headers["Authorization"] == "Bearer test-openai-key"
        assert json_body["model"] == "gpt-test"
        return {
            "choices": [{"message": {"content": '{"value": "ok-openai"}'}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }

    monkeypatch.setattr(provider, "_post_json", fake_post_json)

    output = provider.run_structured("Return JSON.", {}, SimpleOutput)

    assert output == {"value": "ok-openai"}
    assert provider.last_run_metadata is not None
    assert provider.last_run_metadata.token_usage is not None
    assert provider.last_run_metadata.token_usage.total_tokens == 15


def test_anthropic_provider_runs_structured_call_with_mocked_http(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QRM_EXTERNAL_MODEL_CALLS_ENABLED", "true")
    monkeypatch.setenv("QRM_ALLOWED_MODEL_PROVIDERS", "anthropic")
    monkeypatch.setenv("QRM_ANTHROPIC_API_KEY", "test-anthropic-key")
    get_settings.cache_clear()
    provider = AnthropicProvider(configured_model_id="claude-test")

    def fake_post_json(
        *,
        url: str,
        headers: dict[str, str],
        json_body: dict[str, Any],
    ) -> dict[str, Any]:
        assert url.endswith("/v1/messages")
        assert headers["x-api-key"] == "test-anthropic-key"
        assert json_body["model"] == "claude-test"
        return {
            "content": [{"type": "text", "text": '{"value": "ok-anthropic"}'}],
            "usage": {"input_tokens": 12, "output_tokens": 6},
        }

    monkeypatch.setattr(provider, "_post_json", fake_post_json)

    output = provider.run_structured("Return JSON.", {}, SimpleOutput)

    assert output == {"value": "ok-anthropic"}
    assert provider.last_run_metadata is not None
    assert provider.last_run_metadata.token_usage is not None
    assert provider.last_run_metadata.token_usage.total_tokens == 18


def test_gemini_provider_runs_structured_call_with_mocked_http(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QRM_EXTERNAL_MODEL_CALLS_ENABLED", "true")
    monkeypatch.setenv("QRM_ALLOWED_MODEL_PROVIDERS", "gemini")
    monkeypatch.setenv("QRM_GEMINI_API_KEY", "test-gemini-key")
    get_settings.cache_clear()
    provider = GeminiProvider(configured_model_id="gemini-test")

    def fake_post_json(
        *,
        url: str,
        headers: dict[str, str],
        json_body: dict[str, Any],
    ) -> dict[str, Any]:
        assert "models/gemini-test:generateContent" in url
        assert headers["Content-Type"] == "application/json"
        assert headers["x-goog-api-key"] == "test-gemini-key"
        assert json_body["generationConfig"]["responseMimeType"] == "application/json"
        return {
            "candidates": [
                {"content": {"parts": [{"text": '{"value": "ok-gemini"}'}]}}
            ],
            "usageMetadata": {
                "promptTokenCount": 11,
                "candidatesTokenCount": 7,
                "totalTokenCount": 18,
            },
        }

    monkeypatch.setattr(provider, "_post_json", fake_post_json)

    output = provider.run_structured("Return JSON.", {}, SimpleOutput)

    assert output == {"value": "ok-gemini"}
    assert provider.last_run_metadata is not None
    assert provider.last_run_metadata.token_usage is not None
    assert provider.last_run_metadata.token_usage.total_tokens == 18


def test_external_provider_requires_api_key_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QRM_EXTERNAL_MODEL_CALLS_ENABLED", "true")
    monkeypatch.setenv("QRM_ALLOWED_MODEL_PROVIDERS", "openai")
    monkeypatch.delenv("QRM_OPENAI_API_KEY", raising=False)
    get_settings.cache_clear()
    provider = OpenAIProvider(configured_model_id="gpt-test")

    with pytest.raises(ProviderConfigurationError):
        provider.run_structured("Return JSON.", {}, SimpleOutput)


def test_default_agents_use_real_provider_mapping_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QRM_EXTERNAL_MODEL_CALLS_ENABLED", "true")
    monkeypatch.setenv("QRM_ALLOWED_MODEL_PROVIDERS", "openai,anthropic")
    monkeypatch.setenv("QRM_OPENAI_MODEL_ID", "gpt-test")
    monkeypatch.setenv("QRM_ANTHROPIC_MODEL_ID", "claude-test")
    get_settings.cache_clear()

    agents = default_reviewer_agents()
    providers_by_role = {agent.role: agent.provider.provider_name for agent in agents}

    assert providers_by_role == {
        "GMPDataIntegrityReviewer": "anthropic",
        "DeviationReviewer": "anthropic",
        "CAPAReviewer": "anthropic",
        "BatchImpactReviewer": "openai",
        "ValidationAndSterilityReviewer": "anthropic",
        "RegulatoryConsistencyReviewer": "anthropic",
        "ContradictionHunter": "openai",
    }


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


def test_provider_runtime_options_include_a_total_retry_deadline() -> None:
    options = ProviderRuntimeOptions()

    assert hasattr(options, "retry_deadline_seconds")


def test_base_provider_is_the_only_retry_owner_and_records_retry_metadata() -> None:
    provider = RetryOnceProvider(
        runtime_options=ProviderRuntimeOptions(
            max_retries=1,
            retry_deadline_seconds=1,
        )
    )

    output = provider.run_structured("Return JSON.", {}, SimpleOutput)

    assert output == {"value": "ok"}
    assert provider.calls == 2
    assert provider.last_run_metadata is not None
    assert provider.last_run_metadata.retry_count == 1


def test_external_post_returns_retryable_429_to_the_base_retry_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0
    response = httpx.Response(
        429,
        headers={"retry-after": "99"},
        request=httpx.Request("POST", "https://provider.example/test"),
    )

    class FailingClient:
        def __init__(self, *, timeout: float) -> None:
            assert timeout == 30

        def __enter__(self) -> FailingClient:
            return self

        def __exit__(self, *args: Any) -> None:
            return None

        def post(self, *args: Any, **kwargs: Any) -> httpx.Response:
            nonlocal calls
            calls += 1
            raise httpx.HTTPStatusError(
                "too many requests",
                request=response.request,
                response=response,
            )

    monkeypatch.setattr(external_base.httpx, "Client", FailingClient)
    provider = ExternalProviderBase(
        provider_name="external-test",
        model_name="test-model",
        model_version="v1",
        configured_model_id="test-model",
        external_calls_required=False,
    )

    with pytest.raises(ProviderCallError) as raised:
        provider._post_json(url="https://provider.example/test", headers={}, json_body={})

    assert calls == 1
    assert raised.value.retryable is True
    assert raised.value.retry_after_seconds == 30


def test_provider_retry_deadline_prevents_a_long_retry_after_sleep() -> None:
    provider = AlwaysRetryableProvider(
        runtime_options=ProviderRuntimeOptions(
            max_retries=3,
            retry_deadline_seconds=0.001,
        )
    )

    with pytest.raises(ProviderCallError, match="retry deadline exceeded"):
        provider.run_structured("Return JSON.", {}, SimpleOutput)

    assert provider.calls == 1


def test_provider_retry_deadline_starts_after_shared_queue_wait() -> None:
    provider = ImmediateProvider(
        runtime_options=ProviderRuntimeOptions(
            retry_deadline_seconds=0.01,
            max_concurrent_calls=1,
        )
    )
    semaphore = provider._provider_semaphore()
    assert semaphore.acquire(blocking=False)
    result: list[dict[str, Any]] = []

    worker = Thread(
        target=lambda: result.append(provider.run_structured("Return JSON.", {}, SimpleOutput))
    )
    worker.start()
    sleep(0.03)
    semaphore.release()
    worker.join(timeout=1)

    assert not worker.is_alive()
    assert result == [{"value": "ok"}]


def test_provider_circuit_state_is_shared_by_provider_and_model() -> None:
    options = ProviderRuntimeOptions(max_retries=0, circuit_breaker_failure_threshold=1)
    first = AlwaysRetryableProvider(runtime_options=options, provider_name="circuit-test")
    second = AlwaysRetryableProvider(runtime_options=options, provider_name="circuit-test")

    with pytest.raises(ProviderCallError):
        first.run_structured("Return JSON.", {}, SimpleOutput)

    with pytest.raises(ProviderCircuitOpenError):
        second.run_structured("Return JSON.", {}, SimpleOutput)

    assert second.calls == 0


class RetryOnceProvider(BaseModelProvider):
    def __init__(self, *, runtime_options: ProviderRuntimeOptions) -> None:
        super().__init__(
            provider_name="retry-test",
            model_name="retry-test-model",
            model_version="v1",
            configured_model_id="retry-test-model",
            runtime_options=runtime_options,
            external_calls_required=False,
        )
        self.calls = 0

    def _run_structured_once(
        self,
        *,
        prompt: str,
        input_schema: dict[str, Any],
        output_schema: type[BaseModel],
    ) -> dict[str, Any]:
        self.calls += 1
        if self.calls == 1:
            raise ProviderCallError("transient failure", retryable=True, retry_after_seconds=0)
        return {"value": "ok"}


class AlwaysRetryableProvider(BaseModelProvider):
    def __init__(
        self,
        *,
        runtime_options: ProviderRuntimeOptions,
        provider_name: str = "deadline-test",
    ) -> None:
        super().__init__(
            provider_name=provider_name,
            model_name="deadline-test-model",
            model_version="v1",
            configured_model_id="deadline-test-model",
            runtime_options=runtime_options,
            external_calls_required=False,
        )
        self.calls = 0

    def _run_structured_once(
        self,
        *,
        prompt: str,
        input_schema: dict[str, Any],
        output_schema: type[BaseModel],
    ) -> dict[str, Any]:
        self.calls += 1
        raise ProviderCallError("transient failure", retryable=True, retry_after_seconds=30)


class ImmediateProvider(BaseModelProvider):
    def __init__(self, *, runtime_options: ProviderRuntimeOptions) -> None:
        super().__init__(
            provider_name="queue-test",
            model_name="queue-test-model",
            model_version="v1",
            configured_model_id="queue-test-model",
            runtime_options=runtime_options,
            external_calls_required=False,
        )

    def _run_structured_once(
        self,
        *,
        prompt: str,
        input_schema: dict[str, Any],
        output_schema: type[BaseModel],
    ) -> dict[str, Any]:
        return {"value": "ok"}


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


def test_mistral_provider_runs_structured_call_with_mocked_http(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QRM_EXTERNAL_MODEL_CALLS_ENABLED", "true")
    monkeypatch.setenv("QRM_ALLOWED_MODEL_PROVIDERS", "mistral")
    monkeypatch.setenv("QRM_MISTRAL_API_KEY", "test-mistral-key")
    get_settings.cache_clear()
    provider = MistralProvider(configured_model_id="mistral-test")

    def fake_post_json(
        *,
        url: str,
        headers: dict[str, str],
        json_body: dict[str, Any],
    ) -> dict[str, Any]:
        assert url.endswith("/v1/chat/completions")
        assert "mistral.ai" in url
        assert headers["Authorization"] == "Bearer test-mistral-key"
        assert json_body["model"] == "mistral-test"
        assert json_body["response_format"]["type"] == "json_schema"
        assert json_body["response_format"]["json_schema"]["name"] == "simpleoutput"
        assert json_body["response_format"]["json_schema"]["schema"]["type"] == "object"
        assert "output_schema" not in json_body["messages"][1]["content"]
        return {
            "choices": [{"message": {"content": '{"value": "ok-mistral"}'}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }

    monkeypatch.setattr(provider, "_post_json", fake_post_json)

    output = provider.run_structured("Return JSON.", {}, SimpleOutput)

    assert output == {"value": "ok-mistral"}
    assert provider.last_run_metadata is not None
    assert provider.last_run_metadata.token_usage is not None
    assert provider.last_run_metadata.token_usage.total_tokens == 15
