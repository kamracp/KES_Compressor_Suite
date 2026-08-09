from dataclasses import dataclass
from decimal import Decimal


class InvalidSurgeInputError(ValueError):
    """Raised when centrifugal surge-control inputs are invalid."""


@dataclass(frozen=True, slots=True)
class SurgeControlResult:
    """Centrifugal compressor surge-control and operating-envelope result."""

    design_flow_m3_per_hr: Decimal
    surge_flow_m3_per_hr: Decimal
    anti_surge_setpoint_m3_per_hr: Decimal
    surge_margin_fraction: Decimal
    stonewall_flow_m3_per_hr: Decimal
    operating_range_m3_per_hr: Decimal
    design_point_is_within_envelope: bool


def calculate_surge_control(
    design_flow_m3_per_hr: Decimal,
    surge_flow_fraction: Decimal = Decimal("0.70"),
    anti_surge_margin_fraction: Decimal = Decimal("0.10"),
    stonewall_flow_fraction: Decimal = Decimal("1.25"),
) -> SurgeControlResult:
    """Calculate centrifugal compressor surge and stonewall operating limits."""

    if design_flow_m3_per_hr <= 0:
        raise InvalidSurgeInputError("Design flow must be greater than zero.")

    if surge_flow_fraction <= 0 or surge_flow_fraction >= 1:
        raise InvalidSurgeInputError(
            "Surge flow fraction must be greater than zero and less than one."
        )

    if anti_surge_margin_fraction < 0:
        raise InvalidSurgeInputError("Anti-surge margin fraction cannot be negative.")

    if stonewall_flow_fraction <= 1:
        raise InvalidSurgeInputError("Stonewall flow fraction must be greater than one.")

    surge_flow_m3_per_hr = design_flow_m3_per_hr * surge_flow_fraction

    anti_surge_setpoint_m3_per_hr = surge_flow_m3_per_hr * (
        Decimal("1") + anti_surge_margin_fraction
    )

    surge_margin_fraction = (design_flow_m3_per_hr - surge_flow_m3_per_hr) / design_flow_m3_per_hr

    stonewall_flow_m3_per_hr = design_flow_m3_per_hr * stonewall_flow_fraction

    operating_range_m3_per_hr = stonewall_flow_m3_per_hr - surge_flow_m3_per_hr

    design_point_is_within_envelope = (
        surge_flow_m3_per_hr < design_flow_m3_per_hr < stonewall_flow_m3_per_hr
    )

    return SurgeControlResult(
        design_flow_m3_per_hr=design_flow_m3_per_hr,
        surge_flow_m3_per_hr=surge_flow_m3_per_hr,
        anti_surge_setpoint_m3_per_hr=anti_surge_setpoint_m3_per_hr,
        surge_margin_fraction=surge_margin_fraction,
        stonewall_flow_m3_per_hr=stonewall_flow_m3_per_hr,
        operating_range_m3_per_hr=operating_range_m3_per_hr,
        design_point_is_within_envelope=design_point_is_within_envelope,
    )
