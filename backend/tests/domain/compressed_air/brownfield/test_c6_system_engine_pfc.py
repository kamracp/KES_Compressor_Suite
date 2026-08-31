"""
C-6 system engine tests — motor/PFC result carried through the
integrated Brownfield analysis.

The engine must expose the measured motor power and capacitor sizing
(IEEE Std 141 / IS 15167) as structured data, and must never let a
power-factor opportunity inflate the station energy-saving totals.
"""

from decimal import Decimal

import pytest

from app.domain.compressed_air.brownfield.audit_models import (
    AuditOperatingState,
    BrownfieldAuditCase,
    CompressorMeasurementPoint,
    ExistingCompressor,
    SystemMeasurementPoint,
)
from app.domain.compressed_air.brownfield.system_engine import (
    BrownfieldSystemEngineInput,
    analyze_brownfield_system,
)
from app.domain.compressed_air.energy.motor_pfc import MotorMeasurementInput
from app.domain.compressed_air.station.station_models import (
    CompressorControlMode,
    CompressorTechnology,
)


def _audit() -> BrownfieldAuditCase:
    compressor = ExistingCompressor(
        unit_code="C-01",
        equipment_source="TEST",
        model="TEST",
        technology=CompressorTechnology.ROTARY_SCREW_OIL_INJECTED,
        control_mode=CompressorControlMode.LOAD_UNLOAD,
        rated_fad_nm3_per_hr=Decimal("600"),
        rated_discharge_pressure_bar_g=Decimal("7.0"),
        rated_motor_power_kw=Decimal("55"),
    )
    return BrownfieldAuditCase(
        audit_code="C6-SE-TEST",
        project_id=1,
        compressors=(compressor,),
        compressor_measurements=(
            CompressorMeasurementPoint(
                unit_code="C-01",
                timestamp_label="T1",
                operating_state=AuditOperatingState.LOADED,
                measured_flow_nm3_per_hr=Decimal("300"),
                measured_discharge_pressure_bar_g=Decimal("7.0"),
                measured_power_kw=Decimal("45"),
            ),
        ),
        system_measurements=(
            SystemMeasurementPoint(
                timestamp_label="T1",
                total_flow_nm3_per_hr=Decimal("300"),
                header_pressure_bar_g=Decimal("6.8"),
                total_power_kw=Decimal("45"),
            ),
        ),
        electricity_tariff_per_kwh=Decimal("8"),
        annual_operating_hours=Decimal("8000"),
    )


def _motor() -> MotorMeasurementInput:
    return MotorMeasurementInput(
        measured_voltage_v=Decimal("415"),
        measured_current_a=Decimal("78"),
        measured_power_factor=Decimal("0.82"),
        target_power_factor=Decimal("0.95"),
        rated_motor_power_kw=Decimal("55"),
    )


@pytest.fixture
def result_with_motor():
    return analyze_brownfield_system(
        BrownfieldSystemEngineInput(
            audit=_audit(),
            motor_measurement=_motor(),
        )
    )


def test_motor_pfc_absent_without_measurement():
    result = analyze_brownfield_system(BrownfieldSystemEngineInput(audit=_audit()))
    assert result.motor_pfc is None


def test_motor_pfc_present_with_measurement(result_with_motor):
    assert result_with_motor.motor_pfc is not None


def test_motor_active_power_matches_ieee_141(result_with_motor):
    """P = 1.7320508 x 415 x 78 x 0.82 / 1000 = 45.9745 kW."""
    assert result_with_motor.motor_pfc.measured_active_power_kw == Decimal("45.9745")


def test_capacitor_sizing_matches_is_15167(result_with_motor):
    """Qc = P x (tan(arccos 0.82) - tan(arccos 0.95)) = 16.98 kVAr."""
    kvar = result_with_motor.motor_pfc.required_capacitor_kvar
    assert Decimal("16.9") < kvar < Decimal("17.1")


def test_nameplate_deviation_reported(result_with_motor):
    """45.97 kW measured against a 55 kW nameplate is about -16 percent."""
    deviation = result_with_motor.motor_pfc.power_deviation_from_nameplate
    assert Decimal("-0.20") < deviation < Decimal("-0.10")


def test_pf_opportunity_reaches_the_register(result_with_motor):
    codes = [o.opportunity_code for o in result_with_motor.opportunities.opportunities]
    assert "PF-CORRECTION" in codes


def test_pf_opportunity_does_not_change_station_totals(result_with_motor):
    """Station energy totals must be unaffected by the PF opportunity."""
    without = analyze_brownfield_system(BrownfieldSystemEngineInput(audit=_audit()))
    assert (
        result_with_motor.estimated_total_annual_energy_saving_kwh
        == without.estimated_total_annual_energy_saving_kwh
    )
    assert (
        result_with_motor.estimated_optimized_average_power_kw
        == without.estimated_optimized_average_power_kw
    )
