from decimal import Decimal

import pytest

from app.domain.compressed_air.pressure.pressure_budget import (
    InvalidPressureBudgetInputError,
    PressureLossComponent,
    calculate_pressure_budget,
)


def build_components() -> tuple[PressureLossComponent, ...]:
    return (
        PressureLossComponent(
            component_code="DRYER",
            name="Refrigerated Dryer",
            pressure_drop_bar=Decimal("0.15"),
            category="TREATMENT",
        ),
        PressureLossComponent(
            component_code="FILTERS",
            name="Pre and After Filters",
            pressure_drop_bar=Decimal("0.10"),
            category="TREATMENT",
        ),
        PressureLossComponent(
            component_code="HEADER",
            name="Main Ring Header",
            pressure_drop_bar=Decimal("0.12"),
            category="DISTRIBUTION",
        ),
        PressureLossComponent(
            component_code="BRANCH",
            name="Critical Consumer Branch",
            pressure_drop_bar=Decimal("0.08"),
            category="DISTRIBUTION",
        ),
        PressureLossComponent(
            component_code="SKID",
            name="Compressor Skid Internal Loss",
            pressure_drop_bar=Decimal("0.05"),
            category="SKID",
        ),
    )


def test_calculate_pressure_budget() -> None:
    result = calculate_pressure_budget(
        minimum_point_of_use_pressure_bar_g=Decimal("6.0"),
        components=build_components(),
        control_margin_bar=Decimal("0.20"),
    )

    assert result.distribution_pressure_drop_bar == Decimal("0.20")
    assert result.treatment_pressure_drop_bar == Decimal("0.25")
    assert result.skid_pressure_drop_bar == Decimal("0.05")
    assert result.other_pressure_drop_bar == Decimal("0")
    assert result.total_pressure_drop_bar == Decimal("0.50")

    assert result.required_compressor_discharge_pressure_bar_g == Decimal("6.70")


def test_other_category_is_accumulated() -> None:
    components = (
        PressureLossComponent(
            component_code="REG",
            name="Point of Use Regulator",
            pressure_drop_bar=Decimal("0.12"),
            category="POINT_OF_USE",
        ),
    )

    result = calculate_pressure_budget(
        minimum_point_of_use_pressure_bar_g=Decimal("6"),
        components=components,
    )

    assert result.other_pressure_drop_bar == Decimal("0.12")
    assert result.total_pressure_drop_bar == Decimal("0.12")
    assert result.required_compressor_discharge_pressure_bar_g == Decimal("6.12")


def test_empty_components_are_supported() -> None:
    result = calculate_pressure_budget(
        minimum_point_of_use_pressure_bar_g=Decimal("6"),
        components=(),
        control_margin_bar=Decimal("0.2"),
    )

    assert result.total_pressure_drop_bar == Decimal("0")
    assert result.required_compressor_discharge_pressure_bar_g == Decimal("6.2")


def test_negative_point_of_use_pressure_is_rejected() -> None:
    with pytest.raises(
        InvalidPressureBudgetInputError,
        match="Minimum point-of-use pressure cannot be negative",
    ):
        calculate_pressure_budget(
            minimum_point_of_use_pressure_bar_g=Decimal("-0.1"),
            components=(),
        )


def test_negative_control_margin_is_rejected() -> None:
    with pytest.raises(
        InvalidPressureBudgetInputError,
        match="Control margin cannot be negative",
    ):
        calculate_pressure_budget(
            minimum_point_of_use_pressure_bar_g=Decimal("6"),
            components=(),
            control_margin_bar=Decimal("-0.1"),
        )


def test_negative_component_pressure_drop_is_rejected() -> None:
    components = (
        PressureLossComponent(
            component_code="BAD",
            name="Invalid Component",
            pressure_drop_bar=Decimal("-0.01"),
            category="DISTRIBUTION",
        ),
    )

    with pytest.raises(
        InvalidPressureBudgetInputError,
        match="Pressure drop cannot be negative",
    ):
        calculate_pressure_budget(
            minimum_point_of_use_pressure_bar_g=Decimal("6"),
            components=components,
        )


def test_empty_component_code_is_rejected() -> None:
    components = (
        PressureLossComponent(
            component_code="",
            name="Invalid Component",
            pressure_drop_bar=Decimal("0.1"),
            category="DISTRIBUTION",
        ),
    )

    with pytest.raises(
        InvalidPressureBudgetInputError,
        match="Pressure-loss component code cannot be empty",
    ):
        calculate_pressure_budget(
            minimum_point_of_use_pressure_bar_g=Decimal("6"),
            components=components,
        )


def test_empty_component_category_is_rejected() -> None:
    components = (
        PressureLossComponent(
            component_code="X",
            name="Invalid Component",
            pressure_drop_bar=Decimal("0.1"),
            category="",
        ),
    )

    with pytest.raises(
        InvalidPressureBudgetInputError,
        match="Pressure-loss component category cannot be empty",
    ):
        calculate_pressure_budget(
            minimum_point_of_use_pressure_bar_g=Decimal("6"),
            components=components,
        )
