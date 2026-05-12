from __future__ import annotations

from typing import Any
from urllib.parse import quote

from pydantic import BaseModel

from app.agents.providers.base import ProviderRuntimeOptions
from app.agents.providers.external_base import ExternalProviderBase


class GeminiProvider(ExternalProviderBase):
    api_key_env_var = "QRM_GEMINI_API_KEY"

    def __init__(
        self,
        *,
        configured_model_id: str = "",
        model_version: str | None = None,
        prompt_version: str = "gemini-provider-v0.1",
        runtime_options: ProviderRuntimeOptions | None = None,
    ) -> None:
        super().__init__(
            provider_name="gemini",
            model_name="gemini",
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
        model_id = quote(self.configured_model_id, safe="")
        endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model_id}:generateContent"
        )
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": self._json_user_content(
                                prompt=(
                                    "You are a conservative GMP review model. "
                                    "Return only valid JSON. "
                                    f"{prompt}"
                                ),
                                input_schema=input_schema,
                                output_schema=output_schema,
                            )
                        }
                    ],
                }
            ],
            "generationConfig": {
                "temperature": 0,
                "responseMimeType": "application/json",
            },
        }
        response = self._post_json(
            url=endpoint,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": api_key,
            },
            json_body=payload,
        )
        output = self._parse_json_object_from_text(_gemini_text(response))
        usage = response.get("usageMetadata")
        if isinstance(usage, dict):
            output["token_usage"] = {
                "input_tokens": usage.get("promptTokenCount", 0),
                "output_tokens": usage.get("candidatesTokenCount", 0),
                "total_tokens": usage.get("totalTokenCount", 0),
            }
        return output


def _gemini_text(response: dict[str, Any]) -> str:
    candidates = response.get("candidates", [])
    if not isinstance(candidates, list) or not candidates:
        return ""
    first_candidate = candidates[0]
    if not isinstance(first_candidate, dict):
        return ""
    content = first_candidate.get("content", {})
    if not isinstance(content, dict):
        return ""
    parts = content.get("parts", [])
    if not isinstance(parts, list):
        return ""
    texts = [str(part.get("text", "")) for part in parts if isinstance(part, dict)]
    return "\n".join(text for text in texts if text)
