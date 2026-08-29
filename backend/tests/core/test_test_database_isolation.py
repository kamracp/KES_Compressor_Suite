import pytest
from sqlalchemy.engine import make_url

from tests import conftest as test_bootstrap


def test_derives_test_database_url_from_development_url() -> None:
    development_url = "postgresql+psycopg://postgres:secret@localhost:5432/kes_compressor"

    test_url = test_bootstrap._derive_test_database_url(development_url)

    assert test_url.database == "kes_compressor_test"
    assert test_url.drivername == "postgresql+psycopg"
    assert test_url.host == "localhost"
    assert test_url.port == 5432
    assert test_url.username == "postgres"
    assert test_url.password == "secret"


def test_preserves_an_explicit_test_database_url() -> None:
    explicit_test_url = make_url(
        "postgresql+psycopg://postgres:secret@localhost:5432/custom_suite_test"
    )

    derived_url = test_bootstrap._derive_test_database_url(
        explicit_test_url.render_as_string(hide_password=False)
    )

    assert derived_url == explicit_test_url
    test_bootstrap._validate_test_database_url(derived_url)


def test_rejects_non_test_database_url() -> None:
    unsafe_url = make_url("postgresql+psycopg://postgres:secret@localhost:5432/kes_compressor")

    with pytest.raises(
        pytest.UsageError,
        match="Refusing to run database-backed tests",
    ):
        test_bootstrap._validate_test_database_url(unsafe_url)
