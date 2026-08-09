from decimal import Decimal

import pytest

from app.domain.gas.density import (
    InvalidDensityInputError,
    calculate_real_gas_density,
)


def test_calculate_real_gas_density() -> None:
    result = calculate_real_gas_density(
        pressure_bar=Decimal("30"),
        temperature_k=Decimal("308.15"),
        molecular_weight_kg_per_kmol=Decimal("19.075"),
        z_factor=Decimal("0.9398"),
    )

    assert result.density_kg_per_m3 > Decimal("23")
    assert result.density_kg_per_m3 < Decimal("25")


def test_zero_pressure_is_rejected() -> None:
    with pytest.raises(
        InvalidDensityInputError,
        match="Absolute pressure must be greater than zero",
    ):
        calculate_real_gas_density(
            pressure_bar=Decimal("0"),
            temperature_k=Decimal("308.15"),
            molecular_weight_kg_per_kmol=Decimal("19.075"),
            z_factor=Decimal("0.9398"),
        )


def test_zero_temperature_is_rejected() -> None:
    with pytest.raises(
        InvalidDensityInputError,
        match="Absolute temperature must be greater than zero",
    ):
        calculate_real_gas_density(
            pressure_bar=Decimal("30"),
            temperature_k=Decimal("0"),
            molecular_weight_kg_per_kmol=Decimal("19.075"),
            z_factor=Decimal("0.9398"),
        )


def test_zero_molecular_weight_is_rejected() -> None:
    with pytest.raises(
        InvalidDensityInputError,
        match="Molecular weight must be greater than zero",
    ):
        calculate_real_gas_density(
            pressure_bar=Decimal("30"),
            temperature_k=Decimal("308.15"),
            molecular_weight_kg_per_kmol=Decimal("0"),
            z_factor=Decimal("0.9398"),
        )


def test_zero_z_factor_is_rejected() -> None:
    with pytest.raises(
        InvalidDensityInputError,
        match="Z-factor must be greater than zero",
    ):
        calculate_real_gas_density(
            pressure_bar=Decimal("30"),
            temperature_k=Decimal("308.15"),
            molecular_weight_kg_per_kmol=Decimal("19.075"),
            z_factor=Decimal("0"),
        )
