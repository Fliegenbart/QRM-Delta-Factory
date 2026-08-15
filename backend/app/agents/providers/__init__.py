from app.agents.providers.anthropic_provider import AnthropicProvider
from app.agents.providers.base import (
    BaseModelProvider,
    ExternalModelCallsDisabledError,
    ModelProviderNotAllowedError,
    ProviderCallError,
    ProviderCircuitOpenError,
    ProviderConfigurationError,
    ProviderRunMetadata,
    ProviderRuntimeOptions,
    ProviderStructuredOutputError,
)
from app.agents.providers.external_base import ExternalProviderBase
from app.agents.providers.gemini_provider import GeminiProvider
from app.agents.providers.mock_provider import MockProvider
from app.agents.providers.openai_provider import OpenAIProvider


class ExternalModelProviderStub(ExternalProviderBase):
    api_key_env_var = "QRM_EXTERNAL_MODEL_API_KEY"

    def __init__(
        self,
        *,
        provider_name: str,
        model_name: str,
        model_version: str,
    ) -> None:
        super().__init__(
            provider_name=provider_name,
            model_name=model_name,
            model_version=model_version,
            configured_model_id=model_name,
            prompt_version="external-provider-stub-v0.1",
            external_calls_required=True,
        )

__all__ = [
    "AnthropicProvider",
    "BaseModelProvider",
    "ExternalModelCallsDisabledError",
    "ExternalModelProviderStub",
    "GeminiProvider",
    "MockProvider",
    "ModelProviderNotAllowedError",
    "OpenAIProvider",
    "ProviderCallError",
    "ProviderCircuitOpenError",
    "ProviderConfigurationError",
    "ProviderRunMetadata",
    "ProviderRuntimeOptions",
    "ProviderStructuredOutputError",
]
