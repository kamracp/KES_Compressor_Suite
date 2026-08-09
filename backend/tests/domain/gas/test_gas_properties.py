from decimal import Decimal

import pytest

from app.domain.gas.gas_models import GasComponent, GasMixture
from app.domain.gas.gas_properties import (
    AIR_MOLECULAR_WEIGHT,
    InvalidGasMixtureError,
    calculate_mixture_properties,
    validate_gas_mixture,
)


def build_valid_mixture() -> GasMixture:
    return GasMixture(
        components=(
            GasComponent(
                name="Methane",
                formula="CH4",
                molecular_weight=Decimal("16.043"),
                mole_fraction=Decimal("0.85"),
            ),
            GasComponent(
                name="Ethane",
                formula="C2H6",
                molecular_weight=Decimal("30.070"),
                mole_fraction=Decimal("0.08"),
            ),
            GasComponent(
                name="Propane",
                formula="C3H8",
                molecular_weight=Decimal("44.097"),
                mole_fraction=Decimal("0.07"),
            ),
        )
    )


def test_validate_gas_mixture_accepts_valid_mixture() -> None:
    mixture = build_valid_mixture()

    validate_gas_mixture(mixture)


def test_calculate_mixture_properties() -> None:
    mixture = build_valid_mixture()

    result = calculate_mixture_properties(mixture)

    expected_molecular_weight = Decimal("19.12894")
    expected_specific_gravity = expected_molecular_weight / AIR_MOLECULAR_WEIGHT

    assert result.molecular_weight == expected_molecular_weight
    assert result.specific_gravity == expected_specific_gravity


def test_empty_mixture_is_rejected() -> None:
    mixture = GasMixture(components=())

    with pytest.raises(
        InvalidGasMixtureError,
        match="Gas mixture must contain at least one component",
    ):
        validate_gas_mixture(mixture)


def test_negative_mole_fraction_is_rejected() -> None:
    mixture = GasMixture(
        components=(
            GasComponent(
                name="Methane",
                formula="CH4",
                molecular_weight=Decimal("16.043"),
                mole_fraction=Decimal("1.01"),
            ),
            GasComponent(
                name="Nitrogen",
                formula="N2",
                molecular_weight=Decimal("28.014"),
                mole_fraction=Decimal("-0.01"),
            ),
        )
    )

    with pytest.raises(
        InvalidGasMixtureError,
        match="Mole fraction cannot be negative",
    ):
        validate_gas_mixture(mixture)


def test_non_positive_molecular_weight_is_rejected() -> None:
    mixture = GasMixture(
        components=(
            GasComponent(
                name="Invalid Gas",
                formula="X",
                molecular_weight=Decimal("0"),
                mole_fraction=Decimal("1"),
            ),
        )
    )

    with pytest.raises(
        InvalidGasMixtureError,
        match="Molecular weight must be positive",
    ):
        validate_gas_mixture(mixture)


def test_mole_fraction_total_must_equal_one() -> None:
    mixture = GasMixture(
        components=(
            GasComponent(
                name="Methane",
                formula="CH4",
                molecular_weight=Decimal("16.043"),
                mole_fraction=Decimal("0.80"),
            ),
            GasComponent(
                name="Ethane",
                formula="C2H6",
                molecular_weight=Decimal("30.070"),
                mole_fraction=Decimal("0.10"),
            ),
        )
    )

    with pytest.raises(
        InvalidGasMixtureError,
        match="Gas mixture mole fractions must sum to 1.0",
    ):
        validate_gas_mixture(mixture)


def test_small_mole_fraction_rounding_error_is_accepted() -> None:
    mixture = GasMixture(
        components=(
            GasComponent(
                name="Methane",
                formula="CH4",
                molecular_weight=Decimal("16.043"),
                mole_fraction=Decimal("0.9000004"),
            ),
            GasComponent(
                name="Nitrogen",
                formula="N2",
                molecular_weight=Decimal("28.014"),
                mole_fraction=Decimal("0.0999995"),
            ),
        )
    )

    validate_gas_mixture(mixture)
