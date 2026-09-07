"""C-8: part-load guideline constants and their evidence linkage."""

from decimal import Decimal

from app.data.evidence.loader import derived_bounds
from app.domain.compliance.standards_registry import get_standard
from app.schemas._bounds import (
    DEFAULT_MODULATION_FLOOR_CAPACITY_FRACTION,
    MAX_CENTRIFUGAL_TURNDOWN_FRACTION,
    MAX_CENTRIFUGAL_UNLOAD_POWER_FRACTION,
    MAX_MODULATION_FLOOR_CAPACITY_FRACTION,
    MIN_CENTRIFUGAL_POWER_FRACTION_AT_TURNDOWN,
    MIN_CENTRIFUGAL_TURNDOWN_FRACTION,
    MIN_CENTRIFUGAL_UNLOAD_POWER_FRACTION,
    MIN_MODULATION_FLOOR_CAPACITY_FRACTION,
    MODULATION_ZERO_FLOW_POWER_FRACTION,
    VARIABLE_DISPLACEMENT_FLOOR_CAPACITY_FRACTION,
)


def test_registry_carries_the_c8_sources() -> None:
    cagi = get_standard("CAGI-CENTRIFUGAL-CAPACITY-CONTROLS")
    cam = get_standard("ATLASCOPCO-CAM-9ED-2019")

    assert "30-40 percent" in cagi.notes
    assert "15-30 percent" in cam.notes
    assert "20 percent" in cam.notes


def test_modulation_constants_follow_doe_and_atlas_copco() -> None:
    assert Decimal("0.70") == MODULATION_ZERO_FLOW_POWER_FRACTION
    assert Decimal("0.10") == MIN_MODULATION_FLOOR_CAPACITY_FRACTION
    assert Decimal("0.40") == MAX_MODULATION_FLOOR_CAPACITY_FRACTION
    assert DEFAULT_MODULATION_FLOOR_CAPACITY_FRACTION == MAX_MODULATION_FLOOR_CAPACITY_FRACTION
    assert Decimal("0.50") == VARIABLE_DISPLACEMENT_FLOOR_CAPACITY_FRACTION


def test_centrifugal_bounds_enclose_the_published_points() -> None:
    # CAGI typical 30-40 %, Atlas Copco ZH "over 25 %", CAGI example 15 %.
    for turndown in (Decimal("0.15"), Decimal("0.25"), Decimal("0.30"), Decimal("0.40")):
        assert MIN_CENTRIFUGAL_TURNDOWN_FRACTION <= turndown <= MAX_CENTRIFUGAL_TURNDOWN_FRACTION
    # published IGV example: 80 % power at 75 % flow
    assert Decimal("0.80") >= MIN_CENTRIFUGAL_POWER_FRACTION_AT_TURNDOWN
    # Atlas Copco CAM: auto-dual off-loaded ~20 %
    assert (
        MIN_CENTRIFUGAL_UNLOAD_POWER_FRACTION
        <= Decimal("0.20")
        <= MAX_CENTRIFUGAL_UNLOAD_POWER_FRACTION
    )


def test_atlas_copco_evidence_set_documents_the_centrifugal_points() -> None:
    turndown = derived_bounds("centrifugal_turndown_fraction")
    unload = derived_bounds("centrifugal_unload_power_fraction")
    igv = derived_bounds("igv_energy_saving_vs_inlet_throttle_fraction")

    assert len(turndown) == 1 and turndown[0].minimum == 0.25
    assert len(unload) == 1 and unload[0].maximum == 0.20
    assert len(igv) == 1 and igv[0].maximum == 0.09
    assert all(
        b.evidence_set_id == "MFR-ATLASCOPCO-AIR-RANGE-2026-09" for b in (*turndown, *unload, *igv)
    )
