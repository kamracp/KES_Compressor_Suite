"""C-8c: modulation, variable displacement and IGV units inside the simulator."""

from decimal import Decimal

import pytest

from app.domain.compressed_air.performance.part_load import BelowTurndownMode
from app.domain.compressed_air.profiles.demand_profile import DemandProfilePoint
from app.domain.compressed_air.sequencing.pressure_band_simulator import (
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
BAND = PressureBand(load_pressure_bar_g=D("6.5"), unload_pressure_bar_g=D("7.5"))


def machine(control_mode: ControlMode, **overrides) -> SequencedMachine:
    base = {
        "unit_code": "M1",
        "control_mode": control_mode,
        "rated_fad_nm3_per_hr": D("1000"),
        "rated_power_kw": D("100"),
        "band": BAND,
        "unload_power_fraction": D("0.25"),
    }
    base.update(overrides)
    return SequencedMachine(**base)


def run(demand: str, *machines: SequencedMachine, receiver: str = "10"):
    inputs = SequencingInput(
        analysis_code="C8",
        machines=machines,
        demand_profile=(
            DemandProfilePoint(
                period_index=0,
                label="P0",
                demand_nm3_per_hr=D(demand),
                required_pressure_bar_g=D("6.5"),
                duration_hours=D("1"),
            ),
        ),
        receiver_volume_m3=D(receiver),
        electricity_tariff_per_kwh=D("7"),
    )
    return simulate_pressure_bands(inputs)


def test_modulating_unit_trims_continuously_above_its_floor() -> None:
    result = run("500", machine(ControlMode.MODULATION))
    m = result.periods[0].machines[0]

    assert m.duty_role is DutyRole.TRIM
    assert m.average_power_kw == D("85")  # DOE: 85 % power at 50 % flow
    assert m.load_fraction == D("1")
    assert m.cycles_per_hour is None
    assert result.unload_energy_kwh == D("0")


def test_modulating_unit_cycles_below_the_doe_floor() -> None:
    result = run("200", machine(ControlMode.MODULATION))
    m = result.periods[0].machines[0]

    assert m.average_power_kw == D("53.5")  # duty 0.5 between 82 kW and 25 kW
    assert m.load_fraction == D("0.5")
    assert m.cycles_per_hour is not None and m.cycles_per_hour > D("0")
    assert result.unload_energy_kwh == D("12.5")  # 100 x 0.25 x 0.5 unloaded share


def test_modulation_floor_can_be_lowered_per_machine() -> None:
    result = run(
        "200",
        machine(ControlMode.MODULATION, modulation_floor_capacity_fraction=D("0.10")),
    )
    m = result.periods[0].machines[0]

    assert m.average_power_kw == D("76")  # still throttling: 70 + 30 x 0.2
    assert m.cycles_per_hour is None


def test_variable_displacement_is_proportional_then_cycles() -> None:
    above = run("750", machine(ControlMode.VARIABLE_DISPLACEMENT))
    below = run("250", machine(ControlMode.VARIABLE_DISPLACEMENT))

    assert above.periods[0].machines[0].average_power_kw == D("75")
    assert below.periods[0].machines[0].average_power_kw == D("37.5")
    assert below.periods[0].machines[0].load_fraction == D("0.5")


def igv(below: BelowTurndownMode = BelowTurndownMode.BLOW_OFF) -> SequencedMachine:
    return machine(
        ControlMode.INLET_GUIDE_VANE,
        unload_power_fraction=D("0.20") if below is BelowTurndownMode.UNLOAD else None,
        turndown_flow_fraction=D("0.25"),
        power_fraction_at_turndown=D("0.80"),
        below_turndown=below,
    )


def test_igv_throttles_to_turndown_then_blows_off_at_constant_power() -> None:
    throttling = run("875", igv()).periods[0].machines[0]
    blowing_off = run("500", igv()).periods[0].machines[0]

    assert throttling.average_power_kw == D("90")
    assert throttling.wasted_flow_nm3_per_hr == D("0")

    assert blowing_off.average_power_kw == D("80")
    assert blowing_off.delivered_flow_nm3_per_hr == D("500")
    assert blowing_off.wasted_flow_nm3_per_hr == D("250")
    assert blowing_off.load_fraction == D("1")


def test_igv_auto_dual_cycles_against_off_loaded_power() -> None:
    result = run("375", igv(BelowTurndownMode.UNLOAD))
    m = result.periods[0].machines[0]

    assert m.average_power_kw == D("50")  # duty 0.5 between 80 kW and 20 kW
    assert m.wasted_flow_nm3_per_hr == D("0")
    assert m.cycles_per_hour is not None
    assert result.unload_energy_kwh == D("10")


def test_blowdown_transient_raises_load_unload_power_and_shrinks_with_storage() -> None:
    ideal = run("500", machine(ControlMode.FIXED_SPEED_LOAD_UNLOAD))
    small = run(
        "500",
        machine(ControlMode.FIXED_SPEED_LOAD_UNLOAD, unload_blowdown_seconds=D("40")),
        receiver="2",
    )
    large = run(
        "500",
        machine(ControlMode.FIXED_SPEED_LOAD_UNLOAD, unload_blowdown_seconds=D("40")),
        receiver="20",
    )

    p_ideal = ideal.periods[0].machines[0].average_power_kw
    p_small = small.periods[0].machines[0].average_power_kw
    p_large = large.periods[0].machines[0].average_power_kw

    assert p_ideal == D("62.5")
    assert p_small > p_large > p_ideal


def test_curve_errors_carry_the_unit_code() -> None:
    with pytest.raises(InvalidSequencingInputError, match="M1: turndown_flow_fraction is required"):
        run("500", machine(ControlMode.INLET_GUIDE_VANE, unload_power_fraction=None))

    with pytest.raises(
        InvalidSequencingInputError, match="M1: unload_power_fraction must be within"
    ):
        run("500", machine(ControlMode.FIXED_SPEED_LOAD_UNLOAD, unload_power_fraction=D("0.5")))
