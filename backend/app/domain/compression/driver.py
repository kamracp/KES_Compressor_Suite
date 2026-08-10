from dataclasses import dataclass
from decimal import Decimal


class InvalidDriverInputError(ValueError):
    """Raised when driver-sizing inputs are invalid."""


@dataclass(frozen=True, slots=True)
class DriverSizingResult:
    """Compressor driver sizing result."""

    shaft_power_kw: Decimal
    service_factor: Decimal
    required_driver_power_kw: Decimal
    selected_driver_power_kw: Decimal
    driver_margin_kw: Decimal
    driver_is_adequate: bool
    motor_efficiency: Decimal | None
    electrical_input_power_kw: Decimal | None


def size_driver(
    shaft_power_kw: Decimal,
    selected_driver_power_kw: Decimal,
    service_factor: Decimal = Decimal("0.10"),
    motor_efficiency: Decimal | None = None,
) -> DriverSizingResult:
    """Size compressor driver and calculate electrical input when applicable."""

    if shaft_power_kw <= 0:
        raise InvalidDriverInputError("Shaft power must be greater than zero.")

    if selected_driver_power_kw <= 0:
        raise InvalidDriverInputError("Selected driver power must be greater than zero.")

    if service_factor < 0:
        raise InvalidDriverInputError("Service factor cannot be negative.")

    if motor_efficiency is not None and (motor_efficiency <= 0 or motor_efficiency > 1):
        raise InvalidDriverInputError(
            "Motor efficiency must be greater than zero and not exceed one."
        )

    required_driver_power_kw = shaft_power_kw * (Decimal("1") + service_factor)

    driver_margin_kw = selected_driver_power_kw - required_driver_power_kw

    driver_is_adequate = selected_driver_power_kw >= required_driver_power_kw

    electrical_input_power_kw: Decimal | None = None

    if motor_efficiency is not None:
        electrical_input_power_kw = required_driver_power_kw / motor_efficiency

    return DriverSizingResult(
        shaft_power_kw=shaft_power_kw,
        service_factor=service_factor,
        required_driver_power_kw=required_driver_power_kw,
        selected_driver_power_kw=selected_driver_power_kw,
        driver_margin_kw=driver_margin_kw,
        driver_is_adequate=driver_is_adequate,
        motor_efficiency=motor_efficiency,
        electrical_input_power_kw=electrical_input_power_kw,
    )
