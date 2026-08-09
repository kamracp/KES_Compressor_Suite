from dataclasses import dataclass
from decimal import Decimal


class InvalidPressureBudgetInputError(ValueError):
    """Raised when compressed-air pressure-budget inputs are invalid."""


@dataclass(frozen=True, slots=True)
class PressureLossComponent:
    """One pressure-loss component in the compressed-air system."""

    component_code: str
    name: str
    pressure_drop_bar: Decimal
    category: str
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class PressureBudgetResult:
    """Calculated compressed-air system pressure budget."""

    minimum_point_of_use_pressure_bar_g: Decimal

    distribution_pressure_drop_bar: Decimal
    treatment_pressure_drop_bar: Decimal
    skid_pressure_drop_bar: Decimal
    other_pressure_drop_bar: Decimal

    total_pressure_drop_bar: Decimal

    control_margin_bar: Decimal

    required_compressor_discharge_pressure_bar_g: Decimal

    components: tuple[PressureLossComponent, ...]


def calculate_pressure_budget(
    *,
    minimum_point_of_use_pressure_bar_g: Decimal,
    components: tuple[PressureLossComponent, ...],
    control_margin_bar: Decimal = Decimal("0"),
) -> PressureBudgetResult:
    """Calculate required compressor discharge pressure."""

    if minimum_point_of_use_pressure_bar_g < 0:
        raise InvalidPressureBudgetInputError("Minimum point-of-use pressure cannot be negative.")

    if control_margin_bar < 0:
        raise InvalidPressureBudgetInputError("Control margin cannot be negative.")

    for component in components:
        _validate_component(component)

    distribution_pressure_drop_bar = _sum_category(
        components,
        "DISTRIBUTION",
    )

    treatment_pressure_drop_bar = _sum_category(
        components,
        "TREATMENT",
    )

    skid_pressure_drop_bar = _sum_category(
        components,
        "SKID",
    )

    other_pressure_drop_bar = sum(
        (
            component.pressure_drop_bar
            for component in components
            if component.category.upper()
            not in {
                "DISTRIBUTION",
                "TREATMENT",
                "SKID",
            }
        ),
        start=Decimal("0"),
    )

    total_pressure_drop_bar = sum(
        (component.pressure_drop_bar for component in components),
        start=Decimal("0"),
    )

    required_compressor_discharge_pressure_bar_g = (
        minimum_point_of_use_pressure_bar_g + total_pressure_drop_bar + control_margin_bar
    )

    return PressureBudgetResult(
        minimum_point_of_use_pressure_bar_g=(minimum_point_of_use_pressure_bar_g),
        distribution_pressure_drop_bar=distribution_pressure_drop_bar,
        treatment_pressure_drop_bar=treatment_pressure_drop_bar,
        skid_pressure_drop_bar=skid_pressure_drop_bar,
        other_pressure_drop_bar=other_pressure_drop_bar,
        total_pressure_drop_bar=total_pressure_drop_bar,
        control_margin_bar=control_margin_bar,
        required_compressor_discharge_pressure_bar_g=(required_compressor_discharge_pressure_bar_g),
        components=components,
    )


def _validate_component(
    component: PressureLossComponent,
) -> None:
    if not component.component_code.strip():
        raise InvalidPressureBudgetInputError("Pressure-loss component code cannot be empty.")

    if not component.name.strip():
        raise InvalidPressureBudgetInputError("Pressure-loss component name cannot be empty.")

    if not component.category.strip():
        raise InvalidPressureBudgetInputError("Pressure-loss component category cannot be empty.")

    if component.pressure_drop_bar < 0:
        raise InvalidPressureBudgetInputError("Pressure drop cannot be negative.")


def _sum_category(
    components: tuple[PressureLossComponent, ...],
    category: str,
) -> Decimal:
    return sum(
        (
            component.pressure_drop_bar
            for component in components
            if component.category.upper() == category
        ),
        start=Decimal("0"),
    )
