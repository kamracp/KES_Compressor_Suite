from decimal import Decimal

import pytest

from app.domain.compression.driver import (
    InvalidDriverInputError,
    size_driver,
)


def test_size_driver_with_adequate_motor() -> None:
    result = size_driver(
        shaft_power_kw=Decimal("19101.2"),
        selected_driver_power_kw=Decimal("22000"),
        service_factor=Decimal("0.10"),
        motor_efficiency=Decimal("0.96"),
    )

    assert result.required_driver_power_kw == Decimal("21011.32")
    assert result.driver_is_adequate is True
    assert result.driver_margin_kw == Decimal("988.68")
    assert result.electrical_input_power_kw is not None
    assert result.electrical_input_power_kw > Decimal("21800")
    assert result.electrical_input_power_kw < Decimal("21900")


def test_undersized_driver_is_detected() -> None:
    result = size_driver(
        shaft_power_kw=Decimal("19101.2"),
        selected_driver_power_kw=Decimal("20000"),
        service_factor=Decimal("0.10"),
    )

    assert result.driver_is_adequate is False
    assert result.driver_margin_kw < Decimal("0")


def test_zero_service_factor_is_allowed() -> None:
    result = size_driver(
        shaft_power_kw=Decimal("1000"),
        selected_driver_power_kw=Decimal("1000"),
        service_factor=Decimal("0"),
    )

    assert result.required_driver_power_kw == Decimal("1000")
    assert result.driver_is_adequate is True


def test_no_motor_efficiency_returns_no_electrical_input() -> None:
    result = size_driver(
        shaft_power_kw=Decimal("1000"),
        selected_driver_power_kw=Decimal("1200"),
    )

    assert result.motor_efficiency is None
    assert result.electrical_input_power_kw is None


def test_zero_shaft_power_is_rejected() -> None:
    with pytest.raises(
        InvalidDriverInputError,
        match="Shaft power must be greater than zero",
    ):
        size_driver(
            shaft_power_kw=Decimal("0"),
            selected_driver_power_kw=Decimal("1200"),
        )


def test_zero_selected_driver_power_is_rejected() -> None:
    with pytest.raises(
        InvalidDriverInputError,
        match="Selected driver power must be greater than zero",
    ):
        size_driver(
            shaft_power_kw=Decimal("1000"),
            selected_driver_power_kw=Decimal("0"),
        )


def test_negative_service_factor_is_rejected() -> None:
    with pytest.raises(
        InvalidDriverInputError,
        match="Service factor cannot be negative",
    ):
        size_driver(
            shaft_power_kw=Decimal("1000"),
            selected_driver_power_kw=Decimal("1200"),
            service_factor=Decimal("-0.01"),
        )


def test_zero_motor_efficiency_is_rejected() -> None:
    with pytest.raises(
        InvalidDriverInputError,
        match="Motor efficiency must be greater than zero and not exceed one",
    ):
        size_driver(
            shaft_power_kw=Decimal("1000"),
            selected_driver_power_kw=Decimal("1200"),
            motor_efficiency=Decimal("0"),
        )


def test_motor_efficiency_above_one_is_rejected() -> None:
    with pytest.raises(
        InvalidDriverInputError,
        match="Motor efficiency must be greater than zero and not exceed one",
    ):
        size_driver(
            shaft_power_kw=Decimal("1000"),
            selected_driver_power_kw=Decimal("1200"),
            motor_efficiency=Decimal("1.01"),
        )
