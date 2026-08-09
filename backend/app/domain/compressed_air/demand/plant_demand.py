from dataclasses import dataclass
from decimal import Decimal

from app.domain.compressed_air.consumers.consumer_models import (
    AirConsumerDemandResult,
    ConsumerCriticality,
)


class InvalidPlantDemandInputError(ValueError):
    """Raised when plant compressed-air demand inputs are invalid."""


@dataclass(frozen=True, slots=True)
class PlantDemandResult:
    """Aggregated plant compressed-air demand result."""

    total_theoretical_flow_nm3_per_hr: Decimal
    total_duty_adjusted_flow_nm3_per_hr: Decimal
    total_simultaneous_flow_nm3_per_hr: Decimal

    critical_flow_nm3_per_hr: Decimal
    essential_flow_nm3_per_hr: Decimal

    leakage_fraction: Decimal
    leakage_allowance_nm3_per_hr: Decimal

    future_expansion_fraction: Decimal
    future_expansion_allowance_nm3_per_hr: Decimal

    other_allowance_fraction: Decimal
    other_allowance_nm3_per_hr: Decimal

    design_flow_nm3_per_hr: Decimal
    annual_air_volume_nm3: Decimal


def calculate_plant_demand(
    consumer_results: tuple[AirConsumerDemandResult, ...],
    *,
    leakage_fraction: Decimal = Decimal("0"),
    future_expansion_fraction: Decimal = Decimal("0"),
    other_allowance_fraction: Decimal = Decimal("0"),
) -> PlantDemandResult:
    """Aggregate consumer demand and explicit plant allowances."""

    if not consumer_results:
        raise InvalidPlantDemandInputError("At least one consumer demand result is required.")

    _validate_fraction(
        leakage_fraction,
        "Leakage fraction",
    )
    _validate_fraction(
        future_expansion_fraction,
        "Future expansion fraction",
    )
    _validate_fraction(
        other_allowance_fraction,
        "Other allowance fraction",
    )

    total_theoretical_flow = sum(
        (result.theoretical_flow_nm3_per_hr for result in consumer_results),
        start=Decimal("0"),
    )

    total_duty_adjusted_flow = sum(
        (result.duty_adjusted_flow_nm3_per_hr for result in consumer_results),
        start=Decimal("0"),
    )

    total_simultaneous_flow = sum(
        (result.simultaneous_flow_nm3_per_hr for result in consumer_results),
        start=Decimal("0"),
    )

    annual_air_volume = sum(
        (result.annual_air_volume_nm3 for result in consumer_results),
        start=Decimal("0"),
    )

    critical_flow = sum(
        (
            result.simultaneous_flow_nm3_per_hr
            for result in consumer_results
            if result.criticality == ConsumerCriticality.CRITICAL
        ),
        start=Decimal("0"),
    )

    essential_flow = sum(
        (
            result.simultaneous_flow_nm3_per_hr
            for result in consumer_results
            if result.criticality
            in {
                ConsumerCriticality.CRITICAL,
                ConsumerCriticality.ESSENTIAL,
            }
        ),
        start=Decimal("0"),
    )

    leakage_allowance = total_simultaneous_flow * leakage_fraction

    future_expansion_allowance = total_simultaneous_flow * future_expansion_fraction

    other_allowance = total_simultaneous_flow * other_allowance_fraction

    design_flow = (
        total_simultaneous_flow + leakage_allowance + future_expansion_allowance + other_allowance
    )

    return PlantDemandResult(
        total_theoretical_flow_nm3_per_hr=total_theoretical_flow,
        total_duty_adjusted_flow_nm3_per_hr=total_duty_adjusted_flow,
        total_simultaneous_flow_nm3_per_hr=total_simultaneous_flow,
        critical_flow_nm3_per_hr=critical_flow,
        essential_flow_nm3_per_hr=essential_flow,
        leakage_fraction=leakage_fraction,
        leakage_allowance_nm3_per_hr=leakage_allowance,
        future_expansion_fraction=future_expansion_fraction,
        future_expansion_allowance_nm3_per_hr=future_expansion_allowance,
        other_allowance_fraction=other_allowance_fraction,
        other_allowance_nm3_per_hr=other_allowance,
        design_flow_nm3_per_hr=design_flow,
        annual_air_volume_nm3=annual_air_volume,
    )


def _validate_fraction(
    value: Decimal,
    label: str,
) -> None:
    if value < 0 or value > 1:
        raise InvalidPlantDemandInputError(f"{label} must be between zero and one.")
