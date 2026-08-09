from decimal import Decimal

import pytest

from app.domain.compressed_air.brownfield.audit_models import (
    AuditOperatingState,
    BrownfieldAuditCase,
    CompressorMeasurementPoint,
    ExistingCompressor,
    LeakageSurveySummary,
    SystemMeasurementPoint,
)
from app.domain.compressed_air.brownfield.system_engine import (
    BrownfieldSystemEngineInput,
    InvalidBrownfieldSystemEngineInputError,
    analyze_brownfield_system,
)
from app.domain.compressed_air.station.station_models import (
    CompressorControlMode,
    CompressorTechnology,
)


def build_compressor(
    *,
    unit_code: str,
    rated_fad: str,
    motor_power: str,
) -> ExistingCompressor:
    return ExistingCompressor(
        unit_code=unit_code,
        manufacturer="TEST",
        model="TEST-MODEL",
        technology=CompressorTechnology.ROTARY_SCREW_OIL_INJECTED,
        control_mode=CompressorControlMode.LOAD_UNLOAD,
        rated_fad_nm3_per_hr=Decimal(rated_fad),
        rated_discharge_pressure_bar_g=Decimal("7.0"),
        rated_motor_power_kw=Decimal(motor_power),
    )


def build_audit() -> BrownfieldAuditCase:
    return BrownfieldAuditCase(
        audit_code="BF-SYS-001",
        project_id=1,
        compressors=(
            build_compressor(
                unit_code="AC-01",
                rated_fad="1800",
                motor_power="250",
            ),
            build_compressor(
                unit_code="AC-02",
                rated_fad="1800",
                motor_power="250",
            ),
            build_compressor(
                unit_code="AC-03",
                rated_fad="1800",
                motor_power="250",
            ),
        ),
        compressor_measurements=(
            CompressorMeasurementPoint(
                unit_code="AC-01",
                timestamp_label="T1",
                operating_state=AuditOperatingState.LOADED,
                measured_flow_nm3_per_hr=Decimal("1500"),
                measured_discharge_pressure_bar_g=Decimal("7.1"),
                measured_power_kw=Decimal("225"),
            ),
            CompressorMeasurementPoint(
                unit_code="AC-02",
                timestamp_label="T1",
                operating_state=AuditOperatingState.UNLOADED,
                measured_flow_nm3_per_hr=Decimal("100"),
                measured_discharge_pressure_bar_g=Decimal("7.1"),
                measured_power_kw=Decimal("80"),
            ),
            CompressorMeasurementPoint(
                unit_code="AC-01",
                timestamp_label="T2",
                operating_state=AuditOperatingState.LOADED,
                measured_flow_nm3_per_hr=Decimal("1600"),
                measured_discharge_pressure_bar_g=Decimal("7.0"),
                measured_power_kw=Decimal("230"),
            ),
            CompressorMeasurementPoint(
                unit_code="AC-02",
                timestamp_label="T2",
                operating_state=AuditOperatingState.UNLOADED,
                measured_flow_nm3_per_hr=Decimal("120"),
                measured_discharge_pressure_bar_g=Decimal("7.0"),
                measured_power_kw=Decimal("82"),
            ),
        ),
        system_measurements=(
            SystemMeasurementPoint(
                timestamp_label="T1",
                total_flow_nm3_per_hr=Decimal("2200"),
                header_pressure_bar_g=Decimal("7.1"),
                total_power_kw=Decimal("340"),
                production_state="LOW",
            ),
            SystemMeasurementPoint(
                timestamp_label="T2",
                total_flow_nm3_per_hr=Decimal("3000"),
                header_pressure_bar_g=Decimal("7.0"),
                total_power_kw=Decimal("450"),
                production_state="NORMAL",
            ),
            SystemMeasurementPoint(
                timestamp_label="T3",
                total_flow_nm3_per_hr=Decimal("4000"),
                header_pressure_bar_g=Decimal("6.9"),
                total_power_kw=Decimal("580"),
                production_state="PEAK",
            ),
        ),
        leakage_summary=LeakageSurveySummary(
            measured_leakage_flow_nm3_per_hr=Decimal("450"),
            survey_method="Plant shutdown flow test",
            estimated_repair_fraction=Decimal("0.80"),
        ),
        electricity_tariff_per_kwh=Decimal("8"),
        annual_operating_hours=Decimal("8000"),
    )


