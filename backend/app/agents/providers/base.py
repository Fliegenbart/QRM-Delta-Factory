from __future__ import annotations

import ast
import json
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from hashlib import sha256
from threading import Lock, Semaphore
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from app.core.config import get_settings


class ExternalModelCallsDisabledError(Exception):
    pass


class ModelProviderNotAllowedError(Exception):
    pass


class ProviderConfigurationError(Exception):
    pass


class ProviderCircuitOpenError(Exception):
    pass


class ProviderStructuredOutputError(Exception):
    pass


class _StructuredPayloadNormalizationError(ValueError):
    pass


class ProviderCallError(Exception):
    def __init__(
        self,
        message: str,
        *,
        retryable: bool = False,
        retry_after_seconds: float | None = None,
    ) -> None:
        super().__init__(message)
        self.retryable = retryable
        self.retry_after_seconds = retry_after_seconds


@dataclass(frozen=True)
class ProviderRuntimeOptions:
    timeout_seconds: float = 30.0
    max_retries: int = 0
    retry_deadline_seconds: float = 120.0
    max_concurrent_calls: int = 2
    circuit_breaker_failure_threshold: int = 3

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than 0")
        if self.max_retries < 0:
            raise ValueError("max_retries must be greater than or equal to 0")
        if self.retry_deadline_seconds <= 0:
            raise ValueError("retry_deadline_seconds must be greater than 0")
        if self.max_concurrent_calls <= 0:
            raise ValueError("max_concurrent_calls must be greater than 0")
        if self.circuit_breaker_failure_threshold <= 0:
            raise ValueError("circuit_breaker_failure_threshold must be greater than 0")


class ProviderTokenUsage(BaseModel):
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)


class ProviderRunMetadata(BaseModel):
    provider: str
    model_name: str
    model_version: str
    configured_model_id: str
    prompt_version: str
    request_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    response_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    latency_ms: int = Field(ge=0)
    retry_count: int = Field(default=0, ge=0)
    retry_delay_ms: int = Field(default=0, ge=0)
    token_usage: ProviderTokenUsage | None = None


