from dataclasses import dataclass
from decimal import Decimal


class InvalidDemandProfileInputError(ValueError):
    """Raised when compressed-air demand profile inputs are invalid."""


@dataclass(frozen=True, slots=True)
class DemandProfilePoint:
    """One compressed-air demand point in a time profile."""

    period_index: int
    label: str

    demand_nm3_per_hr: Decimal
    required_pressure_bar_g: Decimal

    duration_hours: Decimal


@dataclass(frozen=True, slots=True)
class DemandProfileResult:
    """Calculated compressed-air demand profile summary."""

    points: tuple[DemandProfilePoint, ...]

    minimum_demand_nm3_per_hr: Decimal
    average_demand_nm3_per_hr: Decimal
    maximum_demand_nm3_per_hr: Decimal

    peak_to_average_ratio: Decimal

    total_profile_hours: Decimal
    total_air_volume_nm3: Decimal

    minimum_required_pressure_bar_g: Decimal
    maximum_required_pressure_bar_g: Decimal


def calculate_demand_profile(
    points: tuple[DemandProfilePoint, ...],
) -> DemandProfileResult:
    """Calculate weighted compressed-air demand profile statistics."""

    if not points:
        raise InvalidDemandProfileInputError("At least one demand profile point is required.")

    for point in points:
        _validate_point(point)

    total_profile_hours = sum(
        (point.duration_hours for point in points),
        start=Decimal("0"),
    )

    if total_profile_hours <= 0:
        raise InvalidDemandProfileInputError("Total profile duration must be greater than zero.")

    total_air_volume_nm3 = sum(
        (point.demand_nm3_per_hr * point.duration_hours for point in points),
        start=Decimal("0"),
    )

    average_demand_nm3_per_hr = total_air_volume_nm3 / total_profile_hours

    minimum_demand_nm3_per_hr = min(point.demand_nm3_per_hr for point in points)

    maximum_demand_nm3_per_hr = max(point.demand_nm3_per_hr for point in points)

    peak_to_average_ratio = (
        maximum_demand_nm3_per_hr / average_demand_nm3_per_hr
        if average_demand_nm3_per_hr > 0
        else Decimal("0")
    )

    minimum_required_pressure_bar_g = min(point.required_pressure_bar_g for point in points)

    maximum_required_pressure_bar_g = max(point.required_pressure_bar_g for point in points)

    return DemandProfileResult(
        points=points,
        minimum_demand_nm3_per_hr=minimum_demand_nm3_per_hr,
        average_demand_nm3_per_hr=average_demand_nm3_per_hr,
        maximum_demand_nm3_per_hr=maximum_demand_nm3_per_hr,
        peak_to_average_ratio=peak_to_average_ratio,
        total_profile_hours=total_profile_hours,
        total_air_volume_nm3=total_air_volume_nm3,
        minimum_required_pressure_bar_g=minimum_required_pressure_bar_g,
        maximum_required_pressure_bar_g=maximum_required_pressure_bar_g,
    )


def _validate_point(
    point: DemandProfilePoint,
) -> None:
    if point.period_index < 0:
        raise InvalidDemandProfileInputError("Profile period index cannot be negative.")

    if not point.label.strip():
        raise InvalidDemandProfileInputError("Profile point label cannot be empty.")

    if point.demand_nm3_per_hr < 0:
        raise InvalidDemandProfileInputError("Demand cannot be negative.")

    if point.required_pressure_bar_g < 0:
        raise InvalidDemandProfileInputError("Required pressure cannot be negative.")

    if point.duration_hours <= 0:
        raise InvalidDemandProfileInputError("Profile point duration must be greater than zero.")
