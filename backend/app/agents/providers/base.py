from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from hashlib import sha256
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


class ProviderCallError(Exception):
    pass


@dataclass(frozen=True)
class ProviderRuntimeOptions:
    timeout_seconds: float = 30.0
    max_retries: int = 0
    circuit_breaker_failure_threshold: int = 3

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than 0")
        if self.max_retries < 0:
            raise ValueError("max_retries must be greater than or equal to 0")
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
    token_usage: ProviderTokenUsage | None = None


class BaseModelProvider(ABC):
    provider_name: str
    model_name: str
    model_version: str
    configured_model_id: str
    prompt_version: str
    external_calls_required: bool

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
        self._failure_count = 0

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
        started = time.perf_counter()
        last_error: Exception | None = None
        attempt_prompt = prompt
        for attempt in range(self.runtime_options.max_retries + 1):
            try:
                raw_output = self._run_structured_once(
                    prompt=attempt_prompt,
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
                _validate_reviewer_requirement_references(
                    validation_payload,
                    input_schema=input_schema,
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
                    token_usage=token_usage,
                )
                self._failure_count = 0
                return structured_output
            except (ValidationError, ProviderStructuredOutputError) as exc:
                self._record_failure()
                if attempt < self.runtime_options.max_retries:
                    last_error = ProviderStructuredOutputError(str(exc))
                    attempt_prompt = _repair_prompt_for_structured_output(
                        prompt=prompt,
                        validation_error=str(exc),
                    )
                    continue
                raise ProviderStructuredOutputError(str(exc)) from exc
            except Exception as exc:
                last_error = exc
                self._record_failure()
                if self._failure_count >= self.runtime_options.circuit_breaker_failure_threshold:
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
        if self._failure_count >= self.runtime_options.circuit_breaker_failure_threshold:
            raise ProviderCircuitOpenError(f"Circuit breaker is open for {self.provider_name}")

    def _record_failure(self) -> None:
        self._failure_count += 1


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
    findings = normalized.get("findings")
    if not isinstance(findings, list):
        return normalized

    normalized_findings: list[Any] = []
    for finding in findings:
        if not isinstance(finding, dict):
            normalized_findings.append(finding)
            continue

        normalized_finding = dict(finding)
        evidence_items = normalized_finding.get("evidence_items")
        if isinstance(evidence_items, list):
            normalized_finding["evidence_items"] = [
                _normalize_evidence_item(item) for item in evidence_items
            ]
        normalized_findings.append(normalized_finding)

    normalized["findings"] = normalized_findings
    return normalized


def _normalize_evidence_item(item: Any) -> Any:
    if not isinstance(item, dict):
        return item

    normalized = dict(item)
    quote_hash = normalized.get("quote_hash")
    quote = normalized.get("quote")
    if isinstance(quote, str) and not _is_sha256_hash(quote_hash):
        normalized["quote_hash"] = sha256(quote.encode()).hexdigest()
    support_type = normalized.get("support_type")
    if isinstance(support_type, str) and support_type.strip().lower() in {
        "strong",
        "partial",
        "weak",
    }:
        normalized["support_type"] = "contextual"
    return normalized


def _validate_reviewer_requirement_references(
    payload: dict[str, Any],
    *,
    input_schema: dict[str, Any],
    output_schema: type[BaseModel],
) -> None:
    if output_schema.__name__ != "ReviewerAgentOutput":
        return

    supplied_requirements = input_schema.get("requirements")
    if not isinstance(supplied_requirements, list):
        return
    allowed_requirement_ids = {
        requirement.get("requirement_id")
        for requirement in supplied_requirements
        if isinstance(requirement, dict)
        and isinstance(requirement.get("requirement_id"), str)
    }
    if not allowed_requirement_ids:
        return

    findings = payload.get("findings")
    if not isinstance(findings, list):
        return
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            continue
        references = finding.get("requirement_references")
        if not isinstance(references, list) or not references:
            raise ProviderStructuredOutputError(
                f"findings.{index}.requirement_references must contain at least one "
                "requirement_id copied exactly from the supplied requirements"
            )
        unknown_references = [
            reference
            for reference in references
            if not isinstance(reference, str) or reference not in allowed_requirement_ids
        ]
        if unknown_references:
            raise ProviderStructuredOutputError(
                f"findings.{index}.requirement_references contains unknown IDs: "
                f"{', '.join(map(str, unknown_references))}"
            )


def _repair_prompt_for_structured_output(*, prompt: str, validation_error: str) -> str:
    return (
        f"{prompt}\n\n"
        "REPAIR REQUIRED: Your previous JSON failed schema validation. Return a new "
        "complete JSON object only. For every finding, copy at least one "
        "requirement_id exactly from the supplied requirements. Each evidence_item "
        "support_type must be exactly one of: supports, contradicts, contextual. "
        "Use strong, partial, weak, or none only for evidence_support, never for "
        f"evidence_item.support_type. Validation error: {validation_error}"
    )


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
