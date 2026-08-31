from dataclasses import dataclass
from decimal import Decimal

from app.domain.compressed_air.brownfield.audit_analysis import (
    BrownfieldAuditAnalysisResult,
    analyze_brownfield_audit,
)
from app.domain.compressed_air.brownfield.audit_models import BrownfieldAuditCase
from app.domain.compressed_air.brownfield.opportunity_engine import (
    BrownfieldOpportunityResult,
    identify_brownfield_opportunities,
)
from app.domain.compressed_air.energy.leakage_energy import (
    LeakageEnergyResult,
)
from app.domain.compressed_air.energy.motor_pfc import (
    MotorMeasurementInput,
)
from app.domain.compressed_air.energy.pressure_energy import (
    PressureEnergyInput,
    PressureEnergyResult,
    calculate_pressure_energy_saving,
)
from app.domain.compressed_air.optimization.system_optimizer import (
    SystemOptimizationResult,
    optimize_compressed_air_system,
)


class InvalidBrownfieldSystemEngineInputError(ValueError):
    """Raised when integrated brownfield system inputs are invalid."""


@dataclass(frozen=True, slots=True)
class BrownfieldSystemEngineInput:
    """Integrated input for existing compressed-air system assessment."""

    audit: BrownfieldAuditCase

    optimized_discharge_pressure_bar_g: Decimal | None = None
    condensate_drain_air_loss_nm3_per_hr: Decimal | None = None
    filter_excess_pressure_drop_bar: Decimal | None = None

    expected_leak_repair_fraction: Decimal = Decimal("0.80")

    demand_saving_control_factor: Decimal = Decimal("1")

    power_penalty_fraction_per_bar: Decimal | None = None

    # Field-measured motor electrical data; drives the PF-CORRECTION
    # opportunity (IEEE Std 141 power, IS 15167 capacitor sizing).
    motor_measurement: MotorMeasurementInput | None = None

    # Annual PF penalty the utility is currently billing the site.
    # User-supplied only; never assumed from a tariff.
    pf_penalty_annual_cost: Decimal | None = None


@dataclass(frozen=True, slots=True)
class BrownfieldSystemEngineResult:
    """Integrated result for an existing compressed-air system."""

    audit_analysis: BrownfieldAuditAnalysisResult

    leakage_energy: LeakageEnergyResult | None
    pressure_energy: PressureEnergyResult | None

    opportunities: BrownfieldOpportunityResult
    optimization: SystemOptimizationResult

    current_average_power_kw: Decimal
    current_annual_energy_kwh: Decimal
    current_annual_energy_cost: Decimal

    estimated_total_power_saving_kw: Decimal
    estimated_total_annual_energy_saving_kwh: Decimal
    estimated_total_annual_cost_saving: Decimal

    estimated_optimized_average_power_kw: Decimal
    estimated_optimized_annual_energy_kwh: Decimal
    estimated_optimized_annual_energy_cost: Decimal

    estimated_energy_reduction_fraction: Decimal


