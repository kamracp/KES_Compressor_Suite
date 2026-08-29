from decimal import Decimal

import pytest

from app.domain.rotary_screw.displacement import (
    InvalidRotaryScrewGeometryError,
    calculate_theoretical_displacement,
)
from app.domain.rotary_screw.models import RotaryScrewRotorGeometry


def test_theoretical_displacement_matches_hand_calculation() -> None:
    # D = 0.2 m, L = 0.3 m, C-theta = 0.5 (typical mid-range value), N = 3000 rpm
    # V_th_per_rev = 0.5 * 0.2^2 * 0.3 = 0.006 m3/rev
    # flow = 0.006 * 3000 = 18 m3/min
    geometry = RotaryScrewRotorGeometry(
        male_rotor_diameter_mm=Decimal("200"),
        rotor_length_mm=Decimal("300"),
        area_utilisation_coefficient=Decimal("0.5"),
    )

    result = calculate_theoretical_displacement(
        geometry=geometry,
        rotational_speed_rpm=Decimal("3000"),
    )

    assert result.theoretical_displacement_m3_per_min == Decimal("18.000")


def test_rejects_zero_rotor_diameter() -> None:
    geometry = RotaryScrewRotorGeometry(
        male_rotor_diameter_mm=Decimal("0"),
        rotor_length_mm=Decimal("300"),
        area_utilisation_coefficient=Decimal("0.5"),
    )

    with pytest.raises(InvalidRotaryScrewGeometryError):
        calculate_theoretical_displacement(
            geometry=geometry,
            rotational_speed_rpm=Decimal("3000"),
        )


def test_rejects_negative_rotational_speed() -> None:
    geometry = RotaryScrewRotorGeometry(
        male_rotor_diameter_mm=Decimal("200"),
        rotor_length_mm=Decimal("300"),
        area_utilisation_coefficient=Decimal("0.5"),
    )

    with pytest.raises(InvalidRotaryScrewGeometryError):
        calculate_theoretical_displacement(
            geometry=geometry,
            rotational_speed_rpm=Decimal("-100"),
        )
