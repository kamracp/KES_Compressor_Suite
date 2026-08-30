from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from app.domain.compressed_air.distribution.network_models import (
    CompressedAirNetwork,
)
from app.domain.compressed_air.distribution.network_solver import (
    NetworkHydraulicResult,
)
from app.domain.compressed_air.distribution.pipe_sizing import (
    VELOCITY_RECOMMENDED_LIMIT_M_PER_S,
    PipeSizingInput,
)
from app.domain.compressed_air.distribution.pressure_drop import (
    PressureDropInput,
    calculate_pressure_drop,
)


class InvalidNetworkOptimizationInputError(ValueError):
    """Raised when compressed-air network optimization inputs are invalid."""


class OptimizationRecommendationStatus(StrEnum):
    """Status of one distribution optimization recommendation."""

    RECOMMENDED = "RECOMMENDED"
    REVIEW = "REVIEW"
    NO_CHANGE_REQUIRED = "NO_CHANGE_REQUIRED"


@dataclass(frozen=True, slots=True)
class SegmentOptimizationRecommendation:
    """Optimization recommendation for one compressed-air pipe segment."""

    segment_code: str
    segment_name: str

    affected_deficient_paths: tuple[str, ...]

    current_internal_diameter_mm: Decimal
    recommended_internal_diameter_mm: Decimal

    current_velocity_m_per_s: Decimal
    recommended_velocity_m_per_s: Decimal

    current_pressure_drop_bar: Decimal
    recommended_pressure_drop_bar: Decimal

    pressure_drop_reduction_bar: Decimal
    pressure_drop_reduction_fraction: Decimal

    recommendation_status: OptimizationRecommendationStatus
    rationale: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class NetworkOptimizationResult:
    """Distribution optimization assessment for a compressed-air network."""

    network_code: str

    deficient_path_codes: tuple[str, ...]

    recommendations: tuple[SegmentOptimizationRecommendation, ...]

    total_current_target_segment_drop_bar: Decimal
    total_recommended_target_segment_drop_bar: Decimal
    estimated_total_pressure_drop_reduction_bar: Decimal

    optimization_required: bool


def optimize_distribution_network(
    *,
    network: CompressedAirNetwork,
    hydraulic_result: NetworkHydraulicResult,
    candidate_internal_diameters_mm: tuple[Decimal, ...],
    air_density_kg_per_m3: Decimal,
    darcy_friction_factor: Decimal,
    # Default calibrated to CAGI (<= 20 ft/s ~ 6 m/s) and BCAS (6-7 m/s
    # design, never above 9 m/s) guidance -- see standards registry entries
    # CAGI-CAGH and BCAS-BPG-101.
    maximum_preferred_velocity_m_per_s: Decimal = VELOCITY_RECOMMENDED_LIMIT_M_PER_S,
    minimum_pressure_drop_reduction_fraction: Decimal = Decimal("0.20"),
) -> NetworkOptimizationResult:
    """Recommend pipe-diameter improvements for deficient network paths."""

    _validate_inputs(
        candidate_internal_diameters_mm=candidate_internal_diameters_mm,
        air_density_kg_per_m3=air_density_kg_per_m3,
        darcy_friction_factor=darcy_friction_factor,
        maximum_preferred_velocity_m_per_s=maximum_preferred_velocity_m_per_s,
        minimum_pressure_drop_reduction_fraction=(minimum_pressure_drop_reduction_fraction),
    )

    deficient_path_codes = hydraulic_result.pressure_deficient_path_codes

    if not deficient_path_codes:
        return NetworkOptimizationResult(
            network_code=network.network_code,
            deficient_path_codes=(),
            recommendations=(),
            total_current_target_segment_drop_bar=Decimal("0"),
            total_recommended_target_segment_drop_bar=Decimal("0"),
            estimated_total_pressure_drop_reduction_bar=Decimal("0"),
            optimization_required=False,
        )

    deficient_path_lookup = {
        result.path_code: result
        for result in hydraulic_result.path_results
        if result.path_code in deficient_path_codes
    }

    segment_to_paths: dict[str, list[str]] = {}

    for path_code, path_result in deficient_path_lookup.items():
        for segment_result in path_result.segment_results:
            segment_to_paths.setdefault(
                segment_result.segment_code,
                [],
            ).append(path_code)

    segment_lookup = {segment.segment_code: segment for segment in network.segments}

    recommendations: list[SegmentOptimizationRecommendation] = []

    for segment_code, affected_paths in segment_to_paths.items():
        segment = segment_lookup.get(segment_code)

        if segment is None:
            raise InvalidNetworkOptimizationInputError(
                f"Hydraulic result references unknown segment '{segment_code}'."
            )

        recommendation = _optimize_segment(
            segment=segment,
            affected_paths=tuple(sorted(set(affected_paths))),
            candidate_internal_diameters_mm=candidate_internal_diameters_mm,
            air_density_kg_per_m3=air_density_kg_per_m3,
            darcy_friction_factor=darcy_friction_factor,
            maximum_preferred_velocity_m_per_s=(maximum_preferred_velocity_m_per_s),
            minimum_pressure_drop_reduction_fraction=(minimum_pressure_drop_reduction_fraction),
        )

        recommendations.append(recommendation)

    recommendations.sort(
        key=lambda item: (
            item.pressure_drop_reduction_bar,
            item.current_pressure_drop_bar,
        ),
        reverse=True,
    )

    total_current_drop = sum(
        (item.current_pressure_drop_bar for item in recommendations),
        start=Decimal("0"),
    )

    total_recommended_drop = sum(
        (item.recommended_pressure_drop_bar for item in recommendations),
        start=Decimal("0"),
    )

    estimated_reduction = total_current_drop - total_recommended_drop

    return NetworkOptimizationResult(
        network_code=network.network_code,
        deficient_path_codes=deficient_path_codes,
        recommendations=tuple(recommendations),
        total_current_target_segment_drop_bar=total_current_drop,
        total_recommended_target_segment_drop_bar=total_recommended_drop,
        estimated_total_pressure_drop_reduction_bar=estimated_reduction,
        optimization_required=True,
    )


