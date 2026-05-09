from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel

from app.agents.providers.base import BaseModelProvider, ProviderRuntimeOptions

MockOutputFactory = Callable[[str, dict[str, Any], type[BaseModel]], dict[str, Any]]


class MockProvider(BaseModelProvider):
    def __init__(
        self,
        *,
        model_name: str = "mock-reviewer",
        model_version: str = "0.1.0",
        configured_model_id: str = "mock-local",
        prompt_version: str = "mock-provider-v0.1",
        runtime_options: ProviderRuntimeOptions | None = None,
        structured_output: dict[str, Any] | None = None,
        output_factory: MockOutputFactory | None = None,
        delay_seconds: float = 0.0,
    ) -> None:
        super().__init__(
            provider_name="mock",
            model_name=model_name,
            model_version=model_version,
            configured_model_id=configured_model_id,
            prompt_version=prompt_version,
            runtime_options=runtime_options,
            external_calls_required=False,
        )
        self.structured_output = structured_output or {
            "findings": [],
            "coverage_summary": "MockProvider generated no findings.",
        }
        self.output_factory = output_factory
        self.delay_seconds = delay_seconds

    def _run_structured_once(
        self,
        *,
        prompt: str,
        input_schema: dict[str, Any],
        output_schema: type[BaseModel],
    ) -> dict[str, Any]:
        if self.delay_seconds:
            time.sleep(self.delay_seconds)
        if self.output_factory is not None:
            return self.output_factory(prompt, input_schema, output_schema)
        return dict(self.structured_output)
