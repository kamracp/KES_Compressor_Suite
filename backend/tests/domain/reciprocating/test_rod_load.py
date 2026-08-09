from decimal import Decimal

import pytest

from app.domain.reciprocating.rod_load import (
    InvalidRodLoadInputError,
    calculate_rod_load,
)


def test_calculate_rod_load() -> None:
    result = calculate_rod_load(
        piston_area_m2=Decimal("0.0706858"),
        rod_area_m2=Decimal("0.0038484"),
        suction_pressure_bar=Decimal("30"),
        discharge_pressure_bar=Decimal("43.27"),
        allowable_rod_load_kn=Decimal("450"),
    )

    assert result.compression_load_kn > Decimal("90")
    assert result.compression_load_kn < Decimal("95")

    assert result.tension_load_kn > Decimal("85")
    assert result.tension_load_kn < Decimal("90")

    assert result.maximum_absolute_load_kn == result.compression_load_kn
    assert result.rod_load_is_adequate is True


def test_overload_is_detected() -> None:
    result = calculate_rod_load(
        piston_area_m2=Decimal("0.0706858"),
        rod_area_m2=Decimal("0.0038484"),
        suction_pressure_bar=Decimal("30"),
        discharge_pressure_bar=Decimal("90"),
        allowable_rod_load_kn=Decimal("400"),
    )

    assert result.maximum_absolute_load_kn > Decimal("400")
    assert result.rod_load_is_adequate is False


def test_zero_piston_area_is_rejected() -> None:
    with pytest.raises(
        InvalidRodLoadInputError,
        match="Piston area must be greater than zero",
    ):
        calculate_rod_load(
            piston_area_m2=Decimal("0"),
            rod_area_m2=Decimal("0.003"),
            suction_pressure_bar=Decimal("30"),
            discharge_pressure_bar=Decimal("43"),
            allowable_rod_load_kn=Decimal("450"),
        )


def test_negative_rod_area_is_rejected() -> None:
    with pytest.raises(
        InvalidRodLoadInputError,
        match="Rod area cannot be negative",
    ):
        calculate_rod_load(
            piston_area_m2=Decimal("0.07"),
            rod_area_m2=Decimal("-0.001"),
            suction_pressure_bar=Decimal("30"),
            discharge_pressure_bar=Decimal("43"),
            allowable_rod_load_kn=Decimal("450"),
        )


def test_rod_area_must_be_smaller_than_piston_area() -> None:
    with pytest.raises(
        InvalidRodLoadInputError,
        match="Rod area must be smaller than piston area",
    ):
        calculate_rod_load(
            piston_area_m2=Decimal("0.07"),
            rod_area_m2=Decimal("0.07"),
            suction_pressure_bar=Decimal("30"),
            discharge_pressure_bar=Decimal("43"),
            allowable_rod_load_kn=Decimal("450"),
        )


def test_zero_suction_pressure_is_rejected() -> None:
    with pytest.raises(
        InvalidRodLoadInputError,
        match="Suction absolute pressure must be greater than zero",
    ):
        calculate_rod_load(
            piston_area_m2=Decimal("0.07"),
            rod_area_m2=Decimal("0.003"),
            suction_pressure_bar=Decimal("0"),
            discharge_pressure_bar=Decimal("43"),
            allowable_rod_load_kn=Decimal("450"),
        )


def test_discharge_pressure_must_exceed_suction_pressure() -> None:
    with pytest.raises(
        InvalidRodLoadInputError,
        match="Discharge pressure must be greater than suction pressure",
    ):
        calculate_rod_load(
            piston_area_m2=Decimal("0.07"),
            rod_area_m2=Decimal("0.003"),
            suction_pressure_bar=Decimal("30"),
            discharge_pressure_bar=Decimal("30"),
            allowable_rod_load_kn=Decimal("450"),
        )


def test_allowable_rod_load_must_be_positive() -> None:
    with pytest.raises(
        InvalidRodLoadInputError,
        match="Allowable rod load must be greater than zero",
    ):
        calculate_rod_load(
            piston_area_m2=Decimal("0.07"),
            rod_area_m2=Decimal("0.003"),
            suction_pressure_bar=Decimal("30"),
            discharge_pressure_bar=Decimal("43"),
            allowable_rod_load_kn=Decimal("0"),
        )
