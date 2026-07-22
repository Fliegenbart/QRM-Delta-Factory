from __future__ import annotations

import pytest

from app.services.identifiers import InvalidIdentifierError, with_prefix


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (" qrm_author ", "user_qrm_author"),
        (" user_qrm-author ", "user_qrm-author"),
    ],
)
def test_with_prefix_trims_and_preserves_a_valid_prefix(value: str, expected: str) -> None:
    assert with_prefix(value, "user", field_name="uploaded_by") == expected


@pytest.mark.parametrize("value", ["", "   ", "qrm/author", "qrm author"])
def test_with_prefix_rejects_blank_or_invalid_identifier_bodies(value: str) -> None:
    with pytest.raises(InvalidIdentifierError):
        with_prefix(value, "user", field_name="uploaded_by")
