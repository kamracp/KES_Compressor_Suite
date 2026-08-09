from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class GasComponent:
    """Represents a pure gas component used in a gas mixture."""

    name: str
    formula: str
    molecular_weight: Decimal
    mole_fraction: Decimal


@dataclass(frozen=True, slots=True)
class GasMixture:
    """Represents a gas mixture defined by component mole fractions."""

    components: tuple[GasComponent, ...]

    @property
    def total_mole_fraction(self) -> Decimal:
        return sum(
            (component.mole_fraction for component in self.components),
            start=Decimal("0"),
        )

    @property
    def molecular_weight(self) -> Decimal:
        return sum(
            (component.mole_fraction * component.molecular_weight for component in self.components),
            start=Decimal("0"),
        )
