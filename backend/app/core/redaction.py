from __future__ import annotations

import json
import re
from hashlib import sha256
from typing import Any

SENSITIVE_METADATA_KEYS = {
    "api_key",
    "authorization",
    "content",
    "document_text",
    "file_content",
    "full_text",
    "password",
    "raw_text",
    "raw_text_quote",
    "secret",
    "token",
}

PLACEHOLDER_PATTERNS = [
    re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b"),
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
]


def redact_personal_placeholders(text: str) -> str:
    redacted = text
    for pattern in PLACEHOLDER_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def redact_log_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in metadata.items():
        if _is_sensitive_key(key):
            redacted[key] = _redacted_value(value)
        else:
            redacted[key] = _redact_value(value)
    return redacted


def _redact_value(value: Any) -> Any:
    if isinstance(value, dict):
        return redact_log_metadata(value)
    if isinstance(value, list):
        return [_redact_value(item) for item in value]
    if isinstance(value, str):
        if len(value) > 256:
            return _redacted_value(value)
        return redact_personal_placeholders(value)
    return value


def _redacted_value(value: Any) -> dict[str, Any]:
    text = json.dumps(value, sort_keys=True, default=str)
    return {
        "redacted": True,
        "sha256": sha256(text.encode()).hexdigest(),
        "length": len(text),
    }


def _is_sensitive_key(key: str) -> bool:
    normalized = key.lower()
    return any(sensitive in normalized for sensitive in SENSITIVE_METADATA_KEYS)
