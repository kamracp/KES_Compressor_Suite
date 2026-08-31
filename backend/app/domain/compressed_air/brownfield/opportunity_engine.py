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
from app.domain.compressed_air.energy.motor_pfc import (
    MotorMeasurementInput,
    calculate_motor_pfc,
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
    CONDENSATE_DRAIN = "CONDENSATE_DRAIN"
    FILTER_EFFICIENCY = "FILTER_EFFICIENCY"
    POWER_FACTOR = "POWER_FACTOR"


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
    demand_saving_control_factor: Decimal = Decimal("1"),
    optimized_discharge_pressure_bar_g: Decimal | None = None,
    power_penalty_fraction_per_bar: Decimal | None = None,
    # Condensate drain air loss: total Nm³/hr lost through all timed
    # solenoid drains firing regardless of condensate level.
    # Zero-loss (float/electronic) drains eliminate this waste entirely.
    # Ref: US DOE / Compressed Air Challenge, 'Improving Compressed Air
    # System Performance: A Sourcebook for Industry'.
    condensate_drain_air_loss_nm3_per_hr: Decimal | None = None,
    # Extra pressure drop across dirty/undersized filters beyond their
    # clean design delta-p. Compressor must generate this additional
    # pressure, incurring extra power. Ref: DOE/CAC sourcebook;
    # manufacturer filter performance curves.
    filter_excess_pressure_drop_bar: Decimal | None = None,
    # Field-measured motor electrical data (line voltage, line current,
    # power factor) for the compressor motor. When supplied, the required
    # power-factor correction capacitor bank is sized per IS 15167.
    motor_measurement: MotorMeasurementInput | None = None,
    # Power-factor penalty (or kVAh surcharge) the utility is currently
    # billing the site, per year, in local currency. USER-SUPPLIED ONLY:
    # tariff penalty structures vary by state utility, so no default is
    # assumed and no penalty saving is claimed without this figure.
    pf_penalty_annual_cost: Decimal | None = None,
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
                demand_saving_control_factor=(demand_saving_control_factor),
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

    # ── Condensate drain opportunity ─────────────────────────────────
    if (
        condensate_drain_air_loss_nm3_per_hr is not None
        and condensate_drain_air_loss_nm3_per_hr > 0
        and analysis.measured_specific_power_kw_per_nm3_per_min is not None
    ):
        drain_energy = calculate_leakage_energy(
            LeakageEnergyInput(
                leakage_flow_nm3_per_hr=condensate_drain_air_loss_nm3_per_hr,
                specific_power_kw_per_nm3_per_min=(
                    analysis.measured_specific_power_kw_per_nm3_per_min
                ),
                annual_operating_hours=analysis.annual_operating_hours,
                electricity_tariff_per_kwh=analysis.electricity_tariff_per_kwh,
                expected_repair_fraction=Decimal("1"),
                demand_saving_control_factor=demand_saving_control_factor,
            )
        )
        opportunities.append(
            BrownfieldOpportunity(
                opportunity_code="CONDENSATE-DRAIN",
                category=OpportunityCategory.CONDENSATE_DRAIN,
                priority=OpportunityPriority.MEDIUM,
                title="Replace timed condensate drains with zero-loss drains",
                rationale=(
                    "Timed solenoid drains expel compressed air with every "
                    "cycle regardless of condensate level. Zero-loss "
                    "(float or electronic) drains eliminate this waste "
                    "entirely. Ref: DOE / Compressed Air Challenge "
                    "Sourcebook for Industry."
                ),
                estimated_power_saving_kw=drain_energy.recoverable_power_kw,
                estimated_annual_energy_saving_kwh=drain_energy.annual_energy_saving_kwh,
                estimated_annual_cost_saving=drain_energy.annual_cost_saving,
            )
        )

    # ── Filter pressure-drop penalty opportunity ──────────────────────
    if filter_excess_pressure_drop_bar is not None and filter_excess_pressure_drop_bar > 0:
        filter_pressure_result = calculate_pressure_energy_saving(
            PressureEnergyInput(
                current_discharge_pressure_bar_g=(
                    analysis.average_header_pressure_bar_g + filter_excess_pressure_drop_bar
                ),
                optimized_discharge_pressure_bar_g=(analysis.average_header_pressure_bar_g),
                current_average_power_kw=analysis.average_system_power_kw,
                annual_operating_hours=analysis.annual_operating_hours,
                electricity_tariff_per_kwh=analysis.electricity_tariff_per_kwh,
                power_penalty_fraction_per_bar=power_penalty_fraction_per_bar,
            )
        )
        if filter_pressure_result.pressure_reduction_is_beneficial:
            opportunities.append(
                BrownfieldOpportunity(
                    opportunity_code="FILTER-PENALTY",
                    category=OpportunityCategory.FILTER_EFFICIENCY,
                    priority=OpportunityPriority.MEDIUM,
                    title="Restore or upgrade filter elements to reduce pressure drop",
                    rationale=(
                        "Blocked or undersized filter elements force the "
                        "compressor to generate extra pressure to compensate, "
                        "incurring avoidable power. Replacing or upgrading "
                        "filter elements to their clean design delta-p recovers "
                        "this energy. Ref: DOE / Compressed Air Challenge "
                        "Sourcebook for Industry; manufacturer filter curves."
                    ),
                    estimated_power_saving_kw=(filter_pressure_result.estimated_power_saving_kw),
                    estimated_annual_energy_saving_kwh=(
                        filter_pressure_result.annual_energy_saving_kwh
                    ),
                    estimated_annual_cost_saving=(filter_pressure_result.annual_cost_saving),
                )
            )

    # -- Power-factor correction opportunity --------------------------
    #
    # HONESTY NOTE (project Rule 1): power-factor correction does NOT
    # reduce the motor's active power draw. The capacitor supplies
    # reactive current locally, which reduces line current, transformer
    # and cable loading, I2R distribution losses and -- in most Indian
    # state tariffs -- the PF penalty / kVAh surcharge on the bill.
    # Therefore this opportunity reports ZERO kW and ZERO kWh saving,
    # and reports a cost saving only when the site has told us the PF
    # penalty it is actually being billed.
    #
    # Refs: IEEE Std 141 (Red Book) three-phase power measurement;
    # IS 15167 shunt capacitor kVAr sizing.
    if motor_measurement is not None:
        pfc = calculate_motor_pfc(motor_measurement)

        if pfc.pfc_correction_beneficial:
            avoided_penalty = (
                pf_penalty_annual_cost if pf_penalty_annual_cost is not None else Decimal("0")
            )

            opportunities.append(
                BrownfieldOpportunity(
                    opportunity_code="PF-CORRECTION",
                    category=OpportunityCategory.POWER_FACTOR,
                    priority=(
                        OpportunityPriority.MEDIUM
                        if avoided_penalty > 0
                        else OpportunityPriority.LOW
                    ),
                    title=(
                        "Install "
                        f"{pfc.required_capacitor_kvar} kVAr power-factor "
                        "correction at the compressor motor"
                    ),
                    rationale=(
                        "Measured power factor "
                        f"{pfc.measured_power_factor} is below the target "
                        f"{pfc.target_power_factor}. Measured active power "
                        f"{pfc.measured_active_power_kw} kW "
                        "(P = sqrt3 x V x I x PF, IEEE Std 141) draws "
                        f"{pfc.measured_reactive_power_kvar} kVAr reactive; "
                        "a capacitor bank of "
                        f"{pfc.required_capacitor_kvar} kVAr "
                        "(Qc = P x (tan phi1 - tan phi2), IS 15167) brings "
                        "the motor to target. Power-factor correction "
                        "reduces reactive current, cable and transformer "
                        "loading and the utility PF penalty; it does NOT "
                        "reduce the motor active power draw, so no kW or "
                        "kWh saving is claimed here. The cost saving shown "
                        "is the annual PF penalty reported by the site; "
                        "where no penalty figure was supplied it is zero."
                    ),
                    estimated_power_saving_kw=Decimal("0"),
                    estimated_annual_energy_saving_kwh=Decimal("0"),
                    estimated_annual_cost_saving=avoided_penalty,
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
