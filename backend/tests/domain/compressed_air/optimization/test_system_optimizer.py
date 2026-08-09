from decimal import Decimal

from app.domain.compressed_air.brownfield.audit_analysis import (
    BrownfieldAuditAnalysisResult,
)
from app.domain.compressed_air.brownfield.opportunity_engine import (
    BrownfieldOpportunity,
    BrownfieldOpportunityResult,
    OpportunityCategory,
    OpportunityPriority,
)
from app.domain.compressed_air.distribution.network_optimizer import (
    NetworkOptimizationResult,
)
from app.domain.compressed_air.optimization.system_optimizer import (
    SystemOptimizationCategory,
    SystemOptimizationPriority,
    optimize_compressed_air_system,
)
from app.domain.compressed_air.skid.skid_models import AirSkidAssessmentResult
from app.domain.compressed_air.station.station_models import (
    CompressorStationCapacityResult,
)


def build_station_capacity(
    *,
    available_is_adequate: bool,
) -> CompressorStationCapacityResult:
    return CompressorStationCapacityResult(
        total_installed_fad_nm3_per_hr=Decimal("5000"),
        available_fad_nm3_per_hr=(Decimal("5000") if available_is_adequate else Decimal("2500")),
        duty_fad_nm3_per_hr=Decimal("1800"),
        standby_fad_nm3_per_hr=Decimal("1800"),
        trim_fad_nm3_per_hr=Decimal("1400"),
        design_flow_nm3_per_hr=Decimal("3000"),
        installed_capacity_margin_nm3_per_hr=Decimal("2000"),
        available_capacity_margin_nm3_per_hr=(
            Decimal("2000") if available_is_adequate else Decimal("-500")
        ),
        design_capacity_is_adequate=True,
        available_capacity_is_adequate=available_is_adequate,
        active_unit_count=2,
        standby_unit_count=1,
    )


def build_skid_assessment(
    *,
    flow_adequate: bool = True,
    pressure_adequate: bool = True,
    instrumentation_complete: bool = True,
) -> AirSkidAssessmentResult:
    return AirSkidAssessmentResult(
        skid_code="SKID-001",
        design_flow_nm3_per_hr=Decimal("3000"),
        design_pressure_bar_g=Decimal("7"),
        total_component_count=12,
        total_pressure_drop_bar=Decimal("0.35"),
        minimum_component_flow_capacity_nm3_per_hr=(
            Decimal("3400") if flow_adequate else Decimal("2500")
        ),
        minimum_component_pressure_rating_bar_g=(
            Decimal("10") if pressure_adequate else Decimal("6.5")
        ),
        flow_capacity_is_adequate=flow_adequate,
        pressure_rating_is_adequate=pressure_adequate,
        has_wet_receiver=True,
        has_dry_receiver=True,
        has_flow_metering=instrumentation_complete,
        has_pressure_monitoring=instrumentation_complete,
        has_dew_point_monitoring=instrumentation_complete,
        master_control_enabled=True,
        instrumentation_is_complete=instrumentation_complete,
        skid_is_adequate=(flow_adequate and pressure_adequate and instrumentation_complete),
    )


def build_distribution_optimization(
    *,
    required: bool,
) -> NetworkOptimizationResult:
    return NetworkOptimizationResult(
        network_code="NET-001",
        deficient_path_codes=(("PATH-C01",) if required else ()),
        recommendations=(),
        total_current_target_segment_drop_bar=(Decimal("0.25") if required else Decimal("0")),
        total_recommended_target_segment_drop_bar=(Decimal("0.10") if required else Decimal("0")),
        estimated_total_pressure_drop_reduction_bar=(Decimal("0.15") if required else Decimal("0")),
        optimization_required=required,
    )


def build_brownfield_analysis(
    *,
    high_unloaded: bool = True,
    significant_leakage: bool = True,
) -> BrownfieldAuditAnalysisResult:
    return BrownfieldAuditAnalysisResult(
        audit_code="AUDIT-001",
        project_id=1,
        installed_capacity_nm3_per_hr=Decimal("5400"),
        available_capacity_nm3_per_hr=Decimal("5400"),
        average_system_flow_nm3_per_hr=Decimal("3000"),
        peak_system_flow_nm3_per_hr=Decimal("4000"),
        minimum_system_flow_nm3_per_hr=Decimal("1800"),
        average_system_power_kw=Decimal("450"),
        peak_system_power_kw=Decimal("600"),
        average_header_pressure_bar_g=Decimal("7.0"),
        maximum_header_pressure_bar_g=Decimal("7.2"),
        minimum_header_pressure_bar_g=Decimal("6.8"),
        average_capacity_utilization_fraction=Decimal("0.55"),
        peak_capacity_utilization_fraction=Decimal("0.74"),
        measured_specific_power_kw_per_nm3_per_min=Decimal("9.0"),
        unloaded_measurement_fraction=(Decimal("0.30") if high_unloaded else Decimal("0.05")),
        leakage_flow_nm3_per_hr=(Decimal("450") if significant_leakage else Decimal("50")),
        leakage_fraction_of_average_demand=(
            Decimal("0.15") if significant_leakage else Decimal("0.02")
        ),
        annual_operating_hours=Decimal("8000"),
        electricity_tariff_per_kwh=Decimal("8"),
        estimated_annual_energy_kwh=Decimal("3600000"),
        estimated_annual_energy_cost=Decimal("28800000"),
        installed_capacity_is_sufficient_for_peak=True,
        high_unloaded_running_detected=high_unloaded,
        significant_leakage_detected=significant_leakage,
    )