def _optimize_segment(
    *,
    segment,
    affected_paths: tuple[str, ...],
    candidate_internal_diameters_mm: tuple[Decimal, ...],
    air_density_kg_per_m3: Decimal,
    darcy_friction_factor: Decimal,
    maximum_preferred_velocity_m_per_s: Decimal,
    minimum_pressure_drop_reduction_fraction: Decimal,
) -> SegmentOptimizationRecommendation:
    current_result = _calculate_segment_case(
        segment=segment,
        diameter_mm=segment.internal_diameter_mm,
        air_density_kg_per_m3=air_density_kg_per_m3,
        darcy_friction_factor=darcy_friction_factor,
    )

    larger_candidates = tuple(
        sorted(
            diameter
            for diameter in candidate_internal_diameters_mm
            if diameter > segment.internal_diameter_mm
        )
    )

    selected_result = current_result
    selected_diameter = segment.internal_diameter_mm
    status = OptimizationRecommendationStatus.REVIEW

    for candidate_diameter in larger_candidates:
        candidate_result = _calculate_segment_case(
            segment=segment,
            diameter_mm=candidate_diameter,
            air_density_kg_per_m3=air_density_kg_per_m3,
            darcy_friction_factor=darcy_friction_factor,
        )

        reduction_fraction = _pressure_drop_reduction_fraction(
            current_pressure_drop_bar=current_result.pressure_drop_bar,
            candidate_pressure_drop_bar=candidate_result.pressure_drop_bar,
        )

        if (
            candidate_result.pipe_result.air_velocity_m_per_s <= maximum_preferred_velocity_m_per_s
            and reduction_fraction >= minimum_pressure_drop_reduction_fraction
        ):
            selected_result = candidate_result
            selected_diameter = candidate_diameter
            status = OptimizationRecommendationStatus.RECOMMENDED
            break

    if status != OptimizationRecommendationStatus.RECOMMENDED and larger_candidates:
        selected_diameter = larger_candidates[-1]

        selected_result = _calculate_segment_case(
            segment=segment,
            diameter_mm=selected_diameter,
            air_density_kg_per_m3=air_density_kg_per_m3,
            darcy_friction_factor=darcy_friction_factor,
        )

    reduction_bar = current_result.pressure_drop_bar - selected_result.pressure_drop_bar

    reduction_fraction = _pressure_drop_reduction_fraction(
        current_pressure_drop_bar=current_result.pressure_drop_bar,
        candidate_pressure_drop_bar=selected_result.pressure_drop_bar,
    )

    rationale = _build_rationale(
        current_velocity=current_result.pipe_result.air_velocity_m_per_s,
        recommended_velocity=(selected_result.pipe_result.air_velocity_m_per_s),
        maximum_preferred_velocity=maximum_preferred_velocity_m_per_s,
        reduction_fraction=reduction_fraction,
        minimum_reduction_fraction=minimum_pressure_drop_reduction_fraction,
        affected_paths=affected_paths,
        diameter_changed=(selected_diameter != segment.internal_diameter_mm),
    )

    return SegmentOptimizationRecommendation(
        segment_code=segment.segment_code,
        segment_name=segment.name,
        affected_deficient_paths=affected_paths,
        current_internal_diameter_mm=segment.internal_diameter_mm,
        recommended_internal_diameter_mm=selected_diameter,
        current_velocity_m_per_s=(current_result.pipe_result.air_velocity_m_per_s),
        recommended_velocity_m_per_s=(selected_result.pipe_result.air_velocity_m_per_s),
        current_pressure_drop_bar=current_result.pressure_drop_bar,
        recommended_pressure_drop_bar=selected_result.pressure_drop_bar,
        pressure_drop_reduction_bar=reduction_bar,
        pressure_drop_reduction_fraction=reduction_fraction,
        recommendation_status=status,
        rationale=rationale,
    )


