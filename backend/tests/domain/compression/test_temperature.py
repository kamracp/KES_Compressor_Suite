from decimal import Decimal

import pytest

from app.domain.compression.temperature import (
    InvalidTemperatureInputError,
    calculate_discharge_temperature,
)


def test_calculate_discharge_temperature() -> None:
    result = calculate_discharge_temperature(
        inlet_temperature_k=Decimal("308.15"),
        stage_compression_ratio=Decimal("1.442"),
        isentropic_exponent=Decimal("1.27"),
        isentropic_efficiency=Decimal("0.80"),
    )

    assert Decimal("332") < result.isentropic_discharge_temperature_k < Decimal("334")
    assert Decimal("338") < result.actual_discharge_temperature_k < Decimal("341")


def test_actual_temperature_exceeds_isentropic_temperature() -> None:
    result = calculate_discharge_temperature(
        inlet_temperature_k=Decimal("300"),
        stage_compression_ratio=Decimal("2"),
        isentropic_exponent=Decimal("1.30"),
        isentropic_efficiency=Decimal("0.75"),
    )

    assert result.actual_discharge_temperature_k > result.isentropic_discharge_temperature_k


def test_inlet_temperature_must_be_positive() -> None:
    with pytest.raises(
        InvalidTemperatureInputError,
        match="Inlet absolute temperature must be greater than zero",
    ):
        calculate_discharge_temperature(
            inlet_temperature_k=Decimal("0"),
            stage_compression_ratio=Decimal("1.5"),
            isentropic_exponent=Decimal("1.27"),
            isentropic_efficiency=Decimal("0.80"),
        )


def test_stage_compression_ratio_must_exceed_one() -> None:
    with pytest.raises(
        InvalidTemperatureInputError,
        match="Stage compression ratio must be greater than one",
    ):
        calculate_discharge_temperature(
            inlet_temperature_k=Decimal("308.15"),
            stage_compression_ratio=Decimal("1"),
            isentropic_exponent=Decimal("1.27"),
            isentropic_efficiency=Decimal("0.80"),
        )


def test_isentropic_exponent_must_exceed_one() -> None:
    with pytest.raises(
        InvalidTemperatureInputError,
        match="Isentropic exponent must be greater than one",
    ):
        calculate_discharge_temperature(
            inlet_temperature_k=Decimal("308.15"),
            stage_compression_ratio=Decimal("1.5"),
            isentropic_exponent=Decimal("1"),
            isentropic_efficiency=Decimal("0.80"),
        )


def test_zero_isentropic_efficiency_is_rejected() -> None:
    with pytest.raises(
        InvalidTemperatureInputError,
        match="Isentropic efficiency must be greater than zero and not exceed one",
    ):
        calculate_discharge_temperature(
            inlet_temperature_k=Decimal("308.15"),
            stage_compression_ratio=Decimal("1.5"),
            isentropic_exponent=Decimal("1.27"),
            isentropic_efficiency=Decimal("0"),
        )


def test_isentropic_efficiency_above_one_is_rejected() -> None:
    with pytest.raises(
        InvalidTemperatureInputError,
        match="Isentropic efficiency must be greater than zero and not exceed one",
    ):
        calculate_discharge_temperature(
            inlet_temperature_k=Decimal("308.15"),
            stage_compression_ratio=Decimal("1.5"),
            isentropic_exponent=Decimal("1.27"),
            isentropic_efficiency=Decimal("1.01"),
        )
