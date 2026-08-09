from dataclasses import dataclass
from decimal import Decimal

from app.domain.centrifugal.centrifugal_models import CentrifugalDriverType


class InvalidCentrifugalPowerInputError(ValueError):
    """Raised when centrifugal compressor power inputs are invalid."""


@dataclass(frozen=True, slots=True)
class CentrifugalPowerCalculationResult:
    """Centrifugal compressor power calculation result."""

    gas_power_kw: Decimal
    shaft_power_kw: Decimal
    required_driver_power_kw: Decimal
    selected_driver_power_kw: Decimal
    driver_margin_kw: Decimal
    driver_is_adequate: bool
    electrical_input_power_kw: Decimal | None
    driver_type: CentrifugalDriverType


def calculate_centrifugal_power(
    mass_flow_kg_per_s: Decimal,
    polytropic_head_kj_per_kg: Decimal,
    polytropic_efficiency: Decimal,
    mechanical_loss_fraction: Decimal,
    driver_margin_fraction: Decimal,
    selected_driver_power_kw: Decimal,
    driver_type: CentrifugalDriverType,
    motor_efficiency: Decimal | None = None,
) -> CentrifugalPowerCalculationResult:
    """Calculate centrifugal compressor power and driver requirements."""

    if mass_flow_kg_per_s <= 0:
        raise InvalidCentrifugalPowerInputError("Mass flow must be greater than zero.")

    if polytropic_head_kj_per_kg <= 0:
        raise InvalidCentrifugalPowerInputError("Polytropic head must be greater than zero.")

    if polytropic_efficiency <= 0 or polytropic_efficiency > 1:
        raise InvalidCentrifugalPowerInputError(
            "Polytropic efficiency must be greater than zero and not exceed one."
        )

    if mechanical_loss_fraction < 0:
        raise InvalidCentrifugalPowerInputError("Mechanical loss fraction cannot be negative.")

    if driver_margin_fraction < 0:
        raise InvalidCentrifugalPowerInputError("Driver margin fraction cannot be negative.")

    if selected_driver_power_kw <= 0:
        raise InvalidCentrifugalPowerInputError("Selected driver power must be greater than zero.")

    if motor_efficiency is not None:
        if motor_efficiency <= 0 or motor_efficiency > 1:
            raise InvalidCentrifugalPowerInputError(
                "Motor efficiency must be greater than zero and not exceed one."
            )

    gas_power_kw = mass_flow_kg_per_s * polytropic_head_kj_per_kg / polytropic_efficiency

    shaft_power_kw = gas_power_kw * (Decimal("1") + mechanical_loss_fraction)

    required_driver_power_kw = shaft_power_kw * (Decimal("1") + driver_margin_fraction)

    driver_margin_kw = selected_driver_power_kw - required_driver_power_kw

    driver_is_adequate = selected_driver_power_kw >= required_driver_power_kw

    electrical_input_power_kw: Decimal | None = None

    if driver_type == CentrifugalDriverType.ELECTRIC_MOTOR and motor_efficiency is not None:
        electrical_input_power_kw = required_driver_power_kw / motor_efficiency

    return CentrifugalPowerCalculationResult(
        gas_power_kw=gas_power_kw,
        shaft_power_kw=shaft_power_kw,
        required_driver_power_kw=required_driver_power_kw,
        selected_driver_power_kw=selected_driver_power_kw,
        driver_margin_kw=driver_margin_kw,
        driver_is_adequate=driver_is_adequate,
        electrical_input_power_kw=electrical_input_power_kw,
        driver_type=driver_type,
    )
