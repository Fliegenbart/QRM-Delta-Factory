from __future__ import annotations

from hashlib import sha256
from typing import Any

import pytest
from pydantic import BaseModel

from app.agents.providers.mock_provider import MockProvider
from app.schemas.domain import ClaimType, DocumentChunk
from app.services.claim_ledger import (
    ClaimLedgerValidationError,
    LLMClaimExtractor,
    _locate_verbatim_quote,
    _safe_claim_type,
)

CHUNK_TEXT = (
    "Abweichungsbericht DEV-2026-891. Die Abweichung wird als Minor eingestuft. "
    "Geprüft durch: Dr. Anna Klar (Qualitätssicherung) – Digitale Signatur am 14.12.2026."
)


def _chunk() -> DocumentChunk:
    return DocumentChunk(
        chunk_id="chunk_test_p1",
        document_id="doc_test",
        page_start=1,
        page_end=1,
        text=CHUNK_TEXT,
        token_count=len(CHUNK_TEXT.split()),
        extraction_confidence=0.95,
        bbox=None,
        source_hash=sha256(CHUNK_TEXT.encode()).hexdigest(),
    )


def _provider_with(claims: list[dict[str, Any]]) -> MockProvider:
    def factory(
        prompt: str,
        input_schema: dict[str, Any],
        output_schema: type[BaseModel],
    ) -> dict[str, Any]:
        return {"claims": claims, "coverage_summary": "test"}

    return MockProvider(output_factory=factory)


def _draft(quote: str, claim_type: str = "date_or_deadline") -> dict[str, Any]:
    return {
        "claim_type": claim_type,
        "normalized_subject": "qa_signature",
        "normalized_predicate": "signed_on",
        "normalized_object": "2026-12-14",
        "exact_quote": quote,
        "confidence": 0.9,
    }


def test_extractor_keeps_verbatim_quotes() -> None:
    extractor = LLMClaimExtractor(
        provider=_provider_with([_draft("Digitale Signatur am 14.12.2026")])
    )
    claims = extractor.extract_claims("ds_test", [_chunk()], [])
    assert len(claims) == 1
    assert claims[0].raw_text_quote in CHUNK_TEXT
    assert claims[0].claim_type == ClaimType.DATE_OR_DEADLINE


def test_extractor_repairs_whitespace_variants() -> None:
    extractor = LLMClaimExtractor(
        provider=_provider_with([_draft("Digitale  Signatur   am 14.12.2026")])
    )
    claims = extractor.extract_claims("ds_test", [_chunk()], [])
    assert len(claims) == 1
    assert claims[0].raw_text_quote in CHUNK_TEXT


def test_extractor_drops_hallucinated_quotes() -> None:
    extractor = LLMClaimExtractor(
        provider=_provider_with(
            [
                _draft("Dieser Satz steht nirgendwo im Dokument"),
                _draft("Die Abweichung wird als Minor eingestuft"),
            ]
        )
    )
    claims = extractor.extract_claims("ds_test", [_chunk()], [])
    assert len(claims) == 1
    assert claims[0].raw_text_quote == "Die Abweichung wird als Minor eingestuft"


def test_unknown_claim_type_falls_back() -> None:
    assert _safe_claim_type("signature_anomaly") == ClaimType.DEVIATION_DESCRIPTION
    assert _safe_claim_type("QA_APPROVAL") == ClaimType.QA_APPROVAL


def test_locate_verbatim_quote_case_insensitive_fallback() -> None:
    located = _locate_verbatim_quote("die abweichung wird als minor eingestuft", CHUNK_TEXT)
    assert located == "Die Abweichung wird als Minor eingestuft"


def test_extractor_raises_when_all_chunks_fail() -> None:
    class FailingProvider(MockProvider):
        def _run_structured_once(
            self,
            *,
            prompt: str,
            input_schema: dict[str, Any],
            output_schema: type[BaseModel],
        ) -> dict[str, Any]:
            raise RuntimeError("simulated provider outage")

    extractor = LLMClaimExtractor(provider=FailingProvider())
    with pytest.raises(ClaimLedgerValidationError):
        extractor.extract_claims("ds_test", [_chunk()], [])
