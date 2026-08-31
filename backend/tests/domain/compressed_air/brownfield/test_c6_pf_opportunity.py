"""
C-6 opportunity engine tests — power-factor correction (PF-CORRECTION).

The PF-CORRECTION opportunity reuses the C-6 motor/PFC engine:
    P    = sqrt3 x V x I x PF          (IEEE Std 141)
    Q_c  = P x (tan phi1 - tan phi2)   (IS 15167)

Honesty contract enforced by these tests: power-factor correction does
not reduce the motor's active power draw, so the opportunity must report
zero kW and zero kWh saving. A cost saving appears only when the site
supplies the PF penalty it is actually being billed.
"""

from decimal import Decimal

import pytest

from app.domain.compressed_air.brownfield.audit_analysis import (
    analyze_brownfield_audit,
)
from app.domain.compressed_air.brownfield.audit_models import (
    AuditOperatingState,
    BrownfieldAuditCase,
    CompressorMeasurementPoint,
    ExistingCompressor,
    SystemMeasurementPoint,
)
from app.domain.compressed_air.brownfield.opportunity_engine import (
    OpportunityCategory,
    OpportunityPriority,
    identify_brownfield_opportunities,
)
from app.domain.compressed_air.energy.motor_pfc import MotorMeasurementInput
from app.domain.compressed_air.station.station_models import (
    CompressorControlMode,
    CompressorTechnology,
)


def _base_audit() -> BrownfieldAuditCase:
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
        audit_code="C6-TEST",
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


@pytest.fixture
def base_analysis():
    return analyze_brownfield_audit(_base_audit())


def _poor_pf_motor() -> MotorMeasurementInput:
    """415 V, 78 A, PF 0.82 measured; target 0.95."""
    return MotorMeasurementInput(
        measured_voltage_v=Decimal("415"),
        measured_current_a=Decimal("78"),
        measured_power_factor=Decimal("0.82"),
        target_power_factor=Decimal("0.95"),
        rated_motor_power_kw=Decimal("55"),
    )


def _good_pf_motor() -> MotorMeasurementInput:
    """Already corrected motor: measured PF above target."""
    return MotorMeasurementInput(
        measured_voltage_v=Decimal("415"),
        measured_current_a=Decimal("70"),
        measured_power_factor=Decimal("0.96"),
        target_power_factor=Decimal("0.95"),
    )


def _pf_opportunity(result):
    return next(o for o in result.opportunities if o.opportunity_code == "PF-CORRECTION")


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------


def test_pf_opportunity_appears_when_pf_below_target(base_analysis):
    result = identify_brownfield_opportunities(
        analysis=base_analysis,
        motor_measurement=_poor_pf_motor(),
    )
    codes = [o.opportunity_code for o in result.opportunities]
    assert "PF-CORRECTION" in codes


def test_pf_opportunity_category(base_analysis):
    result = identify_brownfield_opportunities(
        analysis=base_analysis,
        motor_measurement=_poor_pf_motor(),
    )
    assert _pf_opportunity(result).category == OpportunityCategory.POWER_FACTOR


def test_pf_opportunity_absent_when_no_measurement(base_analysis):
    result = identify_brownfield_opportunities(analysis=base_analysis)
    codes = [o.opportunity_code for o in result.opportunities]
    assert "PF-CORRECTION" not in codes


def test_pf_opportunity_absent_when_pf_already_above_target(base_analysis):
    result = identify_brownfield_opportunities(
        analysis=base_analysis,
        motor_measurement=_good_pf_motor(),
    )
    codes = [o.opportunity_code for o in result.opportunities]
    assert "PF-CORRECTION" not in codes


# ---------------------------------------------------------------------------
# Honesty contract: no fabricated kW / kWh saving
# ---------------------------------------------------------------------------


def test_pf_opportunity_claims_no_power_saving(base_analysis):
    result = identify_brownfield_opportunities(
        analysis=base_analysis,
        motor_measurement=_poor_pf_motor(),
    )
    assert _pf_opportunity(result).estimated_power_saving_kw == Decimal("0")


def test_pf_opportunity_claims_no_energy_saving(base_analysis):
    result = identify_brownfield_opportunities(
        analysis=base_analysis,
        motor_measurement=_poor_pf_motor(),
    )
    opp = _pf_opportunity(result)
    assert opp.estimated_annual_energy_saving_kwh == Decimal("0")


def test_pf_opportunity_cost_zero_without_penalty_data(base_analysis):
    result = identify_brownfield_opportunities(
        analysis=base_analysis,
        motor_measurement=_poor_pf_motor(),
    )
    assert _pf_opportunity(result).estimated_annual_cost_saving == Decimal("0")


def test_pf_opportunity_cost_equals_reported_penalty(base_analysis):
    result = identify_brownfield_opportunities(
        analysis=base_analysis,
        motor_measurement=_poor_pf_motor(),
        pf_penalty_annual_cost=Decimal("48000"),
    )
    assert _pf_opportunity(result).estimated_annual_cost_saving == Decimal("48000")


def test_pf_priority_low_without_penalty_data(base_analysis):
    result = identify_brownfield_opportunities(
        analysis=base_analysis,
        motor_measurement=_poor_pf_motor(),
    )
    assert _pf_opportunity(result).priority == OpportunityPriority.LOW


def test_pf_priority_medium_with_penalty_data(base_analysis):
    result = identify_brownfield_opportunities(
        analysis=base_analysis,
        motor_measurement=_poor_pf_motor(),
        pf_penalty_annual_cost=Decimal("48000"),
    )
    assert _pf_opportunity(result).priority == OpportunityPriority.MEDIUM


# ---------------------------------------------------------------------------
# Engineering content
# ---------------------------------------------------------------------------


def test_pf_opportunity_title_carries_capacitor_size(base_analysis):
    """
    Manual cross-check (IEEE 141 / IS 15167):
      P    = 1.7320508 x 415 x 78 x 0.82 / 1000 = 45.97 kW
      phi1 = arccos(0.82) = 34.915 deg, tan phi1 = 0.6979
      phi2 = arccos(0.95) = 18.195 deg, tan phi2 = 0.3287
      Q_c  = 45.97 x (0.6979 - 0.3287) = 16.98 kVAr
    """
    result = identify_brownfield_opportunities(
        analysis=base_analysis,
        motor_measurement=_poor_pf_motor(),
    )
    opp = _pf_opportunity(result)
    assert "kVAr" in opp.title
    assert "16.9" in opp.title


def test_pf_rationale_states_no_kw_saving(base_analysis):
    result = identify_brownfield_opportunities(
        analysis=base_analysis,
        motor_measurement=_poor_pf_motor(),
    )
    rationale = _pf_opportunity(result).rationale
    assert "IEEE Std 141" in rationale
    assert "IS 15167" in rationale
    assert "does NOT" in rationale


def test_pf_opportunity_does_not_inflate_totals(base_analysis):
    """Totals must be identical with and without the PF opportunity."""
    without = identify_brownfield_opportunities(analysis=base_analysis)
    with_pf = identify_brownfield_opportunities(
        analysis=base_analysis,
        motor_measurement=_poor_pf_motor(),
    )
    assert with_pf.total_estimated_power_saving_kw == without.total_estimated_power_saving_kw
    assert (
        with_pf.total_estimated_annual_energy_saving_kwh
        == without.total_estimated_annual_energy_saving_kwh
    )
