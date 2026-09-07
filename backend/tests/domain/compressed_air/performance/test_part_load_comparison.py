"""C-8c: side-by-side part-load comparison."""

from decimal import Decimal

import pytest

from app.domain.compressed_air.performance.part_load import (
    BelowTurndownMode,
    PartLoadCurve,
    PartLoadMode,
)
from app.domain.compressed_air.performance.part_load_comparison import (
    InvalidPartLoadComparisonInputError,
    LoadDurationBin,
    PartLoadCandidate,
    PartLoadComparisonInput,
    compare_part_load,
)

D = Decimal
FRACTIONS = (D("0.25"), D("0.5"), D("0.75"), D("1"))

LOAD_UNLOAD = PartLoadCandidate(
    "load/unload", PartLoadCurve(mode=PartLoadMode.LOAD_UNLOAD, unload_power_fraction=D("0.25"))
)
MODULATION = PartLoadCandidate(
    "modulation", PartLoadCurve(mode=PartLoadMode.MODULATION, unload_power_fraction=D("0.25"))
)
VSD = PartLoadCandidate(
    "vsd",
    PartLoadCurve(
        mode=PartLoadMode.VARIABLE_SPEED,
        unload_power_fraction=D("0.20"),
        minimum_flow_fraction=D("0.25"),
        minimum_flow_power_fraction=D("0.35"),
    ),
)
IGV = PartLoadCandidate(
    "igv blow-off",
    PartLoadCurve(
        mode=PartLoadMode.INLET_GUIDE_VANE,
        turndown_flow_fraction=D("0.25"),
        power_fraction_at_turndown=D("0.80"),
        below_turndown=BelowTurndownMode.BLOW_OFF,
    ),
)


def inputs(*candidates: PartLoadCandidate, **overrides) -> PartLoadComparisonInput:
    base = {
        "analysis_code": "PL-1",
        "rated_fad_nm3_per_hr": D("1000"),
        "rated_power_kw": D("100"),
        "candidates": candidates,
        "capacity_fractions": FRACTIONS,
    }
    base.update(overrides)
    return PartLoadComparisonInput(**base)


def test_points_follow_the_curves_and_specific_power_is_per_nm3_per_min() -> None:
    result = compare_part_load(inputs(LOAD_UNLOAD, MODULATION))
    lu, mod = result.candidates

    assert [p.power_kw for p in lu.points] == [D("43.75"), D("62.5"), D("81.25"), D("100")]
    # 25 % sits below the DOE 40 % modulation floor: duty 0.625 x 82 + 0.375 x 25
    assert [p.power_kw for p in mod.points] == [D("60.63"), D("85"), D("92.5"), D("100")]
    # 100 kW / (1000/60 Nm3/min) = 6 kW per Nm3/min at full load
    assert lu.points[3].specific_power_kw_per_nm3_per_min == D("6")
    assert mod.points[0].specific_power_kw_per_nm3_per_min == D("14.5512")  # 60.63 / 4.1667
    assert lu.annual_energy_kwh is None and result.lowest_annual_energy_label is None


def test_lowest_power_per_point_picks_the_cheapest_mode() -> None:
    result = compare_part_load(inputs(LOAD_UNLOAD, MODULATION, VSD))
    winners = {w.capacity_fraction: w.label for w in result.lowest_power_per_point}

    assert winners[D("0.25")] == "vsd"
    assert winners[D("0.5")] == "vsd"
    # at full load every mode draws rated power -> tie broken alphabetically
    assert winners[D("1")] == "load/unload"


def test_load_duration_profile_gives_annual_energy_cost_and_blow_off() -> None:
    profile = (LoadDurationBin(D("0.5"), D("4000")), LoadDurationBin(D("1"), D("2000")))
    result = compare_part_load(
        inputs(LOAD_UNLOAD, IGV, load_duration=profile, electricity_tariff_per_kwh=D("7"))
    )
    lu, igv = result.candidates

    assert result.profile_hours == D("6000")
    assert lu.annual_energy_kwh == D("450000")  # 62.5 x 4000 + 100 x 2000
    assert lu.annual_energy_cost == D("3150000")
    assert lu.annual_blow_off_volume_nm3 == D("0")
    assert igv.annual_energy_kwh == D("520000")  # 80 x 4000 + 100 x 2000
    assert igv.annual_blow_off_volume_nm3 == D("1000000")  # 250 Nm3/h x 4000 h
    assert result.lowest_annual_energy_label == "load/unload"


def test_zero_flow_specific_power_is_undefined_not_zero() -> None:
    result = compare_part_load(inputs(MODULATION, capacity_fractions=(D("0"),)))
    point = result.candidates[0].points[0]

    assert point.power_kw == D("25")  # duty 0 -> unloaded
    assert point.specific_power_kw_per_nm3_per_min is None


@pytest.mark.parametrize(
    "kwargs, message",
    [
        ({"candidates": ()}, "At least one control-mode candidate"),
        ({"candidates": (LOAD_UNLOAD, LOAD_UNLOAD)}, "labels must be unique"),
        ({"capacity_fractions": (D("1.5"),)}, "within 0 and 1"),
        ({"load_duration": (LoadDurationBin(D("0.5"), D("9000")),)}, "exceed a calendar year"),
    ],
)
def test_inconsistent_requests_are_rejected(kwargs: dict, message: str) -> None:
    base = {"candidates": (LOAD_UNLOAD,)}
    base.update(kwargs)
    with pytest.raises(InvalidPartLoadComparisonInputError, match=message):
        compare_part_load(inputs(*base.pop("candidates"), **base))


def test_curve_errors_carry_the_candidate_label() -> None:
    bad = PartLoadCandidate("igv", PartLoadCurve(mode=PartLoadMode.INLET_GUIDE_VANE))
    with pytest.raises(InvalidPartLoadComparisonInputError, match="igv: turndown_flow_fraction"):
        compare_part_load(inputs(bad))
