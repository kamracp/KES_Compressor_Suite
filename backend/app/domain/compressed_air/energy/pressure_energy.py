from dataclasses import dataclass
from decimal import Decimal


class InvalidPressureEnergyInputError(ValueError):
    """Raised when pressure-energy optimization inputs are invalid."""


@dataclass(frozen=True, slots=True)
class PressureEnergyInput:
    """Input data for compressed-air pressure-energy analysis."""

    current_discharge_pressure_bar_g: Decimal
    optimized_discharge_pressure_bar_g: Decimal

    current_average_power_kw: Decimal
    annual_operating_hours: Decimal

    electricity_tariff_per_kwh: Decimal

    power_penalty_fraction_per_bar: Decimal = Decimal("0.07")


@dataclass(frozen=True, slots=True)
class PressureEnergyResult:
    """Calculated energy impact of reducing compressed-air pressure."""

    current_discharge_pressure_bar_g: Decimal
    optimized_discharge_pressure_bar_g: Decimal

    pressure_reduction_bar: Decimal

    current_average_power_kw: Decimal
    estimated_optimized_power_kw: Decimal
    estimated_power_saving_kw: Decimal

    power_saving_fraction: Decimal

    annual_operating_hours: Decimal

    annual_energy_saving_kwh: Decimal

    electricity_tariff_per_kwh: Decimal
    annual_cost_saving: Decimal

    power_penalty_fraction_per_bar: Decimal

    pressure_reduction_is_beneficial: bool


def calculate_pressure_energy_saving(
    inputs: PressureEnergyInput,
) -> PressureEnergyResult:
    """Estimate energy savings from reducing compressor discharge pressure."""

    _validate_inputs(inputs)

    pressure_reduction_bar = (
        inputs.current_discharge_pressure_bar_g - inputs.optimized_discharge_pressure_bar_g
    )

    if pressure_reduction_bar <= 0:
        power_saving_fraction = Decimal("0")
    else:
        power_saving_fraction = pressure_reduction_bar * inputs.power_penalty_fraction_per_bar

    if power_saving_fraction > Decimal("1"):
        power_saving_fraction = Decimal("1")

    estimated_power_saving_kw = inputs.current_average_power_kw * power_saving_fraction

    estimated_optimized_power_kw = inputs.current_average_power_kw - estimated_power_saving_kw

    annual_energy_saving_kwh = estimated_power_saving_kw * inputs.annual_operating_hours

    annual_cost_saving = annual_energy_saving_kwh * inputs.electricity_tariff_per_kwh

    return PressureEnergyResult(
        current_discharge_pressure_bar_g=(inputs.current_discharge_pressure_bar_g),
        optimized_discharge_pressure_bar_g=(inputs.optimized_discharge_pressure_bar_g),
        pressure_reduction_bar=pressure_reduction_bar,
        current_average_power_kw=inputs.current_average_power_kw,
        estimated_optimized_power_kw=estimated_optimized_power_kw,
        estimated_power_saving_kw=estimated_power_saving_kw,
        power_saving_fraction=power_saving_fraction,
        annual_operating_hours=inputs.annual_operating_hours,
        annual_energy_saving_kwh=annual_energy_saving_kwh,
        electricity_tariff_per_kwh=inputs.electricity_tariff_per_kwh,
        annual_cost_saving=annual_cost_saving,
        power_penalty_fraction_per_bar=(inputs.power_penalty_fraction_per_bar),
        pressure_reduction_is_beneficial=(pressure_reduction_bar > 0),
    )


def _validate_inputs(
    inputs: PressureEnergyInput,
) -> None:
    if inputs.current_discharge_pressure_bar_g < 0:
        raise InvalidPressureEnergyInputError("Current discharge pressure cannot be negative.")

    if inputs.optimized_discharge_pressure_bar_g < 0:
        raise InvalidPressureEnergyInputError("Optimized discharge pressure cannot be negative.")

    if inputs.current_average_power_kw <= 0:
        raise InvalidPressureEnergyInputError("Current average power must be greater than zero.")

    if inputs.annual_operating_hours <= 0:
        raise InvalidPressureEnergyInputError("Annual operating hours must be greater than zero.")

    if inputs.electricity_tariff_per_kwh < 0:
        raise InvalidPressureEnergyInputError("Electricity tariff cannot be negative.")

    if inputs.power_penalty_fraction_per_bar < 0 or inputs.power_penalty_fraction_per_bar > 1:
        raise InvalidPressureEnergyInputError(
            "Power penalty fraction per bar must be between zero and one."
        )
