from decimal import Decimal

import pytest

from app.domain.compressed_air.profiles.demand_profile import DemandProfilePoint
from app.domain.compressed_air.sequencing.pressure_band_simulator import (
    cascade_order,
    simulate_pressure_bands,
)
from app.domain.compressed_air.sequencing.sequencing_models import (
    ControlMode,
    DutyRole,
    InvalidSequencingInputError,
    PressureBand,
    SequencedMachine,
    SequencingInput,
)

D = Decimal


def fixed(code: str, load: str, unload: str, *, unload_fraction: str = "0.25") -> SequencedMachine:
    return SequencedMachine(
        unit_code=code,
        control_mode=ControlMode.FIXED_SPEED_LOAD_UNLOAD,
        rated_fad_nm3_per_hr=D("1000"),
        rated_power_kw=D("100"),
        band=PressureBand(D(load), D(unload)),
        unload_power_fraction=D(unload_fraction),
    )


def vsd(code: str, load: str, unload: str) -> SequencedMachine:
    return SequencedMachine(
        unit_code=code,
        control_mode=ControlMode.VARIABLE_SPEED,
        rated_fad_nm3_per_hr=D("1000"),
        rated_power_kw=D("100"),
        band=PressureBand(D(load), D(unload)),
        unload_power_fraction=D("0.2"),
        minimum_flow_fraction=D("0.3"),
        minimum_flow_power_fraction=D("0.4"),
    )


def period(demand: str, hours: str = "10") -> DemandProfilePoint:
    return DemandProfilePoint(
        period_index=1,
        label="shift",
        demand_nm3_per_hr=D(demand),
        required_pressure_bar_g=D("6"),
        duration_hours=D(hours),
    )


def run(machines, *periods, volume: str = "1"):
    return simulate_pressure_bands(
        SequencingInput(
            analysis_code="SEQ-001",
            machines=tuple(machines),
            demand_profile=tuple(periods),
            receiver_volume_m3=D(volume),
            electricity_tariff_per_kwh=D("8"),
        )
    )


def test_single_fixed_speed_unit_cycles_at_the_mass_balance_duty() -> None:
    # 1000 Nm3/h unit, 400 Nm3/h demand for 10 h, band 6.5-7.5 (1 bar), 1 m3.
    # load duty f = 0.4; power = 100 x (0.4 + 0.6 x 0.25) = 55 kW.
    # stored free air S = 1 x 1 / 1.01325 Nm3; t_up = S/600, t_down = S/400;
    # cycles/h = 1 / (S x (1/600 + 1/400)) = 240 / S = 240 x 1.01325 = 243.18.
    result = run([fixed("C1", "6.5", "7.5")], period("400"))
    p = result.periods[0]
    m = p.machines[0]

    assert m.duty_role is DutyRole.TRIM
    assert m.load_fraction == D("0.4000")
    assert m.average_power_kw == D("55.0000")
    assert m.cycles_per_hour == D("243.1800")
    assert p.average_header_pressure_bar_g == D("7.0000")
    assert p.shortfall_nm3_per_hr == D("0.0000")
    assert result.total_energy_kwh == D("550.0000")
    assert result.total_energy_cost == D("4400.0000")
    assert result.unload_energy_kwh == D("150.0000")  # 100 x 0.25 x 0.6 x 10 h
    assert result.specific_power_kw_per_nm3_per_min == D("8.2500")  # 55 / (400/60)
    assert result.unmet_demand_hours == D("0.0000")


def test_cascade_loads_the_highest_band_first_whatever_the_input_order() -> None:
    trim = fixed("B", "6.5", "7.0")
    base = fixed("A", "6.8", "7.3")
    assert [m.unit_code for m in cascade_order((trim, base))] == ["A", "B"]

    result = run([trim, base], period("1500"))
    by_code = {m.unit_code: m for m in result.periods[0].machines}

    assert by_code["A"].duty_role is DutyRole.BASE
    assert by_code["A"].average_power_kw == D("100.0000")
    assert by_code["B"].duty_role is DutyRole.TRIM
    assert by_code["B"].load_fraction == D("0.5000")
    assert by_code["B"].average_power_kw == D("62.5000")  # 100 x (0.5 + 0.5 x 0.25)
    assert result.periods[0].total_power_kw == D("162.5000")
    assert result.periods[0].average_header_pressure_bar_g == D("6.7500")
    assert result.unload_energy_kwh == D("125.0000")  # 100 x 0.25 x 0.5 x 10 h