def build_brownfield_opportunities() -> BrownfieldOpportunityResult:
    opportunities = (
        BrownfieldOpportunity(
            opportunity_code="LEAK-REPAIR",
            category=OpportunityCategory.LEAKAGE,
            priority=OpportunityPriority.HIGH,
            title="Compressed-air leakage reduction",
            rationale="Leakage is significant.",
            estimated_power_saving_kw=Decimal("40"),
            estimated_annual_energy_saving_kwh=Decimal("320000"),
            estimated_annual_cost_saving=Decimal("2560000"),
        ),
        BrownfieldOpportunity(
            opportunity_code="PRESSURE-REDUCTION",
            category=OpportunityCategory.PRESSURE,
            priority=OpportunityPriority.MEDIUM,
            title="Reduce system operating pressure",
            rationale="Lower pressure is feasible.",
            estimated_power_saving_kw=Decimal("20"),
            estimated_annual_energy_saving_kwh=Decimal("160000"),
            estimated_annual_cost_saving=Decimal("1280000"),
        ),
    )

    return BrownfieldOpportunityResult(
        audit_code="AUDIT-001",
        opportunities=opportunities,
        total_estimated_power_saving_kw=Decimal("60"),
        total_estimated_annual_energy_saving_kwh=Decimal("480000"),
        total_estimated_annual_cost_saving=Decimal("3840000"),
    )


def test_integrated_optimizer_collects_system_issues() -> None:
    result = optimize_compressed_air_system(
        station_capacity=build_station_capacity(
            available_is_adequate=False,
        ),
        skid_assessment=build_skid_assessment(
            flow_adequate=False,
            pressure_adequate=True,
            instrumentation_complete=False,
        ),
        distribution_optimization=build_distribution_optimization(
            required=True,
        ),
        brownfield_analysis=build_brownfield_analysis(),
        brownfield_opportunities=build_brownfield_opportunities(),
    )

    codes = {action.action_code for action in result.actions}

    assert "STATION-CAPACITY-SHORTFALL" in codes
    assert "SKID-FLOW-CAPACITY" in codes
    assert "SKID-INSTRUMENTATION" in codes
    assert "DISTRIBUTION-UPGRADE" in codes
    assert "CONTROL-UNLOAD-REDUCTION" in codes
    assert "LEAKAGE-REDUCTION" in codes
    assert "BF-LEAK-REPAIR" in codes
    assert "BF-PRESSURE-REDUCTION" in codes

    assert result.system_requires_improvement is True


def test_capacity_shortfall_is_critical_priority() -> None:
    result = optimize_compressed_air_system(
        station_capacity=build_station_capacity(
            available_is_adequate=False,
        )
    )

    action = result.actions[0]

    assert action.category == SystemOptimizationCategory.CAPACITY
    assert action.priority == SystemOptimizationPriority.CRITICAL
    assert result.critical_action_count == 1


def test_skid_pressure_rating_issue_is_critical() -> None:
    result = optimize_compressed_air_system(
        skid_assessment=build_skid_assessment(
            pressure_adequate=False,
        )
    )

    action = next(item for item in result.actions if item.action_code == "SKID-PRESSURE-RATING")

    assert action.priority == SystemOptimizationPriority.CRITICAL


def test_distribution_problem_is_high_priority() -> None:
    result = optimize_compressed_air_system(
        distribution_optimization=build_distribution_optimization(
            required=True,
        )
    )

    action = result.actions[0]

    assert action.category == SystemOptimizationCategory.DISTRIBUTION
    assert action.priority == SystemOptimizationPriority.HIGH


def test_brownfield_savings_are_integrated() -> None:
    result = optimize_compressed_air_system(
        brownfield_opportunities=build_brownfield_opportunities(),
    )

    assert result.total_estimated_power_saving_kw == Decimal("60")
    assert result.total_estimated_annual_energy_saving_kwh == Decimal("480000")
    assert result.total_estimated_annual_cost_saving == Decimal("3840000")


def test_healthy_system_has_no_actions() -> None:
    result = optimize_compressed_air_system(
        station_capacity=build_station_capacity(
            available_is_adequate=True,
        ),
        skid_assessment=build_skid_assessment(),
        distribution_optimization=build_distribution_optimization(
            required=False,
        ),
        brownfield_analysis=build_brownfield_analysis(
            high_unloaded=False,
            significant_leakage=False,
        ),
    )

    assert result.actions == ()
    assert result.system_requires_improvement is False
    assert result.critical_action_count == 0
    assert result.high_priority_action_count == 0

    assert result.total_estimated_power_saving_kw == Decimal("0")
    assert result.total_estimated_annual_energy_saving_kwh == Decimal("0")
    assert result.total_estimated_annual_cost_saving == Decimal("0")


def test_actions_are_sorted_by_priority() -> None:
    result = optimize_compressed_air_system(
        station_capacity=build_station_capacity(
            available_is_adequate=False,
        ),
        skid_assessment=build_skid_assessment(
            instrumentation_complete=False,
        ),
        distribution_optimization=build_distribution_optimization(
            required=True,
        ),
    )

    priorities = [action.priority for action in result.actions]

    assert priorities[0] == SystemOptimizationPriority.CRITICAL

    assert priorities[-1] in {
        SystemOptimizationPriority.MEDIUM,
        SystemOptimizationPriority.HIGH,
    }
