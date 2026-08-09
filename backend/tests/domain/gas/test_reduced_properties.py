from decimal import Decimal

import pytest

from app.domain.gas.pseudocritical import PseudoCriticalProperties
from app.domain.gas.reduced_properties import (
    InvalidOperatingConditionError,
    calculate_reduced_properties,
)


def build_pseudocritical() -> PseudoCriticalProperties:
    return PseudoCriticalProperties(
        temperature_k=Decimal("208.8075"),
        pressure_bar=Decimal("46.1882"),
    )


def test_calculate_reduced_properties() -> None:
    pseudocritical = build_pseudocritical()

    result = calculate_reduced_properties(
        pressure_bar=Decimal("30"),
        temperature_k=Decimal("308.15"),
        pseudocritical=pseudocritical,
    )

    expected_pressure = Decimal("30") / Decimal("46.1882")
    expected_temperature = Decimal("308.15") / Decimal("208.8075")

    assert result.reduced_pressure == expected_pressure
    assert result.reduced_temperature == expected_temperature


def test_zero_pressure_is_rejected() -> None:
    pseudocritical = build_pseudocritical()

    with pytest.raises(
        InvalidOperatingConditionError,
        match="Absolute pressure must be greater than zero",
    ):
        calculate_reduced_properties(
            pressure_bar=Decimal("0"),
            temperature_k=Decimal("308.15"),
            pseudocritical=pseudocritical,
        )


def test_negative_pressure_is_rejected() -> None:
    pseudocritical = build_pseudocritical()

    with pytest.raises(
        InvalidOperatingConditionError,
        match="Absolute pressure must be greater than zero",
    ):
        calculate_reduced_properties(
            pressure_bar=Decimal("-1"),
            temperature_k=Decimal("308.15"),
            pseudocritical=pseudocritical,
        )


def test_zero_temperature_is_rejected() -> None:
    pseudocritical = build_pseudocritical()

    with pytest.raises(
        InvalidOperatingConditionError,
        match="Absolute temperature must be greater than zero",
    ):
        calculate_reduced_properties(
            pressure_bar=Decimal("30"),
            temperature_k=Decimal("0"),
            pseudocritical=pseudocritical,
        )


def test_invalid_pseudocritical_pressure_is_rejected() -> None:
    pseudocritical = PseudoCriticalProperties(
        temperature_k=Decimal("208.8075"),
        pressure_bar=Decimal("0"),
    )

    with pytest.raises(
        InvalidOperatingConditionError,
        match="Pseudo-critical pressure must be greater than zero",
    ):
        calculate_reduced_properties(
            pressure_bar=Decimal("30"),
            temperature_k=Decimal("308.15"),
            pseudocritical=pseudocritical,
        )


def test_invalid_pseudocritical_temperature_is_rejected() -> None:
    pseudocritical = PseudoCriticalProperties(
        temperature_k=Decimal("0"),
        pressure_bar=Decimal("46.1882"),
    )

    with pytest.raises(
        InvalidOperatingConditionError,
        match="Pseudo-critical temperature must be greater than zero",
    ):
        calculate_reduced_properties(
            pressure_bar=Decimal("30"),
            temperature_k=Decimal("308.15"),
            pseudocritical=pseudocritical,
        )
