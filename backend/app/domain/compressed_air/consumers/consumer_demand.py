from decimal import Decimal

from app.domain.compressed_air.consumers.consumer_models import (
    AirConsumer,
    AirConsumerDemandResult,
    AirConsumptionBasis,
)


class InvalidAirConsumerInputError(ValueError):
    """Raised when compressed-air consumer inputs are invalid."""


NL_PER_NM3 = Decimal("1000")
MINUTES_PER_HOUR = Decimal("60")


def calculate_consumer_demand(
    consumer: AirConsumer,
) -> AirConsumerDemandResult:
    """Calculate compressed-air demand for one consumer."""

    if not consumer.consumer_code.strip():
        raise InvalidAirConsumerInputError("Consumer code cannot be empty.")

    if not consumer.name.strip():
        raise InvalidAirConsumerInputError("Consumer name cannot be empty.")

    if consumer.quantity <= 0:
        raise InvalidAirConsumerInputError("Consumer quantity must be greater than zero.")

    if consumer.required_pressure_bar_g < 0:
        raise InvalidAirConsumerInputError("Required pressure cannot be negative.")

    if consumer.duty_factor < 0 or consumer.duty_factor > 1:
        raise InvalidAirConsumerInputError("Duty factor must be between zero and one.")

    if consumer.simultaneity_factor < 0 or consumer.simultaneity_factor > 1:
        raise InvalidAirConsumerInputError("Simultaneity factor must be between zero and one.")

    if consumer.operating_hours_per_day < 0 or consumer.operating_hours_per_day > 24:
        raise InvalidAirConsumerInputError("Operating hours per day must be between zero and 24.")

    if consumer.operating_days_per_year < 0 or consumer.operating_days_per_year > 366:
        raise InvalidAirConsumerInputError("Operating days per year must be between zero and 366.")

    theoretical_flow_nm3_per_hr = _calculate_theoretical_flow(
        consumer,
    )

    duty_adjusted_flow_nm3_per_hr = theoretical_flow_nm3_per_hr * consumer.duty_factor

    simultaneous_flow_nm3_per_hr = duty_adjusted_flow_nm3_per_hr * consumer.simultaneity_factor

    annual_air_volume_nm3 = (
        simultaneous_flow_nm3_per_hr
        * consumer.operating_hours_per_day
        * consumer.operating_days_per_year
    )

    return AirConsumerDemandResult(
        consumer_code=consumer.consumer_code,
        name=consumer.name,
        category=consumer.category,
        quantity=consumer.quantity,
        required_pressure_bar_g=consumer.required_pressure_bar_g,
        air_quality_class=consumer.air_quality_class,
        theoretical_flow_nm3_per_hr=theoretical_flow_nm3_per_hr,
        duty_adjusted_flow_nm3_per_hr=duty_adjusted_flow_nm3_per_hr,
        simultaneous_flow_nm3_per_hr=simultaneous_flow_nm3_per_hr,
        annual_air_volume_nm3=annual_air_volume_nm3,
        criticality=consumer.criticality,
    )


def _calculate_theoretical_flow(
    consumer: AirConsumer,
) -> Decimal:
    """Calculate theoretical flow before duty and simultaneity adjustments."""

    if consumer.consumption_basis in {
        AirConsumptionBasis.CONTINUOUS_FLOW,
        AirConsumptionBasis.FLOW_WHEN_OPERATING,
    }:
        if consumer.flow_per_unit_nm3_per_hr is None:
            raise InvalidAirConsumerInputError(
                "Flow per unit is required for flow-based consumers."
            )

        if consumer.flow_per_unit_nm3_per_hr < 0:
            raise InvalidAirConsumerInputError("Flow per unit cannot be negative.")

        return Decimal(consumer.quantity) * consumer.flow_per_unit_nm3_per_hr

    if consumer.consumption_basis == AirConsumptionBasis.PER_CYCLE:
        if consumer.air_per_cycle_nl is None:
            raise InvalidAirConsumerInputError("Air per cycle is required for per-cycle consumers.")

        if consumer.cycles_per_minute is None:
            raise InvalidAirConsumerInputError(
                "Cycles per minute is required for per-cycle consumers."
            )

        if consumer.air_per_cycle_nl < 0:
            raise InvalidAirConsumerInputError("Air per cycle cannot be negative.")

        if consumer.cycles_per_minute < 0:
            raise InvalidAirConsumerInputError("Cycles per minute cannot be negative.")

        air_per_unit_nm3_per_hr = (
            consumer.air_per_cycle_nl * consumer.cycles_per_minute * MINUTES_PER_HOUR / NL_PER_NM3
        )

        return Decimal(consumer.quantity) * air_per_unit_nm3_per_hr

    raise InvalidAirConsumerInputError(
        f"Unsupported consumption basis: {consumer.consumption_basis}"
    )
