"""Pytest bootstrap that isolates database-backed tests from development data."""

import os

import pytest
from sqlalchemy.engine import URL, make_url

from app.core.config import get_settings

TEST_DATABASE_URL_ENV = "TEST_DATABASE_URL"
TEST_DATABASE_SUFFIX = "_test"


def _derive_test_database_url(database_url: str) -> URL:
    """Return a dedicated test URL derived from the configured application URL."""

    url = make_url(database_url)
    database_name = url.database

    if not database_name:
        raise pytest.UsageError("The configured database URL must include a database name.")

    if database_name.lower().endswith(TEST_DATABASE_SUFFIX):
        return url

    return url.set(database=f"{database_name}{TEST_DATABASE_SUFFIX}")


def _validate_test_database_url(test_database_url: URL) -> None:
    """Reject any pytest database URL that is not explicitly test-only."""

    database_name = test_database_url.database

    if not database_name or not database_name.lower().endswith(TEST_DATABASE_SUFFIX):
        raise pytest.UsageError(
            "Refusing to run database-backed tests against a non-test database. "
            f"Database names must end with '{TEST_DATABASE_SUFFIX}'."
        )


def _configure_test_database() -> URL:
    """Set the isolated database URL before application modules are collected."""

    configured_database_url = get_settings().database_url
    explicit_test_database_url = os.getenv(TEST_DATABASE_URL_ENV)

    test_database_url = (
        make_url(explicit_test_database_url)
        if explicit_test_database_url
        else _derive_test_database_url(configured_database_url)
    )

    _validate_test_database_url(test_database_url)

    os.environ["DATABASE_URL"] = test_database_url.render_as_string(hide_password=False)
    os.environ["ENVIRONMENT"] = "test"
    get_settings.cache_clear()

    return test_database_url


TEST_DATABASE_URL = _configure_test_database()


def pytest_report_header() -> str:
    """Expose the isolated database name in pytest's session header."""

    return f"isolated test database: {TEST_DATABASE_URL.database}"
