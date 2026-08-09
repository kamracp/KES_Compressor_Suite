from dataclasses import dataclass
from decimal import Decimal


class InvalidReceiverSizingInputError(ValueError):
    """Raised when compressed-air receiver sizing inputs are invalid."""


ATMOSPHERIC_PRESSURE_BAR = Decimal("1.01325")
SECONDS_PER_HOUR = Decimal("3600")


@dataclass(frozen=True, slots=True)
class ReceiverSizingInput:
    """Input data for compressed-air receiver sizing."""

    peak_demand_nm3_per_hr: Decimal
    available_compressor_flow_nm3_per_hr: Decimal

    event_duration_seconds: Decimal

    receiver_high_pressure_bar_g: Decimal
    receiver_low_pressure_bar_g: Decimal

    reserve_fraction: Decimal = Decimal("0")


@dataclass(frozen=True, slots=True)
class ReceiverSizingResult:
    """Calculated compressed-air receiver sizing result."""

    peak_demand_nm3_per_hr: Decimal
    available_compressor_flow_nm3_per_hr: Decimal

    flow_deficit_nm3_per_hr: Decimal

    event_duration_seconds: Decimal

    receiver_high_pressure_bar_g: Decimal
    receiver_low_pressure_bar_g: Decimal
    pressure_band_bar: Decimal

    base_receiver_volume_m3: Decimal
    reserve_fraction: Decimal
    recommended_receiver_volume_m3: Decimal

    storage_required: bool


def calculate_receiver_size(
    inputs: ReceiverSizingInput,
) -> ReceiverSizingResult:
    """Calculate receiver volume for short-duration compressed-air demand peaks."""

    _validate_inputs(inputs)

    flow_deficit_nm3_per_hr = max(
        inputs.peak_demand_nm3_per_hr - inputs.available_compressor_flow_nm3_per_hr,
        Decimal("0"),
    )

    pressure_band_bar = inputs.receiver_high_pressure_bar_g - inputs.receiver_low_pressure_bar_g

    if flow_deficit_nm3_per_hr == 0:
        base_receiver_volume_m3 = Decimal("0")
    else:
        deficit_volume_nm3 = (
            flow_deficit_nm3_per_hr * inputs.event_duration_seconds / SECONDS_PER_HOUR
        )

        high_pressure_bar_abs = inputs.receiver_high_pressure_bar_g + ATMOSPHERIC_PRESSURE_BAR

        low_pressure_bar_abs = inputs.receiver_low_pressure_bar_g + ATMOSPHERIC_PRESSURE_BAR

        pressure_ratio_difference = (
            high_pressure_bar_abs - low_pressure_bar_abs
        ) / ATMOSPHERIC_PRESSURE_BAR

        base_receiver_volume_m3 = deficit_volume_nm3 / pressure_ratio_difference

    recommended_receiver_volume_m3 = base_receiver_volume_m3 * (
        Decimal("1") + inputs.reserve_fraction
    )

    return ReceiverSizingResult(
        peak_demand_nm3_per_hr=inputs.peak_demand_nm3_per_hr,
        available_compressor_flow_nm3_per_hr=(inputs.available_compressor_flow_nm3_per_hr),
        flow_deficit_nm3_per_hr=flow_deficit_nm3_per_hr,
        event_duration_seconds=inputs.event_duration_seconds,
        receiver_high_pressure_bar_g=inputs.receiver_high_pressure_bar_g,
        receiver_low_pressure_bar_g=inputs.receiver_low_pressure_bar_g,
        pressure_band_bar=pressure_band_bar,
        base_receiver_volume_m3=base_receiver_volume_m3,
        reserve_fraction=inputs.reserve_fraction,
        recommended_receiver_volume_m3=(recommended_receiver_volume_m3),
        storage_required=flow_deficit_nm3_per_hr > 0,
    )


def _validate_inputs(
    inputs: ReceiverSizingInput,
) -> None:
    if inputs.peak_demand_nm3_per_hr < 0:
        raise InvalidReceiverSizingInputError("Peak demand cannot be negative.")

    if inputs.available_compressor_flow_nm3_per_hr < 0:
        raise InvalidReceiverSizingInputError("Available compressor flow cannot be negative.")

    if inputs.event_duration_seconds <= 0:
        raise InvalidReceiverSizingInputError("Event duration must be greater than zero.")

    if inputs.receiver_low_pressure_bar_g < 0:
        raise InvalidReceiverSizingInputError("Receiver low pressure cannot be negative.")

    if inputs.receiver_high_pressure_bar_g <= inputs.receiver_low_pressure_bar_g:
        raise InvalidReceiverSizingInputError(
            "Receiver high pressure must be greater than receiver low pressure."
        )

    if inputs.reserve_fraction < 0 or inputs.reserve_fraction > 1:
        raise InvalidReceiverSizingInputError("Reserve fraction must be between zero and one.")
