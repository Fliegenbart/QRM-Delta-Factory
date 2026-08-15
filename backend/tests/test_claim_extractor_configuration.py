from app.core.config import get_settings
from app.services.claim_ledger import MockClaimExtractor, default_claim_extractor


def test_claim_extraction_defaults_to_deterministic_source_indexing(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("QRM_EXTERNAL_MODEL_CALLS_ENABLED", "true")
    monkeypatch.setenv("QRM_LLM_CLAIM_EXTRACTION_ENABLED", "false")
    monkeypatch.setenv("QRM_REVIEWER_PROVIDER_OVERRIDE", "anthropic")
    monkeypatch.setenv("QRM_ALLOWED_MODEL_PROVIDERS", "anthropic,mock")
    monkeypatch.setenv("QRM_ANTHROPIC_MODEL_ID", "claude-sonnet-4-6")
    get_settings.cache_clear()

    try:
        assert isinstance(default_claim_extractor(), MockClaimExtractor)
    finally:
        get_settings.cache_clear()
