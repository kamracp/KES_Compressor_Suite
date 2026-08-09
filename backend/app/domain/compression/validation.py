from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class ValidationStatus(StrEnum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


@dataclass(frozen=True, slots=True)
class ValidationCheck:
    """Represents one engineering validation check."""

    code: str
    description: str
    status: ValidationStatus
    actual_value: Decimal | bool | str | None
    limit_description: str


def check_stage_compression_ratio(
    stage_ratio: Decimal,
    minimum_ratio: Decimal = Decimal("1.2"),
    maximum_ratio: Decimal = Decimal("4.0"),
) -> ValidationCheck:
    """Validate stage compression ratio against engineering limits."""

    if stage_ratio < minimum_ratio:
        return ValidationCheck(
            code="STAGE_RATIO_LOW",
            description="Stage compression ratio is below the recommended range.",
            status=ValidationStatus.WARN,
            actual_value=stage_ratio,
            limit_description=f">= {minimum_ratio}",
        )

    if stage_ratio > maximum_ratio:
        return ValidationCheck(
            code="STAGE_RATIO_HIGH",
            description="Stage compression ratio exceeds the allowable range.",
            status=ValidationStatus.FAIL,
            actual_value=stage_ratio,
            limit_description=f"<= {maximum_ratio}",
        )

    return ValidationCheck(
        code="STAGE_RATIO_OK",
        description="Stage compression ratio is within the recommended range.",
        status=ValidationStatus.PASS,
        actual_value=stage_ratio,
        limit_description=f"{minimum_ratio} to {maximum_ratio}",
    )


def check_discharge_temperature(
    temperature_k: Decimal,
    maximum_temperature_k: Decimal = Decimal("473.15"),
) -> ValidationCheck:
    """Validate compressor discharge temperature."""

    if temperature_k > maximum_temperature_k:
        return ValidationCheck(
            code="DISCHARGE_TEMP_HIGH",
            description="Discharge temperature exceeds the allowable limit.",
            status=ValidationStatus.FAIL,
            actual_value=temperature_k,
            limit_description=f"<= {maximum_temperature_k} K",
        )

    return ValidationCheck(
        code="DISCHARGE_TEMP_OK",
        description="Discharge temperature is within the allowable limit.",
        status=ValidationStatus.PASS,
        actual_value=temperature_k,
        limit_description=f"<= {maximum_temperature_k} K",
    )


def check_driver_adequacy(
    driver_is_adequate: bool,
) -> ValidationCheck:
    """Validate whether the selected compressor driver is adequately sized."""

    if driver_is_adequate:
        return ValidationCheck(
            code="DRIVER_OK",
            description="Selected driver rating is adequate.",
            status=ValidationStatus.PASS,
            actual_value=True,
            limit_description="Selected driver >= required driver",
        )

    return ValidationCheck(
        code="DRIVER_UNDERSIZED",
        description="Selected driver rating is below the required power.",
        status=ValidationStatus.FAIL,
        actual_value=False,
        limit_description="Selected driver >= required driver",
    )


def summarize_validation_checks(
    checks: tuple[ValidationCheck, ...],
) -> ValidationStatus:
    """Return the overall validation status."""

    if any(check.status == ValidationStatus.FAIL for check in checks):
        return ValidationStatus.FAIL

    if any(check.status == ValidationStatus.WARN for check in checks):
        return ValidationStatus.WARN

    return ValidationStatus.PASS
