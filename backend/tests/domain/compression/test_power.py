from decimal import Decimal

import pytest

from app.domain.compression.power import (
    InvalidPowerInputError,
    calculate_compression_power,
)


def test_calculate_compression_power() -> None:
    result = calculate_compression_power(
        mass_flow_kg_per_s=Decimal("93.376"),
        inlet_temperature_k=Decimal("308.15"),
        stage_compression_ratio=Decimal("1.442"),
        isentropic_exponent=Decimal("1.27"),
        specific_heat_cp_kj_per_kg_k=Decimal("2.35"),
        number_of_stages=3,
        isentropic_efficiency=Decimal("0.78"),
        mechanical_efficiency=Decimal("0.95"),
        driver_margin_fraction=Decimal("0.10"),
    )

    assert result.specific_isentropic_work_kj_per_kg > Decimal("170")
    assert result.specific_isentropic_work_kj_per_kg < Decimal("180")

    assert result.isentropic_power_kw > Decimal("16000")
    assert result.isentropic_power_kw < Decimal("17000")

    assert result.shaft_power_kw > result.isentropic_power_kw
    assert result.required_driver_power_kw > result.shaft_power_kw


def test_driver_margin_increases_required_power() -> None:
    without_margin = calculate_compression_power(
        mass_flow_kg_per_s=Decimal("10"),
        inlet_temperature_k=Decimal("300"),
        stage_compression_ratio=Decimal("2"),
        isentropic_exponent=Decimal("1.30"),
        specific_heat_cp_kj_per_kg_k=Decimal("2.20"),
        number_of_stages=2,
        isentropic_efficiency=Decimal("0.80"),
        mechanical_efficiency=Decimal("0.95"),
        driver_margin_fraction=Decimal("0"),
    )

    with_margin = calculate_compression_power(
        mass_flow_kg_per_s=Decimal("10"),
        inlet_temperature_k=Decimal("300"),
        stage_compression_ratio=Decimal("2"),
        isentropic_exponent=Decimal("1.30"),
        specific_heat_cp_kj_per_kg_k=Decimal("2.20"),
        number_of_stages=2,
        isentropic_efficiency=Decimal("0.80"),
        mechanical_efficiency=Decimal("0.95"),
        driver_margin_fraction=Decimal("0.10"),
    )

    assert with_margin.required_driver_power_kw > without_margin.required_driver_power_kw


def test_zero_mass_flow_is_rejected() -> None:
    with pytest.raises(
        InvalidPowerInputError,
        match="Mass flow must be greater than zero",
    ):
        calculate_compression_power(
            mass_flow_kg_per_s=Decimal("0"),
            inlet_temperature_k=Decimal("300"),
            stage_compression_ratio=Decimal("2"),
            isentropic_exponent=Decimal("1.30"),
            specific_heat_cp_kj_per_kg_k=Decimal("2.20"),
            number_of_stages=2,
            isentropic_efficiency=Decimal("0.80"),
            mechanical_efficiency=Decimal("0.95"),
        )


def test_invalid_inlet_temperature_is_rejected() -> None:
    with pytest.raises(
        InvalidPowerInputError,
        match="Inlet absolute temperature must be greater than zero",
    ):
        calculate_compression_power(
            mass_flow_kg_per_s=Decimal("10"),
            inlet_temperature_k=Decimal("0"),
            stage_compression_ratio=Decimal("2"),
            isentropic_exponent=Decimal("1.30"),
            specific_heat_cp_kj_per_kg_k=Decimal("2.20"),
            number_of_stages=2,
            isentropic_efficiency=Decimal("0.80"),
            mechanical_efficiency=Decimal("0.95"),
        )


def test_invalid_stage_ratio_is_rejected() -> None:
    with pytest.raises(
        InvalidPowerInputError,
        match="Stage compression ratio must be greater than one",
    ):
        calculate_compression_power(
            mass_flow_kg_per_s=Decimal("10"),
            inlet_temperature_k=Decimal("300"),
            stage_compression_ratio=Decimal("1"),
            isentropic_exponent=Decimal("1.30"),
            specific_heat_cp_kj_per_kg_k=Decimal("2.20"),
            number_of_stages=2,
            isentropic_efficiency=Decimal("0.80"),
            mechanical_efficiency=Decimal("0.95"),
        )


