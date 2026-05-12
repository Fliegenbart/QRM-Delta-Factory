from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.agents.providers.base import ProviderRuntimeOptions
from app.agents.providers.external_base import ExternalProviderBase


class AnthropicProvider(ExternalProviderBase):
    api_key_env_var = "QRM_ANTHROPIC_API_KEY"
    endpoint = "https://api.anthropic.com/v1/messages"

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
            "max_tokens": 4096,
            "temperature": 0,
            "system": (
                "You are a conservative GMP review model. Use only the provided inputs. "
                "Return one valid JSON object matching the schema, with no markdown."
            ),
            "messages": [
                {
                    "role": "user",
                    "content": self._json_user_content(
                        prompt=prompt,
                        input_schema=input_schema,
                        output_schema=output_schema,
                    ),
                }
            ],
        }
        response = self._post_json(
            url=self.endpoint,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json_body=payload,
        )
        output = self._parse_json_object_from_text(_anthropic_text(response))
        usage = response.get("usage")
        if isinstance(usage, dict):
            input_tokens = int(usage.get("input_tokens", 0) or 0)
            output_tokens = int(usage.get("output_tokens", 0) or 0)
            output["token_usage"] = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
            }
        return output


def _anthropic_text(response: dict[str, Any]) -> str:
    content_blocks = response.get("content", [])
    if not isinstance(content_blocks, list):
        return ""
    texts = [
        str(block.get("text", ""))
        for block in content_blocks
        if isinstance(block, dict) and block.get("type") == "text"
    ]
    return "\n".join(text for text in texts if text)
