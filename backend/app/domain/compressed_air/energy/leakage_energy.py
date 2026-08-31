from dataclasses import dataclass
from decimal import Decimal


class InvalidLeakageEnergyInputError(ValueError):
    """Raised when compressed-air leakage energy inputs are invalid."""


MINUTES_PER_HOUR = Decimal("60")


@dataclass(frozen=True, slots=True)
class LeakageEnergyInput:
    """Input data for compressed-air leakage energy analysis."""

    leakage_flow_nm3_per_hr: Decimal

    specific_power_kw_per_nm3_per_min: Decimal

    annual_operating_hours: Decimal
    electricity_tariff_per_kwh: Decimal

    expected_repair_fraction: Decimal = Decimal("1")

    # Fraction of the avoided air demand that the compressor controls
    # actually convert into electrical savings. 1 = fully effective
    # turndown (VSD or a well-sequenced multi-machine station); an
    # inlet-modulating machine without unloading converts roughly half.
    # Deliberately an explicit input rather than a hidden assumption:
    # this is the most over-claimed number in compressed-air proposals.
    demand_saving_control_factor: Decimal = Decimal("1")


@dataclass(frozen=True, slots=True)
class LeakageEnergyResult:
    """Calculated energy and cost impact of compressed-air leakage."""

    leakage_flow_nm3_per_hr: Decimal
    leakage_flow_nm3_per_min: Decimal

    wasted_power_kw: Decimal

    annual_wasted_energy_kwh: Decimal
    annual_wasted_energy_cost: Decimal

    expected_repair_fraction: Decimal
    demand_saving_control_factor: Decimal

    recoverable_leakage_flow_nm3_per_hr: Decimal
    recoverable_power_kw: Decimal

    annual_energy_saving_kwh: Decimal
    annual_cost_saving: Decimal

    residual_leakage_flow_nm3_per_hr: Decimal


def calculate_leakage_energy(
    inputs: LeakageEnergyInput,
) -> LeakageEnergyResult:
    """Calculate compressed-air leakage energy loss and repair savings."""

    _validate_inputs(inputs)

    leakage_flow_nm3_per_min = inputs.leakage_flow_nm3_per_hr / MINUTES_PER_HOUR

    wasted_power_kw = leakage_flow_nm3_per_min * inputs.specific_power_kw_per_nm3_per_min

    annual_wasted_energy_kwh = wasted_power_kw * inputs.annual_operating_hours

    annual_wasted_energy_cost = annual_wasted_energy_kwh * inputs.electricity_tariff_per_kwh

    recoverable_leakage_flow_nm3_per_hr = (
        inputs.leakage_flow_nm3_per_hr * inputs.expected_repair_fraction
    )

    # Flow quantities stay physical: repaired leaks stop leaking air
    # regardless of controls. Only the electrical conversion below is
    # scaled by the demand-saving control factor.
    recoverable_power_kw = (
        wasted_power_kw * inputs.expected_repair_fraction * inputs.demand_saving_control_factor
    )

    annual_energy_saving_kwh = (
        annual_wasted_energy_kwh
        * inputs.expected_repair_fraction
        * inputs.demand_saving_control_factor
    )

    annual_cost_saving = (
        annual_wasted_energy_cost
        * inputs.expected_repair_fraction
        * inputs.demand_saving_control_factor
    )

    residual_leakage_flow_nm3_per_hr = (
        inputs.leakage_flow_nm3_per_hr - recoverable_leakage_flow_nm3_per_hr
    )

    return LeakageEnergyResult(
        leakage_flow_nm3_per_hr=inputs.leakage_flow_nm3_per_hr,
        leakage_flow_nm3_per_min=leakage_flow_nm3_per_min,
        wasted_power_kw=wasted_power_kw,
        annual_wasted_energy_kwh=annual_wasted_energy_kwh,
        annual_wasted_energy_cost=annual_wasted_energy_cost,
        expected_repair_fraction=inputs.expected_repair_fraction,
        demand_saving_control_factor=(inputs.demand_saving_control_factor),
        recoverable_leakage_flow_nm3_per_hr=(recoverable_leakage_flow_nm3_per_hr),
        recoverable_power_kw=recoverable_power_kw,
        annual_energy_saving_kwh=annual_energy_saving_kwh,
        annual_cost_saving=annual_cost_saving,
        residual_leakage_flow_nm3_per_hr=(residual_leakage_flow_nm3_per_hr),
    )


def _validate_inputs(
    inputs: LeakageEnergyInput,
) -> None:
    if inputs.leakage_flow_nm3_per_hr < 0:
        raise InvalidLeakageEnergyInputError("Leakage flow cannot be negative.")

    if inputs.specific_power_kw_per_nm3_per_min <= 0:
        raise InvalidLeakageEnergyInputError("Specific power must be greater than zero.")

    if inputs.annual_operating_hours <= 0:
        raise InvalidLeakageEnergyInputError("Annual operating hours must be greater than zero.")

    if inputs.electricity_tariff_per_kwh < 0:
        raise InvalidLeakageEnergyInputError("Electricity tariff cannot be negative.")

    if inputs.demand_saving_control_factor < 0 or inputs.demand_saving_control_factor > 1:
        raise InvalidLeakageEnergyInputError(
            "Demand-saving control factor must be between zero and one."
        )

    if inputs.expected_repair_fraction < 0 or inputs.expected_repair_fraction > 1:
        raise InvalidLeakageEnergyInputError(
            "Expected repair fraction must be between zero and one."
        )
