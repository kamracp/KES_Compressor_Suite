from decimal import Decimal

from app.domain.compressed_air.skid.skid_models import (
    AirSkidAssessmentResult,
    AirSkidConfiguration,
    SkidComponentType,
)


class InvalidAirSkidInputError(ValueError):
    """Raised when compressed-air skid inputs are invalid."""


_FLOW_CRITICAL_COMPONENT_TYPES = {
    SkidComponentType.AFTERCOOLER,
    SkidComponentType.MOISTURE_SEPARATOR,
    SkidComponentType.PREFILTER,
    SkidComponentType.DRYER,
    SkidComponentType.AFTERFILTER,
    SkidComponentType.FLOW_METER,
}

_PRESSURE_CRITICAL_COMPONENT_TYPES = {
    SkidComponentType.AFTERCOOLER,
    SkidComponentType.MOISTURE_SEPARATOR,
    SkidComponentType.WET_RECEIVER,
    SkidComponentType.PREFILTER,
    SkidComponentType.DRYER,
    SkidComponentType.AFTERFILTER,
    SkidComponentType.DRY_RECEIVER,
    SkidComponentType.FLOW_METER,
    SkidComponentType.ISOLATION_VALVE,
    SkidComponentType.CHECK_VALVE,
}


def assess_air_skid(
    configuration: AirSkidConfiguration,
) -> AirSkidAssessmentResult:
    """Assess an integrated compressed-air skid configuration."""

    _validate_configuration(configuration)

    flow_ratings = tuple(
        component.rated_flow_nm3_per_hr
        for component in configuration.components
        if component.component_type in _FLOW_CRITICAL_COMPONENT_TYPES
        and component.rated_flow_nm3_per_hr is not None
    )

    pressure_ratings = tuple(
        component.rated_pressure_bar_g
        for component in configuration.components
        if component.component_type in _PRESSURE_CRITICAL_COMPONENT_TYPES
        and component.rated_pressure_bar_g is not None
    )

    minimum_component_flow_capacity = min(flow_ratings) if flow_ratings else None

    minimum_component_pressure_rating = min(pressure_ratings) if pressure_ratings else None

    flow_capacity_is_adequate = (
        minimum_component_flow_capacity is not None
        and minimum_component_flow_capacity >= configuration.design_flow_nm3_per_hr
    )

    pressure_rating_is_adequate = (
        minimum_component_pressure_rating is not None
        and minimum_component_pressure_rating >= configuration.design_pressure_bar_g
    )

    total_pressure_drop = sum(
        (component.pressure_drop_bar for component in configuration.components),
        start=Decimal("0"),
    )

    has_wet_receiver = configuration.has_wet_receiver and _contains_component(
        configuration,
        SkidComponentType.WET_RECEIVER,
    )

    has_dry_receiver = configuration.has_dry_receiver and _contains_component(
        configuration,
        SkidComponentType.DRY_RECEIVER,
    )

    has_flow_metering = configuration.has_flow_metering and _contains_component(
        configuration,
        SkidComponentType.FLOW_METER,
    )

    has_pressure_monitoring = configuration.has_pressure_monitoring and _contains_component(
        configuration,
        SkidComponentType.PRESSURE_SENSOR,
    )

    has_dew_point_monitoring = configuration.has_dew_point_monitoring and _contains_component(
        configuration,
        SkidComponentType.DEW_POINT_SENSOR,
    )

    master_control_enabled = configuration.master_control_enabled and _contains_component(
        configuration,
        SkidComponentType.MASTER_CONTROLLER,
    )

    instrumentation_is_complete = (
        has_flow_metering and has_pressure_monitoring and has_dew_point_monitoring
    )

    skid_is_adequate = (
        flow_capacity_is_adequate
        and pressure_rating_is_adequate
        and instrumentation_is_complete
        and has_wet_receiver
        and has_dry_receiver
    )

    return AirSkidAssessmentResult(
        skid_code=configuration.skid_code,
        design_flow_nm3_per_hr=configuration.design_flow_nm3_per_hr,
        design_pressure_bar_g=configuration.design_pressure_bar_g,
        total_component_count=sum(component.quantity for component in configuration.components),
        total_pressure_drop_bar=total_pressure_drop,
        minimum_component_flow_capacity_nm3_per_hr=(minimum_component_flow_capacity),
        minimum_component_pressure_rating_bar_g=(minimum_component_pressure_rating),
        flow_capacity_is_adequate=flow_capacity_is_adequate,
        pressure_rating_is_adequate=pressure_rating_is_adequate,
        has_wet_receiver=has_wet_receiver,
        has_dry_receiver=has_dry_receiver,
        has_flow_metering=has_flow_metering,
        has_pressure_monitoring=has_pressure_monitoring,
        has_dew_point_monitoring=has_dew_point_monitoring,
        master_control_enabled=master_control_enabled,
        instrumentation_is_complete=instrumentation_is_complete,
        skid_is_adequate=skid_is_adequate,
    )


def _contains_component(
    configuration: AirSkidConfiguration,
    component_type: SkidComponentType,
) -> bool:
    return any(
        component.component_type == component_type and component.quantity > 0
        for component in configuration.components
    )


def _validate_configuration(
    configuration: AirSkidConfiguration,
) -> None:
    if not configuration.skid_code.strip():
        raise InvalidAirSkidInputError("Skid code cannot be empty.")

    if configuration.design_flow_nm3_per_hr <= 0:
        raise InvalidAirSkidInputError("Skid design flow must be greater than zero.")

    if configuration.design_pressure_bar_g <= 0:
        raise InvalidAirSkidInputError("Skid design pressure must be greater than zero.")

    if not configuration.components:
        raise InvalidAirSkidInputError("At least one skid component is required.")

    component_codes: set[str] = set()

    for component in configuration.components:
        if not component.component_code.strip():
            raise InvalidAirSkidInputError("Skid component code cannot be empty.")

        if component.component_code in component_codes:
            raise InvalidAirSkidInputError(
                f"Duplicate skid component code: {component.component_code}."
            )

        component_codes.add(component.component_code)

        if component.quantity <= 0:
            raise InvalidAirSkidInputError("Skid component quantity must be greater than zero.")

        if component.pressure_drop_bar < 0:
            raise InvalidAirSkidInputError("Component pressure drop cannot be negative.")

        if component.rated_flow_nm3_per_hr is not None and component.rated_flow_nm3_per_hr <= 0:
            raise InvalidAirSkidInputError("Component rated flow must be greater than zero.")

        if component.rated_pressure_bar_g is not None and component.rated_pressure_bar_g <= 0:
            raise InvalidAirSkidInputError("Component rated pressure must be greater than zero.")
