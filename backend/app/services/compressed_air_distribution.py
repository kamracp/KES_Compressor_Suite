from dataclasses import dataclass

from app.domain.compressed_air.distribution.network_models import (
    CompressedAirNetwork,
    NetworkNode,
    NetworkPath,
    NetworkValidationResult,
    PipeSegment,
)
from app.domain.compressed_air.distribution.network_optimizer import (
    NetworkOptimizationResult,
    optimize_distribution_network,
)
from app.domain.compressed_air.distribution.network_solver import (
    NetworkHydraulicResult,
    solve_network,
)
from app.domain.compressed_air.distribution.network_validation import (
    InvalidCompressedAirNetworkError,
    validate_network,
)
from app.schemas.compressed_air_distribution import (
    DistributionNetworkCalculationRequest,
)


def build_network(
    payload: DistributionNetworkCalculationRequest,
) -> CompressedAirNetwork:
    """Convert a validated request payload into the domain network model."""

    nodes = tuple(
        NetworkNode(
            node_code=node.node_code,
            name=node.name,
            node_type=node.node_type,
            elevation_m=node.elevation_m,
            demand_nm3_per_hr=node.demand_nm3_per_hr,
            minimum_pressure_bar_g=node.minimum_pressure_bar_g,
            area=node.area,
            notes=node.notes,
        )
        for node in payload.nodes
    )

    segments = tuple(
        PipeSegment(
            segment_code=segment.segment_code,
            name=segment.name,
            role=segment.role,
            start_node_code=segment.start_node_code,
            end_node_code=segment.end_node_code,
            length_m=segment.length_m,
            equivalent_fitting_length_m=segment.equivalent_fitting_length_m,
            internal_diameter_mm=segment.internal_diameter_mm,
            roughness_mm=segment.roughness_mm,
            design_flow_nm3_per_hr=segment.design_flow_nm3_per_hr,
            operating_pressure_bar_g=segment.operating_pressure_bar_g,
            operating_temperature_k=segment.operating_temperature_k,
            material=segment.material,
            notes=segment.notes,
        )
        for segment in payload.segments
    )

    return CompressedAirNetwork(
        network_code=payload.network_code,
        topology=payload.topology,
        nodes=nodes,
        segments=segments,
        design_source_pressure_bar_g=payload.design_source_pressure_bar_g,
        description=payload.description,
    )


def build_paths(
    payload: DistributionNetworkCalculationRequest,
) -> tuple[NetworkPath, ...]:
    """Convert request path payloads into domain network paths."""

    return tuple(
        NetworkPath(
            path_code=path.path_code,
            node_codes=tuple(path.node_codes),
            segment_codes=tuple(path.segment_codes),
        )
        for path in payload.paths
    )


@dataclass(frozen=True, slots=True)
class DistributionNetworkAnalysisResult:
    """Combined distribution network analysis result."""

    validation: NetworkValidationResult
    hydraulics: NetworkHydraulicResult
    optimization: NetworkOptimizationResult | None


class CompressedAirDistributionService:
    """Orchestrate distribution network validation, solving and optimization."""

    def calculate(
        self,
        payload: DistributionNetworkCalculationRequest,
    ) -> DistributionNetworkAnalysisResult:
        network = build_network(payload)

        validation = validate_network(network)

        if not validation.is_structurally_valid:
            raise InvalidCompressedAirNetworkError(
                "Network is not structurally valid: "
                f"duplicate nodes {list(validation.duplicate_node_codes)}, "
                f"duplicate segments {list(validation.duplicate_segment_codes)}, "
                f"orphan segments {list(validation.orphan_segment_codes)}, "
                f"source nodes {validation.source_node_count}, "
                f"consumer nodes {validation.consumer_node_count}."
            )

        paths = build_paths(payload)

        hydraulics = solve_network(
            network=network,
            paths=paths,
            air_density_kg_per_m3=payload.air_density_kg_per_m3,
            darcy_friction_factor=payload.darcy_friction_factor,
        )

        optimization: NetworkOptimizationResult | None = None

        if payload.candidate_internal_diameters_mm is not None:
            optimization = optimize_distribution_network(
                network=network,
                hydraulic_result=hydraulics,
                candidate_internal_diameters_mm=tuple(payload.candidate_internal_diameters_mm),
                air_density_kg_per_m3=payload.air_density_kg_per_m3,
                darcy_friction_factor=payload.darcy_friction_factor,
                maximum_preferred_velocity_m_per_s=(payload.maximum_preferred_velocity_m_per_s),
                minimum_pressure_drop_reduction_fraction=(
                    payload.minimum_pressure_drop_reduction_fraction
                ),
            )

        return DistributionNetworkAnalysisResult(
            validation=validation,
            hydraulics=hydraulics,
            optimization=optimization,
        )


compressed_air_distribution_service = CompressedAirDistributionService()
