from __future__ import annotations

from app.agents.providers.base import ProviderRuntimeOptions
from app.agents.providers.external_base import ExternalProviderBase


class AnthropicProvider(ExternalProviderBase):
    api_key_env_var = "QRM_ANTHROPIC_API_KEY"

    def __init__(
        self,
        *,
        configured_model_id: str = "",
        model_version: str | None = None,
        prompt_version: str = "anthropic-provider-v0.1",
        runtime_options: ProviderRuntimeOptions | None = None,
    ) -> None:
        super().__init__(
            provider_name="anthropic",
            model_name="anthropic",
            model_version=model_version or configured_model_id,
            configured_model_id=configured_model_id,
            prompt_version=prompt_version,
            runtime_options=runtime_options,
            external_calls_required=True,
        )
