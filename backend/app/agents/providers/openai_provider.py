from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.agents.providers.base import ProviderRuntimeOptions
from app.agents.providers.external_base import ExternalProviderBase
from app.core.config import get_settings

_OPENAI_STRUCTURED_OUTPUT_TOKEN_LIMIT = 8192


class OpenAIProvider(ExternalProviderBase):
    api_key_env_var = "QRM_OPENAI_API_KEY"
    endpoint = "https://api.openai.com/v1/chat/completions"
    #: OpenAI proper rejects the classic field on current models with HTTP 400
    #: ("'max_tokens' is not supported with this model. Use
    #: 'max_completion_tokens' instead"). Shipping max_tokens on 2026-08-22
    #: tripped the circuit breaker on every OpenAI role in production for most
    #: of a day. OpenAI-compatible hosts still speak the classic name.
    max_output_tokens_field = "max_completion_tokens"

    def __init__(
        self,
        *,
        configured_model_id: str = "",
        model_version: str | None = None,
        prompt_version: str = "openai-provider-v0.1",
        runtime_options: ProviderRuntimeOptions | None = None,
    ) -> None:
        super().__init__(
            provider_name="openai",
            model_name="openai",
            model_version=model_version or configured_model_id,
            configured_model_id=configured_model_id,
            prompt_version=prompt_version,
            runtime_options=runtime_options,
            external_calls_required=True,
        )

    def _response_format(self, output_schema: type[BaseModel]) -> dict[str, Any]:
        """How the endpoint is asked for JSON. OpenAI proper takes json_object;
        OpenAI-compatible servers that enforce a schema override this."""
        return {"type": "json_object"}

    def _payload_extras(self) -> dict[str, Any]:
        """Endpoint-specific request fields merged into the payload last."""
        return {}

    def _call_external_structured(
        self,
        *,
        api_key: str,
        prompt: str,
        input_schema: dict[str, Any],
        output_schema: type[BaseModel],
    ) -> dict[str, Any]:
        payload = {
            "model": self.configured_model_id,
            "temperature": 0,
            # The other two adapters have always bounded their output; this one
            # did not, so model_provider_max_output_tokens quietly did not apply
            # to OpenAI at all. That was survivable while OpenAI carried two of
            # seven reviewer roles and no verification work. It is not now.
            self.max_output_tokens_field: self._bounded_max_output_tokens(
                get_settings().model_provider_max_output_tokens,
                provider_max_tokens=_OPENAI_STRUCTURED_OUTPUT_TOKEN_LIMIT,
            ),
            "response_format": self._response_format(output_schema),
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a conservative GMP review model. Use only the provided "
                        "inputs and return one valid JSON object matching the schema."
                    ),
                },
                {
                    "role": "user",
                    "content": self._json_user_content(
                        prompt=prompt,
                        input_schema=input_schema,
                        output_schema=output_schema,
                    ),
                },
            ],
        }
        payload.update(self._payload_extras())
        response = self._post_json(
            url=self.endpoint,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json_body=payload,
        )
        # A cut-off completion is not a shorter answer, it is a dead role: the
        # JSON is unclosed and the reviewer produces nothing. Detect it from
        # finish_reason and raise the shared sanitized, retryable error instead
        # of letting the parser fail on a half-written payload -- otherwise the
        # operator sees a JSON error and looks for a prompt bug that isn't there.
        choice = response["choices"][0]
        if isinstance(choice, dict) and choice.get("finish_reason") in {
            "length",
            "max_tokens",
        }:
            raise self._truncated_output_error()
        content = choice["message"]["content"]
        output = self._parse_json_object_from_text(str(content))
        usage = response.get("usage")
        if isinstance(usage, dict):
            output["token_usage"] = {
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
            }
        return output
