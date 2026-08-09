from decimal import Decimal

import pytest

from app.domain.gas.gas_models import GasComponent, GasMixture
from app.domain.gas.pseudocritical import (
    MissingCriticalPropertyError,
    calculate_pseudocritical_properties,
)


def build_reference_mixture() -> GasMixture:
    return GasMixture(
        components=(
            GasComponent(
                name="methane",
                formula="CH4",
                molecular_weight=Decimal("16.043"),
                mole_fraction=Decimal("0.85"),
            ),
            GasComponent(
                name="ethane",
                formula="C2H6",
                molecular_weight=Decimal("30.070"),
                mole_fraction=Decimal("0.08"),
            ),
            GasComponent(
                name="propane",
                formula="C3H8",
                molecular_weight=Decimal("44.097"),
                mole_fraction=Decimal("0.03"),
            ),
            GasComponent(
                name="isobutane",
                formula="i-C4H10",
                molecular_weight=Decimal("58.124"),
                mole_fraction=Decimal("0.01"),
            ),
            GasComponent(
                name="n_butane",
                formula="n-C4H10",
                molecular_weight=Decimal("58.124"),
                mole_fraction=Decimal("0.005"),
            ),
            GasComponent(
                name="nitrogen",
                formula="N2",
                molecular_weight=Decimal("28.014"),
                mole_fraction=Decimal("0.015"),
            ),
            GasComponent(
                name="carbon_dioxide",
                formula="CO2",
                molecular_weight=Decimal("44.010"),
                mole_fraction=Decimal("0.008"),
            ),
            GasComponent(
                name="hydrogen_sulfide",
                formula="H2S",
                molecular_weight=Decimal("34.081"),
                mole_fraction=Decimal("0.002"),
            ),
        )
    )


def test_calculate_pseudocritical_properties() -> None:
    mixture = build_reference_mixture()

    result = calculate_pseudocritical_properties(mixture)

    assert result.temperature_k == Decimal("208.8075")
    assert result.pressure_bar == Decimal("46.1882")


def test_single_component_returns_component_critical_properties() -> None:
    mixture = GasMixture(
        components=(
            GasComponent(
                name="methane",
                formula="CH4",
                molecular_weight=Decimal("16.043"),
                mole_fraction=Decimal("1"),
            ),
        )
    )

    result = calculate_pseudocritical_properties(mixture)

    assert result.temperature_k == Decimal("190.6")
    assert result.pressure_bar == Decimal("46.1")


def test_missing_critical_temperature_is_rejected() -> None:
    mixture = GasMixture(
        components=(
            GasComponent(
                name="hydrogen",
                formula="H2",
                molecular_weight=Decimal("2.016"),
                mole_fraction=Decimal("1"),
            ),
        )
    )

    with pytest.raises(
        MissingCriticalPropertyError,
        match="Critical temperature is unavailable",
    ):
        calculate_pseudocritical_properties(mixture)


def test_invalid_mole_fraction_total_is_rejected() -> None:
    mixture = GasMixture(
        components=(
            GasComponent(
                name="methane",
                formula="CH4",
                molecular_weight=Decimal("16.043"),
                mole_fraction=Decimal("0.80"),
            ),
        )
    )

    with pytest.raises(
        ValueError,
        match="Gas mixture mole fractions must sum to 1.0",
    ):
        calculate_pseudocritical_properties(mixture)
