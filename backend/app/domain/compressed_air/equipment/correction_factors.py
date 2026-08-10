from dataclasses import dataclass
from decimal import Decimal

STANDARD_ATMOSPHERIC_PRESSURE_BAR_A = Decimal("1.01325")
STANDARD_REFERENCE_TEMPERATURE_C = Decimal("20")
KELVIN_OFFSET = Decimal("273.15")


class InvalidCorrectionFactorInputError(ValueError):
    """Raised when equipment correction-factor inputs are invalid."""


@dataclass(frozen=True, slots=True)
class EquipmentCorrectionInput:
    """Operating and reference conditions for equipment correction."""

    actual_inlet_pressure_bar_a: Decimal
    actual_inlet_temperature_c: Decimal

    reference_inlet_pressure_bar_a: Decimal = STANDARD_ATMOSPHERIC_PRESSURE_BAR_A
    reference_inlet_temperature_c: Decimal = STANDARD_REFERENCE_TEMPERATURE_C


@dataclass(frozen=True, slots=True)
class EquipmentCorrectionResult:
    """Vendor-neutral inlet-condition correction result."""

    pressure_factor: Decimal
    temperature_factor: Decimal
    combined_capacity_factor: Decimal

    actual_inlet_pressure_bar_a: Decimal
    actual_inlet_temperature_c: Decimal

    reference_inlet_pressure_bar_a: Decimal
    reference_inlet_temperature_c: Decimal


def calculate_inlet_condition_correction(
    inputs: EquipmentCorrectionInput,
) -> EquipmentCorrectionResult:
    """Calculate ideal-gas inlet-condition capacity correction."""

    _validate_inputs(inputs)

    actual_temperature_k = inputs.actual_inlet_temperature_c + KELVIN_OFFSET
    reference_temperature_k = inputs.reference_inlet_temperature_c + KELVIN_OFFSET

    pressure_factor = inputs.actual_inlet_pressure_bar_a / inputs.reference_inlet_pressure_bar_a

    temperature_factor = reference_temperature_k / actual_temperature_k

    combined_capacity_factor = pressure_factor * temperature_factor

    return EquipmentCorrectionResult(
        pressure_factor=pressure_factor,
        temperature_factor=temperature_factor,
        combined_capacity_factor=combined_capacity_factor,
        actual_inlet_pressure_bar_a=inputs.actual_inlet_pressure_bar_a,
        actual_inlet_temperature_c=inputs.actual_inlet_temperature_c,
        reference_inlet_pressure_bar_a=(inputs.reference_inlet_pressure_bar_a),
        reference_inlet_temperature_c=(inputs.reference_inlet_temperature_c),
    )


def apply_capacity_correction(
    *,
    reference_capacity_nm3_per_hr: Decimal,
    correction: EquipmentCorrectionResult,
) -> Decimal:
    """Apply inlet-condition correction to reference capacity."""

    if reference_capacity_nm3_per_hr <= 0:
        raise InvalidCorrectionFactorInputError("Reference capacity must be greater than zero.")

    return reference_capacity_nm3_per_hr * correction.combined_capacity_factor


def calculate_site_pressure_bar_a(
    *,
    altitude_m: Decimal,
) -> Decimal:
    """Estimate atmospheric pressure from site altitude.

    Uses the standard-atmosphere tropospheric approximation and is intended
    for preliminary engineering correction, not certified performance testing.
    """

    if altitude_m < Decimal("-500"):
        raise InvalidCorrectionFactorInputError(
            "Altitude is outside the supported preliminary-engineering range."
        )

    if altitude_m > Decimal("11000"):
        raise InvalidCorrectionFactorInputError(
            "Altitude is outside the supported preliminary-engineering range."
        )

    altitude = float(altitude_m)

    pressure_ratio = (1.0 - (2.25577e-5 * altitude)) ** 5.25588

    return STANDARD_ATMOSPHERIC_PRESSURE_BAR_A * Decimal(str(pressure_ratio))


def _validate_inputs(
    inputs: EquipmentCorrectionInput,
) -> None:
    if inputs.actual_inlet_pressure_bar_a <= 0:
        raise InvalidCorrectionFactorInputError(
            "Actual inlet absolute pressure must be greater than zero."
        )

    if inputs.reference_inlet_pressure_bar_a <= 0:
        raise InvalidCorrectionFactorInputError(
            "Reference inlet absolute pressure must be greater than zero."
        )

    if inputs.actual_inlet_temperature_c + KELVIN_OFFSET <= 0:
        raise InvalidCorrectionFactorInputError(
            "Actual inlet temperature must be above absolute zero."
        )

    if inputs.reference_inlet_temperature_c + KELVIN_OFFSET <= 0:
        raise InvalidCorrectionFactorInputError(
            "Reference inlet temperature must be above absolute zero."
        )
