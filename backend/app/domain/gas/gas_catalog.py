from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class GasComponentData:
    """Reference data for a pure gas component."""

    name: str
    formula: str
    molecular_weight: Decimal
    critical_temperature_k: Decimal | None = None
    critical_pressure_bar: Decimal | None = None


GAS_COMPONENTS: dict[str, GasComponentData] = {
    "methane": GasComponentData(
        name="Methane",
        formula="CH4",
        molecular_weight=Decimal("16.043"),
        critical_temperature_k=Decimal("190.6"),
        critical_pressure_bar=Decimal("46.1"),
    ),
    "ethane": GasComponentData(
        name="Ethane",
        formula="C2H6",
        molecular_weight=Decimal("30.070"),
        critical_temperature_k=Decimal("305.3"),
        critical_pressure_bar=Decimal("48.7"),
    ),
    "propane": GasComponentData(
        name="Propane",
        formula="C3H8",
        molecular_weight=Decimal("44.097"),
        critical_temperature_k=Decimal("369.8"),
        critical_pressure_bar=Decimal("42.5"),
    ),
    "isobutane": GasComponentData(
        name="Isobutane",
        formula="i-C4H10",
        molecular_weight=Decimal("58.124"),
        critical_temperature_k=Decimal("408.1"),
        critical_pressure_bar=Decimal("36.5"),
    ),
    "n_butane": GasComponentData(
        name="n-Butane",
        formula="n-C4H10",
        molecular_weight=Decimal("58.124"),
        critical_temperature_k=Decimal("425.1"),
        critical_pressure_bar=Decimal("37.9"),
    ),
    "isopentane": GasComponentData(
        name="Isopentane",
        formula="i-C5H12",
        molecular_weight=Decimal("72.151"),
    ),
    "n_pentane": GasComponentData(
        name="n-Pentane",
        formula="n-C5H12",
        molecular_weight=Decimal("72.151"),
    ),
    "hexane": GasComponentData(
        name="Hexane",
        formula="C6H14",
        molecular_weight=Decimal("86.178"),
    ),
    "nitrogen": GasComponentData(
        name="Nitrogen",
        formula="N2",
        molecular_weight=Decimal("28.014"),
        critical_temperature_k=Decimal("126.2"),
        critical_pressure_bar=Decimal("33.9"),
    ),
    "carbon_dioxide": GasComponentData(
        name="Carbon Dioxide",
        formula="CO2",
        molecular_weight=Decimal("44.010"),
        critical_temperature_k=Decimal("304.2"),
        critical_pressure_bar=Decimal("73.8"),
    ),
    "hydrogen_sulfide": GasComponentData(
        name="Hydrogen Sulfide",
        formula="H2S",
        molecular_weight=Decimal("34.081"),
        critical_temperature_k=Decimal("373.2"),
        critical_pressure_bar=Decimal("89.4"),
    ),
    "hydrogen": GasComponentData(
        name="Hydrogen",
        formula="H2",
        molecular_weight=Decimal("2.016"),
    ),
    "oxygen": GasComponentData(
        name="Oxygen",
        formula="O2",
        molecular_weight=Decimal("31.999"),
    ),
    "water": GasComponentData(
        name="Water",
        formula="H2O",
        molecular_weight=Decimal("18.015"),
    ),
}


def get_gas_component(key: str) -> GasComponentData:
    """Return reference data for a gas component."""

    normalized_key = key.strip().lower()

    try:
        return GAS_COMPONENTS[normalized_key]
    except KeyError as exc:
        raise ValueError(f"Unsupported gas component: {key}") from exc
