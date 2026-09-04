from dataclasses import replace
from decimal import Decimal

from app.domain.compressed_air.profiles.demand_profile import DemandProfilePoint
from app.domain.compressed_air.sequencing.sequencing_assessment import (
    SequencingAssessmentInput,
    assess_sequencing,
    propose_central_cascade,
)
from app.domain.compressed_air.sequencing.sequencing_models import (
    ControlMode,
    DutyRole,
    PressureBand,
    SequencedMachine,
)

D = Decimal


def fixed(code: str, load: str, unload: str, *, idle: bool = False) -> SequencedMachine:
    return SequencedMachine(
        unit_code=code,
        control_mode=ControlMode.FIXED_SPEED_LOAD_UNLOAD,
        rated_fad_nm3_per_hr=D("1000"),
        rated_power_kw=D("100"),
        band=PressureBand(D(load), D(unload)),
        unload_power_fraction=D("0.25"),
        standby_runs_unloaded=idle,
    )


def vsd(code: str, load: str, unload: str, *, idle: bool = False) -> SequencedMachine:
    return SequencedMachine(
        unit_code=code,
        control_mode=ControlMode.VARIABLE_SPEED,
        rated_fad_nm3_per_hr=D("1000"),
        rated_power_kw=D("100"),
        band=PressureBand(D(load), D(unload)),
        unload_power_fraction=D("0.2"),
        minimum_flow_fraction=D("0.3"),
        minimum_flow_power_fraction=D("0.4"),
        standby_runs_unloaded=idle,
    )


def assessment(*, demand: str = "1500", proposed=("6.3", "6.6")) -> SequencingAssessmentInput:
    return SequencingAssessmentInput(
        analysis_code="SEQ-ASSESS-001",
        baseline_machines=(
            fixed("A", "6.8", "7.3"),
            fixed("B", "6.5", "7.0", idle=True),
            vsd("C", "6.2", "6.7", idle=True),
        ),
        demand_profile=(
            DemandProfilePoint(
                period_index=1,
                label="shift",
                demand_nm3_per_hr=D(demand),
                required_pressure_bar_g=D("6"),
                duration_hours=D("10"),
            ),
        ),
        receiver_volume_m3=D("1"),
        electricity_tariff_per_kwh=D("8"),
        proposed_band=PressureBand(D(proposed[0]), D(proposed[1])),
        annual_operating_hours=D("8000"),
    )


def test_proposal_orders_fixed_units_by_specific_power_and_puts_the_vsd_last() -> None:
    cheap = replace(fixed("X", "6", "7"), rated_power_kw=D("90"))
    proposed = propose_central_cascade(
        (vsd("V", "6", "7"), fixed("Y", "6", "7"), cheap), PressureBand(D("6.3"), D("6.6"))
    )

    assert [(m.unit_code, m.priority) for m in proposed] == [("X", 1), ("Y", 2), ("V", 3)]
    assert all(m.band == PressureBand(D("6.3"), D("6.6")) for m in proposed)
    assert not any(m.standby_runs_unloaded for m in proposed)


def test_savings_are_decomposed_and_annualised() -> None:
    # Baseline: A base 100 kW, B trim 62.5 kW (500/1000, unload 0.25),
    # C idle running unloaded 20 kW -> 182.5 kW at header (6.5+7.0)/2 = 6.75.
    # Proposed: A base, B stands down, C trims 500: 40 + 60 x 200/700 = 57.1429 kW
    # -> 157.1429 kW at header 6.45. Simulated saving 25.3571 kW = standby 20 + trim 5.3571.
    result = assess_sequencing(assessment())
    factor = D("800")  # 8000 h / 10 h profile

    roles = {m.unit_code: m.duty_role for m in result.proposed.periods[0].machines}
    assert roles == {"A": DutyRole.BASE, "B": DutyRole.STANDBY, "C": DutyRole.TRIM}
    assert result.baseline.periods[0].total_power_kw == D("182.5000")
    assert result.proposed.periods[0].total_power_kw == D("157.1429")
    assert result.baseline_average_header_pressure_bar_g == D("6.7500")
    assert result.proposed_average_header_pressure_bar_g == D("6.4500")
    assert result.annualisation_factor == factor
    assert result.standby_saving_kwh == D("200") * factor
    assert result.trim_saving_kwh == (D("53.5714") * factor).quantize(D("0.0001"))
    assert result.pressure_saving_kwh > D("0")
    assert result.saving_claimed is True
    assert result.total_annual_saving_kwh == (
        result.standby_saving_kwh + result.trim_saving_kwh + result.pressure_saving_kwh
    )
    assert result.total_annual_cost_saving == result.total_annual_saving_kwh * D("8")


def test_no_saving_is_claimed_when_the_proposal_is_not_better() -> None:
    # A proposed band above the as-found headers raises pressure and, with no
    # idle units in the baseline, buys nothing: the assessment says so.
    inputs = assessment(proposed=("7.5", "8.0"))
    inputs = replace(
        inputs,
        baseline_machines=tuple(
            replace(m, standby_runs_unloaded=False) for m in inputs.baseline_machines
        ),
    )
    result = assess_sequencing(inputs)

    assert result.saving_claimed is False
    assert result.total_annual_saving_kwh == D("0.0000")
    assert "does not reduce energy" in result.note
    assert result.pressure_saving_kwh < D("0")
