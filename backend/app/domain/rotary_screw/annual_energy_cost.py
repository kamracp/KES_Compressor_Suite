from decimal import Decimal

from app.domain.rotary_screw.models import RotaryScrewAnnualEnergyCostResult


class InvalidAnnualEnergyCostInputError(ValueError):
    """Raised when annual energy cost inputs are invalid."""


def calculate_annual_energy_cost(
    package_input_power_kw: Decimal,
    annual_operating_hours: Decimal,
    electricity_tariff_per_kwh: Decimal,
) -> RotaryScrewAnnualEnergyCostResult:
    """Calculate annual electrical energy consumption and cost.

    A direct arithmetic result from manufacturer-verified package input
    power: energy = power x time, cost = energy x tariff. This does not
    estimate or predict machine performance -- it multiplies real,
    already-verified figures by the operating basis the user supplies.
    """

    if package_input_power_kw <= 0:
        raise InvalidAnnualEnergyCostInputError(
            "Package input power must be greater than zero."
        )

    if annual_operating_hours < 0:
        raise InvalidAnnualEnergyCostInputError(
            "Annual operating hours cannot be negative."
        )

    if annual_operating_hours > Decimal("8760"):
        raise InvalidAnnualEnergyCostInputError(
            "Annual operating hours cannot exceed the hours in a year (8760)."
        )

    if electricity_tariff_per_kwh < 0:
        raise InvalidAnnualEnergyCostInputError(
            "Electricity tariff cannot be negative."
        )

    annual_energy_kwh = package_input_power_kw * annual_operating_hours
    annual_energy_cost = annual_energy_kwh * electricity_tariff_per_kwh

    return RotaryScrewAnnualEnergyCostResult(
        annual_operating_hours=annual_operating_hours,
        electricity_tariff_per_kwh=electricity_tariff_per_kwh,
        annual_energy_kwh=annual_energy_kwh,
        annual_energy_cost=annual_energy_cost,
    )
