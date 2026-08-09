from dataclasses import dataclass
from decimal import Decimal

from app.domain.compressed_air.profiles.demand_profile import DemandProfileResult


class InvalidSystemEnergyInputError(ValueError):
    """Raised when compressed-air energy inputs are invalid."""


MINUTES_PER_HOUR = Decimal("60")


@dataclass(frozen=True, slots=True)
class SystemEnergyInput:
    """Input data for compressed-air system energy estimation."""

    demand_profile: DemandProfileResult

    specific_power_kw_per_nm3_per_min: Decimal

    annual_operating_days: Decimal
    profile_repetitions_per_day: Decimal = Decimal("1")

    electricity_tariff_per_kwh: Decimal = Decimal("0")

    unload_power_fraction: Decimal = Decimal("0")
    average_unloaded_fraction: Decimal = Decimal("0")


@dataclass(frozen=True, slots=True)
class SystemEnergyResult:
    """Calculated compressed-air annual energy performance."""

    average_demand_nm3_per_hr: Decimal
    maximum_demand_nm3_per_hr: Decimal

    average_demand_nm3_per_min: Decimal

    loaded_power_kw: Decimal
    unload_power_kw: Decimal
    effective_average_power_kw: Decimal

    annual_operating_hours: Decimal
    annual_energy_kwh: Decimal

    electricity_tariff_per_kwh: Decimal
    annual_energy_cost: Decimal

    specific_power_kw_per_nm3_per_min: Decimal
    effective_specific_energy_kwh_per_1000_nm3: Decimal


def calculate_system_energy(
    inputs: SystemEnergyInput,
) -> SystemEnergyResult:
    """Estimate annual compressed-air system energy consumption and cost."""

    _validate_inputs(inputs)

    average_demand_nm3_per_min = inputs.demand_profile.average_demand_nm3_per_hr / MINUTES_PER_HOUR

    loaded_power_kw = average_demand_nm3_per_min * inputs.specific_power_kw_per_nm3_per_min

    unload_power_kw = loaded_power_kw * inputs.unload_power_fraction

    effective_average_power_kw = (
        loaded_power_kw * (Decimal("1") - inputs.average_unloaded_fraction)
        + unload_power_kw * inputs.average_unloaded_fraction
    )

    annual_operating_hours = (
        inputs.demand_profile.total_profile_hours
        * inputs.profile_repetitions_per_day
        * inputs.annual_operating_days
    )

    annual_energy_kwh = effective_average_power_kw * annual_operating_hours

    annual_energy_cost = annual_energy_kwh * inputs.electricity_tariff_per_kwh

    annual_air_volume_nm3 = (
        inputs.demand_profile.total_air_volume_nm3
        * inputs.profile_repetitions_per_day
        * inputs.annual_operating_days
    )

    if annual_air_volume_nm3 > 0:
        effective_specific_energy_kwh_per_1000_nm3 = (
            annual_energy_kwh / annual_air_volume_nm3 * Decimal("1000")
        )
    else:
        effective_specific_energy_kwh_per_1000_nm3 = Decimal("0")

    return SystemEnergyResult(
        average_demand_nm3_per_hr=(inputs.demand_profile.average_demand_nm3_per_hr),
        maximum_demand_nm3_per_hr=(inputs.demand_profile.maximum_demand_nm3_per_hr),
        average_demand_nm3_per_min=average_demand_nm3_per_min,
        loaded_power_kw=loaded_power_kw,
        unload_power_kw=unload_power_kw,
        effective_average_power_kw=effective_average_power_kw,
        annual_operating_hours=annual_operating_hours,
        annual_energy_kwh=annual_energy_kwh,
        electricity_tariff_per_kwh=inputs.electricity_tariff_per_kwh,
        annual_energy_cost=annual_energy_cost,
        specific_power_kw_per_nm3_per_min=(inputs.specific_power_kw_per_nm3_per_min),
        effective_specific_energy_kwh_per_1000_nm3=(effective_specific_energy_kwh_per_1000_nm3),
    )


def _validate_inputs(
    inputs: SystemEnergyInput,
) -> None:
    if inputs.specific_power_kw_per_nm3_per_min <= 0:
        raise InvalidSystemEnergyInputError("Specific power must be greater than zero.")

    if inputs.annual_operating_days <= 0:
        raise InvalidSystemEnergyInputError("Annual operating days must be greater than zero.")

    if inputs.profile_repetitions_per_day <= 0:
        raise InvalidSystemEnergyInputError(
            "Profile repetitions per day must be greater than zero."
        )

    if inputs.electricity_tariff_per_kwh < 0:
        raise InvalidSystemEnergyInputError("Electricity tariff cannot be negative.")

    if inputs.unload_power_fraction < 0 or inputs.unload_power_fraction > 1:
        raise InvalidSystemEnergyInputError("Unload power fraction must be between zero and one.")

    if inputs.average_unloaded_fraction < 0 or inputs.average_unloaded_fraction > 1:
        raise InvalidSystemEnergyInputError(
            "Average unloaded fraction must be between zero and one."
        )
