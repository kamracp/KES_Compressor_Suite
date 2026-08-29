from decimal import Decimal

import pytest

from app.domain.rotary_screw.annual_energy_cost import (
    InvalidAnnualEnergyCostInputError,
    calculate_annual_energy_cost,
)


def test_annual_energy_cost_matches_hand_calculation() -> None:
    # power=60 kW, hours=8000 hr/year, tariff=Rs.5/kWh
    # energy = 60 * 8000 = 480000 kWh
    # cost = 480000 * 5 = 2400000
    result = calculate_annual_energy_cost(
        package_input_power_kw=Decimal("60"),
        annual_operating_hours=Decimal("8000"),
        electricity_tariff_per_kwh=Decimal("5"),
    )

    assert result.annual_energy_kwh == Decimal("480000")
    assert result.annual_energy_cost == Decimal("2400000")


def test_rejects_zero_package_input_power() -> None:
    with pytest.raises(InvalidAnnualEnergyCostInputError):
        calculate_annual_energy_cost(
            package_input_power_kw=Decimal("0"),
            annual_operating_hours=Decimal("8000"),
            electricity_tariff_per_kwh=Decimal("5"),
        )


def test_rejects_negative_operating_hours() -> None:
    with pytest.raises(InvalidAnnualEnergyCostInputError):
        calculate_annual_energy_cost(
            package_input_power_kw=Decimal("60"),
            annual_operating_hours=Decimal("-1"),
            electricity_tariff_per_kwh=Decimal("5"),
        )


def test_rejects_operating_hours_exceeding_year() -> None:
    with pytest.raises(InvalidAnnualEnergyCostInputError):
        calculate_annual_energy_cost(
            package_input_power_kw=Decimal("60"),
            annual_operating_hours=Decimal("8761"),
            electricity_tariff_per_kwh=Decimal("5"),
        )


def test_rejects_negative_electricity_tariff() -> None:
    with pytest.raises(InvalidAnnualEnergyCostInputError):
        calculate_annual_energy_cost(
            package_input_power_kw=Decimal("60"),
            annual_operating_hours=Decimal("8000"),
            electricity_tariff_per_kwh=Decimal("-1"),
        )
