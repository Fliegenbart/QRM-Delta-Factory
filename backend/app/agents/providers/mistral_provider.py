from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.agents.providers.base import ProviderRuntimeOptions
from app.agents.providers.external_base import ExternalProviderBase


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
            "response_format": {"type": "json_object"},
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
        response = self._post_json(
            url=self.endpoint,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json_body=payload,
        )
        content = response["choices"][0]["message"]["content"]
        output = self._parse_json_object_from_text(str(content))
        usage = response.get("usage")
        if isinstance(usage, dict):
            output["token_usage"] = {
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
            }
        return output
