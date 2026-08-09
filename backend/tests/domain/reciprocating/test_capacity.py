from decimal import Decimal

import pytest

from app.domain.reciprocating.capacity import (
    InvalidCapacityInputError,
    calculate_required_cylinders,
)


def test_calculate_required_cylinders() -> None:
    result = calculate_required_cylinders(
        required_flow_m3_per_hr=Decimal("14143.4"),
        delivered_flow_per_cylinder_m3_per_hr=Decimal("1908.836"),
    )

    assert result.required_cylinders == 8
    assert result.installed_capacity_m3_per_hr == Decimal("15270.688")
    assert result.capacity_margin_m3_per_hr == Decimal("1127.288")
    assert result.capacity_is_adequate is True
    assert result.capacity_margin_fraction > Decimal("0")


def test_exact_capacity_fit_requires_one_cylinder() -> None:
    result = calculate_required_cylinders(
        required_flow_m3_per_hr=Decimal("1000"),
        delivered_flow_per_cylinder_m3_per_hr=Decimal("1000"),
    )

    assert result.required_cylinders == 1
    assert result.installed_capacity_m3_per_hr == Decimal("1000")
    assert result.capacity_margin_m3_per_hr == Decimal("0")
    assert result.capacity_margin_fraction == Decimal("0")
    assert result.capacity_is_adequate is True


def test_fractional_cylinder_requirement_rounds_up() -> None:
    result = calculate_required_cylinders(
        required_flow_m3_per_hr=Decimal("1001"),
        delivered_flow_per_cylinder_m3_per_hr=Decimal("1000"),
    )

    assert result.required_cylinders == 2
    assert result.installed_capacity_m3_per_hr == Decimal("2000")
    assert result.capacity_is_adequate is True


def test_zero_required_flow_is_rejected() -> None:
    with pytest.raises(
        InvalidCapacityInputError,
        match="Required flow must be greater than zero",
    ):
        calculate_required_cylinders(
            required_flow_m3_per_hr=Decimal("0"),
            delivered_flow_per_cylinder_m3_per_hr=Decimal("1000"),
        )


def test_negative_required_flow_is_rejected() -> None:
    with pytest.raises(
        InvalidCapacityInputError,
        match="Required flow must be greater than zero",
    ):
        calculate_required_cylinders(
            required_flow_m3_per_hr=Decimal("-1"),
            delivered_flow_per_cylinder_m3_per_hr=Decimal("1000"),
        )


def test_zero_delivered_flow_is_rejected() -> None:
    with pytest.raises(
        InvalidCapacityInputError,
        match="Delivered flow per cylinder must be greater than zero",
    ):
        calculate_required_cylinders(
            required_flow_m3_per_hr=Decimal("1000"),
            delivered_flow_per_cylinder_m3_per_hr=Decimal("0"),
        )


def test_negative_delivered_flow_is_rejected() -> None:
    with pytest.raises(
        InvalidCapacityInputError,
        match="Delivered flow per cylinder must be greater than zero",
    ):
        calculate_required_cylinders(
            required_flow_m3_per_hr=Decimal("1000"),
            delivered_flow_per_cylinder_m3_per_hr=Decimal("-1"),
        )