def test_complete_brownfield_system_analysis() -> None:
    result = analyze_brownfield_system(
        BrownfieldSystemEngineInput(
            audit=build_audit(),
            optimized_discharge_pressure_bar_g=Decimal("6.5"),
            expected_leak_repair_fraction=Decimal("0.80"),
            power_penalty_fraction_per_bar=Decimal("0.07"),
        )
    )

    assert result.audit_analysis.audit_code == "BF-SYS-001"

    assert result.audit_analysis.average_system_flow_nm3_per_hr > Decimal("0")
    assert result.audit_analysis.average_system_power_kw > Decimal("0")

    assert result.leakage_energy is not None
    assert result.pressure_energy is not None

    assert result.opportunities.opportunities
    assert result.optimization.actions

    assert result.current_annual_energy_kwh > Decimal("0")
    assert result.current_annual_energy_cost > Decimal("0")

    assert result.estimated_total_power_saving_kw > Decimal("0")
    assert result.estimated_total_annual_energy_saving_kwh > Decimal("0")
    assert result.estimated_total_annual_cost_saving > Decimal("0")

    assert result.estimated_optimized_average_power_kw < result.current_average_power_kw

    assert result.estimated_optimized_annual_energy_kwh < result.current_annual_energy_kwh

    assert result.estimated_optimized_annual_energy_cost < result.current_annual_energy_cost

    assert result.estimated_energy_reduction_fraction > Decimal("0")


def test_leakage_energy_is_generated_for_significant_leakage() -> None:
    result = analyze_brownfield_system(
        BrownfieldSystemEngineInput(
            audit=build_audit(),
        )
    )

    assert result.leakage_energy is not None

    assert result.leakage_energy.leakage_flow_nm3_per_hr == Decimal("450")
    assert result.leakage_energy.recoverable_power_kw > Decimal("0")


def test_pressure_energy_is_optional() -> None:
    result = analyze_brownfield_system(
        BrownfieldSystemEngineInput(
            audit=build_audit(),
            optimized_discharge_pressure_bar_g=None,
        )
    )

    assert result.pressure_energy is None


def test_pressure_reduction_saving_is_generated() -> None:
    result = analyze_brownfield_system(
        BrownfieldSystemEngineInput(
            audit=build_audit(),
            optimized_discharge_pressure_bar_g=Decimal("6.5"),
        )
    )

    assert result.pressure_energy is not None
    assert result.pressure_energy.pressure_reduction_bar > Decimal("0")
    assert result.pressure_energy.estimated_power_saving_kw > Decimal("0")
    assert result.pressure_energy.annual_cost_saving > Decimal("0")


def test_total_saving_does_not_make_energy_negative() -> None:
    result = analyze_brownfield_system(
        BrownfieldSystemEngineInput(
            audit=build_audit(),
            optimized_discharge_pressure_bar_g=Decimal("0"),
            expected_leak_repair_fraction=Decimal("1"),
            power_penalty_fraction_per_bar=Decimal("1"),
        )
    )

    assert result.estimated_optimized_average_power_kw >= Decimal("0")
    assert result.estimated_optimized_annual_energy_kwh >= Decimal("0")
    assert result.estimated_optimized_annual_energy_cost >= Decimal("0")


def test_invalid_leak_repair_fraction_is_rejected() -> None:
    with pytest.raises(
        InvalidBrownfieldSystemEngineInputError,
        match="Expected leak repair fraction must be between zero and one",
    ):
        analyze_brownfield_system(
            BrownfieldSystemEngineInput(
                audit=build_audit(),
                expected_leak_repair_fraction=Decimal("1.10"),
            )
        )


def test_invalid_pressure_penalty_fraction_is_rejected() -> None:
    with pytest.raises(
        InvalidBrownfieldSystemEngineInputError,
        match="Power penalty fraction per bar must be between zero and one",
    ):
        analyze_brownfield_system(
            BrownfieldSystemEngineInput(
                audit=build_audit(),
                power_penalty_fraction_per_bar=Decimal("1.10"),
            )
        )


def test_negative_optimized_pressure_is_rejected() -> None:
    with pytest.raises(
        InvalidBrownfieldSystemEngineInputError,
        match="Optimized discharge pressure cannot be negative",
    ):
        analyze_brownfield_system(
            BrownfieldSystemEngineInput(
                audit=build_audit(),
                optimized_discharge_pressure_bar_g=Decimal("-0.1"),
            )
        )
