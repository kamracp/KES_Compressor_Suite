from decimal import Decimal

import pytest

from app.domain.centrifugal.surge import (
    InvalidSurgeInputError,
    calculate_surge_control,
)


def test_calculate_surge_control() -> None:
    result = calculate_surge_control(
        design_flow_m3_per_hr=Decimal("14143.4"),
        surge_flow_fraction=Decimal("0.70"),
        anti_surge_margin_fraction=Decimal("0.10"),
        stonewall_flow_fraction=Decimal("1.25"),
    )

    assert result.surge_flow_m3_per_hr == Decimal("9900.380")
    assert result.anti_surge_setpoint_m3_per_hr == Decimal("10890.4180")
    assert result.surge_margin_fraction == Decimal("0.30")
    assert result.stonewall_flow_m3_per_hr == Decimal("17679.250")
    assert result.operating_range_m3_per_hr == Decimal("7778.870")
    assert result.design_point_is_within_envelope is True


def test_zero_design_flow_is_rejected() -> None:
    with pytest.raises(
        InvalidSurgeInputError,
        match="Design flow must be greater than zero",
    ):
        calculate_surge_control(
            design_flow_m3_per_hr=Decimal("0"),
        )


def test_invalid_surge_fraction_zero_is_rejected() -> None:
    with pytest.raises(
        InvalidSurgeInputError,
        match="Surge flow fraction must be greater than zero and less than one",
    ):
        calculate_surge_control(
            design_flow_m3_per_hr=Decimal("1000"),
            surge_flow_fraction=Decimal("0"),
        )


def test_invalid_surge_fraction_one_is_rejected() -> None:
    with pytest.raises(
        InvalidSurgeInputError,
        match="Surge flow fraction must be greater than zero and less than one",
    ):
        calculate_surge_control(
            design_flow_m3_per_hr=Decimal("1000"),
            surge_flow_fraction=Decimal("1"),
        )


def test_negative_anti_surge_margin_is_rejected() -> None:
    with pytest.raises(
        InvalidSurgeInputError,
        match="Anti-surge margin fraction cannot be negative",
    ):
        calculate_surge_control(
            design_flow_m3_per_hr=Decimal("1000"),
            anti_surge_margin_fraction=Decimal("-0.01"),
        )


def test_invalid_stonewall_fraction_is_rejected() -> None:
    with pytest.raises(
        InvalidSurgeInputError,
        match="Stonewall flow fraction must be greater than one",
    ):
        calculate_surge_control(
            design_flow_m3_per_hr=Decimal("1000"),
            stonewall_flow_fraction=Decimal("1"),
        )


def test_design_point_is_inside_operating_envelope() -> None:
    result = calculate_surge_control(
        design_flow_m3_per_hr=Decimal("1000"),
        surge_flow_fraction=Decimal("0.70"),
        stonewall_flow_fraction=Decimal("1.25"),
    )

    assert result.surge_flow_m3_per_hr < result.design_flow_m3_per_hr
    assert result.design_flow_m3_per_hr < result.stonewall_flow_m3_per_hr
    assert result.design_point_is_within_envelope is True
