from decimal import Decimal

import pytest

from app.domain.compression.cooling import (
    InvalidCoolingInputError,
    calculate_cooling_duty,
)


def test_calculate_cooling_duty() -> None:
    result = calculate_cooling_duty(
        gas_mass_flow_kg_per_s=Decimal("93.376"),
        gas_specific_heat_kj_per_kg_k=Decimal("2.35"),
        gas_inlet_temperature_k=Decimal("333.10"),
        gas_outlet_temperature_k=Decimal("313.15"),
        cooling_water_inlet_temperature_k=Decimal("303.15"),
        cooling_water_outlet_temperature_k=Decimal("313.15"),
    )

    assert result.cooling_duty_kw > Decimal("4300")
    assert result.cooling_duty_kw < Decimal("4400")

    assert result.cooling_water_mass_flow_kg_per_s > Decimal("100")
    assert result.cooling_water_flow_m3_per_hr > Decimal("350")
    assert result.cooling_water_flow_m3_per_hr < Decimal("400")


def test_gas_mass_flow_must_be_positive() -> None:
    with pytest.raises(
        InvalidCoolingInputError,
        match="Gas mass flow must be greater than zero",
    ):
        calculate_cooling_duty(
            gas_mass_flow_kg_per_s=Decimal("0"),
            gas_specific_heat_kj_per_kg_k=Decimal("2.35"),
            gas_inlet_temperature_k=Decimal("333.10"),
            gas_outlet_temperature_k=Decimal("313.15"),
            cooling_water_inlet_temperature_k=Decimal("303.15"),
            cooling_water_outlet_temperature_k=Decimal("313.15"),
        )


def test_specific_heat_must_be_positive() -> None:
    with pytest.raises(
        InvalidCoolingInputError,
        match="Gas specific heat capacity must be greater than zero",
    ):
        calculate_cooling_duty(
            gas_mass_flow_kg_per_s=Decimal("93.376"),
            gas_specific_heat_kj_per_kg_k=Decimal("0"),
            gas_inlet_temperature_k=Decimal("333.10"),
            gas_outlet_temperature_k=Decimal("313.15"),
            cooling_water_inlet_temperature_k=Decimal("303.15"),
            cooling_water_outlet_temperature_k=Decimal("313.15"),
        )


def test_gas_inlet_temperature_must_exceed_outlet_temperature() -> None:
    with pytest.raises(
        InvalidCoolingInputError,
        match="Gas inlet temperature must be greater than gas outlet temperature",
    ):
        calculate_cooling_duty(
            gas_mass_flow_kg_per_s=Decimal("93.376"),
            gas_specific_heat_kj_per_kg_k=Decimal("2.35"),
            gas_inlet_temperature_k=Decimal("313.15"),
            gas_outlet_temperature_k=Decimal("313.15"),
            cooling_water_inlet_temperature_k=Decimal("303.15"),
            cooling_water_outlet_temperature_k=Decimal("313.15"),
        )


def test_cooling_water_inlet_temperature_must_be_positive() -> None:
    with pytest.raises(
        InvalidCoolingInputError,
        match="Cooling-water inlet temperature must be greater than zero",
    ):
        calculate_cooling_duty(
            gas_mass_flow_kg_per_s=Decimal("93.376"),
            gas_specific_heat_kj_per_kg_k=Decimal("2.35"),
            gas_inlet_temperature_k=Decimal("333.10"),
            gas_outlet_temperature_k=Decimal("313.15"),
            cooling_water_inlet_temperature_k=Decimal("0"),
            cooling_water_outlet_temperature_k=Decimal("313.15"),
        )


def test_cooling_water_outlet_temperature_must_exceed_inlet() -> None:
    with pytest.raises(
        InvalidCoolingInputError,
        match="Cooling-water outlet temperature must exceed inlet temperature",
    ):
        calculate_cooling_duty(
            gas_mass_flow_kg_per_s=Decimal("93.376"),
            gas_specific_heat_kj_per_kg_k=Decimal("2.35"),
            gas_inlet_temperature_k=Decimal("333.10"),
            gas_outlet_temperature_k=Decimal("313.15"),
            cooling_water_inlet_temperature_k=Decimal("303.15"),
            cooling_water_outlet_temperature_k=Decimal("303.15"),
        )
