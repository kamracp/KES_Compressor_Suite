from decimal import Decimal

from app.domain.compression.validation import (
    ValidationStatus,
    check_discharge_temperature,
    check_driver_adequacy,
    check_stage_compression_ratio,
    summarize_validation_checks,
)


def test_stage_ratio_pass() -> None:
    result = check_stage_compression_ratio(Decimal("1.50"))

    assert result.status == ValidationStatus.PASS
    assert result.code == "STAGE_RATIO_OK"


def test_stage_ratio_warn_when_too_low() -> None:
    result = check_stage_compression_ratio(Decimal("1.10"))

    assert result.status == ValidationStatus.WARN
    assert result.code == "STAGE_RATIO_LOW"


def test_stage_ratio_fail_when_too_high() -> None:
    result = check_stage_compression_ratio(Decimal("4.50"))

    assert result.status == ValidationStatus.FAIL
    assert result.code == "STAGE_RATIO_HIGH"


def test_discharge_temperature_pass() -> None:
    result = check_discharge_temperature(Decimal("400"))

    assert result.status == ValidationStatus.PASS
    assert result.code == "DISCHARGE_TEMP_OK"


def test_discharge_temperature_fail() -> None:
    result = check_discharge_temperature(Decimal("500"))

    assert result.status == ValidationStatus.FAIL
    assert result.code == "DISCHARGE_TEMP_HIGH"


def test_driver_adequacy_pass() -> None:
    result = check_driver_adequacy(True)

    assert result.status == ValidationStatus.PASS
    assert result.code == "DRIVER_OK"


def test_driver_adequacy_fail() -> None:
    result = check_driver_adequacy(False)

    assert result.status == ValidationStatus.FAIL
    assert result.code == "DRIVER_UNDERSIZED"


def test_summary_returns_fail_when_any_check_fails() -> None:
    checks = (
        check_stage_compression_ratio(Decimal("1.50")),
        check_discharge_temperature(Decimal("500")),
        check_driver_adequacy(True),
    )

    result = summarize_validation_checks(checks)

    assert result == ValidationStatus.FAIL


def test_summary_returns_warn_when_no_fail_but_warn_exists() -> None:
    checks = (
        check_stage_compression_ratio(Decimal("1.10")),
        check_discharge_temperature(Decimal("400")),
        check_driver_adequacy(True),
    )

    result = summarize_validation_checks(checks)

    assert result == ValidationStatus.WARN


def test_summary_returns_pass_when_all_checks_pass() -> None:
    checks = (
        check_stage_compression_ratio(Decimal("1.50")),
        check_discharge_temperature(Decimal("400")),
        check_driver_adequacy(True),
    )

    result = summarize_validation_checks(checks)

    assert result == ValidationStatus.PASS
