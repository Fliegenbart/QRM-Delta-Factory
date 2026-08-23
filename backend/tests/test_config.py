from pytest import MonkeyPatch

from app.core.config import Settings


def test_config_loads_safe_defaults() -> None:
    settings = Settings()

    assert settings.app_name == "Pharma AI Risk Orchestration Backend"
    assert settings.environment == "local"
    assert settings.allow_model_live_internet is False
    assert settings.max_upload_bytes == 20 * 1024 * 1024
    assert "postgresql+psycopg://" in settings.database_url
    assert settings.redis_url.startswith("redis://")


def test_config_accepts_environment_override(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("QRM_ENVIRONMENT", "test")
    monkeypatch.setenv("QRM_APP_VERSION", "9.9.9-test")

    settings = Settings()

    assert settings.environment == "test"
    assert settings.app_version == "9.9.9-test"


def test_config_accepts_upload_size_override(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("QRM_MAX_UPLOAD_BYTES", "1024")

    settings = Settings()

    assert settings.max_upload_bytes == 1024


def test_model_stack_preset_fills_only_unset_fields(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("QRM_MODEL_STACK", "cascade")
    monkeypatch.setenv("QRM_CRITIC_PROVIDERS", "")

    settings = Settings()

    assert settings.reviewer_provider_override == "hetzner"
    assert settings.requirement_review_assessor_provider == "hetzner"
    assert settings.requirement_review_entailment_provider == "anthropic"
    assert settings.requirement_review_assessor_mode == "narrow"
    assert settings.allowed_model_providers == "hetzner,anthropic,mock"
    # Explicitly set, so the preset must not touch it.
    assert settings.critic_providers == ""


def test_model_stack_cloud_keeps_the_per_role_defaults() -> None:
    settings = Settings()

    assert settings.model_stack == "cloud"
    assert settings.reviewer_provider_override == ""
    assert settings.requirement_review_assessor_provider == "anthropic"
    assert settings.requirement_review_entailment_provider == "openai"
    assert settings.requirement_review_assessor_mode == "grouped"


def test_model_stack_rejects_unknown_preset(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("QRM_MODEL_STACK", "onprem")

    try:
        Settings()
    except ValueError as exc:
        assert "onprem" in str(exc)
    else:
        raise AssertionError("unknown stack accepted")


def test_hetzner_endpoint_is_configurable(monkeypatch: MonkeyPatch) -> None:
    from app.agents.providers.hetzner_provider import HetznerProvider

    monkeypatch.setenv("QRM_HETZNER_ENDPOINT", "http://gpu-01.intern:8000/v1/chat/completions")

    settings = Settings()
    provider = HetznerProvider(configured_model_id="Qwen3.8-27B", endpoint=settings.hetzner_endpoint)

    assert provider.endpoint == "http://gpu-01.intern:8000/v1/chat/completions"
    assert HetznerProvider.endpoint.startswith("https://inference.hetzner.com")
