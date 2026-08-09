from decimal import Decimal

import pytest

from app.domain.compressed_air.consumers.consumer_demand import (
    InvalidAirConsumerInputError,
    calculate_consumer_demand,
)
from app.domain.compressed_air.consumers.consumer_models import (
    AirConsumer,
    AirConsumerCategory,
    AirConsumptionBasis,
    AirQualityClass,
)


def test_flow_based_consumer_demand() -> None:
    consumer = AirConsumer(
        consumer_code="CNC-001",
        name="CNC Machine Group",
        category=AirConsumerCategory.PRODUCTION_MACHINE,
        quantity=10,
        required_pressure_bar_g=Decimal("6.0"),
        air_quality_class=AirQualityClass.GENERAL_PLANT_AIR,
        consumption_basis=AirConsumptionBasis.FLOW_WHEN_OPERATING,
        flow_per_unit_nm3_per_hr=Decimal("25"),
        duty_factor=Decimal("0.70"),
        simultaneity_factor=Decimal("0.80"),
        operating_hours_per_day=Decimal("16"),
        operating_days_per_year=Decimal("300"),
    )

    result = calculate_consumer_demand(consumer)

    assert result.theoretical_flow_nm3_per_hr == Decimal("250")
    assert result.duty_adjusted_flow_nm3_per_hr == Decimal("175.00")
    assert result.simultaneous_flow_nm3_per_hr == Decimal("140.0000")
    assert result.annual_air_volume_nm3 == Decimal("672000.0000")


def test_per_cycle_consumer_demand() -> None:
    consumer = AirConsumer(
        consumer_code="CYL-001",
        name="Pneumatic Cylinder Group",
        category=AirConsumerCategory.PNEUMATIC_CYLINDER,
        quantity=20,
        required_pressure_bar_g=Decimal("6.0"),
        air_quality_class=AirQualityClass.GENERAL_PLANT_AIR,
        consumption_basis=AirConsumptionBasis.PER_CYCLE,
        air_per_cycle_nl=Decimal("2.5"),
        cycles_per_minute=Decimal("6"),
        duty_factor=Decimal("0.75"),
        simultaneity_factor=Decimal("0.60"),
        operating_hours_per_day=Decimal("16"),
        operating_days_per_year=Decimal("300"),
    )

    result = calculate_consumer_demand(consumer)

    assert result.theoretical_flow_nm3_per_hr == Decimal("18.00")
    assert result.duty_adjusted_flow_nm3_per_hr == Decimal("13.5000")
    assert result.simultaneous_flow_nm3_per_hr == Decimal("8.100000")
    assert result.annual_air_volume_nm3 == Decimal("38880.000000")


def test_continuous_flow_consumer() -> None:
    consumer = AirConsumer(
        consumer_code="IA-001",
        name="Instrument Air",
        category=AirConsumerCategory.INSTRUMENT_AIR,
        quantity=1,
        required_pressure_bar_g=Decimal("6.5"),
        air_quality_class=AirQualityClass.INSTRUMENT_AIR,
        consumption_basis=AirConsumptionBasis.CONTINUOUS_FLOW,
        flow_per_unit_nm3_per_hr=Decimal("120"),
    )

    result = calculate_consumer_demand(consumer)

    assert result.theoretical_flow_nm3_per_hr == Decimal("120")
    assert result.duty_adjusted_flow_nm3_per_hr == Decimal("120")
    assert result.simultaneous_flow_nm3_per_hr == Decimal("120")


def test_zero_quantity_is_rejected() -> None:
    consumer = AirConsumer(
        consumer_code="BAD-001",
        name="Invalid Consumer",
        category=AirConsumerCategory.OTHER,
        quantity=0,
        required_pressure_bar_g=Decimal("6"),
        air_quality_class=AirQualityClass.GENERAL_PLANT_AIR,
        consumption_basis=AirConsumptionBasis.CONTINUOUS_FLOW,
        flow_per_unit_nm3_per_hr=Decimal("10"),
    )

    with pytest.raises(
        InvalidAirConsumerInputError,
        match="Consumer quantity must be greater than zero",
    ):
        calculate_consumer_demand(consumer)


def test_missing_flow_for_flow_based_consumer_is_rejected() -> None:
    consumer = AirConsumer(
        consumer_code="BAD-002",
        name="Missing Flow",
        category=AirConsumerCategory.PRODUCTION_MACHINE,
        quantity=1,
        required_pressure_bar_g=Decimal("6"),
        air_quality_class=AirQualityClass.GENERAL_PLANT_AIR,
        consumption_basis=AirConsumptionBasis.FLOW_WHEN_OPERATING,
    )

    with pytest.raises(
        InvalidAirConsumerInputError,
        match="Flow per unit is required",
    ):
        calculate_consumer_demand(consumer)


def test_missing_cycle_data_is_rejected() -> None:
    consumer = AirConsumer(
        consumer_code="BAD-003",
        name="Missing Cycle Data",
        category=AirConsumerCategory.PNEUMATIC_CYLINDER,
        quantity=1,
        required_pressure_bar_g=Decimal("6"),
        air_quality_class=AirQualityClass.GENERAL_PLANT_AIR,
        consumption_basis=AirConsumptionBasis.PER_CYCLE,
        air_per_cycle_nl=Decimal("2.0"),
        cycles_per_minute=None,
    )

    with pytest.raises(
        InvalidAirConsumerInputError,
        match="Cycles per minute is required",
    ):
        calculate_consumer_demand(consumer)


def test_invalid_duty_factor_is_rejected() -> None:
    consumer = AirConsumer(
        consumer_code="BAD-004",
        name="Invalid Duty",
        category=AirConsumerCategory.OTHER,
        quantity=1,
        required_pressure_bar_g=Decimal("6"),
        air_quality_class=AirQualityClass.GENERAL_PLANT_AIR,
        consumption_basis=AirConsumptionBasis.CONTINUOUS_FLOW,
        flow_per_unit_nm3_per_hr=Decimal("10"),
        duty_factor=Decimal("1.1"),
    )

    with pytest.raises(
        InvalidAirConsumerInputError,
        match="Duty factor must be between zero and one",
    ):
        calculate_consumer_demand(consumer)


def test_invalid_simultaneity_factor_is_rejected() -> None:
    consumer = AirConsumer(
        consumer_code="BAD-005",
        name="Invalid Simultaneity",
        category=AirConsumerCategory.OTHER,
        quantity=1,
        required_pressure_bar_g=Decimal("6"),
        air_quality_class=AirQualityClass.GENERAL_PLANT_AIR,
        consumption_basis=AirConsumptionBasis.CONTINUOUS_FLOW,
        flow_per_unit_nm3_per_hr=Decimal("10"),
        simultaneity_factor=Decimal("-0.1"),
    )

    with pytest.raises(
        InvalidAirConsumerInputError,
        match="Simultaneity factor must be between zero and one",
    ):
        calculate_consumer_demand(consumer)
