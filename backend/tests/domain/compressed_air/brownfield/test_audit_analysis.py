from decimal import Decimal

import pytest

from app.domain.compressed_air.brownfield.audit_analysis import (
    InvalidBrownfieldAuditInputError,
    analyze_brownfield_audit,
)
from app.domain.compressed_air.brownfield.audit_models import (
    AuditOperatingState,
    BrownfieldAuditCase,
    CompressorMeasurementPoint,
    ExistingCompressor,
    LeakageSurveySummary,
    SystemMeasurementPoint,
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
    available: bool = True,
) -> ExistingCompressor:
    return ExistingCompressor(
        unit_code=unit_code,
        equipment_source="TEST",
        model="TEST-MODEL",
        technology=CompressorTechnology.ROTARY_SCREW_OIL_INJECTED,
        control_mode=CompressorControlMode.LOAD_UNLOAD,
        rated_fad_nm3_per_hr=Decimal(rated_fad),
        rated_discharge_pressure_bar_g=Decimal("7.0"),
        rated_motor_power_kw=Decimal(motor_power),
        available=available,
    )


def build_audit() -> BrownfieldAuditCase:
    return BrownfieldAuditCase(
        audit_code="AUDIT-001",
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
                unit_code="AC-03",
                timestamp_label="T1",
                operating_state=AuditOperatingState.STOPPED,
                measured_flow_nm3_per_hr=Decimal("0"),
                measured_discharge_pressure_bar_g=Decimal("0"),
                measured_power_kw=Decimal("0"),
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
                total_flow_nm3_per_hr=Decimal("2000"),
                header_pressure_bar_g=Decimal("6.9"),
                total_power_kw=Decimal("320"),
                production_state="LOW",
            ),
            SystemMeasurementPoint(
                timestamp_label="T2",
                total_flow_nm3_per_hr=Decimal("3000"),
                header_pressure_bar_g=Decimal("6.8"),
                total_power_kw=Decimal("430"),
                production_state="NORMAL",
            ),
            SystemMeasurementPoint(
                timestamp_label="T3",
                total_flow_nm3_per_hr=Decimal("4000"),
                header_pressure_bar_g=Decimal("6.7"),
                total_power_kw=Decimal("560"),
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


def test_analyze_brownfield_audit() -> None:
    result = analyze_brownfield_audit(build_audit())

    assert result.audit_code == "AUDIT-001"
    assert result.project_id == 1

    assert result.installed_capacity_nm3_per_hr == Decimal("5400")
    assert result.available_capacity_nm3_per_hr == Decimal("5400")

    assert result.average_system_flow_nm3_per_hr == Decimal("3000")
    assert result.minimum_system_flow_nm3_per_hr == Decimal("2000")
    assert result.peak_system_flow_nm3_per_hr == Decimal("4000")

    assert result.average_system_power_kw == (
        Decimal("320") + Decimal("430") + Decimal("560")
    ) / Decimal("3")

    assert result.average_capacity_utilization_fraction == (Decimal("3000") / Decimal("5400"))

    assert result.peak_capacity_utilization_fraction == (Decimal("4000") / Decimal("5400"))


def test_measured_specific_power_is_calculated() -> None:
    result = analyze_brownfield_audit(build_audit())

    expected_specific_power = result.average_system_power_kw / (Decimal("3000") / Decimal("60"))

    assert result.measured_specific_power_kw_per_nm3_per_min == (expected_specific_power)


def test_unloaded_running_is_detected() -> None:
    result = analyze_brownfield_audit(build_audit())

    assert result.unloaded_measurement_fraction == Decimal("2") / Decimal("5")
    assert result.high_unloaded_running_detected is True


def test_significant_leakage_is_detected() -> None:
    result = analyze_brownfield_audit(build_audit())

    assert result.leakage_flow_nm3_per_hr == Decimal("450")

    assert result.leakage_fraction_of_average_demand == (Decimal("450") / Decimal("3000"))

    assert result.significant_leakage_detected is True


def test_annual_energy_and_cost_are_estimated() -> None:
    result = analyze_brownfield_audit(build_audit())

    assert result.estimated_annual_energy_kwh == (result.average_system_power_kw * Decimal("8000"))

    assert result.estimated_annual_energy_cost == (
        result.estimated_annual_energy_kwh * Decimal("8")
    )


def test_peak_capacity_is_sufficient() -> None:
    result = analyze_brownfield_audit(build_audit())

    assert result.available_capacity_nm3_per_hr == Decimal("5400")
    assert result.peak_system_flow_nm3_per_hr == Decimal("4000")
    assert result.installed_capacity_is_sufficient_for_peak is True


def test_unavailable_compressor_reduces_available_capacity() -> None:
    audit = build_audit()

    compressors = (
        audit.compressors[0],
        audit.compressors[1],
        build_compressor(
            unit_code="AC-03",
            rated_fad="1800",
            motor_power="250",
            available=False,
        ),
    )

    modified = BrownfieldAuditCase(
        audit_code=audit.audit_code,
        project_id=audit.project_id,
        compressors=compressors,
        compressor_measurements=audit.compressor_measurements,
        system_measurements=audit.system_measurements,
        leakage_summary=audit.leakage_summary,
        observations=audit.observations,
        electricity_tariff_per_kwh=audit.electricity_tariff_per_kwh,
        annual_operating_hours=audit.annual_operating_hours,
        notes=audit.notes,
    )

    result = analyze_brownfield_audit(modified)

    assert result.installed_capacity_nm3_per_hr == Decimal("5400")
    assert result.available_capacity_nm3_per_hr == Decimal("3600")

    assert result.installed_capacity_is_sufficient_for_peak is False


def test_missing_system_measurements_is_rejected() -> None:
    audit = build_audit()

    invalid = BrownfieldAuditCase(
        audit_code=audit.audit_code,
        project_id=audit.project_id,
        compressors=audit.compressors,
        compressor_measurements=audit.compressor_measurements,
        system_measurements=(),
        leakage_summary=audit.leakage_summary,
        electricity_tariff_per_kwh=audit.electricity_tariff_per_kwh,
        annual_operating_hours=audit.annual_operating_hours,
    )

    with pytest.raises(
        InvalidBrownfieldAuditInputError,
        match="At least one system measurement is required",
    ):
        analyze_brownfield_audit(invalid)


def test_zero_operating_hours_is_rejected() -> None:
    audit = build_audit()

    invalid = BrownfieldAuditCase(
        audit_code=audit.audit_code,
        project_id=audit.project_id,
        compressors=audit.compressors,
        compressor_measurements=audit.compressor_measurements,
        system_measurements=audit.system_measurements,
        leakage_summary=audit.leakage_summary,
        electricity_tariff_per_kwh=audit.electricity_tariff_per_kwh,
        annual_operating_hours=Decimal("0"),
    )

    with pytest.raises(
        InvalidBrownfieldAuditInputError,
        match="Annual operating hours must be greater than zero",
    ):
        analyze_brownfield_audit(invalid)


def test_invalid_leakage_repair_fraction_is_rejected() -> None:
    audit = build_audit()

    invalid = BrownfieldAuditCase(
        audit_code=audit.audit_code,
        project_id=audit.project_id,
        compressors=audit.compressors,
        compressor_measurements=audit.compressor_measurements,
        system_measurements=audit.system_measurements,
        leakage_summary=LeakageSurveySummary(
            measured_leakage_flow_nm3_per_hr=Decimal("450"),
            survey_method="Test",
            estimated_repair_fraction=Decimal("1.10"),
        ),
        electricity_tariff_per_kwh=audit.electricity_tariff_per_kwh,
        annual_operating_hours=audit.annual_operating_hours,
    )

    with pytest.raises(
        InvalidBrownfieldAuditInputError,
        match="Estimated repair fraction must be between zero and one",
    ):
        analyze_brownfield_audit(invalid)
