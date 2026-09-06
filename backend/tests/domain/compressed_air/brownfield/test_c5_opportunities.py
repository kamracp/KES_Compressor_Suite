"""
C-5 opportunity engine tests — condensate drain and filter pressure-drop penalty.

Both opportunities reuse existing engines:
- CONDENSATE-DRAIN  : calculate_leakage_energy (air waste = leak waste physics)
- FILTER-PENALTY    : calculate_pressure_energy_saving (adiabatic, C-1 engine)

Citation: US DOE / Compressed Air Challenge, "Improving Compressed Air
System Performance: A Sourcebook for Industry."
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
        audit_code="C5-TEST",
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


# ---------------------------------------------------------------------------
# CONDENSATE-DRAIN tests
# ---------------------------------------------------------------------------


def test_condensate_drain_opportunity_appears(base_analysis):
    result = identify_brownfield_opportunities(
        analysis=base_analysis,
        condensate_drain_air_loss_nm3_per_hr=Decimal("12"),
    )
    codes = [o.opportunity_code for o in result.opportunities]
    assert "CONDENSATE-DRAIN" in codes


def test_condensate_drain_category(base_analysis):
    result = identify_brownfield_opportunities(
        analysis=base_analysis,
        condensate_drain_air_loss_nm3_per_hr=Decimal("12"),
    )
    opp = next(o for o in result.opportunities if o.opportunity_code == "CONDENSATE-DRAIN")
    assert opp.category == OpportunityCategory.CONDENSATE_DRAIN


def test_condensate_drain_power_saving_is_positive(base_analysis):
    result = identify_brownfield_opportunities(
        analysis=base_analysis,
        condensate_drain_air_loss_nm3_per_hr=Decimal("12"),
    )
    opp = next(o for o in result.opportunities if o.opportunity_code == "CONDENSATE-DRAIN")
    assert opp.estimated_power_saving_kw > 0


def test_condensate_drain_energy_saving_formula(base_analysis):
    """
    Manual cross-check:
      specific power = 45 kW / (300/60) Nm3/min = 9.0 kW/(Nm3/min)
      drain flow     = 12 Nm3/hr = 0.2 Nm3/min
      wasted power   = 0.2 x 9.0 = 1.8 kW
      annual saving  = 1.8 x 8000 = 14400 kWh
    """
    result = identify_brownfield_opportunities(
        analysis=base_analysis,
        condensate_drain_air_loss_nm3_per_hr=Decimal("12"),
    )
    opp = next(o for o in result.opportunities if o.opportunity_code == "CONDENSATE-DRAIN")
    assert opp.estimated_power_saving_kw == Decimal("1.8")
    assert opp.estimated_annual_energy_saving_kwh == Decimal("14400")


def test_condensate_drain_zero_suppressed(base_analysis):
    result = identify_brownfield_opportunities(
        analysis=base_analysis,
        condensate_drain_air_loss_nm3_per_hr=Decimal("0"),
    )
    codes = [o.opportunity_code for o in result.opportunities]
    assert "CONDENSATE-DRAIN" not in codes


def test_condensate_drain_none_suppressed(base_analysis):
    result = identify_brownfield_opportunities(
        analysis=base_analysis,
        condensate_drain_air_loss_nm3_per_hr=None,
    )
    codes = [o.opportunity_code for o in result.opportunities]
    assert "CONDENSATE-DRAIN" not in codes


# ---------------------------------------------------------------------------
# FILTER-PENALTY tests
# ---------------------------------------------------------------------------


def test_filter_penalty_opportunity_appears(base_analysis):
    result = identify_brownfield_opportunities(
        analysis=base_analysis,
        filter_excess_pressure_drop_bar=Decimal("0.3"),
    )
    codes = [o.opportunity_code for o in result.opportunities]
    assert "FILTER-PENALTY" in codes


def test_filter_penalty_category(base_analysis):
    result = identify_brownfield_opportunities(
        analysis=base_analysis,
        filter_excess_pressure_drop_bar=Decimal("0.3"),
    )
    opp = next(o for o in result.opportunities if o.opportunity_code == "FILTER-PENALTY")
    assert opp.category == OpportunityCategory.FILTER_EFFICIENCY


def test_filter_penalty_power_saving_is_positive(base_analysis):
    result = identify_brownfield_opportunities(
        analysis=base_analysis,
        filter_excess_pressure_drop_bar=Decimal("0.3"),
    )
    opp = next(o for o in result.opportunities if o.opportunity_code == "FILTER-PENALTY")
    assert opp.estimated_power_saving_kw > 0


def test_filter_penalty_zero_suppressed(base_analysis):
    result = identify_brownfield_opportunities(
        analysis=base_analysis,
        filter_excess_pressure_drop_bar=Decimal("0"),
    )
    codes = [o.opportunity_code for o in result.opportunities]
    assert "FILTER-PENALTY" not in codes


def test_filter_penalty_none_suppressed(base_analysis):
    result = identify_brownfield_opportunities(
        analysis=base_analysis,
        filter_excess_pressure_drop_bar=None,
    )
    codes = [o.opportunity_code for o in result.opportunities]
    assert "FILTER-PENALTY" not in codes


def test_both_opportunities_together(base_analysis):
    result = identify_brownfield_opportunities(
        analysis=base_analysis,
        condensate_drain_air_loss_nm3_per_hr=Decimal("12"),
        filter_excess_pressure_drop_bar=Decimal("0.3"),
    )
    codes = [o.opportunity_code for o in result.opportunities]
    assert "CONDENSATE-DRAIN" in codes
    assert "FILTER-PENALTY" in codes


def test_total_saving_includes_both(base_analysis):
    result = identify_brownfield_opportunities(
        analysis=base_analysis,
        condensate_drain_air_loss_nm3_per_hr=Decimal("12"),
        filter_excess_pressure_drop_bar=Decimal("0.3"),
    )
    individual_sum = sum(o.estimated_power_saving_kw for o in result.opportunities)
    assert result.total_estimated_power_saving_kw == individual_sum


# --- C-7c: central sequencer opportunity from a sequencing assessment ---------


def _sequencing_assessment(*, proposed_band=("6.3", "6.6"), idle: bool = True):
    from app.domain.compressed_air.profiles.demand_profile import DemandProfilePoint
    from app.domain.compressed_air.sequencing.sequencing_assessment import (
        SequencingAssessmentInput,
        assess_sequencing,
    )
    from app.domain.compressed_air.sequencing.sequencing_models import (
        ControlMode,
        PressureBand,
        SequencedMachine,
    )

    def unit(code, low, high, *, vsd=False):
        return SequencedMachine(
            unit_code=code,
            control_mode=ControlMode.VARIABLE_SPEED if vsd else ControlMode.FIXED_SPEED_LOAD_UNLOAD,
            rated_fad_nm3_per_hr=Decimal("1000"),
            rated_power_kw=Decimal("100"),
            band=PressureBand(Decimal(low), Decimal(high)),
            unload_power_fraction=Decimal("0.2" if vsd else "0.25"),
            minimum_flow_fraction=Decimal("0.3") if vsd else None,
            minimum_flow_power_fraction=Decimal("0.4") if vsd else None,
            standby_runs_unloaded=idle and code != "A",
        )

    return assess_sequencing(
        SequencingAssessmentInput(
            analysis_code="SEQ",
            baseline_machines=(
                unit("A", "6.8", "7.3"),
                unit("B", "6.5", "7.0"),
                unit("C", "6.2", "6.7", vsd=True),
            ),
            demand_profile=(
                DemandProfilePoint(
                    period_index=1,
                    label="shift",
                    demand_nm3_per_hr=Decimal("1500"),
                    required_pressure_bar_g=Decimal("6"),
                    duration_hours=Decimal("10"),
                ),
            ),
            receiver_volume_m3=Decimal("1"),
            electricity_tariff_per_kwh=Decimal("8"),
            proposed_band=PressureBand(Decimal(proposed_band[0]), Decimal(proposed_band[1])),
            annual_operating_hours=Decimal("8000"),
        )
    )


def test_central_sequencer_opportunity_carries_the_assessment_savings(base_analysis):
    assessment = _sequencing_assessment()
    result = identify_brownfield_opportunities(
        analysis=base_analysis, sequencing_assessment=assessment
    )
    seq = next(o for o in result.opportunities if o.opportunity_code == "CENTRAL-SEQUENCER")

    assert seq.category is OpportunityCategory.SEQUENCING
    assert seq.priority is OpportunityPriority.HIGH
    assert seq.estimated_annual_energy_saving_kwh == assessment.total_annual_saving_kwh
    assert seq.estimated_annual_cost_saving == assessment.total_annual_cost_saving
    assert seq.estimated_power_saving_kw == (
        assessment.total_annual_saving_kwh / Decimal("8000")
    ).quantize(Decimal("0.0001"))
    assert "standby" in seq.rationale and "header" in seq.rationale
    without = identify_brownfield_opportunities(analysis=base_analysis)
    assert result.total_estimated_annual_energy_saving_kwh == (
        without.total_estimated_annual_energy_saving_kwh + seq.estimated_annual_energy_saving_kwh
    )


def test_central_sequencer_opportunity_reports_zero_when_nothing_is_claimed(base_analysis):
    assessment = _sequencing_assessment(proposed_band=("7.5", "8.0"), idle=False)
    assert assessment.saving_claimed is False

    result = identify_brownfield_opportunities(
        analysis=base_analysis, sequencing_assessment=assessment
    )
    seq = next(o for o in result.opportunities if o.opportunity_code == "CENTRAL-SEQUENCER")

    assert seq.priority is OpportunityPriority.LOW
    assert seq.estimated_annual_energy_saving_kwh == Decimal("0")
    assert seq.estimated_power_saving_kw == Decimal("0.0000")
    assert "no saving claimed" in seq.rationale


def test_opportunities_unchanged_without_a_sequencing_assessment(base_analysis):
    result = identify_brownfield_opportunities(analysis=base_analysis)
    assert not any(o.opportunity_code == "CENTRAL-SEQUENCER" for o in result.opportunities)
