from dataclasses import dataclass
from decimal import Decimal


class InvalidPerformanceMapInputError(ValueError):
    """Raised when centrifugal performance-map inputs are invalid."""


@dataclass(frozen=True, slots=True)
class PerformanceMapPoint:
    """Represents one centrifugal compressor speed-line point."""

    speed_fraction: Decimal
    speed_rpm: Decimal
    flow_m3_per_hr: Decimal
    head_kj_per_kg: Decimal


@dataclass(frozen=True, slots=True)
class PerformanceMapResult:
    """Centrifugal compressor performance-map scaling result."""

    design_speed_rpm: Decimal
    design_flow_m3_per_hr: Decimal
    design_head_kj_per_kg: Decimal
    points: tuple[PerformanceMapPoint, ...]


def calculate_performance_map(
    design_speed_rpm: Decimal,
    design_flow_m3_per_hr: Decimal,
    design_head_kj_per_kg: Decimal,
    speed_fractions: tuple[Decimal, ...] = (
        Decimal("1.00"),
        Decimal("0.90"),
        Decimal("0.80"),
    ),
) -> PerformanceMapResult:
    """Calculate centrifugal compressor speed-line points using affinity laws."""

    if design_speed_rpm <= 0:
        raise InvalidPerformanceMapInputError("Design speed must be greater than zero.")

    if design_flow_m3_per_hr <= 0:
        raise InvalidPerformanceMapInputError("Design flow must be greater than zero.")

    if design_head_kj_per_kg <= 0:
        raise InvalidPerformanceMapInputError("Design head must be greater than zero.")

    if not speed_fractions:
        raise InvalidPerformanceMapInputError("At least one speed fraction must be provided.")

    points: list[PerformanceMapPoint] = []

    for speed_fraction in speed_fractions:
        if speed_fraction <= 0:
            raise InvalidPerformanceMapInputError("Speed fractions must be greater than zero.")

        speed_rpm = design_speed_rpm * speed_fraction
        flow_m3_per_hr = design_flow_m3_per_hr * speed_fraction
        head_kj_per_kg = design_head_kj_per_kg * speed_fraction * speed_fraction

        points.append(
            PerformanceMapPoint(
                speed_fraction=speed_fraction,
                speed_rpm=speed_rpm,
                flow_m3_per_hr=flow_m3_per_hr,
                head_kj_per_kg=head_kj_per_kg,
            )
        )

    return PerformanceMapResult(
        design_speed_rpm=design_speed_rpm,
        design_flow_m3_per_hr=design_flow_m3_per_hr,
        design_head_kj_per_kg=design_head_kj_per_kg,
        points=tuple(points),
    )
