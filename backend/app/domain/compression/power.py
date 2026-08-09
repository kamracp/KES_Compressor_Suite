from dataclasses import dataclass
from decimal import Decimal


class InvalidPowerInputError(ValueError):
    """Raised when compressor power inputs are invalid."""


@dataclass(frozen=True, slots=True)
class CompressionPowerResult:
    """Compressor power calculation result."""

    specific_isentropic_work_kj_per_kg: Decimal
    isentropic_power_kw: Decimal
    shaft_power_kw: Decimal
    required_driver_power_kw: Decimal


def calculate_compression_power(
    mass_flow_kg_per_s: Decimal,
    inlet_temperature_k: Decimal,
    stage_compression_ratio: Decimal,
    isentropic_exponent: Decimal,
    specific_heat_cp_kj_per_kg_k: Decimal,
    number_of_stages: int,
    isentropic_efficiency: Decimal,
    mechanical_efficiency: Decimal,
    driver_margin_fraction: Decimal = Decimal("0.10"),
) -> CompressionPowerResult:
    """Calculate compressor isentropic, shaft, and driver power."""

    if mass_flow_kg_per_s <= 0:
        raise InvalidPowerInputError("Mass flow must be greater than zero.")

    if inlet_temperature_k <= 0:
        raise InvalidPowerInputError("Inlet absolute temperature must be greater than zero.")

    if stage_compression_ratio <= 1:
        raise InvalidPowerInputError("Stage compression ratio must be greater than one.")

    if isentropic_exponent <= 1:
        raise InvalidPowerInputError("Isentropic exponent must be greater than one.")

    if specific_heat_cp_kj_per_kg_k <= 0:
        raise InvalidPowerInputError("Specific heat capacity must be greater than zero.")

    if number_of_stages < 1:
        raise InvalidPowerInputError("Number of compression stages must be at least one.")

    if isentropic_efficiency <= 0 or isentropic_efficiency > 1:
        raise InvalidPowerInputError(
            "Isentropic efficiency must be greater than zero and not exceed one."
        )

    if mechanical_efficiency <= 0 or mechanical_efficiency > 1:
        raise InvalidPowerInputError(
            "Mechanical efficiency must be greater than zero and not exceed one."
        )

    if driver_margin_fraction < 0:
        raise InvalidPowerInputError("Driver margin fraction cannot be negative.")

    exponent = float((isentropic_exponent - Decimal("1")) / isentropic_exponent)

    stage_work = (
        specific_heat_cp_kj_per_kg_k
        * inlet_temperature_k
        * Decimal(str(float(stage_compression_ratio) ** exponent - 1.0))
    )

    total_specific_work = stage_work * Decimal(number_of_stages)

    isentropic_power_kw = mass_flow_kg_per_s * total_specific_work

    shaft_power_kw = isentropic_power_kw / isentropic_efficiency / mechanical_efficiency

    required_driver_power_kw = shaft_power_kw * (Decimal("1") + driver_margin_fraction)

    return CompressionPowerResult(
        specific_isentropic_work_kj_per_kg=total_specific_work,
        isentropic_power_kw=isentropic_power_kw,
        shaft_power_kw=shaft_power_kw,
        required_driver_power_kw=required_driver_power_kw,
    )