def _calculate_segment_case(
    *,
    segment,
    diameter_mm: Decimal,
    air_density_kg_per_m3: Decimal,
    darcy_friction_factor: Decimal,
):
    return calculate_pressure_drop(
        PressureDropInput(
            pipe=PipeSizingInput(
                normal_flow_nm3_per_hr=segment.design_flow_nm3_per_hr,
                operating_pressure_bar_g=segment.operating_pressure_bar_g,
                operating_temperature_k=segment.operating_temperature_k,
                pipe_internal_diameter_mm=diameter_mm,
            ),
            straight_length_m=segment.length_m,
            equivalent_fitting_length_m=(segment.equivalent_fitting_length_m),
            air_density_kg_per_m3=air_density_kg_per_m3,
            darcy_friction_factor=darcy_friction_factor,
        )
    )


def _pressure_drop_reduction_fraction(
    *,
    current_pressure_drop_bar: Decimal,
    candidate_pressure_drop_bar: Decimal,
) -> Decimal:
    if current_pressure_drop_bar <= 0:
        return Decimal("0")

    return (current_pressure_drop_bar - candidate_pressure_drop_bar) / current_pressure_drop_bar


def _build_rationale(
    *,
    current_velocity: Decimal,
    recommended_velocity: Decimal,
    maximum_preferred_velocity: Decimal,
    reduction_fraction: Decimal,
    minimum_reduction_fraction: Decimal,
    affected_paths: tuple[str, ...],
    diameter_changed: bool,
) -> tuple[str, ...]:
    rationale: list[str] = []

    rationale.append("Segment is part of one or more pressure-deficient consumer paths.")

    rationale.append("Affected paths: " + ", ".join(affected_paths) + ".")

    if current_velocity > maximum_preferred_velocity:
        rationale.append("Current air velocity exceeds the configured preferred limit.")

    if diameter_changed:
        rationale.append("Increasing internal diameter reduces air velocity and friction loss.")

    if recommended_velocity <= maximum_preferred_velocity:
        rationale.append(
            "Recommended diameter brings velocity within the configured preferred limit."
        )

    if reduction_fraction >= minimum_reduction_fraction:
        rationale.append(
            "Recommended change achieves the configured minimum pressure-drop reduction."
        )
    else:
        rationale.append("Available diameter options require further engineering review.")

    return tuple(rationale)


def _validate_inputs(
    *,
    candidate_internal_diameters_mm: tuple[Decimal, ...],
    air_density_kg_per_m3: Decimal,
    darcy_friction_factor: Decimal,
    maximum_preferred_velocity_m_per_s: Decimal,
    minimum_pressure_drop_reduction_fraction: Decimal,
) -> None:
    if not candidate_internal_diameters_mm:
        raise InvalidNetworkOptimizationInputError(
            "At least one candidate pipe diameter is required."
        )

    if any(diameter <= 0 for diameter in candidate_internal_diameters_mm):
        raise InvalidNetworkOptimizationInputError(
            "Candidate pipe diameters must be greater than zero."
        )

    if air_density_kg_per_m3 <= 0:
        raise InvalidNetworkOptimizationInputError("Air density must be greater than zero.")

    if darcy_friction_factor <= 0 or darcy_friction_factor >= 1:
        raise InvalidNetworkOptimizationInputError(
            "Darcy friction factor must be greater than zero and less than one."
        )

    if maximum_preferred_velocity_m_per_s <= 0:
        raise InvalidNetworkOptimizationInputError(
            "Maximum preferred velocity must be greater than zero."
        )

    if minimum_pressure_drop_reduction_fraction < 0 or minimum_pressure_drop_reduction_fraction > 1:
        raise InvalidNetworkOptimizationInputError(
            "Minimum pressure-drop reduction fraction must be between zero and one."
        )
