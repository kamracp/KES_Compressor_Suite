from decimal import Decimal

from app.domain.gas.gas_models import GasComponent, GasMixture


def test_gas_component_stores_properties() -> None:
    component = GasComponent(
        name="Methane",
        formula="CH4",
        molecular_weight=Decimal("16.04"),
        mole_fraction=Decimal("0.85"),
    )

    assert component.name == "Methane"
    assert component.formula == "CH4"
    assert component.molecular_weight == Decimal("16.04")
    assert component.mole_fraction == Decimal("0.85")


def test_gas_mixture_total_mole_fraction() -> None:
    mixture = GasMixture(
        components=(
            GasComponent(
                name="Methane",
                formula="CH4",
                molecular_weight=Decimal("16.04"),
                mole_fraction=Decimal("0.85"),
            ),
            GasComponent(
                name="Ethane",
                formula="C2H6",
                molecular_weight=Decimal("30.07"),
                mole_fraction=Decimal("0.08"),
            ),
            GasComponent(
                name="Propane",
                formula="C3H8",
                molecular_weight=Decimal("44.10"),
                mole_fraction=Decimal("0.07"),
            ),
        )
    )

    assert mixture.total_mole_fraction == Decimal("1.00")


def test_gas_mixture_molecular_weight() -> None:
    mixture = GasMixture(
        components=(
            GasComponent(
                name="Methane",
                formula="CH4",
                molecular_weight=Decimal("16.04"),
                mole_fraction=Decimal("0.85"),
            ),
            GasComponent(
                name="Ethane",
                formula="C2H6",
                molecular_weight=Decimal("30.07"),
                mole_fraction=Decimal("0.08"),
            ),
            GasComponent(
                name="Propane",
                formula="C3H8",
                molecular_weight=Decimal("44.10"),
                mole_fraction=Decimal("0.07"),
            ),
        )
    )

    assert mixture.molecular_weight == Decimal("19.1266")


def test_empty_gas_mixture_returns_zero_totals() -> None:
    mixture = GasMixture(components=())

    assert mixture.total_mole_fraction == Decimal("0")
    assert mixture.molecular_weight == Decimal("0")
