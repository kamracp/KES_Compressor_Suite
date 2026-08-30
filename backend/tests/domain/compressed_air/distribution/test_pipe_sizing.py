from decimal import Decimal

import pytest

from app.domain.compressed_air.distribution.pipe_sizing import (
    InvalidPipeSizingInputError,
    PipeSizingInput,
    calculate_pipe_velocity,
)


def test_calculate_pipe_velocity() -> None:
    result = calculate_pipe_velocity(
        PipeSizingInput(
            normal_flow_nm3_per_hr=Decimal("3000"),
            operating_pressure_bar_g=Decimal("6.5"),
            operating_temperature_k=Decimal("303.15"),
            pipe_internal_diameter_mm=Decimal("100"),
        )
    )

    assert result.actual_flow_m3_per_hr > Decimal("0")
    assert result.actual_flow_m3_per_s > Decimal("0")
    assert result.pipe_cross_section_area_m2 > Decimal("0")
    assert result.air_velocity_m_per_s > Decimal("0")

    assert result.operating_pressure_bar_abs == (Decimal("6.5") + Decimal("1.01325"))


def test_higher_operating_pressure_reduces_actual_flow() -> None:
    low_pressure = calculate_pipe_velocity(
        PipeSizingInput(
            normal_flow_nm3_per_hr=Decimal("3000"),
            operating_pressure_bar_g=Decimal("5"),
            operating_temperature_k=Decimal("303.15"),
            pipe_internal_diameter_mm=Decimal("100"),
        )
    )

    high_pressure = calculate_pipe_velocity(
        PipeSizingInput(
            normal_flow_nm3_per_hr=Decimal("3000"),
            operating_pressure_bar_g=Decimal("8"),
            operating_temperature_k=Decimal("303.15"),
            pipe_internal_diameter_mm=Decimal("100"),
        )
    )

    assert high_pressure.actual_flow_m3_per_hr < low_pressure.actual_flow_m3_per_hr

    assert high_pressure.air_velocity_m_per_s < low_pressure.air_velocity_m_per_s


def test_larger_pipe_reduces_velocity() -> None:
    small_pipe = calculate_pipe_velocity(
        PipeSizingInput(
            normal_flow_nm3_per_hr=Decimal("3000"),
            operating_pressure_bar_g=Decimal("6.5"),
            operating_temperature_k=Decimal("303.15"),
            pipe_internal_diameter_mm=Decimal("80"),
        )
    )

    large_pipe = calculate_pipe_velocity(
        PipeSizingInput(
            normal_flow_nm3_per_hr=Decimal("3000"),
            operating_pressure_bar_g=Decimal("6.5"),
            operating_temperature_k=Decimal("303.15"),
            pipe_internal_diameter_mm=Decimal("150"),
        )
    )

    assert large_pipe.air_velocity_m_per_s < small_pipe.air_velocity_m_per_s


def test_velocity_screening_recommended() -> None:
    result = calculate_pipe_velocity(
        PipeSizingInput(
            normal_flow_nm3_per_hr=Decimal("1000"),
            operating_pressure_bar_g=Decimal("7"),
            operating_temperature_k=Decimal("303.15"),
            pipe_internal_diameter_mm=Decimal("150"),
        )
    )

    assert result.velocity_screening_status == "RECOMMENDED"


def test_velocity_screening_thresholds_match_bcas_cagi() -> None:
    from app.domain.compressed_air.distribution.pipe_sizing import (
        VELOCITY_ABSOLUTE_LIMIT_M_PER_S,
        VELOCITY_RECOMMENDED_LIMIT_M_PER_S,
        _screen_velocity,
    )

    assert VELOCITY_RECOMMENDED_LIMIT_M_PER_S == Decimal("6")
    assert VELOCITY_ABSOLUTE_LIMIT_M_PER_S == Decimal("9")

    assert _screen_velocity(Decimal("6")) == "RECOMMENDED"
    assert _screen_velocity(Decimal("6.01")) == "CAUTION"
    assert _screen_velocity(Decimal("9")) == "CAUTION"
    assert _screen_velocity(Decimal("9.01")) == "EXCESSIVE"


def test_velocity_screening_excessive() -> None:
    result = calculate_pipe_velocity(
        PipeSizingInput(
            normal_flow_nm3_per_hr=Decimal("5000"),
            operating_pressure_bar_g=Decimal("6"),
            operating_temperature_k=Decimal("303.15"),
            pipe_internal_diameter_mm=Decimal("50"),
        )
    )

    assert result.velocity_screening_status == "EXCESSIVE"


def test_zero_flow_is_rejected() -> None:
    with pytest.raises(
        InvalidPipeSizingInputError,
        match="Normal flow must be greater than zero",
    ):
        calculate_pipe_velocity(
            PipeSizingInput(
                normal_flow_nm3_per_hr=Decimal("0"),
                operating_pressure_bar_g=Decimal("6"),
                operating_temperature_k=Decimal("303.15"),
                pipe_internal_diameter_mm=Decimal("100"),
            )
        )


def test_negative_pressure_is_rejected() -> None:
    with pytest.raises(
        InvalidPipeSizingInputError,
        match="Operating gauge pressure cannot be negative",
    ):
        calculate_pipe_velocity(
            PipeSizingInput(
                normal_flow_nm3_per_hr=Decimal("1000"),
                operating_pressure_bar_g=Decimal("-0.1"),
                operating_temperature_k=Decimal("303.15"),
                pipe_internal_diameter_mm=Decimal("100"),
            )
        )


def test_zero_pipe_diameter_is_rejected() -> None:
    with pytest.raises(
        InvalidPipeSizingInputError,
        match="Pipe internal diameter must be greater than zero",
    ):
        calculate_pipe_velocity(
            PipeSizingInput(
                normal_flow_nm3_per_hr=Decimal("1000"),
                operating_pressure_bar_g=Decimal("6"),
                operating_temperature_k=Decimal("303.15"),
                pipe_internal_diameter_mm=Decimal("0"),
            )
        )


def test_zero_temperature_is_rejected() -> None:
    with pytest.raises(
        InvalidPipeSizingInputError,
        match="Operating temperature must be greater than zero",
    ):
        calculate_pipe_velocity(
            PipeSizingInput(
                normal_flow_nm3_per_hr=Decimal("1000"),
                operating_pressure_bar_g=Decimal("6"),
                operating_temperature_k=Decimal("0"),
                pipe_internal_diameter_mm=Decimal("100"),
            )
        )
