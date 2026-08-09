from decimal import Decimal

import pytest

from app.domain.compression.staging import (
    InvalidStagingInputError,
    calculate_equal_staging,
    recommend_number_of_stages,
)


def test_recommend_number_of_stages() -> None:
    result = recommend_number_of_stages(
        suction_pressure_bar=Decimal("30"),
        discharge_pressure_bar=Decimal("90"),
        maximum_stage_ratio=Decimal("2"),
    )

    assert result == 2


def test_equal_staging_three_stages() -> None:
    result = calculate_equal_staging(
        suction_pressure_bar=Decimal("30"),
        discharge_pressure_bar=Decimal("90"),
        number_of_stages=3,
    )

    assert result.number_of_stages == 3
    assert result.overall_compression_ratio == Decimal("3")
    assert Decimal("1.44") < result.stage_compression_ratio < Decimal("1.45")
    assert len(result.stages) == 3


def test_first_stage_pressures() -> None:
    result = calculate_equal_staging(
        suction_pressure_bar=Decimal("30"),
        discharge_pressure_bar=Decimal("90"),
        number_of_stages=3,
    )

    first_stage = result.stages[0]

    assert first_stage.stage_number == 1
    assert first_stage.inlet_pressure_bar == Decimal("30")
    assert Decimal("43.2") < first_stage.outlet_pressure_bar < Decimal("43.4")


def test_last_stage_reaches_exact_discharge_pressure() -> None:
    result = calculate_equal_staging(
        suction_pressure_bar=Decimal("30"),
        discharge_pressure_bar=Decimal("90"),
        number_of_stages=3,
    )

    last_stage = result.stages[-1]

    assert last_stage.outlet_pressure_bar == Decimal("90")


def test_invalid_suction_pressure_is_rejected() -> None:
    with pytest.raises(
        InvalidStagingInputError,
        match="Suction absolute pressure must be greater than zero",
    ):
        calculate_equal_staging(
            suction_pressure_bar=Decimal("0"),
            discharge_pressure_bar=Decimal("90"),
            number_of_stages=3,
        )


def test_discharge_pressure_must_exceed_suction_pressure() -> None:
    with pytest.raises(
        InvalidStagingInputError,
        match="Discharge pressure must be greater than suction pressure",
    ):
        calculate_equal_staging(
            suction_pressure_bar=Decimal("30"),
            discharge_pressure_bar=Decimal("30"),
            number_of_stages=3,
        )


def test_invalid_number_of_stages_is_rejected() -> None:
    with pytest.raises(
        InvalidStagingInputError,
        match="Number of compression stages must be at least one",
    ):
        calculate_equal_staging(
            suction_pressure_bar=Decimal("30"),
            discharge_pressure_bar=Decimal("90"),
            number_of_stages=0,
        )


def test_invalid_maximum_stage_ratio_is_rejected() -> None:
    with pytest.raises(
        InvalidStagingInputError,
        match="Maximum stage compression ratio must be greater than one",
    ):
        recommend_number_of_stages(
            suction_pressure_bar=Decimal("30"),
            discharge_pressure_bar=Decimal("90"),
            maximum_stage_ratio=Decimal("1"),
        )
