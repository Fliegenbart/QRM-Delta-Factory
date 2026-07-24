from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from app.agents.providers.base import ProviderCallError, ProviderRuntimeOptions
from app.agents.providers.external_base import ExternalProviderBase
from app.core.config import get_settings

_MISTRAL_STRUCTURED_OUTPUT_TOKEN_LIMIT = 8192


class MistralProvider(ExternalProviderBase):
    api_key_env_var = "QRM_MISTRAL_API_KEY"
    endpoint = "https://api.mistral.ai/v1/chat/completions"

    def __init__(
        self,
        *,
        configured_model_id: str = "",
        model_version: str | None = None,
        prompt_version: str = "mistral-provider-v0.1",
        runtime_options: ProviderRuntimeOptions | None = None,
    ) -> None:
        super().__init__(
            provider_name="mistral",
            model_name="mistral",
            model_version=model_version or configured_model_id,
            configured_model_id=configured_model_id,
            prompt_version=prompt_version,
            runtime_options=runtime_options,
            external_calls_required=True,
        )

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
            "max_tokens": self._bounded_max_output_tokens(
                get_settings().model_provider_max_output_tokens,
                provider_max_tokens=_MISTRAL_STRUCTURED_OUTPUT_TOKEN_LIMIT,
            ),
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": output_schema.__name__.lower(),
                    "schema": output_schema.model_json_schema(),
                },
            },
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
                    # The output schema is already supplied through Mistral's
                    # json_schema response format. Sending it again here adds a
                    # large duplicate payload without improving enforcement.
                    "content": json.dumps(
                        {
                            "instructions": prompt,
                            "inputs": input_schema,
                            "hard_output_rule": (
                                "Return exactly one JSON object that follows the "
                                "provided response schema. Do not return markdown, "
                                "prose, or keys outside the schema."
                            ),
                        },
                        sort_keys=True,
                        default=str,
                    ),
                },
            ],
        }
        response = self._post_json(
            url=self.endpoint,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json_body=payload,
        )
        choices = response.get("choices")
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
            raise ProviderCallError("mistral provider returned invalid completion payload")
        choice = choices[0]
        if choice.get("finish_reason") in {"length", "max_tokens"}:
            raise self._truncated_output_error()
        message = choice.get("message")
        if not isinstance(message, dict):
            raise ProviderCallError("mistral provider returned invalid completion payload")
        content = message.get("content")
        if not isinstance(content, str):
            raise ProviderCallError("mistral provider returned invalid completion payload")
        output = self._parse_json_object_from_text(content)
        usage = response.get("usage")
        if isinstance(usage, dict):
            output["token_usage"] = {
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
            }
        return output
