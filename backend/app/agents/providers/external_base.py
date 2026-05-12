from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx
from pydantic import BaseModel

from app.agents.providers.base import (
    BaseModelProvider,
    ProviderCallError,
    ProviderConfigurationError,
)


class ExternalProviderBase(BaseModelProvider):
    api_key_env_var: str

    def _load_api_key(self) -> str:
        api_key = os.environ.get(self.api_key_env_var, "")
        if not api_key:
            raise ProviderConfigurationError(f"{self.api_key_env_var} is not configured")
        return api_key

    def _post_json(
        self,
        *,
        url: str,
        headers: dict[str, str],
        json_body: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            with httpx.Client(timeout=self.runtime_options.timeout_seconds) as client:
                response = client.post(url, headers=headers, json=json_body)
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            raise ProviderCallError(
                f"{self.provider_name} provider call failed with HTTP {status_code}"
            ) from exc
        except httpx.HTTPError as exc:
            raise ProviderCallError(f"{self.provider_name} provider call failed") from exc
        except ValueError as exc:
            raise ProviderCallError(
                f"{self.provider_name} provider returned non-JSON response"
            ) from exc
        if not isinstance(payload, dict):
            raise ProviderCallError(f"{self.provider_name} provider returned invalid JSON payload")
        return payload

    def _json_user_content(
        self,
        *,
        prompt: str,
        input_schema: dict[str, Any],
        output_schema: type[BaseModel],
    ) -> str:
        return json.dumps(
            {
                "instructions": prompt,
                "inputs": input_schema,
                "output_schema": output_schema.model_json_schema(),
                "hard_output_rule": (
                    "Return exactly one JSON object matching output_schema. "
                    "Do not return markdown, prose, or keys outside the schema."
                ),
            },
            sort_keys=True,
            default=str,
        )

    def _parse_json_object_from_text(self, text: str) -> dict[str, Any]:
        stripped = text.strip()
        if not stripped:
            raise ProviderCallError(f"{self.provider_name} provider returned empty text")
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            payload = self._parse_json_from_markdown_or_substring(stripped)
        if not isinstance(payload, dict):
            raise ProviderCallError(
                f"{self.provider_name} provider returned JSON that is not an object"
            )
        return payload

    def _parse_json_from_markdown_or_substring(self, text: str) -> Any:
        fenced_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL)
        if fenced_match:
            return json.loads(fenced_match.group(1))
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace == -1 or last_brace == -1 or first_brace >= last_brace:
            raise ProviderCallError(
                f"{self.provider_name} provider did not return parseable JSON"
            )
        return json.loads(text[first_brace : last_brace + 1])

    def _run_structured_once(
        self,
        *,
        prompt: str,
        input_schema: dict[str, Any],
        output_schema: type[BaseModel],
    ) -> dict[str, Any]:
        api_key = self._load_api_key()
        return self._call_external_structured(
            api_key=api_key,
            prompt=prompt,
            input_schema=input_schema,
            output_schema=output_schema,
        )

    def _call_external_structured(
        self,
        *,
        api_key: str,
        prompt: str,
        input_schema: dict[str, Any],
        output_schema: type[BaseModel],
    ) -> dict[str, Any]:
        raise NotImplementedError