def analyze_brownfield_system(
    inputs: BrownfieldSystemEngineInput,
) -> BrownfieldSystemEngineResult:
    """Run integrated analysis of an existing factory air system."""

    _validate_inputs(inputs)

    audit_analysis = analyze_brownfield_audit(inputs.audit)

    opportunities = identify_brownfield_opportunities(
        analysis=audit_analysis,
        expected_leak_repair_fraction=(inputs.expected_leak_repair_fraction),
        demand_saving_control_factor=(inputs.demand_saving_control_factor),
        optimized_discharge_pressure_bar_g=(inputs.optimized_discharge_pressure_bar_g),
        power_penalty_fraction_per_bar=(inputs.power_penalty_fraction_per_bar),
        condensate_drain_air_loss_nm3_per_hr=(
            inputs.condensate_drain_air_loss_nm3_per_hr
        ),
        filter_excess_pressure_drop_bar=(
            inputs.filter_excess_pressure_drop_bar
        ),
        motor_measurement=inputs.motor_measurement,
        pf_penalty_annual_cost=inputs.pf_penalty_annual_cost,
    )

    leakage_energy = _extract_leakage_energy(
        analysis=audit_analysis,
        opportunities=opportunities,
        expected_repair_fraction=(inputs.expected_leak_repair_fraction),
        demand_saving_control_factor=(inputs.demand_saving_control_factor),
    )

    pressure_energy = _calculate_pressure_energy(
        analysis=audit_analysis,
        optimized_discharge_pressure_bar_g=(inputs.optimized_discharge_pressure_bar_g),
        power_penalty_fraction_per_bar=(inputs.power_penalty_fraction_per_bar),
    )

    optimization = optimize_compressed_air_system(
        brownfield_analysis=audit_analysis,
        brownfield_opportunities=opportunities,
    )

    current_average_power_kw = audit_analysis.average_system_power_kw

    current_annual_energy_kwh = audit_analysis.estimated_annual_energy_kwh

    current_annual_energy_cost = audit_analysis.estimated_annual_energy_cost

    estimated_total_power_saving_kw = optimization.total_estimated_power_saving_kw

    estimated_total_annual_energy_saving_kwh = optimization.total_estimated_annual_energy_saving_kwh

    estimated_total_annual_cost_saving = optimization.total_estimated_annual_cost_saving

    estimated_optimized_average_power_kw = max(
        current_average_power_kw - estimated_total_power_saving_kw,
        Decimal("0"),
    )

    estimated_optimized_annual_energy_kwh = max(
        current_annual_energy_kwh - estimated_total_annual_energy_saving_kwh,
        Decimal("0"),
    )

    estimated_optimized_annual_energy_cost = max(
        current_annual_energy_cost - estimated_total_annual_cost_saving,
        Decimal("0"),
    )

    if current_annual_energy_kwh > 0:
        estimated_energy_reduction_fraction = (
            estimated_total_annual_energy_saving_kwh / current_annual_energy_kwh
        )
    else:
        estimated_energy_reduction_fraction = Decimal("0")

    return BrownfieldSystemEngineResult(
        audit_analysis=audit_analysis,
        leakage_energy=leakage_energy,
        pressure_energy=pressure_energy,
        opportunities=opportunities,
        optimization=optimization,
        current_average_power_kw=current_average_power_kw,
        current_annual_energy_kwh=current_annual_energy_kwh,
        current_annual_energy_cost=current_annual_energy_cost,
        estimated_total_power_saving_kw=(estimated_total_power_saving_kw),
        estimated_total_annual_energy_saving_kwh=(estimated_total_annual_energy_saving_kwh),
        estimated_total_annual_cost_saving=(estimated_total_annual_cost_saving),
        estimated_optimized_average_power_kw=(estimated_optimized_average_power_kw),
        estimated_optimized_annual_energy_kwh=(estimated_optimized_annual_energy_kwh),
        estimated_optimized_annual_energy_cost=(estimated_optimized_annual_energy_cost),
        estimated_energy_reduction_fraction=(estimated_energy_reduction_fraction),
    )


def _extract_leakage_energy(
    *,
    analysis: BrownfieldAuditAnalysisResult,
    opportunities: BrownfieldOpportunityResult,
    expected_repair_fraction: Decimal,
    demand_saving_control_factor: Decimal,
) -> LeakageEnergyResult | None:
    if not analysis.significant_leakage_detected:
        return None

    if analysis.measured_specific_power_kw_per_nm3_per_min is None:
        return None

    from app.domain.compressed_air.energy.leakage_energy import (
        LeakageEnergyInput,
        calculate_leakage_energy,
    )

    return calculate_leakage_energy(
        LeakageEnergyInput(
            leakage_flow_nm3_per_hr=(analysis.leakage_flow_nm3_per_hr),
            specific_power_kw_per_nm3_per_min=(analysis.measured_specific_power_kw_per_nm3_per_min),
            annual_operating_hours=analysis.annual_operating_hours,
            electricity_tariff_per_kwh=(analysis.electricity_tariff_per_kwh),
            expected_repair_fraction=expected_repair_fraction,
            demand_saving_control_factor=(demand_saving_control_factor),
        )
    )


def _calculate_pressure_energy(
    *,
    analysis: BrownfieldAuditAnalysisResult,
    optimized_discharge_pressure_bar_g: Decimal | None,
    power_penalty_fraction_per_bar: Decimal,
) -> PressureEnergyResult | None:
    if optimized_discharge_pressure_bar_g is None:
        return None

    return calculate_pressure_energy_saving(
        PressureEnergyInput(
            current_discharge_pressure_bar_g=(analysis.average_header_pressure_bar_g),
            optimized_discharge_pressure_bar_g=(optimized_discharge_pressure_bar_g),
            current_average_power_kw=analysis.average_system_power_kw,
            annual_operating_hours=analysis.annual_operating_hours,
            electricity_tariff_per_kwh=(analysis.electricity_tariff_per_kwh),
            power_penalty_fraction_per_bar=(power_penalty_fraction_per_bar),
        )
    )


def _validate_inputs(
    inputs: BrownfieldSystemEngineInput,
) -> None:
    if inputs.expected_leak_repair_fraction < 0 or inputs.expected_leak_repair_fraction > 1:
        raise InvalidBrownfieldSystemEngineInputError(
            "Expected leak repair fraction must be between zero and one."
        )

    if inputs.power_penalty_fraction_per_bar is not None and (
        inputs.power_penalty_fraction_per_bar < 0
        or inputs.power_penalty_fraction_per_bar > 1
    ):
        raise InvalidBrownfieldSystemEngineInputError(
            "Power penalty fraction per bar must be between zero and one."
        )

    if (
        inputs.optimized_discharge_pressure_bar_g is not None
        and inputs.optimized_discharge_pressure_bar_g < 0
    ):
        raise InvalidBrownfieldSystemEngineInputError(
            "Optimized discharge pressure cannot be negative."
        )