class BaseModelProvider(ABC):
    provider_name: str
    model_name: str
    model_version: str
    configured_model_id: str
    prompt_version: str
    external_calls_required: bool
    _circuit_lock = Lock()
    _provider_failure_counts: dict[tuple[str, str], int] = {}
    _concurrency_lock = Lock()
    _provider_semaphores: dict[tuple[str, str, int], Semaphore] = {}

    def __init__(
        self,
        *,
        provider_name: str,
        model_name: str,
        model_version: str,
        configured_model_id: str,
        prompt_version: str = "provider-adapter-v0.1",
        runtime_options: ProviderRuntimeOptions | None = None,
        external_calls_required: bool,
    ) -> None:
        if not configured_model_id:
            raise ProviderConfigurationError("configured_model_id is required; no fallback allowed")
        self.provider_name = provider_name
        self.model_name = model_name
        self.model_version = model_version
        self.configured_model_id = configured_model_id
        self.prompt_version = prompt_version
        self.runtime_options = runtime_options or ProviderRuntimeOptions()
        self.external_calls_required = external_calls_required
        self.last_run_metadata: ProviderRunMetadata | None = None

    def run_structured(
        self,
        prompt: str,
        input_schema: dict[str, Any],
        output_schema: type[BaseModel],
    ) -> dict[str, Any]:
        self._ensure_provider_allowed()
        self._ensure_circuit_closed()
        request_hash = _hash_json(
            {
                "provider": self.provider_name,
                "model_name": self.model_name,
                "configured_model_id": self.configured_model_id,
                "prompt_version": self.prompt_version,
                "prompt_hash": sha256(prompt.encode()).hexdigest(),
                "input_schema": input_schema,
                "output_schema": output_schema.__name__,
            }
        )
        last_error: Exception | None = None
        retry_count = 0
        retry_delay_ms = 0
        with self._provider_semaphore():
            # Queue time is controlled by the shared semaphore. The retry deadline
            # applies to the active provider call, not to waiting behind other
            # reviewers that use the same provider and model.
            started = time.perf_counter()
            deadline = time.monotonic() + self.runtime_options.retry_deadline_seconds
            for attempt in range(self.runtime_options.max_retries + 1):
                if time.monotonic() >= deadline:
                    last_error = ProviderCallError(
                        f"Provider retry deadline exceeded for {self.provider_name}"
                    )
                    break
                try:
                    raw_output = self._run_structured_once(
                        prompt=prompt,
                        input_schema=input_schema,
                        output_schema=output_schema,
                    )
                    token_usage = self._extract_token_usage(raw_output)
                    validation_payload = dict(raw_output)
                    validation_payload.pop("token_usage", None)
                    validation_payload = _normalize_structured_payload(
                        validation_payload,
                        output_schema=output_schema,
                    )
                    parsed = output_schema.model_validate(validation_payload)
                    structured_output = parsed.model_dump(mode="json")
                    response_hash = _hash_json(structured_output)
                    self.last_run_metadata = ProviderRunMetadata(
                        provider=self.provider_name,
                        model_name=self.model_name,
                        model_version=self.model_version,
                        configured_model_id=self.configured_model_id,
                        prompt_version=self.prompt_version,
                        request_hash=request_hash,
                        response_hash=response_hash,
                        latency_ms=int((time.perf_counter() - started) * 1000),
                        retry_count=retry_count,
                        retry_delay_ms=retry_delay_ms,
                        token_usage=token_usage,
                    )
                    self._clear_failures()
                    return structured_output
                except (ValidationError, _StructuredPayloadNormalizationError) as exc:
                    raise ProviderStructuredOutputError(str(exc)) from exc
                except ProviderStructuredOutputError:
                    # Schema/model-output failures are not provider transport failures.
                    # The review orchestrator owns their bounded retry policy, while the
                    # shared circuit remains reserved for provider availability faults.
                    raise
                except ProviderCallError as exc:
                    last_error = exc
                    self._record_failure()
                    if (
                        not exc.retryable
                        or attempt >= self.runtime_options.max_retries
                        or self._circuit_is_open()
                    ):
                        break
                    delay = self._retry_delay_seconds(exc, attempt=attempt, deadline=deadline)
                    if delay is None:
                        last_error = ProviderCallError(
                            f"Provider retry deadline exceeded for {self.provider_name}"
                        )
                        break
                    time.sleep(delay)
                    retry_count += 1
                    retry_delay_ms += int(delay * 1000)
                except Exception as exc:
                    last_error = exc
                    self._record_failure()
                    break
        if last_error is not None:
            raise last_error
        raise ProviderCallError("Provider call failed without an exception")

    @abstractmethod
    def _run_structured_once(
        self,
        *,
        prompt: str,
        input_schema: dict[str, Any],
        output_schema: type[BaseModel],
    ) -> dict[str, Any]:
        ...

    def _extract_token_usage(self, raw_output: dict[str, Any]) -> ProviderTokenUsage | None:
        usage = raw_output.get("token_usage")
        if not isinstance(usage, dict):
            return None
        total_tokens = _int_or_zero(usage.get("total_tokens"))
        input_tokens = _int_or_zero(usage.get("input_tokens", usage.get("prompt_tokens")))
        output_tokens = _int_or_zero(usage.get("output_tokens", usage.get("completion_tokens")))
        if not total_tokens:
            total_tokens = input_tokens + output_tokens
        return ProviderTokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
        )

    def _ensure_provider_allowed(self) -> None:
        if not self.external_calls_required:
            return
        settings = get_settings()
        if not settings.external_model_calls_enabled:
            raise ExternalModelCallsDisabledError(
                "External model calls are disabled by QRM_EXTERNAL_MODEL_CALLS_ENABLED"
            )
        if self.provider_name not in settings.allowed_model_provider_set():
            raise ModelProviderNotAllowedError(
                f"Provider {self.provider_name} is not in QRM_ALLOWED_MODEL_PROVIDERS"
            )

    def _ensure_circuit_closed(self) -> None:
        if self._circuit_is_open():
            raise ProviderCircuitOpenError(f"Circuit breaker is open for {self.provider_name}")

    def _record_failure(self) -> None:
        with self._circuit_lock:
            key = self._provider_key()
            self._provider_failure_counts[key] = self._provider_failure_counts.get(key, 0) + 1

    def _clear_failures(self) -> None:
        with self._circuit_lock:
            self._provider_failure_counts.pop(self._provider_key(), None)

    def _circuit_is_open(self) -> bool:
        with self._circuit_lock:
            return (
                self._provider_failure_counts.get(self._provider_key(), 0)
                >= self.runtime_options.circuit_breaker_failure_threshold
            )

    def _provider_key(self) -> tuple[str, str]:
        return self.provider_name, self.configured_model_id

    def _provider_semaphore(self) -> Semaphore:
        key = (*self._provider_key(), self.runtime_options.max_concurrent_calls)
        with self._concurrency_lock:
            semaphore = self._provider_semaphores.get(key)
            if semaphore is None:
                semaphore = Semaphore(self.runtime_options.max_concurrent_calls)
                self._provider_semaphores[key] = semaphore
            return semaphore

    def _retry_delay_seconds(
        self,
        error: ProviderCallError,
        *,
        attempt: int,
        deadline: float,
    ) -> float | None:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return None
        retry_after = error.retry_after_seconds
        capped_retry_after = min(retry_after, 30.0) if retry_after is not None else None
        base_delay = capped_retry_after if capped_retry_after is not None else min(2**attempt, 10.0)
        delay = random.uniform(0, base_delay) if base_delay > 0 else 0.0
        return delay if delay < remaining else None


