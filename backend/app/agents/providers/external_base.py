from __future__ import annotations

import os
from typing import Any

from pydantic import BaseModel

from app.agents.providers.base import BaseModelProvider, ProviderConfigurationError


class ExternalProviderBase(BaseModelProvider):
    api_key_env_var: str

    def _load_api_key(self) -> str:
        api_key = os.environ.get(self.api_key_env_var, "")
        if not api_key:
            raise ProviderConfigurationError(f"{self.api_key_env_var} is not configured")
        return api_key

    def _run_structured_once(
        self,
        *,
        prompt: str,
        input_schema: dict[str, Any],
        output_schema: type[BaseModel],
    ) -> dict[str, Any]:
        self._load_api_key()
        raise NotImplementedError(
            f"{self.provider_name} adapter is configured but real network calls "
            "are intentionally not implemented in the MVP"
        )
