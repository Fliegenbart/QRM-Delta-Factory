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
    monkeypatch.delenv("QRM_MISTRAL_API_KEY", raising=False)
    monkeypatch.delenv("QRM_REVIEWER_PROVIDER_OVERRIDE", raising=False)
    monkeypatch.delenv("QRM_CRITIC_PROVIDERS", raising=False)
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


def test_pure_json_fenced_findings_are_normalized_for_reviewer_output() -> None:
    provider = _reviewer_output_provider(
        findings="```json\n" + json.dumps([_reviewer_finding("finding_fenced")]) + "\n```"
    )

    output = provider.run_structured(
        prompt="Return reviewer output.",
        input_schema={},
        output_schema=ReviewerAgentOutput,
    )

    assert output["findings"][0]["finding_id"] == "finding_fenced"


def test_python_literal_findings_are_normalized_for_reviewer_output() -> None:
    provider = _reviewer_output_provider(
        findings=repr([_reviewer_finding("finding_python_literal")])
    )

    output = provider.run_structured(
        prompt="Return reviewer output.",
        input_schema={},
        output_schema=ReviewerAgentOutput,
    )

    assert output["findings"][0]["finding_id"] == "finding_python_literal"


def test_pure_untagged_fenced_findings_are_normalized_for_reviewer_output() -> None:
    provider = _reviewer_output_provider(
        findings="```\n" + json.dumps([_reviewer_finding("finding_untagged_fence")]) + "\n```"
    )

    output = provider.run_structured(
        prompt="Return reviewer output.",
        input_schema={},
        output_schema=ReviewerAgentOutput,
    )

    assert output["findings"][0]["finding_id"] == "finding_untagged_fence"


@pytest.mark.parametrize(
    ("findings", "message"),
    [
        (
            "The findings are:\n```json\n[]\n```",
            "findings must be a valid list of objects",
        ),
        ("[not valid", "findings must be a valid list of objects"),
        (json.dumps({"finding_id": "finding_object"}), "findings must be a list"),
        (json.dumps(["not an object"]), "findings entries must be objects"),
    ],
)
def test_reviewer_findings_string_normalization_rejects_invalid_shapes(
    findings: str,
    message: str,
) -> None:
    provider = _reviewer_output_provider(findings=findings)

    with pytest.raises(ProviderStructuredOutputError, match=message):
        provider.run_structured(
            prompt="Return reviewer output.",
            input_schema={},
            output_schema=ReviewerAgentOutput,
        )


@pytest.mark.parametrize(
    "findings",
    [
        None,
        {"finding_id": "finding_object"},
        {"findings": [{"finding_id": "arbitrary_nested_object"}]},
    ],
)
def test_reviewer_findings_normalization_rejects_non_string_invalid_values(
    findings: Any,
) -> None:
    provider = _reviewer_output_provider(findings=findings)

    with pytest.raises(ProviderStructuredOutputError, match="findings must be a list"):
        provider.run_structured(
            prompt="Return reviewer output.",
            input_schema={},
            output_schema=ReviewerAgentOutput,
        )


def test_reviewer_findings_normalization_rejects_materialized_non_dict_entries() -> None:
    provider = _reviewer_output_provider(findings=["not an object"])

    with pytest.raises(
        ProviderStructuredOutputError,
        match="findings entries must be objects",
    ):
        provider.run_structured(
            prompt="Return reviewer output.",
            input_schema={},
            output_schema=ReviewerAgentOutput,
        )


@pytest.mark.parametrize(
    "findings",
    [
        "```json\n[]\n```\n```json\n[]\n```",
        "```json\n[\n```json\n{}\n```\n]\n```",
    ],
)
def test_reviewer_findings_normalization_rejects_multiple_or_nested_fences(
    findings: str,
) -> None:
    provider = _reviewer_output_provider(findings=findings)

    with pytest.raises(
        ProviderStructuredOutputError,
        match="findings must be a valid list of objects",
    ):
        provider.run_structured(
            prompt="Return reviewer output.",
            input_schema={},
            output_schema=ReviewerAgentOutput,
        )


