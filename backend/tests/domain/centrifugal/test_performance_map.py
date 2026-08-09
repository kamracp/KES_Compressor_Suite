from decimal import Decimal

import pytest

from app.domain.centrifugal.performance_map import (
    InvalidPerformanceMapInputError,
    calculate_performance_map,
)


def test_calculate_default_performance_map() -> None:
    result = calculate_performance_map(
        design_speed_rpm=Decimal("8000"),
        design_flow_m3_per_hr=Decimal("14143.4"),
        design_head_kj_per_kg=Decimal("155.667"),
    )

    assert len(result.points) == 3

    point_100 = result.points[0]
    point_90 = result.points[1]
    point_80 = result.points[2]

    assert point_100.speed_fraction == Decimal("1.00")
    assert point_100.speed_rpm == Decimal("8000.00")
    assert point_100.flow_m3_per_hr == Decimal("14143.400")
    assert point_100.head_kj_per_kg == Decimal("155.6670000")

    assert point_90.speed_fraction == Decimal("0.90")
    assert point_90.speed_rpm == Decimal("7200.00")
    assert point_90.flow_m3_per_hr == Decimal("12729.060")
    assert point_90.head_kj_per_kg == Decimal("126.0902700")

    assert point_80.speed_fraction == Decimal("0.80")
    assert point_80.speed_rpm == Decimal("6400.00")
    assert point_80.flow_m3_per_hr == Decimal("11314.720")
    assert point_80.head_kj_per_kg == Decimal("99.6268800")


def test_custom_speed_fractions_are_supported() -> None:
    result = calculate_performance_map(
        design_speed_rpm=Decimal("10000"),
        design_flow_m3_per_hr=Decimal("1000"),
        design_head_kj_per_kg=Decimal("100"),
        speed_fractions=(
            Decimal("1.00"),
            Decimal("0.75"),
        ),
    )

    assert len(result.points) == 2
    assert result.points[1].speed_rpm == Decimal("7500.00")
    assert result.points[1].flow_m3_per_hr == Decimal("750.00")
    assert result.points[1].head_kj_per_kg == Decimal("56.250000")


def test_zero_design_speed_is_rejected() -> None:
    with pytest.raises(
        InvalidPerformanceMapInputError,
        match="Design speed must be greater than zero",
    ):
        calculate_performance_map(
            design_speed_rpm=Decimal("0"),
            design_flow_m3_per_hr=Decimal("1000"),
            design_head_kj_per_kg=Decimal("100"),
        )


def test_zero_design_flow_is_rejected() -> None:
    with pytest.raises(
        InvalidPerformanceMapInputError,
        match="Design flow must be greater than zero",
    ):
        calculate_performance_map(
            design_speed_rpm=Decimal("8000"),
            design_flow_m3_per_hr=Decimal("0"),
            design_head_kj_per_kg=Decimal("100"),
        )


def test_zero_design_head_is_rejected() -> None:
    with pytest.raises(
        InvalidPerformanceMapInputError,
        match="Design head must be greater than zero",
    ):
        calculate_performance_map(
            design_speed_rpm=Decimal("8000"),
            design_flow_m3_per_hr=Decimal("1000"),
            design_head_kj_per_kg=Decimal("0"),
        )


def test_empty_speed_fraction_list_is_rejected() -> None:
    with pytest.raises(
        InvalidPerformanceMapInputError,
        match="At least one speed fraction must be provided",
    ):
        calculate_performance_map(
            design_speed_rpm=Decimal("8000"),
            design_flow_m3_per_hr=Decimal("1000"),
            design_head_kj_per_kg=Decimal("100"),
            speed_fractions=(),
        )


def test_zero_speed_fraction_is_rejected() -> None:
    with pytest.raises(
        InvalidPerformanceMapInputError,
        match="Speed fractions must be greater than zero",
    ):
        calculate_performance_map(
            design_speed_rpm=Decimal("8000"),
            design_flow_m3_per_hr=Decimal("1000"),
            design_head_kj_per_kg=Decimal("100"),
            speed_fractions=(
                Decimal("1.00"),
                Decimal("0"),
            ),
        )
