from dataclasses import dataclass
from decimal import Decimal


class InvalidTemperatureInputError(ValueError):
    """Raised when compression-temperature inputs are invalid."""


@dataclass(frozen=True, slots=True)
class CompressionTemperatureResult:
    """Compression discharge-temperature calculation result."""

    inlet_temperature_k: Decimal
    isentropic_discharge_temperature_k: Decimal
    actual_discharge_temperature_k: Decimal


def calculate_discharge_temperature(
    inlet_temperature_k: Decimal,
    stage_compression_ratio: Decimal,
    isentropic_exponent: Decimal,
    isentropic_efficiency: Decimal,
) -> CompressionTemperatureResult:
    """Calculate isentropic and actual discharge temperatures."""

    if inlet_temperature_k <= 0:
        raise InvalidTemperatureInputError("Inlet absolute temperature must be greater than zero.")

    if stage_compression_ratio <= 1:
        raise InvalidTemperatureInputError("Stage compression ratio must be greater than one.")

    if isentropic_exponent <= 1:
        raise InvalidTemperatureInputError("Isentropic exponent must be greater than one.")

    if isentropic_efficiency <= 0 or isentropic_efficiency > 1:
        raise InvalidTemperatureInputError(
            "Isentropic efficiency must be greater than zero and not exceed one."
        )

    exponent = float((isentropic_exponent - Decimal("1")) / isentropic_exponent)

    isentropic_discharge_temperature = Decimal(
        str(float(inlet_temperature_k) * float(stage_compression_ratio) ** exponent)
    )

    actual_discharge_temperature = (
        inlet_temperature_k
        + (isentropic_discharge_temperature - inlet_temperature_k) / isentropic_efficiency
    )

    return CompressionTemperatureResult(
        inlet_temperature_k=inlet_temperature_k,
        isentropic_discharge_temperature_k=isentropic_discharge_temperature,
        actual_discharge_temperature_k=actual_discharge_temperature,
    )
