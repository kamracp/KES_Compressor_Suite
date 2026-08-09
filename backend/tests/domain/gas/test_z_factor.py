from decimal import Decimal

import pytest

from app.domain.gas.reduced_properties import ReducedProperties
from app.domain.gas.z_factor import (
    InvalidReducedPropertyError,
    calculate_papay_z_factor,
)


def test_calculate_papay_z_factor() -> None:
    reduced = ReducedProperties(
        reduced_pressure=Decimal("0.6495"),
        reduced_temperature=Decimal("1.4757"),
    )

    result = calculate_papay_z_factor(reduced)

    assert result.correlation == "Papay"
    assert result.z_factor > Decimal("0")
    assert Decimal("0.90") < result.z_factor < Decimal("1.00")


def test_zero_reduced_pressure_is_rejected() -> None:
    reduced = ReducedProperties(
        reduced_pressure=Decimal("0"),
        reduced_temperature=Decimal("1.4757"),
    )

    with pytest.raises(
        InvalidReducedPropertyError,
        match="Reduced pressure must be greater than zero",
    ):
        calculate_papay_z_factor(reduced)


def test_negative_reduced_pressure_is_rejected() -> None:
    reduced = ReducedProperties(
        reduced_pressure=Decimal("-0.1"),
        reduced_temperature=Decimal("1.4757"),
    )

    with pytest.raises(
        InvalidReducedPropertyError,
        match="Reduced pressure must be greater than zero",
    ):
        calculate_papay_z_factor(reduced)


def test_zero_reduced_temperature_is_rejected() -> None:
    reduced = ReducedProperties(
        reduced_pressure=Decimal("0.6495"),
        reduced_temperature=Decimal("0"),
    )

    with pytest.raises(
        InvalidReducedPropertyError,
        match="Reduced temperature must be greater than zero",
    ):
        calculate_papay_z_factor(reduced)


def test_negative_reduced_temperature_is_rejected() -> None:
    reduced = ReducedProperties(
        reduced_pressure=Decimal("0.6495"),
        reduced_temperature=Decimal("-1"),
    )

    with pytest.raises(
        InvalidReducedPropertyError,
        match="Reduced temperature must be greater than zero",
    ):
        calculate_papay_z_factor(reduced)