def _reviewer_output_provider(*, findings: Any) -> MockProvider:
    return MockProvider(
        model_name="mock-reviewer",
        model_version="0.1.0",
        configured_model_id=f"mock-local-{sha256(repr(findings).encode()).hexdigest()[:8]}",
        structured_output={
            "coverage_summary": "Reviewed one finding.",
            "findings": findings,
        },
        prompt_version="prompt-v1",
    )


def _reviewer_finding(finding_id: str) -> dict[str, Any]:
    return {
        "finding_id": finding_id,
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
                "quote": "QA approval remains pending.",
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


@pytest.mark.parametrize(
    "findings",
    [
        _reviewer_finding("finding_single_object"),
        {"findings": [_reviewer_finding("finding_wrapper_object")]},
    ],
)
def test_reviewer_findings_normalize_safe_object_shapes_to_a_list(findings: Any) -> None:
    provider = _reviewer_output_provider(findings=findings)

    output = provider.run_structured(
        prompt="Return reviewer output.",
        input_schema={},
        output_schema=ReviewerAgentOutput,
    )

    assert isinstance(output["findings"], list)
    assert len(output["findings"]) == 1


@pytest.mark.parametrize(
    "findings",
    ["none", "No findings.", "No findings identified", "No applicable findings"],
)
def test_reviewer_findings_normalize_explicit_no_finding_markers(findings: str) -> None:
    provider = _reviewer_output_provider(findings=findings)

    output = provider.run_structured(
        prompt="Return reviewer output.",
        input_schema={},
        output_schema=ReviewerAgentOutput,
    )

    assert output["findings"] == []


def test_reviewer_findings_reject_wrapper_with_extra_keys() -> None:
    provider = _reviewer_output_provider(
        findings={
            "findings": [_reviewer_finding("finding_extra_wrapper_key")],
            "unexpected": "wrapper keys are strict",
        }
    )

    with pytest.raises(ProviderStructuredOutputError, match="findings must be a list"):
        provider.run_structured(
            prompt="Return reviewer output.",
            input_schema={},
            output_schema=ReviewerAgentOutput,
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
    monkeypatch.setenv("QRM_MODEL_PROVIDER_MAX_OUTPUT_TOKENS", "512")
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
        assert json_body["max_tokens"] == 512
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


@pytest.mark.parametrize(
    "findings",
    [
        _reviewer_finding("finding_anthropic_single_candidate"),
        {
            "candidate_validation": _reviewer_finding("finding_anthropic_candidate_one"),
            "candidate_qa": _reviewer_finding("finding_anthropic_candidate_two"),
        },
    ],
)
def test_anthropic_tool_input_normalizes_safe_finding_dict_shapes(
    monkeypatch: pytest.MonkeyPatch,
    findings: dict[str, Any],
) -> None:
    monkeypatch.setenv("QRM_EXTERNAL_MODEL_CALLS_ENABLED", "true")
    monkeypatch.setenv("QRM_ALLOWED_MODEL_PROVIDERS", "anthropic")
    monkeypatch.setenv("QRM_ANTHROPIC_API_KEY", "test-anthropic-key")
    get_settings.cache_clear()
    provider = AnthropicProvider(configured_model_id="claude-tool-input-test")
    monkeypatch.setattr(
        provider,
        "_post_json",
        lambda **_: {
            "content": [
                {
                    "type": "tool_use",
                    "name": "submit_structured_output",
                    "input": {
                        "coverage_summary": "Anthropic returned candidate findings.",
                        "findings": findings,
                    },
                }
            ]
        },
    )

    output = provider.run_structured("Return JSON.", {}, ReviewerAgentOutput)

    assert isinstance(output["findings"], list)
    assert len(output["findings"]) == (1 if "finding_id" in findings else 2)


def test_anthropic_tool_input_rejects_arbitrary_findings_dict(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QRM_EXTERNAL_MODEL_CALLS_ENABLED", "true")
    monkeypatch.setenv("QRM_ALLOWED_MODEL_PROVIDERS", "anthropic")
    monkeypatch.setenv("QRM_ANTHROPIC_API_KEY", "test-anthropic-key")
    get_settings.cache_clear()
    provider = AnthropicProvider(configured_model_id="claude-tool-input-reject-test")
    monkeypatch.setattr(
        provider,
        "_post_json",
        lambda **_: {
            "content": [
                {
                    "type": "tool_use",
                    "name": "submit_structured_output",
                    "input": {
                        "coverage_summary": "Unsafe candidate shape.",
                        "findings": {"candidate": {"risk_statement": "unsupported"}},
                    },
                }
            ]
        },
    )

    with pytest.raises(ProviderStructuredOutputError, match="findings must be a list"):
        provider.run_structured("Return JSON.", {}, ReviewerAgentOutput)


@pytest.mark.parametrize(
    ("provider_name", "response"),
    [
        (
            "anthropic",
            {
                "stop_reason": "max_tokens",
                "content": [{"type": "text", "text": '{"value": "complete-looking"}'}],
            },
        ),
        (
            "mistral",
            {
                "choices": [
                    {
                        "finish_reason": "length",
                        "message": {"content": '{"value": "complete-looking"}'},
                    }
                ]
            },
        ),
    ],
)
def test_provider_truncation_is_sanitized_and_retryable(
    monkeypatch: pytest.MonkeyPatch,
    provider_name: str,
    response: dict[str, Any],
) -> None:
    monkeypatch.setenv("QRM_EXTERNAL_MODEL_CALLS_ENABLED", "true")
    monkeypatch.setenv("QRM_ALLOWED_MODEL_PROVIDERS", provider_name)
    monkeypatch.setenv(f"QRM_{provider_name.upper()}_API_KEY", "test-provider-key")
    get_settings.cache_clear()
    provider = (
        AnthropicProvider(configured_model_id="claude-truncation-test")
        if provider_name == "anthropic"
        else MistralProvider(configured_model_id="mistral-truncation-test")
    )
    monkeypatch.setattr(provider, "_post_json", lambda **_: response)

    with pytest.raises(ProviderCallError) as raised:
        provider.run_structured("Return JSON.", {}, SimpleOutput)

    assert raised.value.retryable is True
    assert "complete-looking" not in str(raised.value)


@pytest.mark.parametrize(
    "transport_error",
    [
        httpx.ConnectError("connection refused"),
        httpx.ReadError("connection reset by peer"),
        httpx.RemoteProtocolError("server disconnected without sending a response"),
    ],
)
def test_transport_faults_are_retryable_and_name_their_cause(
    monkeypatch: pytest.MonkeyPatch,
    transport_error: httpx.HTTPError,
) -> None:
    """A dropped connection is transient, and the report has to say which one.

    These reached the orchestrator as a non-retryable bare "call failed", which
    is how the Anthropic critic could die in six of ten cases without the run
    recording anything about why.
    """
    monkeypatch.setenv("QRM_EXTERNAL_MODEL_CALLS_ENABLED", "true")
    monkeypatch.setenv("QRM_ALLOWED_MODEL_PROVIDERS", "anthropic")
    monkeypatch.setenv("QRM_ANTHROPIC_API_KEY", "test-provider-key")
    get_settings.cache_clear()
    provider = AnthropicProvider(configured_model_id="claude-transport-test")

    def _raise(*_args: Any, **_kwargs: Any) -> None:
        raise transport_error

    monkeypatch.setattr(httpx.Client, "post", _raise)

    with pytest.raises(ProviderCallError) as raised:
        provider._post_json(url=provider.endpoint, headers={}, json_body={})

    assert raised.value.retryable is True
    assert type(transport_error).__name__ in str(raised.value)


def test_unsupported_protocol_stays_non_retryable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Retrying a misconfigured endpoint only burns the circuit breaker."""
    monkeypatch.setenv("QRM_EXTERNAL_MODEL_CALLS_ENABLED", "true")
    monkeypatch.setenv("QRM_ALLOWED_MODEL_PROVIDERS", "anthropic")
    monkeypatch.setenv("QRM_ANTHROPIC_API_KEY", "test-provider-key")
    get_settings.cache_clear()
    provider = AnthropicProvider(configured_model_id="claude-protocol-test")

    def _raise(*_args: Any, **_kwargs: Any) -> None:
        raise httpx.UnsupportedProtocol("unsupported protocol")

    monkeypatch.setattr(httpx.Client, "post", _raise)

    with pytest.raises(ProviderCallError) as raised:
        provider._post_json(url=provider.endpoint, headers={}, json_body={})

    assert raised.value.retryable is False
    assert "UnsupportedProtocol" in str(raised.value)


@pytest.mark.parametrize(
    "provider",
    [
        AnthropicProvider(configured_model_id="claude-output-cap-test"),
        MistralProvider(configured_model_id="mistral-output-cap-test"),
    ],
)
def test_structured_provider_output_tokens_are_capped(
    monkeypatch: pytest.MonkeyPatch,
    provider: Any,
) -> None:
    provider_name = provider.provider_name
    monkeypatch.setenv("QRM_EXTERNAL_MODEL_CALLS_ENABLED", "true")
    monkeypatch.setenv("QRM_ALLOWED_MODEL_PROVIDERS", provider_name)
    monkeypatch.setenv(f"QRM_{provider_name.upper()}_API_KEY", "test-provider-key")
    monkeypatch.setenv("QRM_MODEL_PROVIDER_MAX_OUTPUT_TOKENS", "8192")
    get_settings.cache_clear()
    captured: dict[str, Any] = {}

    def fake_post_json(*, json_body: dict[str, Any], **_: Any) -> dict[str, Any]:
        captured.update(json_body)
        if provider_name == "anthropic":
            return {"content": [{"type": "text", "text": '{"value": "ok"}'}]}
        return {"choices": [{"finish_reason": "stop", "message": {"content": '{"value": "ok"}'}}]}

    monkeypatch.setattr(provider, "_post_json", fake_post_json)

    assert provider.run_structured("Return JSON.", {}, SimpleOutput) == {"value": "ok"}
    assert captured["max_tokens"] == 8192


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


def test_default_agents_use_mixed_primary_provider_routing_and_all_critics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QRM_EXTERNAL_MODEL_CALLS_ENABLED", "true")
    monkeypatch.setenv("QRM_ALLOWED_MODEL_PROVIDERS", "mistral,anthropic,openai")
    monkeypatch.setenv("QRM_MISTRAL_MODEL_ID", "mistral-test")
    monkeypatch.setenv("QRM_OPENAI_MODEL_ID", "gpt-test")
    monkeypatch.setenv("QRM_ANTHROPIC_MODEL_ID", "claude-test")
    monkeypatch.setenv("QRM_CRITIC_PROVIDERS", "anthropic,openai,mistral")
    get_settings.cache_clear()

    agents = default_reviewer_agents()
    providers_by_role = {agent.role: agent.provider.provider_name for agent in agents}

    assert providers_by_role == {
        "GMPDataIntegrityReviewer": "mistral",
        "DeviationReviewer": "mistral",
        "CAPAReviewer": "mistral",
        "BatchImpactReviewer": "openai",
        "ValidationAndSterilityReviewer": "anthropic",
        "RegulatoryConsistencyReviewer": "anthropic",
        "ContradictionHunter": "openai",
        "RedTeamCriticAnthropic": "anthropic",
        "RedTeamCriticOpenAI": "openai",
        "RedTeamCriticMistral": "mistral",
    }
    assert len(agents) == len({agent.agent_id for agent in agents})
    assert len(agents) == len({agent.role for agent in agents})


def test_critic_provider_configuration_is_deduplicated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QRM_EXTERNAL_MODEL_CALLS_ENABLED", "true")
    monkeypatch.setenv("QRM_ALLOWED_MODEL_PROVIDERS", "mistral,anthropic,openai")
    monkeypatch.setenv("QRM_MISTRAL_MODEL_ID", "mistral-test")
    monkeypatch.setenv("QRM_OPENAI_MODEL_ID", "gpt-test")
    monkeypatch.setenv("QRM_ANTHROPIC_MODEL_ID", "claude-test")
    monkeypatch.setenv(
        "QRM_CRITIC_PROVIDERS", "anthropic,openai,anthropic,mistral,openai"
    )
    get_settings.cache_clear()

    critics = [
        agent for agent in default_reviewer_agents() if agent.role.startswith("RedTeamCritic")
    ]

    assert [agent.provider.provider_name for agent in critics] == [
        "anthropic",
        "openai",
        "mistral",
    ]
    assert len(critics) == len({agent.agent_id for agent in critics})


def test_reviewer_provider_override_still_routes_primary_roles_to_mistral(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QRM_EXTERNAL_MODEL_CALLS_ENABLED", "true")
    monkeypatch.setenv("QRM_ALLOWED_MODEL_PROVIDERS", "mistral,anthropic,openai")
    monkeypatch.setenv("QRM_MISTRAL_MODEL_ID", "mistral-test")
    monkeypatch.setenv("QRM_OPENAI_MODEL_ID", "gpt-test")
    monkeypatch.setenv("QRM_ANTHROPIC_MODEL_ID", "claude-test")
    monkeypatch.setenv("QRM_REVIEWER_PROVIDER_OVERRIDE", "mistral")
    get_settings.cache_clear()

    primary_agents = [
        agent
        for agent in default_reviewer_agents()
        if not agent.role.startswith("RedTeamCritic")
    ]

    assert {agent.provider.provider_name for agent in primary_agents} == {"mistral"}


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


@pytest.mark.parametrize(
    "text",
    [
        '{"value": "RAW-PROVIDER-PAYLOAD-SECRET",}',
        '```json\n{"value": "RAW-PROVIDER-PAYLOAD-SECRET",}\n```',
        'Model preamble {"value": "RAW-PROVIDER-PAYLOAD-SECRET",} trailing prose',
    ],
)
def test_invalid_provider_text_json_is_sanitized_and_retryable(text: str) -> None:
    provider = ExternalProviderBase(
        provider_name="external-json-test",
        model_name="test-model",
        model_version="v1",
        configured_model_id="test-model",
        external_calls_required=False,
    )

    with pytest.raises(ProviderCallError) as raised:
        provider._parse_json_object_from_text(text)

    assert raised.value.retryable is True
    assert "RAW-PROVIDER-PAYLOAD-SECRET" not in str(raised.value)
    assert raised.value.__cause__ is None


def test_malformed_provider_json_is_retried_then_succeeds_without_payload_leak(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QRM_EXTERNAL_MODEL_CALLS_ENABLED", "true")
    monkeypatch.setenv("QRM_ALLOWED_MODEL_PROVIDERS", "mistral")
    monkeypatch.setenv("QRM_MISTRAL_API_KEY", "test-mistral-key")
    get_settings.cache_clear()
    provider = MistralProvider(
        configured_model_id="mistral-json-retry-test",
        runtime_options=ProviderRuntimeOptions(max_retries=1, retry_deadline_seconds=5),
    )
    responses = iter(
        [
            {
                "choices": [
                    {
                        "message": {
                            "content": (
                                "Preamble {\"value\": "
                                "\"RAW-PROVIDER-PAYLOAD-SECRET\",} postscript"
                            )
                        }
                    }
                ]
            },
            {"choices": [{"message": {"content": '{"value": "recovered"}'}}]},
        ]
    )

    monkeypatch.setattr(provider, "_post_json", lambda **_: next(responses))

    output = provider.run_structured("Return JSON.", {}, SimpleOutput)

    assert output == {"value": "recovered"}
    assert provider.last_run_metadata is not None
    assert provider.last_run_metadata.retry_count == 1


def test_anthropic_schema_failures_do_not_open_the_shared_transport_circuit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QRM_EXTERNAL_MODEL_CALLS_ENABLED", "true")
    monkeypatch.setenv("QRM_ALLOWED_MODEL_PROVIDERS", "anthropic")
    monkeypatch.setenv("QRM_ANTHROPIC_API_KEY", "test-anthropic-key")
    get_settings.cache_clear()
    options = ProviderRuntimeOptions(max_retries=0, circuit_breaker_failure_threshold=3)
    failing_role = AnthropicProvider(
        configured_model_id="claude-schema-isolation-test",
        runtime_options=options,
    )
    succeeding_role = AnthropicProvider(
        configured_model_id="claude-schema-isolation-test",
        runtime_options=options,
    )
    responses = iter(
        [
            {"content": [{"type": "text", "text": '{"unexpected": "shape"}'}]},
            {"content": [{"type": "text", "text": '{"unexpected": "shape"}'}]},
            {"content": [{"type": "text", "text": '{"unexpected": "shape"}'}]},
            {"content": [{"type": "text", "text": '{"value": "valid-next-role"}'}]},
        ]
    )

    def fake_post_json(**_: Any) -> dict[str, Any]:
        return next(responses)

    monkeypatch.setattr(failing_role, "_post_json", fake_post_json)
    monkeypatch.setattr(succeeding_role, "_post_json", fake_post_json)

    for _ in range(3):
        with pytest.raises(ProviderStructuredOutputError):
            failing_role.run_structured("Return JSON.", {}, SimpleOutput)

    assert succeeding_role.run_structured("Return JSON.", {}, SimpleOutput) == {
        "value": "valid-next-role"
    }


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


def test_retries_within_one_call_count_as_a_single_circuit_failure() -> None:
    """Retrying must not consume the budget meant for repeated outages.

    Counting every attempt let one unlucky call trip a threshold of three on its
    own, so enabling retries made the breaker more trigger-happy, not less.
    """
    options = ProviderRuntimeOptions(
        max_retries=2,
        circuit_breaker_failure_threshold=3,
        retry_deadline_seconds=30,
    )
    provider = AlwaysRetryableProvider(
        runtime_options=options,
        provider_name="retry-circuit",
        retry_after_seconds=None,
    )

    with pytest.raises(ProviderCallError):
        provider.run_structured("Return JSON.", {}, SimpleOutput)

    assert provider.calls == 3
    assert not provider._circuit_is_open()


def test_open_circuit_admits_a_probe_after_the_cooldown() -> None:
    """An open breaker must be able to recover without a process restart."""
    options = ProviderRuntimeOptions(
        max_retries=0,
        circuit_breaker_failure_threshold=1,
        circuit_breaker_cooldown_seconds=0.05,
    )
    provider = AlwaysRetryableProvider(runtime_options=options, provider_name="cooldown-test")

    with pytest.raises(ProviderCallError):
        provider.run_structured("Return JSON.", {}, SimpleOutput)
    with pytest.raises(ProviderCircuitOpenError):
        provider.run_structured("Return JSON.", {}, SimpleOutput)

    calls_while_open = provider.calls
    sleep(0.06)

    # Half-open: the probe reaches the provider instead of being rejected.
    with pytest.raises(ProviderCallError):
        provider.run_structured("Return JSON.", {}, SimpleOutput)

    assert provider.calls == calls_while_open + 1


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
        retry_after_seconds: float | None = 30,
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
        # A Retry-After of 30 makes the backoff draw from uniform(0, 30), which
        # against a 30 second deadline abandons the retry loop about half the
        # time. Tests that count attempts must not inherit that coin flip.
        self.retry_after_seconds = retry_after_seconds

    def _run_structured_once(
        self,
        *,
        prompt: str,
        input_schema: dict[str, Any],
        output_schema: type[BaseModel],
    ) -> dict[str, Any]:
        self.calls += 1
        raise ProviderCallError(
            "transient failure",
            retryable=True,
            retry_after_seconds=self.retry_after_seconds,
        )


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
