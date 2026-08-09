from decimal import Decimal

import pytest

from app.domain.centrifugal.impeller import (
    InvalidImpellerInputError,
    calculate_impeller_sizing,
)


def test_calculate_impeller_sizing() -> None:
    result = calculate_impeller_sizing(
        total_polytropic_head_kj_per_kg=Decimal("155.667"),
        number_of_impeller_stages=3,
        head_coefficient=Decimal("0.55"),
        rotational_speed_rpm=Decimal("8000"),
    )

    assert result.number_of_impeller_stages == 3
    assert result.head_per_stage_kj_per_kg == Decimal("51.889")
    assert result.impeller_tip_speed_m_per_s > Decimal("300")
    assert result.impeller_tip_speed_m_per_s < Decimal("315")
    assert result.impeller_diameter_m > Decimal("0.70")
    assert result.impeller_diameter_m < Decimal("0.75")


def test_single_impeller_stage() -> None:
    result = calculate_impeller_sizing(
        total_polytropic_head_kj_per_kg=Decimal("100"),
        number_of_impeller_stages=1,
        head_coefficient=Decimal("0.50"),
        rotational_speed_rpm=Decimal("10000"),
    )

    assert result.head_per_stage_kj_per_kg == Decimal("100")
    assert result.number_of_impeller_stages == 1


def test_zero_polytropic_head_is_rejected() -> None:
    with pytest.raises(
        InvalidImpellerInputError,
        match="Total polytropic head must be greater than zero",
    ):
        calculate_impeller_sizing(
            total_polytropic_head_kj_per_kg=Decimal("0"),
            number_of_impeller_stages=3,
            head_coefficient=Decimal("0.55"),
            rotational_speed_rpm=Decimal("8000"),
        )


def test_zero_impeller_stages_is_rejected() -> None:
    with pytest.raises(
        InvalidImpellerInputError,
        match="Number of impeller stages must be at least one",
    ):
        calculate_impeller_sizing(
            total_polytropic_head_kj_per_kg=Decimal("155"),
            number_of_impeller_stages=0,
            head_coefficient=Decimal("0.55"),
            rotational_speed_rpm=Decimal("8000"),
        )


def test_zero_head_coefficient_is_rejected() -> None:
    with pytest.raises(
        InvalidImpellerInputError,
        match="Head coefficient must be greater than zero",
    ):
        calculate_impeller_sizing(
            total_polytropic_head_kj_per_kg=Decimal("155"),
            number_of_impeller_stages=3,
            head_coefficient=Decimal("0"),
            rotational_speed_rpm=Decimal("8000"),
        )


def test_zero_rotational_speed_is_rejected() -> None:
    with pytest.raises(
        InvalidImpellerInputError,
        match="Rotational speed must be greater than zero",
    ):
        calculate_impeller_sizing(
            total_polytropic_head_kj_per_kg=Decimal("155"),
            number_of_impeller_stages=3,
            head_coefficient=Decimal("0.55"),
            rotational_speed_rpm=Decimal("0"),
        )
