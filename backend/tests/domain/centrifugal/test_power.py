from decimal import Decimal

import pytest

from app.domain.centrifugal.centrifugal_models import CentrifugalDriverType
from app.domain.centrifugal.power import (
    InvalidCentrifugalPowerInputError,
    calculate_centrifugal_power,
)


def test_calculate_centrifugal_power() -> None:
    result = calculate_centrifugal_power(
        mass_flow_kg_per_s=Decimal("93.376"),
        polytropic_head_kj_per_kg=Decimal("155.667"),
        polytropic_efficiency=Decimal("0.78"),
        mechanical_loss_fraction=Decimal("0.025"),
        driver_margin_fraction=Decimal("0.10"),
        selected_driver_power_kw=Decimal("22000"),
        driver_type=CentrifugalDriverType.ELECTRIC_MOTOR,
        motor_efficiency=Decimal("0.96"),
    )

    assert result.gas_power_kw > Decimal("18000")
    assert result.gas_power_kw < Decimal("19000")

    assert result.shaft_power_kw > result.gas_power_kw
    assert result.required_driver_power_kw > result.shaft_power_kw

    assert result.driver_is_adequate is True
    assert result.driver_margin_kw > Decimal("0")

    assert result.electrical_input_power_kw is not None
    assert result.electrical_input_power_kw > Decimal("21000")
    assert result.electrical_input_power_kw < Decimal("23000")


def test_undersized_driver_is_detected() -> None:
    result = calculate_centrifugal_power(
        mass_flow_kg_per_s=Decimal("93.376"),
        polytropic_head_kj_per_kg=Decimal("155.667"),
        polytropic_efficiency=Decimal("0.78"),
        mechanical_loss_fraction=Decimal("0.025"),
        driver_margin_fraction=Decimal("0.10"),
        selected_driver_power_kw=Decimal("20000"),
        driver_type=CentrifugalDriverType.ELECTRIC_MOTOR,
        motor_efficiency=Decimal("0.96"),
    )

    assert result.driver_is_adequate is False
    assert result.driver_margin_kw < Decimal("0")


def test_non_electric_driver_returns_no_electrical_input() -> None:
    result = calculate_centrifugal_power(
        mass_flow_kg_per_s=Decimal("10"),
        polytropic_head_kj_per_kg=Decimal("100"),
        polytropic_efficiency=Decimal("0.80"),
        mechanical_loss_fraction=Decimal("0.02"),
        driver_margin_fraction=Decimal("0.10"),
        selected_driver_power_kw=Decimal("1500"),
        driver_type=CentrifugalDriverType.GAS_TURBINE,
    )

    assert result.electrical_input_power_kw is None


def test_zero_mass_flow_is_rejected() -> None:
    with pytest.raises(
        InvalidCentrifugalPowerInputError,
        match="Mass flow must be greater than zero",
    ):
        calculate_centrifugal_power(
            mass_flow_kg_per_s=Decimal("0"),
            polytropic_head_kj_per_kg=Decimal("100"),
            polytropic_efficiency=Decimal("0.80"),
            mechanical_loss_fraction=Decimal("0.02"),
            driver_margin_fraction=Decimal("0.10"),
            selected_driver_power_kw=Decimal("1500"),
            driver_type=CentrifugalDriverType.ELECTRIC_MOTOR,
            motor_efficiency=Decimal("0.96"),
        )


def test_zero_polytropic_head_is_rejected() -> None:
    with pytest.raises(
        InvalidCentrifugalPowerInputError,
        match="Polytropic head must be greater than zero",
    ):
        calculate_centrifugal_power(
            mass_flow_kg_per_s=Decimal("10"),
            polytropic_head_kj_per_kg=Decimal("0"),
            polytropic_efficiency=Decimal("0.80"),
            mechanical_loss_fraction=Decimal("0.02"),
            driver_margin_fraction=Decimal("0.10"),
            selected_driver_power_kw=Decimal("1500"),
            driver_type=CentrifugalDriverType.ELECTRIC_MOTOR,
            motor_efficiency=Decimal("0.96"),
        )


def test_invalid_polytropic_efficiency_is_rejected() -> None:
    with pytest.raises(
        InvalidCentrifugalPowerInputError,
        match="Polytropic efficiency must be greater than zero and not exceed one",
    ):
        calculate_centrifugal_power(
            mass_flow_kg_per_s=Decimal("10"),
            polytropic_head_kj_per_kg=Decimal("100"),
            polytropic_efficiency=Decimal("0"),
            mechanical_loss_fraction=Decimal("0.02"),
            driver_margin_fraction=Decimal("0.10"),
            selected_driver_power_kw=Decimal("1500"),
            driver_type=CentrifugalDriverType.ELECTRIC_MOTOR,
            motor_efficiency=Decimal("0.96"),
        )


def test_negative_mechanical_loss_fraction_is_rejected() -> None:
    with pytest.raises(
        InvalidCentrifugalPowerInputError,
        match="Mechanical loss fraction cannot be negative",
    ):
        calculate_centrifugal_power(
            mass_flow_kg_per_s=Decimal("10"),
            polytropic_head_kj_per_kg=Decimal("100"),
            polytropic_efficiency=Decimal("0.80"),
            mechanical_loss_fraction=Decimal("-0.01"),
            driver_margin_fraction=Decimal("0.10"),
            selected_driver_power_kw=Decimal("1500"),
            driver_type=CentrifugalDriverType.ELECTRIC_MOTOR,
            motor_efficiency=Decimal("0.96"),
        )


def test_negative_driver_margin_fraction_is_rejected() -> None:
    with pytest.raises(
        InvalidCentrifugalPowerInputError,
        match="Driver margin fraction cannot be negative",
    ):
        calculate_centrifugal_power(
            mass_flow_kg_per_s=Decimal("10"),
            polytropic_head_kj_per_kg=Decimal("100"),
            polytropic_efficiency=Decimal("0.80"),
            mechanical_loss_fraction=Decimal("0.02"),
            driver_margin_fraction=Decimal("-0.01"),
            selected_driver_power_kw=Decimal("1500"),
            driver_type=CentrifugalDriverType.ELECTRIC_MOTOR,
            motor_efficiency=Decimal("0.96"),
        )


def test_zero_selected_driver_power_is_rejected() -> None:
    with pytest.raises(
        InvalidCentrifugalPowerInputError,
        match="Selected driver power must be greater than zero",
    ):
        calculate_centrifugal_power(
            mass_flow_kg_per_s=Decimal("10"),
            polytropic_head_kj_per_kg=Decimal("100"),
            polytropic_efficiency=Decimal("0.80"),
            mechanical_loss_fraction=Decimal("0.02"),
            driver_margin_fraction=Decimal("0.10"),
            selected_driver_power_kw=Decimal("0"),
            driver_type=CentrifugalDriverType.ELECTRIC_MOTOR,
            motor_efficiency=Decimal("0.96"),
        )


def test_invalid_motor_efficiency_is_rejected() -> None:
    with pytest.raises(
        InvalidCentrifugalPowerInputError,
        match="Motor efficiency must be greater than zero and not exceed one",
    ):
        calculate_centrifugal_power(
            mass_flow_kg_per_s=Decimal("10"),
            polytropic_head_kj_per_kg=Decimal("100"),
            polytropic_efficiency=Decimal("0.80"),
            mechanical_loss_fraction=Decimal("0.02"),
            driver_margin_fraction=Decimal("0.10"),
            selected_driver_power_kw=Decimal("1500"),
            driver_type=CentrifugalDriverType.ELECTRIC_MOTOR,
            motor_efficiency=Decimal("0"),
        )