def _hash_json(payload: dict[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


def _normalize_structured_payload(
    payload: dict[str, Any],
    *,
    output_schema: type[BaseModel],
) -> dict[str, Any]:
    if output_schema.__name__ != "ReviewerAgentOutput":
        return payload

    normalized = dict(payload)
    findings = _normalize_reviewer_findings(normalized.get("findings"))

    normalized_findings: list[dict[str, Any]] = []
    for finding in findings:
        normalized_finding = dict(finding)
        evidence_items = normalized_finding.get("evidence_items")
        if isinstance(evidence_items, list):
            normalized_finding["evidence_items"] = [
                _normalize_evidence_item(item) for item in evidence_items
            ]
        normalized_findings.append(normalized_finding)

    normalized["findings"] = normalized_findings
    return normalized


def _parse_reviewer_findings(value: str) -> list[dict[str, Any]]:
    normalized_value = _unwrap_pure_json_fence(value)
    try:
        parsed = json.loads(normalized_value)
    except json.JSONDecodeError:
        try:
            parsed = ast.literal_eval(normalized_value)
        except (SyntaxError, ValueError) as exc:
            raise _StructuredPayloadNormalizationError(
                "findings must be a valid list of objects"
            ) from exc

    return _normalize_reviewer_findings(parsed)


_RISK_FINDING_CORE_KEYS = frozenset(
    {
        "finding_id",
        "document_set_id",
        "risk_category",
        "severity",
        "likelihood",
        "detectability",
        "risk_statement",
        "evidence_items",
        "requirement_references",
        "model_provider",
        "model_name",
        "model_version",
        "prompt_version",
        "evidence_support",
        "recommended_action",
        "auto_close_allowed",
        "status",
    }
)


def _normalize_reviewer_findings(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, str):
        return _parse_reviewer_findings(value)
    if isinstance(value, list):
        if not all(isinstance(finding, dict) for finding in value):
            raise _StructuredPayloadNormalizationError("findings entries must be objects")
        return [dict(finding) for finding in value]
    if isinstance(value, dict):
        if _has_risk_finding_core_shape(value):
            return [dict(value)]
        nested_findings = value.get("findings")
        if (
            set(value) == {"findings"}
            and isinstance(nested_findings, list)
            and all(_has_risk_finding_core_shape(finding) for finding in nested_findings)
        ):
            return [dict(finding) for finding in nested_findings]
        if value and all(_has_risk_finding_core_shape(candidate) for candidate in value.values()):
            return [dict(candidate) for candidate in value.values()]
    raise _StructuredPayloadNormalizationError("findings must be a list")


def _has_risk_finding_core_shape(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and value.keys() >= _RISK_FINDING_CORE_KEYS
        and isinstance(value["risk_statement"], str)
        and isinstance(value["evidence_items"], list)
        and isinstance(value["requirement_references"], list)
    )


def _unwrap_pure_json_fence(value: str) -> str:
    trimmed = value.strip()
    if not trimmed.startswith("```"):
        return trimmed

    lines = trimmed.splitlines()
    if (
        len(lines) < 3
        or lines[0].strip().lower() not in {"```", "```json"}
        or lines[-1].strip() != "```"
        or any(line.strip().startswith("```") for line in lines[1:-1])
    ):
        raise _StructuredPayloadNormalizationError("findings must be a valid list of objects")
    return "\n".join(lines[1:-1]).strip()


def _normalize_evidence_item(item: Any) -> Any:
    if not isinstance(item, dict):
        return item

    normalized = dict(item)
    quote_hash = normalized.get("quote_hash")
    quote = normalized.get("quote")
    if isinstance(quote, str) and not _is_sha256_hash(quote_hash):
        normalized["quote_hash"] = sha256(quote.encode()).hexdigest()
    return normalized


def _is_sha256_hash(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _int_or_zero(value: Any) -> int:
    if value is None:
        return 0
    return int(value)
