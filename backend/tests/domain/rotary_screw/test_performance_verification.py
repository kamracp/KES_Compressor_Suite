from decimal import Decimal

import pytest

from app.domain.rotary_screw.performance_verification import (
    InvalidPerformanceInputError,
    verify_manufacturer_performance,
)


def test_specific_power_is_input_power_divided_by_rated_fad() -> None:
    result = verify_manufacturer_performance(
        rated_fad_m3_per_min=Decimal("10"),
        package_input_power_kw=Decimal("60"),
    )

    assert result.rated_fad_m3_per_min == Decimal("10")
    assert result.package_input_power_kw == Decimal("60")
    assert result.specific_power_kw_per_m3_min == Decimal("6.000")


def test_rejects_zero_rated_fad() -> None:
    with pytest.raises(InvalidPerformanceInputError):
        verify_manufacturer_performance(
            rated_fad_m3_per_min=Decimal("0"),
            package_input_power_kw=Decimal("60"),
        )


def test_rejects_negative_package_input_power() -> None:
    with pytest.raises(InvalidPerformanceInputError):
        verify_manufacturer_performance(
            rated_fad_m3_per_min=Decimal("10"),
            package_input_power_kw=Decimal("-5"),
        )
