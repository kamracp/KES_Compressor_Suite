from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from app.domain.compressed_air.brownfield.audit_analysis import (
    BrownfieldAuditAnalysisResult,
)
from app.domain.compressed_air.energy.leakage_energy import (
    LeakageEnergyInput,
    calculate_leakage_energy,
)
from app.domain.compressed_air.energy.pressure_energy import (
    PressureEnergyInput,
    calculate_pressure_energy_saving,
)


class OpportunityCategory(StrEnum):
    LEAKAGE = "LEAKAGE"
    UNLOADED_RUNNING = "UNLOADED_RUNNING"
    PRESSURE = "PRESSURE"
    CAPACITY = "CAPACITY"
    UTILIZATION = "UTILIZATION"


class OpportunityPriority(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass(frozen=True, slots=True)
class BrownfieldOpportunity:
    opportunity_code: str
    category: OpportunityCategory
    priority: OpportunityPriority
    title: str
    rationale: str

    estimated_power_saving_kw: Decimal
    estimated_annual_energy_saving_kwh: Decimal
    estimated_annual_cost_saving: Decimal


@dataclass(frozen=True, slots=True)
class BrownfieldOpportunityResult:
    audit_code: str

    opportunities: tuple[BrownfieldOpportunity, ...]

    total_estimated_power_saving_kw: Decimal
    total_estimated_annual_energy_saving_kwh: Decimal
    total_estimated_annual_cost_saving: Decimal


def identify_brownfield_opportunities(
    *,
    analysis: BrownfieldAuditAnalysisResult,
    expected_leak_repair_fraction: Decimal = Decimal("0.80"),
    optimized_discharge_pressure_bar_g: Decimal | None = None,
    power_penalty_fraction_per_bar: Decimal = Decimal("0.07"),
) -> BrownfieldOpportunityResult:
    opportunities: list[BrownfieldOpportunity] = []

    if analysis.significant_leakage_detected:
        leakage_result = calculate_leakage_energy(
            LeakageEnergyInput(
                leakage_flow_nm3_per_hr=analysis.leakage_flow_nm3_per_hr,
                specific_power_kw_per_nm3_per_min=(
                    analysis.measured_specific_power_kw_per_nm3_per_min or Decimal("0.000001")
                ),
                annual_operating_hours=analysis.annual_operating_hours,
                electricity_tariff_per_kwh=(analysis.electricity_tariff_per_kwh),
                expected_repair_fraction=expected_leak_repair_fraction,
            )
        )

        opportunities.append(
            BrownfieldOpportunity(
                opportunity_code="LEAK-REPAIR",
                category=OpportunityCategory.LEAKAGE,
                priority=OpportunityPriority.HIGH,
                title="Compressed-air leakage reduction",
                rationale=("Measured leakage is significant relative to average system demand."),
                estimated_power_saving_kw=(leakage_result.recoverable_power_kw),
                estimated_annual_energy_saving_kwh=(leakage_result.annual_energy_saving_kwh),
                estimated_annual_cost_saving=(leakage_result.annual_cost_saving),
            )
        )

    if analysis.high_unloaded_running_detected:
        unload_power_saving = (
            analysis.average_system_power_kw
            * analysis.unloaded_measurement_fraction
            * Decimal("0.30")
        )

        annual_energy_saving = unload_power_saving * analysis.annual_operating_hours

        opportunities.append(
            BrownfieldOpportunity(
                opportunity_code="UNLOAD-REDUCTION",
                category=OpportunityCategory.UNLOADED_RUNNING,
                priority=OpportunityPriority.HIGH,
                title="Reduce unloaded compressor running",
                rationale=(
                    "A significant fraction of compressor observations are "
                    "in unloaded operation. Sequencing, VSD trim, controls, "
                    "or storage should be reviewed."
                ),
                estimated_power_saving_kw=unload_power_saving,
                estimated_annual_energy_saving_kwh=annual_energy_saving,
                estimated_annual_cost_saving=(
                    annual_energy_saving * analysis.electricity_tariff_per_kwh
                ),
            )
        )

    if optimized_discharge_pressure_bar_g is not None:
        pressure_result = calculate_pressure_energy_saving(
            PressureEnergyInput(
                current_discharge_pressure_bar_g=(analysis.average_header_pressure_bar_g),
                optimized_discharge_pressure_bar_g=(optimized_discharge_pressure_bar_g),
                current_average_power_kw=analysis.average_system_power_kw,
                annual_operating_hours=analysis.annual_operating_hours,
                electricity_tariff_per_kwh=(analysis.electricity_tariff_per_kwh),
                power_penalty_fraction_per_bar=(power_penalty_fraction_per_bar),
            )
        )

        if pressure_result.pressure_reduction_is_beneficial:
            opportunities.append(
                BrownfieldOpportunity(
                    opportunity_code="PRESSURE-REDUCTION",
                    category=OpportunityCategory.PRESSURE,
                    priority=OpportunityPriority.MEDIUM,
                    title="Reduce system operating pressure",
                    rationale=(
                        "The system appears capable of operating at a lower "
                        "pressure after distribution and control review."
                    ),
                    estimated_power_saving_kw=(pressure_result.estimated_power_saving_kw),
                    estimated_annual_energy_saving_kwh=(pressure_result.annual_energy_saving_kwh),
                    estimated_annual_cost_saving=(pressure_result.annual_cost_saving),
                )
            )

    if not analysis.installed_capacity_is_sufficient_for_peak:
        opportunities.append(
            BrownfieldOpportunity(
                opportunity_code="CAPACITY-REVIEW",
                category=OpportunityCategory.CAPACITY,
                priority=OpportunityPriority.HIGH,
                title="Review compressor station capacity",
                rationale=("Available compressor capacity is below measured peak system demand."),
                estimated_power_saving_kw=Decimal("0"),
                estimated_annual_energy_saving_kwh=Decimal("0"),
                estimated_annual_cost_saving=Decimal("0"),
            )
        )

    if analysis.average_capacity_utilization_fraction < Decimal("0.40"):
        opportunities.append(
            BrownfieldOpportunity(
                opportunity_code="LOW-UTILIZATION",
                category=OpportunityCategory.UTILIZATION,
                priority=OpportunityPriority.MEDIUM,
                title="Review compressor oversizing and sequencing",
                rationale=(
                    "Average demand is low relative to available installed "
                    "capacity. Station sequencing and compressor sizing "
                    "should be reviewed."
                ),
                estimated_power_saving_kw=Decimal("0"),
                estimated_annual_energy_saving_kwh=Decimal("0"),
                estimated_annual_cost_saving=Decimal("0"),
            )
        )

    total_power_saving = sum(
        (item.estimated_power_saving_kw for item in opportunities),
        start=Decimal("0"),
    )

    total_energy_saving = sum(
        (item.estimated_annual_energy_saving_kwh for item in opportunities),
        start=Decimal("0"),
    )

    total_cost_saving = sum(
        (item.estimated_annual_cost_saving for item in opportunities),
        start=Decimal("0"),
    )

    return BrownfieldOpportunityResult(
        audit_code=analysis.audit_code,
        opportunities=tuple(opportunities),
        total_estimated_power_saving_kw=total_power_saving,
        total_estimated_annual_energy_saving_kwh=total_energy_saving,
        total_estimated_annual_cost_saving=total_cost_saving,
    )
