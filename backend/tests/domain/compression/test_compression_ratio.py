from decimal import Decimal

import pytest

from app.domain.compression.compression_ratio import (
    InvalidCompressionInputError,
    calculate_compression_ratio,
)


def test_calculate_compression_ratio() -> None:
    result = calculate_compression_ratio(
        suction_pressure_bar=Decimal("30"),
        discharge_pressure_bar=Decimal("90"),
        number_of_stages=3,
    )

    assert result.overall_compression_ratio == Decimal("3")
    assert Decimal("1.44") < result.stage_compression_ratio < Decimal("1.45")
    assert result.number_of_stages == 3


def test_single_stage_compression_ratio() -> None:
    result = calculate_compression_ratio(
        suction_pressure_bar=Decimal("10"),
        discharge_pressure_bar=Decimal("30"),
        number_of_stages=1,
    )

    assert result.overall_compression_ratio == Decimal("3")
    assert result.stage_compression_ratio == Decimal("3.0")


def test_zero_suction_pressure_is_rejected() -> None:
    with pytest.raises(
        InvalidCompressionInputError,
        match="Suction absolute pressure must be greater than zero",
    ):
        calculate_compression_ratio(
            suction_pressure_bar=Decimal("0"),
            discharge_pressure_bar=Decimal("90"),
            number_of_stages=3,
        )


def test_zero_discharge_pressure_is_rejected() -> None:
    with pytest.raises(
        InvalidCompressionInputError,
        match="Discharge absolute pressure must be greater than zero",
    ):
        calculate_compression_ratio(
            suction_pressure_bar=Decimal("30"),
            discharge_pressure_bar=Decimal("0"),
            number_of_stages=3,
        )


def test_discharge_pressure_must_exceed_suction_pressure() -> None:
    with pytest.raises(
        InvalidCompressionInputError,
        match="Discharge pressure must be greater than suction pressure",
    ):
        calculate_compression_ratio(
            suction_pressure_bar=Decimal("30"),
            discharge_pressure_bar=Decimal("30"),
            number_of_stages=3,
        )


def test_zero_number_of_stages_is_rejected() -> None:
    with pytest.raises(
        InvalidCompressionInputError,
        match="Number of compression stages must be at least one",
    ):
        calculate_compression_ratio(
            suction_pressure_bar=Decimal("30"),
            discharge_pressure_bar=Decimal("90"),
            number_of_stages=0,
        )
