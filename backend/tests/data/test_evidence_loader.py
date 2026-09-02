import pytest

from app.data.evidence.loader import (
    DerivedBound,
    bound_envelope,
    derived_bounds,
    get_evidence,
    list_evidence_files,
    load_all_evidence,
)
from app.domain.compliance.standards_registry import (
    StandardAuthority,
    get_standard,
)

COMPAIR = "MFR-COMPAIR-OILFREE-SCREW-2026-09"
KAESER = "MFR-KAESER-OILFREE-SCREW-2026-09"
KAESER_OI = "MFR-KAESER-OILINJ-SCREW-2026-09"
RECIP = "MFR-RECIP-FRAME-LIMITS-2026-09"
ATLAS = "MFR-ATLASCOPCO-AIR-RANGE-2026-09"


def test_bundled_files_are_discovered() -> None:
    assert list_evidence_files() == (
        "atlas_copco_air_range.json",
        "compair_oil_free_screw.json",
        "kaeser_oil_free_screw.json",
        "kaeser_oil_injected_screw.json",
        "recip_frame_limits.json",
    )


def test_every_evidence_set_is_registered_as_manufacturer() -> None:
    loaded = load_all_evidence()
    assert set(loaded) == {COMPAIR, KAESER, KAESER_OI, RECIP, ATLAS}
    for evidence_id in loaded:
        entry = get_standard(evidence_id)
        assert entry is not None
        assert entry.authority is StandardAuthority.MANUFACTURER


def test_compair_model_count_matches_brochures() -> None:
    data = get_evidence(COMPAIR)
    count = sum(
        len(series.get("fixed_speed_models", [])) + len(series.get("regulated_speed_models", []))
        for series in data["series"]
    )
    assert count == 43
    assert [s["series_id"] for s in data["series"]] == [
        "DH",
        "D37-75",
        "ULTIMA",
        "DX90-160",
        "DX200-355",
    ]


def test_kaeser_model_count_matches_brochure() -> None:
    data = get_evidence(KAESER)
    assert sum(len(series["models"]) for series in data["series"]) == 16
    assert [s["series_id"] for s in data["series"]] == ["CSG-2", "DSG-2", "FSG-2"]


def test_kaeser_heat_recovery_example_is_self_consistent() -> None:
    example = get_evidence(KAESER)["heat_recovery"]["worked_example_brochure_p18"]
    power = example["package_power_kw"]
    fraction = example["recoverable_fraction_of_input"]
    assert power * fraction == pytest.approx(example["recoverable_heat_kw"], abs=0.1)
    assert power / example["rated_motor_kw"] == pytest.approx(
        example["package_power_to_nameplate_ratio"], abs=0.001
    )
    assert example["recoverable_heat_kw"] * example["annual_hours"] == pytest.approx(
        example["annual_recovered_kwh"], rel=0.001
    )


def test_every_derived_bound_has_a_limit_and_a_basis() -> None:
    bounds = derived_bounds()
    assert len(bounds) == 11 + 12 + 4 + 4 + 8
    for bound in bounds:
        assert isinstance(bound, DerivedBound)
        assert bound.minimum is not None or bound.maximum is not None
        assert bound.basis
        if bound.minimum is not None and bound.maximum is not None:
            assert bound.minimum < bound.maximum


def test_bound_envelope_is_union_across_vendors() -> None:
    assert bound_envelope("working_pressure_bar_g") == (3.5, 15)
    assert bound_envelope("rated_motor_power_kw") == (15, 900)
    assert bound_envelope("fad_m3_min") == (0.32, 150)
    assert bound_envelope("package_noise_db_a") == (60, 84)
    assert bound_envelope("recovered_hot_water_temp_c") == (None, 90)
    assert bound_envelope("no_such_parameter") == (None, None)


def test_derived_bounds_filter_by_parameter() -> None:
    ambient = derived_bounds("ambient_temperature_c_design")
    assert {b.evidence_set_id for b in ambient} == {COMPAIR, KAESER}
    assert {b.maximum for b in ambient} == {45, 46}
