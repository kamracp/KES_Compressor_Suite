from decimal import Decimal

import pytest

from app.domain.compressed_air.profiles.demand_profile import (
    DemandProfilePoint,
    InvalidDemandProfileInputError,
    calculate_demand_profile,
)


def test_calculate_demand_profile() -> None:
    points = (
        DemandProfilePoint(
            period_index=1,
            label="Night Shift",
            demand_nm3_per_hr=Decimal("1200"),
            required_pressure_bar_g=Decimal("6.0"),
            duration_hours=Decimal("8"),
        ),
        DemandProfilePoint(
            period_index=2,
            label="Day Shift",
            demand_nm3_per_hr=Decimal("2400"),
            required_pressure_bar_g=Decimal("6.5"),
            duration_hours=Decimal("8"),
        ),
        DemandProfilePoint(
            period_index=3,
            label="Peak Production",
            demand_nm3_per_hr=Decimal("3200"),
            required_pressure_bar_g=Decimal("6.5"),
            duration_hours=Decimal("8"),
        ),
    )

    result = calculate_demand_profile(points)

    assert result.minimum_demand_nm3_per_hr == Decimal("1200")
    assert result.maximum_demand_nm3_per_hr == Decimal("3200")
    assert result.total_profile_hours == Decimal("24")
    assert result.total_air_volume_nm3 == Decimal("54400")

    assert result.average_demand_nm3_per_hr == (Decimal("54400") / Decimal("24"))

    assert result.peak_to_average_ratio == (Decimal("3200") / result.average_demand_nm3_per_hr)

    assert result.minimum_required_pressure_bar_g == Decimal("6.0")
    assert result.maximum_required_pressure_bar_g == Decimal("6.5")


def test_weighted_average_uses_duration() -> None:
    points = (
        DemandProfilePoint(
            period_index=1,
            label="Low Demand",
            demand_nm3_per_hr=Decimal("1000"),
            required_pressure_bar_g=Decimal("6"),
            duration_hours=Decimal("20"),
        ),
        DemandProfilePoint(
            period_index=2,
            label="Peak Demand",
            demand_nm3_per_hr=Decimal("3000"),
            required_pressure_bar_g=Decimal("6"),
            duration_hours=Decimal("4"),
        ),
    )

    result = calculate_demand_profile(points)

    expected_volume = Decimal("1000") * Decimal("20") + Decimal("3000") * Decimal("4")

    expected_average = expected_volume / Decimal("24")

    assert result.total_air_volume_nm3 == expected_volume
    assert result.average_demand_nm3_per_hr == expected_average


def test_zero_demand_profile_is_supported() -> None:
    points = (
        DemandProfilePoint(
            period_index=1,
            label="Plant Shutdown",
            demand_nm3_per_hr=Decimal("0"),
            required_pressure_bar_g=Decimal("0"),
            duration_hours=Decimal("8"),
        ),
    )

    result = calculate_demand_profile(points)

    assert result.minimum_demand_nm3_per_hr == Decimal("0")
    assert result.average_demand_nm3_per_hr == Decimal("0")
    assert result.maximum_demand_nm3_per_hr == Decimal("0")
    assert result.peak_to_average_ratio == Decimal("0")


def test_empty_profile_is_rejected() -> None:
    with pytest.raises(
        InvalidDemandProfileInputError,
        match="At least one demand profile point is required",
    ):
        calculate_demand_profile(())


def test_negative_demand_is_rejected() -> None:
    points = (
        DemandProfilePoint(
            period_index=1,
            label="Invalid Demand",
            demand_nm3_per_hr=Decimal("-1"),
            required_pressure_bar_g=Decimal("6"),
            duration_hours=Decimal("1"),
        ),
    )

    with pytest.raises(
        InvalidDemandProfileInputError,
        match="Demand cannot be negative",
    ):
        calculate_demand_profile(points)


def test_negative_pressure_is_rejected() -> None:
    points = (
        DemandProfilePoint(
            period_index=1,
            label="Invalid Pressure",
            demand_nm3_per_hr=Decimal("1000"),
            required_pressure_bar_g=Decimal("-0.1"),
            duration_hours=Decimal("1"),
        ),
    )

    with pytest.raises(
        InvalidDemandProfileInputError,
        match="Required pressure cannot be negative",
    ):
        calculate_demand_profile(points)


def test_zero_duration_is_rejected() -> None:
    points = (
        DemandProfilePoint(
            period_index=1,
            label="Invalid Duration",
            demand_nm3_per_hr=Decimal("1000"),
            required_pressure_bar_g=Decimal("6"),
            duration_hours=Decimal("0"),
        ),
    )

    with pytest.raises(
        InvalidDemandProfileInputError,
        match="Profile point duration must be greater than zero",
    ):
        calculate_demand_profile(points)


def test_negative_period_index_is_rejected() -> None:
    points = (
        DemandProfilePoint(
            period_index=-1,
            label="Invalid Index",
            demand_nm3_per_hr=Decimal("1000"),
            required_pressure_bar_g=Decimal("6"),
            duration_hours=Decimal("1"),
        ),
    )

    with pytest.raises(
        InvalidDemandProfileInputError,
        match="Profile period index cannot be negative",
    ):
        calculate_demand_profile(points)
