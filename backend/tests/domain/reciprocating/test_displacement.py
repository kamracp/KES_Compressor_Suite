from decimal import Decimal

import pytest

from app.domain.reciprocating.displacement import (
    InvalidReciprocatingGeometryError,
    calculate_displacement,
)
from app.domain.reciprocating.recip_models import (
    CylinderAction,
    ReciprocatingCylinderGeometry,
)


def build_double_acting_geometry() -> ReciprocatingCylinderGeometry:
    return ReciprocatingCylinderGeometry(
        bore_mm=Decimal("300"),
        stroke_mm=Decimal("400"),
        rod_diameter_mm=Decimal("70"),
        speed_rpm=Decimal("600"),
        clearance_fraction=Decimal("0.10"),
        action=CylinderAction.DOUBLE_ACTING,
    )


def test_double_acting_displacement() -> None:
    result = calculate_displacement(build_double_acting_geometry())

    assert result.piston_area_m2 > Decimal("0.070")
    assert result.piston_area_m2 < Decimal("0.071")

    assert result.rod_area_m2 > Decimal("0.0038")
    assert result.rod_area_m2 < Decimal("0.0039")

    assert result.head_end_displacement_m3_per_min > Decimal("16.9")
    assert result.head_end_displacement_m3_per_min < Decimal("17.0")

    assert result.crank_end_displacement_m3_per_min > Decimal("16.0")
    assert result.crank_end_displacement_m3_per_min < Decimal("16.1")

    assert result.total_displacement_m3_per_min > Decimal("33.0")
    assert result.total_displacement_m3_per_min < Decimal("33.1")

    assert result.total_displacement_m3_per_hr > Decimal("1980")
    assert result.total_displacement_m3_per_hr < Decimal("1985")


def test_single_acting_has_no_crank_end_displacement() -> None:
    geometry = ReciprocatingCylinderGeometry(
        bore_mm=Decimal("300"),
        stroke_mm=Decimal("400"),
        rod_diameter_mm=Decimal("70"),
        speed_rpm=Decimal("600"),
        clearance_fraction=Decimal("0.10"),
        action=CylinderAction.SINGLE_ACTING,
    )

    result = calculate_displacement(geometry)

    assert result.crank_end_displacement_m3_per_min == Decimal("0")
    assert result.total_displacement_m3_per_min == result.head_end_displacement_m3_per_min


def test_zero_bore_is_rejected() -> None:
    geometry = ReciprocatingCylinderGeometry(
        bore_mm=Decimal("0"),
        stroke_mm=Decimal("400"),
        rod_diameter_mm=Decimal("70"),
        speed_rpm=Decimal("600"),
        clearance_fraction=Decimal("0.10"),
    )

    with pytest.raises(
        InvalidReciprocatingGeometryError,
        match="Cylinder bore must be greater than zero",
    ):
        calculate_displacement(geometry)


def test_zero_stroke_is_rejected() -> None:
    geometry = ReciprocatingCylinderGeometry(
        bore_mm=Decimal("300"),
        stroke_mm=Decimal("0"),
        rod_diameter_mm=Decimal("70"),
        speed_rpm=Decimal("600"),
        clearance_fraction=Decimal("0.10"),
    )

    with pytest.raises(
        InvalidReciprocatingGeometryError,
        match="Stroke length must be greater than zero",
    ):
        calculate_displacement(geometry)


def test_negative_rod_diameter_is_rejected() -> None:
    geometry = ReciprocatingCylinderGeometry(
        bore_mm=Decimal("300"),
        stroke_mm=Decimal("400"),
        rod_diameter_mm=Decimal("-1"),
        speed_rpm=Decimal("600"),
        clearance_fraction=Decimal("0.10"),
    )

    with pytest.raises(
        InvalidReciprocatingGeometryError,
        match="Rod diameter cannot be negative",
    ):
        calculate_displacement(geometry)


def test_rod_diameter_must_be_smaller_than_bore() -> None:
    geometry = ReciprocatingCylinderGeometry(
        bore_mm=Decimal("300"),
        stroke_mm=Decimal("400"),
        rod_diameter_mm=Decimal("300"),
        speed_rpm=Decimal("600"),
        clearance_fraction=Decimal("0.10"),
    )

    with pytest.raises(
        InvalidReciprocatingGeometryError,
        match="Rod diameter must be smaller than cylinder bore",
    ):
        calculate_displacement(geometry)


def test_zero_speed_is_rejected() -> None:
    geometry = ReciprocatingCylinderGeometry(
        bore_mm=Decimal("300"),
        stroke_mm=Decimal("400"),
        rod_diameter_mm=Decimal("70"),
        speed_rpm=Decimal("0"),
        clearance_fraction=Decimal("0.10"),
    )

    with pytest.raises(
        InvalidReciprocatingGeometryError,
        match="Compressor speed must be greater than zero",
    ):
        calculate_displacement(geometry)
