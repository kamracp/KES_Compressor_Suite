from decimal import Decimal

import pytest

from app.domain.compressed_air.distribution.pipe_sizing import PipeSizingInput
from app.domain.compressed_air.distribution.pressure_drop import (
    InvalidPressureDropInputError,
    PressureDropInput,
    calculate_pressure_drop,
)


def build_input(
    *,
    flow: str = "3000",
    diameter_mm: str = "100",
    straight_length_m: str = "120",
    fitting_length_m: str = "30",
    density: str = "8.5",
    friction_factor: str = "0.02",
) -> PressureDropInput:
    return PressureDropInput(
        pipe=PipeSizingInput(
            normal_flow_nm3_per_hr=Decimal(flow),
            operating_pressure_bar_g=Decimal("6.5"),
            operating_temperature_k=Decimal("303.15"),
            pipe_internal_diameter_mm=Decimal(diameter_mm),
        ),
        straight_length_m=Decimal(straight_length_m),
        equivalent_fitting_length_m=Decimal(fitting_length_m),
        air_density_kg_per_m3=Decimal(density),
        darcy_friction_factor=Decimal(friction_factor),
    )


def test_calculate_pressure_drop() -> None:
    result = calculate_pressure_drop(build_input())

    assert result.total_equivalent_length_m == Decimal("150")
    assert result.pressure_drop_pa > Decimal("0")
    assert result.pressure_drop_bar > Decimal("0")
    assert result.pressure_drop_bar_per_100m > Decimal("0")


def test_longer_pipe_increases_pressure_drop() -> None:
    short_pipe = calculate_pressure_drop(
        build_input(
            straight_length_m="50",
            fitting_length_m="10",
        )
    )

    long_pipe = calculate_pressure_drop(
        build_input(
            straight_length_m="150",
            fitting_length_m="30",
        )
    )

    assert long_pipe.pressure_drop_bar > short_pipe.pressure_drop_bar


def test_fitting_length_increases_pressure_drop() -> None:
    low_fittings = calculate_pressure_drop(
        build_input(
            fitting_length_m="5",
        )
    )

    high_fittings = calculate_pressure_drop(
        build_input(
            fitting_length_m="60",
        )
    )

    assert high_fittings.pressure_drop_bar > low_fittings.pressure_drop_bar


def test_larger_pipe_reduces_pressure_drop() -> None:
    small_pipe = calculate_pressure_drop(
        build_input(
            diameter_mm="80",
        )
    )

    large_pipe = calculate_pressure_drop(
        build_input(
            diameter_mm="150",
        )
    )

    assert large_pipe.pressure_drop_bar < small_pipe.pressure_drop_bar


def test_higher_flow_increases_pressure_drop() -> None:
    low_flow = calculate_pressure_drop(
        build_input(
            flow="1500",
        )
    )

    high_flow = calculate_pressure_drop(
        build_input(
            flow="4500",
        )
    )

    assert high_flow.pressure_drop_bar > low_flow.pressure_drop_bar


def test_higher_friction_factor_increases_pressure_drop() -> None:
    low_friction = calculate_pressure_drop(
        build_input(
            friction_factor="0.015",
        )
    )

    high_friction = calculate_pressure_drop(
        build_input(
            friction_factor="0.030",
        )
    )

    assert high_friction.pressure_drop_bar > low_friction.pressure_drop_bar


def test_zero_total_length_is_rejected() -> None:
    with pytest.raises(
        InvalidPressureDropInputError,
        match="Total equivalent pipe length must be greater than zero",
    ):
        calculate_pressure_drop(
            build_input(
                straight_length_m="0",
                fitting_length_m="0",
            )
        )


def test_negative_straight_length_is_rejected() -> None:
    with pytest.raises(
        InvalidPressureDropInputError,
        match="Straight pipe length cannot be negative",
    ):
        calculate_pressure_drop(
            build_input(
                straight_length_m="-1",
            )
        )


def test_zero_air_density_is_rejected() -> None:
    with pytest.raises(
        InvalidPressureDropInputError,
        match="Air density must be greater than zero",
    ):
        calculate_pressure_drop(
            build_input(
                density="0",
            )
        )


def test_zero_friction_factor_is_rejected() -> None:
    with pytest.raises(
        InvalidPressureDropInputError,
        match="Darcy friction factor must be greater than zero",
    ):
        calculate_pressure_drop(
            build_input(
                friction_factor="0",
            )
        )


def test_friction_factor_equal_to_one_is_rejected() -> None:
    with pytest.raises(
        InvalidPressureDropInputError,
        match="Darcy friction factor must be less than one",
    ):
        calculate_pressure_drop(
            build_input(
                friction_factor="1",
            )
        )
