from decimal import Decimal

import pytest

from app.domain.gas.flow import (
    InvalidFlowInputError,
    calculate_actual_flow,
    calculate_flow_result,
)


def test_calculate_actual_flow() -> None:
    result = calculate_actual_flow(
        standard_flow_m3_per_hr=Decimal("416666.6667"),
        standard_pressure_bar=Decimal("1.01325"),
        standard_temperature_k=Decimal("288.15"),
        actual_pressure_bar=Decimal("30"),
        actual_temperature_k=Decimal("308.15"),
        actual_z_factor=Decimal("0.9398"),
    )

    assert result > Decimal("14000")
    assert result < Decimal("14300")


def test_calculate_flow_result() -> None:
    result = calculate_flow_result(
        standard_flow_m3_per_hr=Decimal("416666.6667"),
        standard_pressure_bar=Decimal("1.01325"),
        standard_temperature_k=Decimal("288.15"),
        actual_pressure_bar=Decimal("30"),
        actual_temperature_k=Decimal("308.15"),
        actual_z_factor=Decimal("0.9398"),
        density_kg_per_m3=Decimal("23.767"),
    )

    assert result.actual_flow_m3_per_hr > Decimal("14000")
    assert result.mass_flow_kg_per_hr > Decimal("330000")
    assert result.mass_flow_kg_per_s > Decimal("90")


def test_zero_standard_flow_is_rejected() -> None:
    with pytest.raises(
        InvalidFlowInputError,
        match="Standard flow must be greater than zero",
    ):
        calculate_actual_flow(
            standard_flow_m3_per_hr=Decimal("0"),
            standard_pressure_bar=Decimal("1.01325"),
            standard_temperature_k=Decimal("288.15"),
            actual_pressure_bar=Decimal("30"),
            actual_temperature_k=Decimal("308.15"),
            actual_z_factor=Decimal("0.9398"),
        )


def test_zero_actual_pressure_is_rejected() -> None:
    with pytest.raises(
        InvalidFlowInputError,
        match="Actual pressure must be greater than zero",
    ):
        calculate_actual_flow(
            standard_flow_m3_per_hr=Decimal("1000"),
            standard_pressure_bar=Decimal("1.01325"),
            standard_temperature_k=Decimal("288.15"),
            actual_pressure_bar=Decimal("0"),
            actual_temperature_k=Decimal("308.15"),
            actual_z_factor=Decimal("0.9398"),
        )


def test_zero_actual_temperature_is_rejected() -> None:
    with pytest.raises(
        InvalidFlowInputError,
        match="Actual temperature must be greater than zero",
    ):
        calculate_actual_flow(
            standard_flow_m3_per_hr=Decimal("1000"),
            standard_pressure_bar=Decimal("1.01325"),
            standard_temperature_k=Decimal("288.15"),
            actual_pressure_bar=Decimal("30"),
            actual_temperature_k=Decimal("0"),
            actual_z_factor=Decimal("0.9398"),
        )


def test_zero_actual_z_factor_is_rejected() -> None:
    with pytest.raises(
        InvalidFlowInputError,
        match="Actual Z-factor must be greater than zero",
    ):
        calculate_actual_flow(
            standard_flow_m3_per_hr=Decimal("1000"),
            standard_pressure_bar=Decimal("1.01325"),
            standard_temperature_k=Decimal("288.15"),
            actual_pressure_bar=Decimal("30"),
            actual_temperature_k=Decimal("308.15"),
            actual_z_factor=Decimal("0"),
        )


def test_zero_density_is_rejected() -> None:
    with pytest.raises(
        InvalidFlowInputError,
        match="Gas density must be greater than zero",
    ):
        calculate_flow_result(
            standard_flow_m3_per_hr=Decimal("1000"),
            standard_pressure_bar=Decimal("1.01325"),
            standard_temperature_k=Decimal("288.15"),
            actual_pressure_bar=Decimal("30"),
            actual_temperature_k=Decimal("308.15"),
            actual_z_factor=Decimal("0.9398"),
            density_kg_per_m3=Decimal("0"),
        )
