from decimal import Decimal

from app.domain.compressed_air.brownfield.audit_analysis import (
    BrownfieldAuditAnalysisResult,
)
from app.domain.compressed_air.brownfield.opportunity_engine import (
    OpportunityCategory,
    OpportunityPriority,
    identify_brownfield_opportunities,
)


def build_analysis(
    *,
    significant_leakage: bool = True,
    high_unloaded: bool = True,
    capacity_sufficient: bool = True,
    average_utilization: str = "0.55",
) -> BrownfieldAuditAnalysisResult:
    return BrownfieldAuditAnalysisResult(
        audit_code="AUDIT-OPP-001",
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
        average_capacity_utilization_fraction=Decimal(average_utilization),
        peak_capacity_utilization_fraction=Decimal("0.74"),
        measured_specific_power_kw_per_nm3_per_min=Decimal("9.0"),
        unloaded_measurement_fraction=(Decimal("0.30") if high_unloaded else Decimal("0.05")),
        leakage_flow_nm3_per_hr=(Decimal("450") if significant_leakage else Decimal("100")),
        leakage_fraction_of_average_demand=(
            Decimal("0.15") if significant_leakage else Decimal("0.03")
        ),
        annual_operating_hours=Decimal("8000"),
        electricity_tariff_per_kwh=Decimal("8"),
        estimated_annual_energy_kwh=Decimal("3600000"),
        estimated_annual_energy_cost=Decimal("28800000"),
        installed_capacity_is_sufficient_for_peak=capacity_sufficient,
        high_unloaded_running_detected=high_unloaded,
        significant_leakage_detected=significant_leakage,
    )


def test_leakage_opportunity_is_identified() -> None:
    result = identify_brownfield_opportunities(
        analysis=build_analysis(),
        expected_leak_repair_fraction=Decimal("0.80"),
    )

    leakage = next(
        item for item in result.opportunities if item.category == OpportunityCategory.LEAKAGE
    )

    assert leakage.opportunity_code == "LEAK-REPAIR"
    assert leakage.priority == OpportunityPriority.HIGH
    assert leakage.estimated_power_saving_kw > Decimal("0")
    assert leakage.estimated_annual_energy_saving_kwh > Decimal("0")
    assert leakage.estimated_annual_cost_saving > Decimal("0")


def test_unloaded_running_opportunity_is_identified() -> None:
    result = identify_brownfield_opportunities(
        analysis=build_analysis(),
    )

    unload = next(
        item
        for item in result.opportunities
        if item.category == OpportunityCategory.UNLOADED_RUNNING
    )

    assert unload.opportunity_code == "UNLOAD-REDUCTION"
    assert unload.priority == OpportunityPriority.HIGH
    assert unload.estimated_power_saving_kw > Decimal("0")
    assert unload.estimated_annual_cost_saving > Decimal("0")


def test_pressure_reduction_opportunity_is_identified() -> None:
    result = identify_brownfield_opportunities(
        analysis=build_analysis(),
        optimized_discharge_pressure_bar_g=Decimal("6.5"),
        power_penalty_fraction_per_bar=Decimal("0.07"),
    )

    pressure = next(
        item for item in result.opportunities if item.category == OpportunityCategory.PRESSURE
    )

    assert pressure.opportunity_code == "PRESSURE-REDUCTION"
    assert pressure.priority == OpportunityPriority.MEDIUM
    assert pressure.estimated_power_saving_kw > Decimal("0")
    assert pressure.estimated_annual_energy_saving_kwh > Decimal("0")


def test_capacity_shortfall_opportunity_is_identified() -> None:
    result = identify_brownfield_opportunities(
        analysis=build_analysis(
            capacity_sufficient=False,
        ),
    )

    capacity = next(
        item for item in result.opportunities if item.category == OpportunityCategory.CAPACITY
    )

    assert capacity.opportunity_code == "CAPACITY-REVIEW"
    assert capacity.priority == OpportunityPriority.HIGH


def test_low_utilization_opportunity_is_identified() -> None:
    result = identify_brownfield_opportunities(
        analysis=build_analysis(
            average_utilization="0.30",
        ),
    )

    utilization = next(
        item for item in result.opportunities if item.category == OpportunityCategory.UTILIZATION
    )

    assert utilization.opportunity_code == "LOW-UTILIZATION"
    assert utilization.priority == OpportunityPriority.MEDIUM


def test_healthy_analysis_does_not_create_unnecessary_opportunities() -> None:
    analysis = build_analysis(
        significant_leakage=False,
        high_unloaded=False,
        capacity_sufficient=True,
        average_utilization="0.60",
    )

    result = identify_brownfield_opportunities(
        analysis=analysis,
    )

    categories = {item.category for item in result.opportunities}

    assert OpportunityCategory.LEAKAGE not in categories
    assert OpportunityCategory.UNLOADED_RUNNING not in categories
    assert OpportunityCategory.CAPACITY not in categories
    assert OpportunityCategory.UTILIZATION not in categories
    assert OpportunityCategory.PRESSURE not in categories


def test_total_savings_equal_sum_of_opportunities() -> None:
    result = identify_brownfield_opportunities(
        analysis=build_analysis(),
        optimized_discharge_pressure_bar_g=Decimal("6.5"),
    )

    expected_power = sum(
        (item.estimated_power_saving_kw for item in result.opportunities),
        start=Decimal("0"),
    )

    expected_energy = sum(
        (item.estimated_annual_energy_saving_kwh for item in result.opportunities),
        start=Decimal("0"),
    )

    expected_cost = sum(
        (item.estimated_annual_cost_saving for item in result.opportunities),
        start=Decimal("0"),
    )

    assert result.total_estimated_power_saving_kw == expected_power
    assert result.total_estimated_annual_energy_saving_kwh == expected_energy
    assert result.total_estimated_annual_cost_saving == expected_cost