def test_invalid_isentropic_exponent_is_rejected() -> None:
    with pytest.raises(
        InvalidPowerInputError,
        match="Isentropic exponent must be greater than one",
    ):
        calculate_compression_power(
            mass_flow_kg_per_s=Decimal("10"),
            inlet_temperature_k=Decimal("300"),
            stage_compression_ratio=Decimal("2"),
            isentropic_exponent=Decimal("1"),
            specific_heat_cp_kj_per_kg_k=Decimal("2.20"),
            number_of_stages=2,
            isentropic_efficiency=Decimal("0.80"),
            mechanical_efficiency=Decimal("0.95"),
        )


def test_invalid_specific_heat_is_rejected() -> None:
    with pytest.raises(
        InvalidPowerInputError,
        match="Specific heat capacity must be greater than zero",
    ):
        calculate_compression_power(
            mass_flow_kg_per_s=Decimal("10"),
            inlet_temperature_k=Decimal("300"),
            stage_compression_ratio=Decimal("2"),
            isentropic_exponent=Decimal("1.30"),
            specific_heat_cp_kj_per_kg_k=Decimal("0"),
            number_of_stages=2,
            isentropic_efficiency=Decimal("0.80"),
            mechanical_efficiency=Decimal("0.95"),
        )


def test_invalid_number_of_stages_is_rejected() -> None:
    with pytest.raises(
        InvalidPowerInputError,
        match="Number of compression stages must be at least one",
    ):
        calculate_compression_power(
            mass_flow_kg_per_s=Decimal("10"),
            inlet_temperature_k=Decimal("300"),
            stage_compression_ratio=Decimal("2"),
            isentropic_exponent=Decimal("1.30"),
            specific_heat_cp_kj_per_kg_k=Decimal("2.20"),
            number_of_stages=0,
            isentropic_efficiency=Decimal("0.80"),
            mechanical_efficiency=Decimal("0.95"),
        )


def test_invalid_isentropic_efficiency_is_rejected() -> None:
    with pytest.raises(
        InvalidPowerInputError,
        match="Isentropic efficiency must be greater than zero and not exceed one",
    ):
        calculate_compression_power(
            mass_flow_kg_per_s=Decimal("10"),
            inlet_temperature_k=Decimal("300"),
            stage_compression_ratio=Decimal("2"),
            isentropic_exponent=Decimal("1.30"),
            specific_heat_cp_kj_per_kg_k=Decimal("2.20"),
            number_of_stages=2,
            isentropic_efficiency=Decimal("0"),
            mechanical_efficiency=Decimal("0.95"),
        )


def test_invalid_mechanical_efficiency_is_rejected() -> None:
    with pytest.raises(
        InvalidPowerInputError,
        match="Mechanical efficiency must be greater than zero and not exceed one",
    ):
        calculate_compression_power(
            mass_flow_kg_per_s=Decimal("10"),
            inlet_temperature_k=Decimal("300"),
            stage_compression_ratio=Decimal("2"),
            isentropic_exponent=Decimal("1.30"),
            specific_heat_cp_kj_per_kg_k=Decimal("2.20"),
            number_of_stages=2,
            isentropic_efficiency=Decimal("0.80"),
            mechanical_efficiency=Decimal("0"),
        )


def test_negative_driver_margin_is_rejected() -> None:
    with pytest.raises(
        InvalidPowerInputError,
        match="Driver margin fraction cannot be negative",
    ):
        calculate_compression_power(
            mass_flow_kg_per_s=Decimal("10"),
            inlet_temperature_k=Decimal("300"),
            stage_compression_ratio=Decimal("2"),
            isentropic_exponent=Decimal("1.30"),
            specific_heat_cp_kj_per_kg_k=Decimal("2.20"),
            number_of_stages=2,
            isentropic_efficiency=Decimal("0.80"),
            mechanical_efficiency=Decimal("0.95"),
            driver_margin_fraction=Decimal("-0.01"),
        )
