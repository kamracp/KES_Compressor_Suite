from decimal import Decimal

import pytest

from app.domain.gas.gas_catalog import GAS_COMPONENTS, get_gas_component


def test_catalog_contains_expected_components() -> None:
    expected_keys = {
        "methane",
        "ethane",
        "propane",
        "isobutane",
        "n_butane",
        "isopentane",
        "n_pentane",
        "hexane",
        "nitrogen",
        "carbon_dioxide",
        "hydrogen_sulfide",
        "hydrogen",
        "oxygen",
        "water",
    }

    assert set(GAS_COMPONENTS) == expected_keys


def test_get_methane_component() -> None:
    component = get_gas_component("methane")

    assert component.name == "Methane"
    assert component.formula == "CH4"
    assert component.molecular_weight == Decimal("16.043")


def test_lookup_is_case_insensitive() -> None:
    component = get_gas_component("CARBON_DIOXIDE")

    assert component.name == "Carbon Dioxide"
    assert component.formula == "CO2"
    assert component.molecular_weight == Decimal("44.010")


def test_lookup_strips_whitespace() -> None:
    component = get_gas_component("  nitrogen  ")

    assert component.name == "Nitrogen"
    assert component.molecular_weight == Decimal("28.014")


def test_unsupported_component_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="Unsupported gas component: unsupported_gas",
    ):
        get_gas_component("unsupported_gas")
