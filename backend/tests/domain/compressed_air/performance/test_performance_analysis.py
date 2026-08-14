from decimal import Decimal

import pytest

from app.domain.compressed_air.performance.performance_analysis import (
    InvalidPerformanceAnalysisInputError,
    analyze_performance,
)
from app.domain.compressed_air.performance.performance_models import (
    PerformanceAnalysisInput,
    PerformanceMeasurementPoint,
    PerformanceOperatingState,
)


def measurement(
    *,
    label: str,
    flow: str,
    pressure: str,
    power: str,
    operating_state: PerformanceOperatingState | None = None,
    load_fraction: str | None = None,
) -> PerformanceMeasurementPoint:
    return PerformanceMeasurementPoint(
        timestamp_label=label,
        flow_nm3_per_hr=Decimal(flow),
        pressure_bar_g=Decimal(pressure),
        power_kw=Decimal(power),
        operating_state=operating_state,
        load_fraction=(Decimal(load_fraction) if load_fraction is not None else None),
    )


def base_input(
    *,
    measurements: tuple[PerformanceMeasurementPoint, ...] | None = None,
    optimized_pressure: Decimal | None = None,
) -> PerformanceAnalysisInput:
    return PerformanceAnalysisInput(
        analysis_code="PERF-001",
        measurements=measurements
        or (
            measurement(
                label="Loaded",
                flow="600",
                pressure="7",
                power="90",
                operating_state=PerformanceOperatingState.LOADED,
                load_fraction="1",
            ),
            measurement(
                label="Part Load",
                flow="300",
                pressure="6.5",
                power="60",
                operating_state=PerformanceOperatingState.PART_LOAD,
                load_fraction="0.5",
            ),
            measurement(
                label="Unloaded",
                flow="0",
                pressure="6",
                power="30",
                operating_state=PerformanceOperatingState.UNLOADED,
                load_fraction="0",
            ),
        ),
        annual_operating_hours=Decimal("8000"),
        electricity_tariff_per_kwh=Decimal("8"),
        rated_capacity_nm3_per_hr=Decimal("600"),
        rated_power_kw=Decimal("100"),
        reference_specific_power_kw_per_nm3_per_min=Decimal("10"),
        optimized_discharge_pressure_bar_g=optimized_pressure,
        power_penalty_fraction_per_bar=Decimal("0.07"),
    )


def test_analyze_performance_calculates_measured_system_kpis() -> None:
    result = analyze_performance(base_input())

    assert result.measurement_count == 3

    assert result.average_flow_nm3_per_hr == Decimal("300")
    assert result.peak_flow_nm3_per_hr == Decimal("600")
    assert result.minimum_flow_nm3_per_hr == Decimal("0")

    assert result.average_pressure_bar_g == Decimal("6.5")
    assert result.maximum_pressure_bar_g == Decimal("7")
    assert result.minimum_pressure_bar_g == Decimal("6")

    assert result.average_power_kw == Decimal("60")
    assert result.peak_power_kw == Decimal("90")


def test_analyze_performance_calculates_specific_power_and_energy() -> None:
    result = analyze_performance(base_input())

    assert result.measured_specific_power_kw_per_nm3_per_min == Decimal("12")
    assert result.measured_specific_energy_kwh_per_1000_nm3 == Decimal("200")


def test_analyze_performance_calculates_utilization_and_deviation() -> None:
    result = analyze_performance(base_input())

    assert result.average_load_fraction == Decimal("0.5")

    assert result.unloaded_measurement_fraction == Decimal("1") / Decimal("3")

    assert result.average_capacity_utilization_fraction == Decimal("0.5")
    assert result.peak_capacity_utilization_fraction == Decimal("1")
    assert result.average_power_utilization_fraction == Decimal("0.6")

    assert result.specific_power_deviation_fraction == Decimal("0.2")


def test_analyze_performance_calculates_annual_energy_and_cost() -> None:
    result = analyze_performance(base_input())

    assert result.annual_energy_kwh == Decimal("480000")
    assert result.annual_energy_cost == Decimal("3840000")


def test_analyze_performance_reuses_pressure_energy_engine() -> None:
    result = analyze_performance(
        base_input(
            optimized_pressure=Decimal("6"),
        )
    )

    pressure = result.pressure_energy

    assert pressure is not None

    assert pressure.current_discharge_pressure_bar_g == Decimal("6.5")
    assert pressure.optimized_discharge_pressure_bar_g == Decimal("6")
    assert pressure.pressure_reduction_bar == Decimal("0.5")

    assert pressure.power_saving_fraction == Decimal("0.035")
    assert pressure.estimated_power_saving_kw == Decimal("2.100")
    assert pressure.estimated_optimized_power_kw == Decimal("57.900")

    assert pressure.annual_energy_saving_kwh == Decimal("16800.000")
    assert pressure.annual_cost_saving == Decimal("134400.000")


def test_zero_flow_returns_no_specific_performance_metric() -> None:
    inputs = PerformanceAnalysisInput(
        analysis_code="PERF-ZERO-FLOW",
        measurements=(
            measurement(
                label="Idle",
                flow="0",
                pressure="6",
                power="20",
                operating_state=PerformanceOperatingState.UNLOADED,
            ),
        ),
        annual_operating_hours=Decimal("1000"),
        electricity_tariff_per_kwh=Decimal("5"),
    )

    result = analyze_performance(inputs)

    assert result.measured_specific_power_kw_per_nm3_per_min is None
    assert result.measured_specific_energy_kwh_per_1000_nm3 is None
    assert result.annual_energy_kwh == Decimal("20000")
    assert result.annual_energy_cost == Decimal("100000")


def test_empty_analysis_code_is_rejected() -> None:
    inputs = base_input()
    inputs = PerformanceAnalysisInput(
        analysis_code=" ",
        measurements=inputs.measurements,
        annual_operating_hours=inputs.annual_operating_hours,
    )

    with pytest.raises(
        InvalidPerformanceAnalysisInputError,
        match="Analysis code cannot be empty",
    ):
        analyze_performance(inputs)


def test_negative_measurement_flow_is_rejected() -> None:
    inputs = base_input(
        measurements=(
            measurement(
                label="Invalid",
                flow="-1",
                pressure="7",
                power="50",
            ),
        )
    )

    with pytest.raises(
        InvalidPerformanceAnalysisInputError,
        match="flow cannot be negative",
    ):
        analyze_performance(inputs)


def test_invalid_load_fraction_is_rejected() -> None:
    inputs = base_input(
        measurements=(
            measurement(
                label="Invalid Load",
                flow="500",
                pressure="7",
                power="80",
                load_fraction="1.1",
            ),
        )
    )

    with pytest.raises(
        InvalidPerformanceAnalysisInputError,
        match="load fraction must be between zero and one",
    ):
        analyze_performance(inputs)


def test_pressure_optimization_requires_positive_average_power() -> None:
    inputs = PerformanceAnalysisInput(
        analysis_code="PERF-ZERO-POWER",
        measurements=(
            measurement(
                label="Stopped",
                flow="0",
                pressure="6",
                power="0",
                operating_state=PerformanceOperatingState.STOPPED,
            ),
        ),
        annual_operating_hours=Decimal("1000"),
        optimized_discharge_pressure_bar_g=Decimal("5.5"),
    )

    with pytest.raises(
        InvalidPerformanceAnalysisInputError,
        match="Pressure optimization requires average measured power",
    ):
        analyze_performance(inputs)
