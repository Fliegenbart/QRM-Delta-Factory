from __future__ import annotations

import json
import os
import re
from threading import Thread
from typing import Any

import httpx
from pydantic import BaseModel

from app.agents.providers.base import (
    BaseModelProvider,
    ProviderCallError,
    ProviderConfigurationError,
)

_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 529}
_MAX_RETRY_AFTER_SECONDS = 30.0


_SAFE_ERROR_KIND = re.compile(r"^[a-z0-9_.-]{1,64}$")

#: Body substrings that identify an exhausted quota rather than a bad request.
#: Checked against a bounded prefix of the body only when the error type alone
#: is ambiguous (Anthropic reports its monthly usage limit as a plain
#: invalid_request_error with HTTP 400).
_USAGE_LIMIT_MARKERS = ("usage limit", "credit balance", "quota")


def _error_kind(response: httpx.Response) -> str | None:
    """A short, safe classifier for a provider error body, or None."""
    try:
        payload = response.json()
    except ValueError:
        return None
    if not isinstance(payload, dict):
        return None
    error = payload.get("error")
    if not isinstance(error, dict):
        return None
    kind = error.get("type") or error.get("code")
    message = error.get("message")
    if isinstance(message, str) and any(
        marker in message[:300].lower() for marker in _USAGE_LIMIT_MARKERS
    ):
        return "usage_limit_reached"
    if isinstance(kind, str) and _SAFE_ERROR_KIND.match(kind):
        return kind
    return None


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
                response = self._post_with_hard_deadline(
                    client, url=url, headers=headers, json_body=json_body
                )
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            retry_after_seconds = _capped_retry_after(exc.response.headers.get("retry-after"))
            # The body's error *type* is a controlled vocabulary and safe to
            # surface; the message text is not (it can quote the payload).
            # Without it, "HTTP 400" hid an exhausted monthly usage limit
            # behind the same three words as a malformed request -- an
            # outage that reads like a bug costs the diagnosis an extra hop.
            error_kind = _error_kind(exc.response)
            suffix = f" ({error_kind})" if error_kind else ""
            raise ProviderCallError(
                f"{self.provider_name} provider call failed with HTTP {status_code}{suffix}",
                retryable=status_code in _RETRYABLE_STATUS_CODES,
                retry_after_seconds=retry_after_seconds,
            ) from exc
        except httpx.TimeoutException as exc:
            raise ProviderCallError(
                f"{self.provider_name} provider call timed out",
                retryable=True,
            ) from exc
        except httpx.HTTPError as exc:
            # Connection resets and protocol faults are transient, but the default
            # ProviderCallError is non-retryable, so these were the one transport
            # failure the retry policy never covered. Name the fault class too:
            # a bare "call failed" is what made the Anthropic critic's six
            # failures undiagnosable. The class name is safe to surface, the
            # exception message is not -- httpx can embed provider payload in it.
            raise ProviderCallError(
                f"{self.provider_name} provider call failed ({type(exc).__name__})",
                retryable=isinstance(
                    exc,
                    httpx.NetworkError | httpx.ProtocolError | httpx.ProxyError,
                ),
            ) from exc
        except ValueError as exc:
            raise ProviderCallError(
                f"{self.provider_name} provider returned non-JSON response"
            ) from exc
        if not isinstance(payload, dict):
            raise ProviderCallError(
                f"{self.provider_name} provider returned invalid JSON payload"
            )
        return payload

    def _post_with_hard_deadline(
        self,
        client: httpx.Client,
        *,
        url: str,
        headers: dict[str, str],
        json_body: dict[str, Any],
    ) -> httpx.Response:
        """POST with a wall-clock cap that a trickling server cannot reset.

        httpx's read timeout is per received chunk: a gateway that keeps the
        connection open and dribbles bytes resets it forever. One such
        connection held a blind benchmark run on a single requirement for
        eleven hours -- 0% CPU, one ESTABLISHED socket, no timeout ever
        firing. The request runs on a helper thread; if it outlives the cap,
        the client is closed (which aborts the socket) and the call fails as
        retryable, exactly like an ordinary timeout.
        """
        hard_deadline = self.runtime_options.timeout_seconds * 1.25 + 15.0
        outcome: dict[str, Any] = {}

        def _do_post() -> None:
            try:
                outcome["response"] = client.post(url, headers=headers, json=json_body)
            except BaseException as exc:  # noqa: BLE001 - re-raised on the caller's thread
                outcome["error"] = exc

        worker = Thread(target=_do_post, daemon=True, name=f"{self.provider_name}-post")
        worker.start()
        worker.join(hard_deadline)
        if worker.is_alive():
            try:
                client.close()
            except Exception:  # noqa: BLE001 - closing is best effort
                pass
            worker.join(5.0)
            raise ProviderCallError(
                f"{self.provider_name} provider call exceeded the hard deadline "
                f"of {hard_deadline:.0f}s",
                retryable=True,
            )
        if "error" in outcome:
            raise outcome["error"]
        return outcome["response"]

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
            direct_json_parse_failed = True
        else:
            direct_json_parse_failed = False
        if direct_json_parse_failed:
            payload = self._parse_json_from_markdown_or_substring(stripped)
        if not isinstance(payload, dict):
            raise ProviderCallError(
                f"{self.provider_name} provider returned JSON that is not an object"
            )
        return payload

    def _parse_json_from_markdown_or_substring(self, text: str) -> Any:
        fenced_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL)
        if fenced_match:
            candidate = fenced_match.group(1)
        else:
            first_brace = text.find("{")
            last_brace = text.rfind("}")
            if first_brace == -1 or last_brace == -1 or first_brace >= last_brace:
                raise self._invalid_json_text_error()
            candidate = text[first_brace : last_brace + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # Provider text is untrusted. Never surface the decoder exception because
            # it retains the complete raw provider payload in its ``doc`` attribute.
            raise self._invalid_json_text_error() from None

    def _invalid_json_text_error(self) -> ProviderCallError:
        return ProviderCallError(
            f"{self.provider_name} provider returned invalid JSON",
            retryable=True,
        )

    def _truncated_output_error(self) -> ProviderCallError:
        return ProviderCallError(
            f"{self.provider_name} provider output was truncated",
            retryable=True,
        )

    def _bounded_max_output_tokens(
        self,
        configured_max_tokens: int,
        *,
        provider_max_tokens: int,
    ) -> int:
        return min(configured_max_tokens, provider_max_tokens)

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


def _capped_retry_after(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return min(max(float(value), 0.0), _MAX_RETRY_AFTER_SECONDS)
    except ValueError:
        return None
