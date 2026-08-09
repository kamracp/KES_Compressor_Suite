from decimal import Decimal

import pytest

from app.domain.compressed_air.skid.skid_assessment import (
    InvalidAirSkidInputError,
    assess_air_skid,
)
from app.domain.compressed_air.skid.skid_models import (
    AirSkidConfiguration,
    SkidArrangement,
    SkidComponent,
    SkidComponentType,
)
from app.domain.compressed_air.treatment.air_treatment import DryerType


def component(
    *,
    code: str,
    component_type: SkidComponentType,
    flow: str | None = None,
    pressure: str | None = None,
    pressure_drop: str = "0",
) -> SkidComponent:
    return SkidComponent(
        component_code=code,
        name=code,
        component_type=component_type,
        rated_flow_nm3_per_hr=Decimal(flow) if flow is not None else None,
        rated_pressure_bar_g=(Decimal(pressure) if pressure is not None else None),
        pressure_drop_bar=Decimal(pressure_drop),
    )


def build_components() -> tuple[SkidComponent, ...]:
    return (
        component(
            code="AC",
            component_type=SkidComponentType.COMPRESSOR,
            flow="3600",
            pressure="7.5",
        ),
        component(
            code="ACR",
            component_type=SkidComponentType.AFTERCOOLER,
            flow="3500",
            pressure="10",
            pressure_drop="0.05",
        ),
        component(
            code="SEP",
            component_type=SkidComponentType.MOISTURE_SEPARATOR,
            flow="3500",
            pressure="10",
            pressure_drop="0.03",
        ),
        component(
            code="WR",
            component_type=SkidComponentType.WET_RECEIVER,
            pressure="10",
        ),
        component(
            code="PF",
            component_type=SkidComponentType.PREFILTER,
            flow="3400",
            pressure="10",
            pressure_drop="0.08",
        ),
        component(
            code="DRYER",
            component_type=SkidComponentType.DRYER,
            flow="3400",
            pressure="10",
            pressure_drop="0.12",
        ),
        component(
            code="AF",
            component_type=SkidComponentType.AFTERFILTER,
            flow="3400",
            pressure="10",
            pressure_drop="0.07",
        ),
        component(
            code="DR",
            component_type=SkidComponentType.DRY_RECEIVER,
            pressure="10",
        ),
        component(
            code="FM",
            component_type=SkidComponentType.FLOW_METER,
            flow="3500",
            pressure="10",
            pressure_drop="0.02",
        ),
        component(
            code="PS",
            component_type=SkidComponentType.PRESSURE_SENSOR,
        ),
        component(
            code="DPS",
            component_type=SkidComponentType.DEW_POINT_SENSOR,
        ),
        component(
            code="MC",
            component_type=SkidComponentType.MASTER_CONTROLLER,
        ),
    )


def build_configuration(
    components: tuple[SkidComponent, ...] | None = None,
) -> AirSkidConfiguration:
    return AirSkidConfiguration(
        skid_code="SKID-001",
        arrangement=SkidArrangement.CENTRALIZED,
        design_flow_nm3_per_hr=Decimal("3000"),
        design_pressure_bar_g=Decimal("7"),
        dryer_type=DryerType.REFRIGERATED,
        components=components if components is not None else build_components(),
        has_wet_receiver=True,
        has_dry_receiver=True,
        has_flow_metering=True,
        has_pressure_monitoring=True,
        has_dew_point_monitoring=True,
        master_control_enabled=True,
    )


def test_complete_air_skid_is_adequate() -> None:
    result = assess_air_skid(build_configuration())

    assert result.skid_code == "SKID-001"
    assert result.flow_capacity_is_adequate is True
    assert result.pressure_rating_is_adequate is True

    assert result.has_wet_receiver is True
    assert result.has_dry_receiver is True

    assert result.has_flow_metering is True
    assert result.has_pressure_monitoring is True
    assert result.has_dew_point_monitoring is True

    assert result.instrumentation_is_complete is True
    assert result.master_control_enabled is True
    assert result.skid_is_adequate is True


def test_total_pressure_drop_is_aggregated() -> None:
    result = assess_air_skid(build_configuration())

    assert result.total_pressure_drop_bar == Decimal("0.37")


def test_minimum_component_flow_capacity_is_detected() -> None:
    result = assess_air_skid(build_configuration())

    assert result.minimum_component_flow_capacity_nm3_per_hr == Decimal("3400")


def test_undersized_dryer_makes_skid_inadequate() -> None:
    components = tuple(
        component(
            code=item.component_code,
            component_type=item.component_type,
            flow=(
                "2500"
                if item.component_type == SkidComponentType.DRYER
                else (
                    str(item.rated_flow_nm3_per_hr)
                    if item.rated_flow_nm3_per_hr is not None
                    else None
                )
            ),
            pressure=(
                str(item.rated_pressure_bar_g) if item.rated_pressure_bar_g is not None else None
            ),
            pressure_drop=str(item.pressure_drop_bar),
        )
        for item in build_components()
    )

    result = assess_air_skid(build_configuration(components))

    assert result.minimum_component_flow_capacity_nm3_per_hr == Decimal("2500")
    assert result.flow_capacity_is_adequate is False
    assert result.skid_is_adequate is False


def test_low_pressure_rating_makes_skid_inadequate() -> None:
    components = tuple(
        component(
            code=item.component_code,
            component_type=item.component_type,
            flow=(
                str(item.rated_flow_nm3_per_hr) if item.rated_flow_nm3_per_hr is not None else None
            ),
            pressure=(
                "6.5"
                if item.component_type == SkidComponentType.DRYER
                else (
                    str(item.rated_pressure_bar_g)
                    if item.rated_pressure_bar_g is not None
                    else None
                )
            ),
            pressure_drop=str(item.pressure_drop_bar),
        )
        for item in build_components()
    )

    result = assess_air_skid(build_configuration(components))

    assert result.minimum_component_pressure_rating_bar_g == Decimal("6.5")
    assert result.pressure_rating_is_adequate is False
    assert result.skid_is_adequate is False


def test_missing_wet_receiver_is_detected() -> None:
    components = tuple(
        item for item in build_components() if item.component_type != SkidComponentType.WET_RECEIVER
    )

    result = assess_air_skid(build_configuration(components))

    assert result.has_wet_receiver is False
    assert result.skid_is_adequate is False


def test_missing_dry_receiver_is_detected() -> None:
    components = tuple(
        item for item in build_components() if item.component_type != SkidComponentType.DRY_RECEIVER
    )

    result = assess_air_skid(build_configuration(components))

    assert result.has_dry_receiver is False
    assert result.skid_is_adequate is False


def test_missing_dew_point_sensor_makes_instrumentation_incomplete() -> None:
    components = tuple(
        item
        for item in build_components()
        if item.component_type != SkidComponentType.DEW_POINT_SENSOR
    )

    result = assess_air_skid(build_configuration(components))

    assert result.has_dew_point_monitoring is False
    assert result.instrumentation_is_complete is False
    assert result.skid_is_adequate is False


def test_duplicate_component_code_is_rejected() -> None:
    components = build_components() + (
        component(
            code="DRYER",
            component_type=SkidComponentType.DRYER,
            flow="3400",
            pressure="10",
        ),
    )

    with pytest.raises(
        InvalidAirSkidInputError,
        match="Duplicate skid component code",
    ):
        assess_air_skid(build_configuration(components))


def test_empty_component_list_is_rejected() -> None:
    with pytest.raises(
        InvalidAirSkidInputError,
        match="At least one skid component is required",
    ):
        assess_air_skid(build_configuration(()))
