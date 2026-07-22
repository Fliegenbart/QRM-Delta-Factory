from __future__ import annotations

import re

_IDENTIFIER_BODY_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


class InvalidIdentifierError(ValueError):
    pass


def with_prefix(value: str, prefix: str, *, field_name: str) -> str:
    expected_prefix = f"{prefix}_"
    normalized = value.strip()
    identifier_body = (
        normalized.removeprefix(expected_prefix)
        if normalized.startswith(expected_prefix)
        else normalized
    )

    if not identifier_body:
        raise InvalidIdentifierError(f"{field_name} must not be blank")
    if not _IDENTIFIER_BODY_PATTERN.fullmatch(identifier_body):
        raise InvalidIdentifierError(
            f"{field_name} may only contain letters, numbers, underscores, or hyphens"
        )

    return f"{expected_prefix}{identifier_body}"
