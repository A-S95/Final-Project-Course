import pytest
from pydantic import ValidationError

from app.core.config import Settings

_DB = "postgresql+psycopg://u:p@localhost:5432/db"
_GOOD_SECRET = "a" * 48  # 48 caracteres, sem marcadores de placeholder


def test_secret_key_shorter_than_32_chars_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(database_url=_DB, secret_key="too-short", environment="development")


def test_placeholder_secret_key_is_rejected_in_production() -> None:
    with pytest.raises(ValidationError):
        Settings(
            database_url=_DB,
            secret_key="dev-only-change-me-before-any-real-deployment-0000",
            environment="production",
        )


def test_placeholder_secret_key_is_allowed_in_development() -> None:
    settings = Settings(
        database_url=_DB,
        secret_key="dev-only-change-me-before-any-real-deployment-0000",
        environment="development",
    )
    assert settings.is_production is False


def test_real_secret_key_works_in_production() -> None:
    settings = Settings(database_url=_DB, secret_key=_GOOD_SECRET, environment="production")
    assert settings.is_production is True


def test_cors_origins_defaults_are_not_a_wildcard() -> None:
    settings = Settings(database_url=_DB, secret_key=_GOOD_SECRET)
    assert "*" not in settings.cors_origins
