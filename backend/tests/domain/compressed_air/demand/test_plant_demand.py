from decimal import Decimal

import pytest

from app.domain.compressed_air.consumers.consumer_models import (
    AirConsumerCategory,
    AirConsumerDemandResult,
    AirQualityClass,
    ConsumerCriticality,
)
from app.domain.compressed_air.demand.plant_demand import (
    InvalidPlantDemandInputError,
    calculate_plant_demand,
)


def build_consumer(
    *,
    code: str,
    simultaneous_flow: Decimal,
    criticality: ConsumerCriticality,
) -> AirConsumerDemandResult:
    return AirConsumerDemandResult(
        consumer_code=code,
        name=code,
        category=AirConsumerCategory.OTHER,
        quantity=1,
        required_pressure_bar_g=Decimal("6"),
        air_quality_class=AirQualityClass.GENERAL_PLANT_AIR,
        theoretical_flow_nm3_per_hr=simultaneous_flow,
        duty_adjusted_flow_nm3_per_hr=simultaneous_flow,
        simultaneous_flow_nm3_per_hr=simultaneous_flow,
        annual_air_volume_nm3=simultaneous_flow * Decimal("8000"),
        criticality=criticality,
    )


def test_calculate_plant_demand() -> None:
    consumers = (
        build_consumer(
            code="C-001",
            simultaneous_flow=Decimal("140"),
            criticality=ConsumerCriticality.NORMAL,
        ),
        build_consumer(
            code="C-002",
            simultaneous_flow=Decimal("120"),
            criticality=ConsumerCriticality.CRITICAL,
        ),
    )

    result = calculate_plant_demand(
        consumers,
        leakage_fraction=Decimal("0.10"),
        future_expansion_fraction=Decimal("0.15"),
    )

    assert result.total_simultaneous_flow_nm3_per_hr == Decimal("260")
    assert result.leakage_allowance_nm3_per_hr == Decimal("26.00")
    assert result.future_expansion_allowance_nm3_per_hr == Decimal("39.00")
    assert result.other_allowance_nm3_per_hr == Decimal("0")
    assert result.design_flow_nm3_per_hr == Decimal("325.00")

    assert result.critical_flow_nm3_per_hr == Decimal("120")
    assert result.essential_flow_nm3_per_hr == Decimal("120")


def test_critical_and_essential_demand_are_separated() -> None:
    consumers = (
        build_consumer(
            code="CRIT",
            simultaneous_flow=Decimal("100"),
            criticality=ConsumerCriticality.CRITICAL,
        ),
        build_consumer(
            code="ESS",
            simultaneous_flow=Decimal("80"),
            criticality=ConsumerCriticality.ESSENTIAL,
        ),
        build_consumer(
            code="NORMAL",
            simultaneous_flow=Decimal("50"),
            criticality=ConsumerCriticality.NORMAL,
        ),
    )

    result = calculate_plant_demand(consumers)

    assert result.critical_flow_nm3_per_hr == Decimal("100")
    assert result.essential_flow_nm3_per_hr == Decimal("180")
    assert result.total_simultaneous_flow_nm3_per_hr == Decimal("230")


def test_all_allowances_are_explicitly_added() -> None:
    consumers = (
        build_consumer(
            code="C-001",
            simultaneous_flow=Decimal("1000"),
            criticality=ConsumerCriticality.NORMAL,
        ),
    )

    result = calculate_plant_demand(
        consumers,
        leakage_fraction=Decimal("0.05"),
        future_expansion_fraction=Decimal("0.10"),
        other_allowance_fraction=Decimal("0.02"),
    )

    assert result.leakage_allowance_nm3_per_hr == Decimal("50.00")
    assert result.future_expansion_allowance_nm3_per_hr == Decimal("100.00")
    assert result.other_allowance_nm3_per_hr == Decimal("20.00")
    assert result.design_flow_nm3_per_hr == Decimal("1170.00")


def test_zero_allowances_do_not_inflate_design_flow() -> None:
    consumers = (
        build_consumer(
            code="C-001",
            simultaneous_flow=Decimal("500"),
            criticality=ConsumerCriticality.NORMAL,
        ),
    )

    result = calculate_plant_demand(consumers)

    assert result.design_flow_nm3_per_hr == Decimal("500")
    assert result.leakage_allowance_nm3_per_hr == Decimal("0")
    assert result.future_expansion_allowance_nm3_per_hr == Decimal("0")
    assert result.other_allowance_nm3_per_hr == Decimal("0")


def test_empty_consumer_list_is_rejected() -> None:
    with pytest.raises(
        InvalidPlantDemandInputError,
        match="At least one consumer demand result is required",
    ):
        calculate_plant_demand(())


@pytest.mark.parametrize(
    ("field_name", "kwargs"),
    [
        (
            "Leakage fraction",
            {"leakage_fraction": Decimal("-0.01")},
        ),
        (
            "Future expansion fraction",
            {"future_expansion_fraction": Decimal("1.01")},
        ),
        (
            "Other allowance fraction",
            {"other_allowance_fraction": Decimal("-0.10")},
        ),
    ],
)
def test_invalid_allowance_fraction_is_rejected(
    field_name: str,
    kwargs: dict[str, Decimal],
) -> None:
    consumers = (
        build_consumer(
            code="C-001",
            simultaneous_flow=Decimal("100"),
            criticality=ConsumerCriticality.NORMAL,
        ),
    )

    with pytest.raises(
        InvalidPlantDemandInputError,
        match=field_name,
    ):
        calculate_plant_demand(
            consumers,
            **kwargs,
        )
