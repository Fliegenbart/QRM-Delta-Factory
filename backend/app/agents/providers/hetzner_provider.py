from __future__ import annotations

from dataclasses import replace
from typing import Any

from pydantic import BaseModel

from app.agents.providers.base import ProviderRuntimeOptions
from app.agents.providers.external_base import ExternalProviderBase
from app.agents.providers.openai_provider import OpenAIProvider


class HetznerProvider(OpenAIProvider):
    """Qwen on the Hetzner Inference API -- the EU-residency option.

    The endpoint is OpenAI-compatible, so the request and response plumbing is
    inherited wholesale. Two things are specific to this host and were both
    learned the hard way on 2026-08-22:

    * Qwen3.8 is a reasoning model. Without ``enable_thinking: false`` it spends
      the entire output budget in ``reasoning_content`` and returns an empty
      ``content`` with ``finish_reason: length`` -- a dead role on every call.
      ``/no_think`` in the prompt no longer works on this model version; the
      chat-template flag is the only switch.
    * It produces 13-23 tokens/s. At the 240s production timeout that caps a
      usable answer at ~4,800 tokens, and extraction passes on dense documents
      have needed more. :func:`hetzner_runtime_options` widens the per-call
      timeout for this provider alone.
    """

    api_key_env_var = "QRM_HETZNER_API_KEY"
    endpoint = "https://inference.hetzner.com/api/v1/chat/completions"
    max_output_tokens_field = "max_tokens"

    def __init__(
        self,
        *,
        configured_model_id: str = "",
        model_version: str | None = None,
        prompt_version: str = "hetzner-provider-v0.1",
        runtime_options: ProviderRuntimeOptions | None = None,
        endpoint: str | None = None,
    ) -> None:
        # The class default is Hetzner's hosted endpoint; a deployment on the
        # customer's own hardware points this at its vLLM server instead and
        # nothing else about the provider changes.
        if endpoint:
            self.endpoint = endpoint
        ExternalProviderBase.__init__(
            self,
            provider_name="hetzner",
            model_name="hetzner",
            model_version=model_version or configured_model_id,
            configured_model_id=configured_model_id,
            prompt_version=prompt_version,
            runtime_options=runtime_options,
            external_calls_required=True,
        )

    def _response_format(self, output_schema: type[BaseModel]) -> dict[str, Any]:
        # vLLM-style servers enforce the schema at decode time, which is worth
        # more than a json_object hint: the probe returned valid, schema-exact
        # JSON on every call with strict mode on.
        return {
            "type": "json_schema",
            "json_schema": {
                "name": output_schema.__name__.lower(),
                "schema": output_schema.model_json_schema(),
                "strict": True,
            },
        }

    def _payload_extras(self) -> dict[str, Any]:
        return {"chat_template_kwargs": {"enable_thinking": False}}


def hetzner_runtime_options(
    base: ProviderRuntimeOptions, *, timeout_seconds: float
) -> ProviderRuntimeOptions:
    """The shared runtime options with a timeout this slow host can meet.

    The retry deadline is widened with it: a deadline shorter than two attempts
    means a slow first attempt can never be retried, which is exactly the
    failure the 600s production deadline was raised to prevent.
    """
    return replace(
        base,
        timeout_seconds=timeout_seconds,
        retry_deadline_seconds=max(base.retry_deadline_seconds, 2.5 * timeout_seconds),
    )
