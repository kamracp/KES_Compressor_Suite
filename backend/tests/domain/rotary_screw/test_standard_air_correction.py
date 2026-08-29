from decimal import Decimal

import pytest

from app.domain.rotary_screw.standard_air_correction import (
    InvalidStandardAirCorrectionInputError,
    correct_fad_to_standard_air,
)


def test_lower_site_pressure_reduces_corrected_fad() -> None:
    # Rated 10 m3/min at 1 bar a / 300 K reference; site at 0.9 bar a, same temp.
    # corrected = 10 * (0.9/1) * (300/300) = 9.000
    result = correct_fad_to_standard_air(
        rated_fad_m3_per_min=Decimal("10"),
        reference_pressure_bar_a=Decimal("1"),
        reference_temperature_k=Decimal("300"),
        site_inlet_pressure_bar_a=Decimal("0.9"),
        site_inlet_temperature_k=Decimal("300"),
    )

    assert result.corrected_fad_m3_per_min == Decimal("9.000")


def test_higher_site_temperature_reduces_corrected_fad() -> None:
    # Rated 10 m3/min at 1 bar a / 300 K reference; cooler site kept exact:
    # 10 * (1/1) * (300/250) = 12.000
    result = correct_fad_to_standard_air(
        rated_fad_m3_per_min=Decimal("10"),
        reference_pressure_bar_a=Decimal("1"),
        reference_temperature_k=Decimal("300"),
        site_inlet_pressure_bar_a=Decimal("1"),
        site_inlet_temperature_k=Decimal("250"),
    )

    assert result.corrected_fad_m3_per_min == Decimal("12.000")


def test_rejects_zero_rated_fad() -> None:
    with pytest.raises(InvalidStandardAirCorrectionInputError):
        correct_fad_to_standard_air(
            rated_fad_m3_per_min=Decimal("0"),
            reference_pressure_bar_a=Decimal("1"),
            reference_temperature_k=Decimal("300"),
            site_inlet_pressure_bar_a=Decimal("1"),
            site_inlet_temperature_k=Decimal("300"),
        )


def test_rejects_zero_site_pressure() -> None:
    with pytest.raises(InvalidStandardAirCorrectionInputError):
        correct_fad_to_standard_air(
            rated_fad_m3_per_min=Decimal("10"),
            reference_pressure_bar_a=Decimal("1"),
            reference_temperature_k=Decimal("300"),
            site_inlet_pressure_bar_a=Decimal("0"),
            site_inlet_temperature_k=Decimal("300"),
        )
