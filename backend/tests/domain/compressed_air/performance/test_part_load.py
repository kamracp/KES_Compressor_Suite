"""C-8b: part-load curves against the cited guideline points."""

from decimal import Decimal

import pytest

from app.domain.compressed_air.performance.part_load import (
    BelowTurndownMode,
    InvalidPartLoadInputError,
    PartLoadCurve,
    PartLoadMode,
    part_load_point,
)

D = Decimal


def load_unload(f: str = "0.25") -> PartLoadCurve:
    return PartLoadCurve(mode=PartLoadMode.LOAD_UNLOAD, unload_power_fraction=D(f))


def modulation(floor: str = "0.40") -> PartLoadCurve:
    return PartLoadCurve(
        mode=PartLoadMode.MODULATION,
        unload_power_fraction=D("0.25"),
        modulation_floor_capacity_fraction=D(floor),
    )


def igv(below: BelowTurndownMode = BelowTurndownMode.BLOW_OFF) -> PartLoadCurve:
    # CAGI published example: 75 % flow at 80 % power (turndown 25 %).
    return PartLoadCurve(
        mode=PartLoadMode.INLET_GUIDE_VANE,
        turndown_flow_fraction=D("0.25"),
        power_fraction_at_turndown=D("0.80"),
        below_turndown=below,
        unload_power_fraction=D("0.20") if below is BelowTurndownMode.UNLOAD else None,
    )


def test_load_unload_is_the_large_storage_asymptote() -> None:
    assert part_load_point(load_unload(), D("1")).power_fraction == D("1")
    assert part_load_point(load_unload(), D("0.5")).power_fraction == D("0.625")
    assert part_load_point(load_unload(), D("0")).power_fraction == D("0.25")


def test_modulation_draws_85_percent_at_half_flow_and_70_at_floor_extrapolation() -> None:
    # DOE: modulating at 50 % demand draws about 85 % of full-load power.
    assert part_load_point(modulation(), D("0.5")).power_fraction == D("0.85")
    at_floor = part_load_point(modulation(), D("0.4"))
    assert at_floor.power_fraction == D("0.82")
    assert at_floor.regime == "inlet modulation"


def test_modulation_below_floor_cycles_between_floor_point_and_unloaded() -> None:
    # duty 0.5 between 0.82 (floor) and 0.25 (unloaded) -> 0.535
    point = part_load_point(modulation(), D("0.2"))
    assert point.power_fraction == D("0.535")
    assert point.regime == "modulation floor / unload cycling"


def test_variable_displacement_is_proportional_to_half_capacity() -> None:
    curve = PartLoadCurve(mode=PartLoadMode.VARIABLE_DISPLACEMENT, unload_power_fraction=D("0.25"))
    assert part_load_point(curve, D("0.75")).power_fraction == D("0.75")
    assert part_load_point(curve, D("0.5")).power_fraction == D("0.5")
    # duty 0.5 between 0.5 and 0.25 -> 0.375
    assert part_load_point(curve, D("0.25")).power_fraction == D("0.375")


def test_variable_speed_is_linear_between_datasheet_points() -> None:
    curve = PartLoadCurve(
        mode=PartLoadMode.VARIABLE_SPEED,
        unload_power_fraction=D("0.20"),
        minimum_flow_fraction=D("0.30"),
        minimum_flow_power_fraction=D("0.40"),
    )
    assert part_load_point(curve, D("0.65")).power_fraction == D("0.7")
    assert part_load_point(curve, D("0.30")).power_fraction == D("0.4")
    # below q_min: duty 0.5 between 0.4 and 0.2 -> 0.3
    assert part_load_point(curve, D("0.15")).power_fraction == D("0.3")


def test_igv_matches_the_cagi_example_and_blows_off_at_constant_power() -> None:
    assert part_load_point(igv(), D("0.75")).power_fraction == D("0.8")
    assert part_load_point(igv(), D("0.875")).power_fraction == D("0.9")

    blow_off = part_load_point(igv(), D("0.5"))
    assert blow_off.power_fraction == D("0.8")
    assert blow_off.wasted_flow_fraction == D("0.25")
    assert blow_off.regime == "blow-off"


def test_igv_auto_dual_cycles_against_off_loaded_power() -> None:
    # duty 0.5/0.75 between 0.80 and 0.20 -> 0.6
    point = part_load_point(igv(BelowTurndownMode.UNLOAD), D("0.375"))
    assert point.power_fraction == D("0.5")
    assert point.wasted_flow_fraction == D("0")
    assert point.regime == "auto-dual unload cycling"


@pytest.mark.parametrize(
    "curve, message",
    [
        (load_unload("0.5"), "unload_power_fraction must be within"),
        (modulation("0.05"), "modulation_floor_capacity_fraction must be within"),
        (
            PartLoadCurve(mode=PartLoadMode.VARIABLE_SPEED, unload_power_fraction=D("0.2")),
            "minimum_flow_fraction is required",
        ),
        (
            PartLoadCurve(
                mode=PartLoadMode.INLET_GUIDE_VANE,
                turndown_flow_fraction=D("0.60"),
                power_fraction_at_turndown=D("0.8"),
            ),
            "turndown_flow_fraction must be within",
        ),
        (
            PartLoadCurve(
                mode=PartLoadMode.LOAD_UNLOAD,
                unload_power_fraction=D("0.25"),
                turndown_flow_fraction=D("0.3"),
            ),
            "does not apply to LOAD_UNLOAD",
        ),
    ],
)
def test_out_of_bound_or_misplaced_inputs_are_rejected(curve: PartLoadCurve, message: str) -> None:
    with pytest.raises(InvalidPartLoadInputError, match=message):
        part_load_point(curve, D("0.5"))


def test_capacity_fraction_outside_unit_interval_is_rejected() -> None:
    with pytest.raises(InvalidPartLoadInputError, match="capacity_fraction"):
        part_load_point(load_unload(), D("1.2"))
