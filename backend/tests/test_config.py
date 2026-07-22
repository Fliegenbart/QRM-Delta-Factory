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