def test_vsd_trim_follows_demand_linearly_above_its_minimum_flow() -> None:
    # Residual 600 Nm3/h on a VSD with q_min 300, p_min 40 kW:
    # power = 40 + 60 x (600 - 300) / 700 = 65.7143 kW, no cycling.
    result = run([fixed("A", "6.8", "7.3"), vsd("V", "6.5", "7.0")], period("1600"))
    v = {m.unit_code: m for m in result.periods[0].machines}["V"]

    assert v.duty_role is DutyRole.TRIM
    assert v.load_fraction == D("1.0000")
    assert v.cycles_per_hour is None
    assert v.average_power_kw == D("65.7143")
    assert result.unload_energy_kwh == D("0.0000")


def test_vsd_trim_cycles_at_minimum_speed_below_its_minimum_flow() -> None:
    # Residual 100 Nm3/h < q_min 300: f = 1/3; band 0.5 bar, 1 m3:
    # S = 0.5/1.01325; cycles = 1 / (S x (1/200 + 1/100)) = 1.01325 / 0.0075 = 135.1.
    # power = 40 x 1/3 + 100 x 0.2 x 2/3 = 26.6667 kW.
    result = run([fixed("A", "6.8", "7.3"), vsd("V", "6.5", "7.0")], period("1100"))
    v = {m.unit_code: m for m in result.periods[0].machines}["V"]

    assert v.load_fraction == D("0.3333")
    assert v.cycles_per_hour == D("135.1000")
    assert v.average_power_kw == D("26.6667")


def test_shortfall_is_reported_not_hidden() -> None:
    result = run([fixed("C1", "6.5", "7.5")], period("1200", "4"))
    p = result.periods[0]

    assert p.machines[0].duty_role is DutyRole.BASE
    assert p.shortfall_nm3_per_hr == D("200.0000")
    assert p.average_header_pressure_bar_g == D("6.5000")  # sags to the load setpoint
    assert result.unmet_demand_hours == D("4.0000")


def test_zero_demand_leaves_every_unit_in_standby_at_the_top_of_the_band() -> None:
    result = run([fixed("A", "6.8", "7.3"), fixed("B", "6.5", "7.0")], period("0"))
    p = result.periods[0]

    assert {m.duty_role for m in p.machines} == {DutyRole.STANDBY}
    assert p.total_power_kw == D("0.0000")
    assert p.average_header_pressure_bar_g == D("7.3000")


def test_periods_accumulate_energy_and_specific_power() -> None:
    result = run([fixed("C1", "6.5", "7.5")], period("400", "10"), period("1000", "5"))

    # 55 kW x 10 h + 100 kW x 5 h = 1050 kWh; supplied 4000 + 5000 = 9000 Nm3 in 15 h
    # -> 10 Nm3/min; specific power = (1050/15) / 10 = 7 kW per Nm3/min.
    assert result.total_energy_kwh == D("1050.0000")
    assert result.specific_power_kw_per_nm3_per_min == D("7.0000")


@pytest.mark.parametrize(
    "machine",
    [
        fixed("bad", "7.0", "6.5"),  # inverted band
        SequencedMachine(
            unit_code="nofrac",
            control_mode=ControlMode.FIXED_SPEED_LOAD_UNLOAD,
            rated_fad_nm3_per_hr=D("1000"),
            rated_power_kw=D("100"),
            band=PressureBand(D("6.5"), D("7.0")),
        ),
    ],
)
def test_invalid_machines_are_rejected(machine: SequencedMachine) -> None:
    with pytest.raises(InvalidSequencingInputError):
        run([machine], period("400"))
