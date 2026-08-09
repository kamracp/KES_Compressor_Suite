from decimal import Decimal

from app.domain.compressed_air.distribution.network_models import (
    CompressedAirNetwork,
    NetworkNode,
    NetworkNodeType,
    NetworkPath,
    NetworkTopology,
    PipeSegment,
    PipeSegmentRole,
)
from app.domain.compressed_air.distribution.network_optimizer import (
    OptimizationRecommendationStatus,
    optimize_distribution_network,
)
from app.domain.compressed_air.distribution.network_solver import solve_network


def build_network() -> CompressedAirNetwork:
    return CompressedAirNetwork(
        network_code="NET-OPT-001",
        topology=NetworkTopology.BRANCHED,
        design_source_pressure_bar_g=Decimal("6.8"),
        nodes=(
            NetworkNode(
                node_code="SRC",
                name="Compressor Station",
                node_type=NetworkNodeType.COMPRESSOR_STATION,
            ),
            NetworkNode(
                node_code="J-01",
                name="Main Header Junction",
                node_type=NetworkNodeType.HEADER_JUNCTION,
            ),
            NetworkNode(
                node_code="C-01",
                name="Restricted Consumer",
                node_type=NetworkNodeType.CONSUMER,
                demand_nm3_per_hr=Decimal("1000"),
                minimum_pressure_bar_g=Decimal("6.65"),
            ),
        ),
        segments=(
            PipeSegment(
                segment_code="P-01",
                name="Main Header",
                role=PipeSegmentRole.MAIN_HEADER,
                start_node_code="SRC",
                end_node_code="J-01",
                length_m=Decimal("80"),
                equivalent_fitting_length_m=Decimal("15"),
                internal_diameter_mm=Decimal("125"),
                roughness_mm=Decimal("0.045"),
                design_flow_nm3_per_hr=Decimal("1800"),
                operating_pressure_bar_g=Decimal("6.8"),
                operating_temperature_k=Decimal("303.15"),
            ),
            PipeSegment(
                segment_code="P-02",
                name="Restricted Branch",
                role=PipeSegmentRole.BRANCH,
                start_node_code="J-01",
                end_node_code="C-01",
                length_m=Decimal("120"),
                equivalent_fitting_length_m=Decimal("30"),
                internal_diameter_mm=Decimal("50"),
                roughness_mm=Decimal("0.045"),
                design_flow_nm3_per_hr=Decimal("1000"),
                operating_pressure_bar_g=Decimal("6.6"),
                operating_temperature_k=Decimal("303.15"),
            ),
        ),
    )


def build_path() -> NetworkPath:
    return NetworkPath(
        path_code="PATH-C01",
        node_codes=("SRC", "J-01", "C-01"),
        segment_codes=("P-01", "P-02"),
    )


def test_optimizer_recommends_larger_diameter_for_restricted_branch() -> None:
    network = build_network()

    hydraulic_result = solve_network(
        network=network,
        paths=(build_path(),),
        air_density_kg_per_m3=Decimal("8.5"),
        darcy_friction_factor=Decimal("0.02"),
    )

    assert hydraulic_result.network_pressure_is_adequate is False

    result = optimize_distribution_network(
        network=network,
        hydraulic_result=hydraulic_result,
        candidate_internal_diameters_mm=(
            Decimal("50"),
            Decimal("65"),
            Decimal("80"),
            Decimal("100"),
            Decimal("125"),
            Decimal("150"),
        ),
        air_density_kg_per_m3=Decimal("8.5"),
        darcy_friction_factor=Decimal("0.02"),
        maximum_preferred_velocity_m_per_s=Decimal("10"),
        minimum_pressure_drop_reduction_fraction=Decimal("0.20"),
    )

    assert result.optimization_required is True
    assert result.deficient_path_codes == ("PATH-C01",)
    assert len(result.recommendations) >= 1

    recommendations = {item.segment_code: item for item in result.recommendations}

    branch = recommendations["P-02"]

    assert branch.recommended_internal_diameter_mm > branch.current_internal_diameter_mm

    assert branch.recommended_velocity_m_per_s < branch.current_velocity_m_per_s

    assert branch.recommended_pressure_drop_bar < branch.current_pressure_drop_bar

    assert branch.pressure_drop_reduction_bar > Decimal("0")

    assert branch.recommendation_status in {
        OptimizationRecommendationStatus.RECOMMENDED,
        OptimizationRecommendationStatus.REVIEW,
    }


def test_optimizer_estimates_total_pressure_drop_reduction() -> None:
    network = build_network()

    hydraulic_result = solve_network(
        network=network,
        paths=(build_path(),),
        air_density_kg_per_m3=Decimal("8.5"),
        darcy_friction_factor=Decimal("0.02"),
    )

    result = optimize_distribution_network(
        network=network,
        hydraulic_result=hydraulic_result,
        candidate_internal_diameters_mm=(
            Decimal("50"),
            Decimal("65"),
            Decimal("80"),
            Decimal("100"),
            Decimal("125"),
        ),
        air_density_kg_per_m3=Decimal("8.5"),
        darcy_friction_factor=Decimal("0.02"),
    )

    assert result.total_current_target_segment_drop_bar > Decimal("0")

    assert (
        result.total_recommended_target_segment_drop_bar
        < result.total_current_target_segment_drop_bar
    )

    assert result.estimated_total_pressure_drop_reduction_bar > Decimal("0")


def test_healthy_network_requires_no_distribution_optimization() -> None:
    network = build_network()

    relaxed_consumer = NetworkNode(
        node_code="C-01",
        name="Relaxed Consumer",
        node_type=NetworkNodeType.CONSUMER,
        demand_nm3_per_hr=Decimal("1000"),
        minimum_pressure_bar_g=Decimal("5.5"),
    )

    healthy_network = CompressedAirNetwork(
        network_code=network.network_code,
        topology=network.topology,
        nodes=(
            network.nodes[0],
            network.nodes[1],
            relaxed_consumer,
        ),
        segments=network.segments,
        design_source_pressure_bar_g=network.design_source_pressure_bar_g,
    )

    hydraulic_result = solve_network(
        network=healthy_network,
        paths=(build_path(),),
        air_density_kg_per_m3=Decimal("8.5"),
        darcy_friction_factor=Decimal("0.02"),
    )

    assert hydraulic_result.network_pressure_is_adequate is True

    result = optimize_distribution_network(
        network=healthy_network,
        hydraulic_result=hydraulic_result,
        candidate_internal_diameters_mm=(
            Decimal("50"),
            Decimal("65"),
            Decimal("80"),
            Decimal("100"),
        ),
        air_density_kg_per_m3=Decimal("8.5"),
        darcy_friction_factor=Decimal("0.02"),
    )

    assert result.optimization_required is False
    assert result.deficient_path_codes == ()
    assert result.recommendations == ()
    assert result.estimated_total_pressure_drop_reduction_bar == Decimal("0")


def test_optimizer_prefers_smallest_suitable_upgrade() -> None:
    network = build_network()

    hydraulic_result = solve_network(
        network=network,
        paths=(build_path(),),
        air_density_kg_per_m3=Decimal("8.5"),
        darcy_friction_factor=Decimal("0.02"),
    )

    result = optimize_distribution_network(
        network=network,
        hydraulic_result=hydraulic_result,
        candidate_internal_diameters_mm=(
            Decimal("50"),
            Decimal("65"),
            Decimal("80"),
            Decimal("100"),
            Decimal("125"),
            Decimal("150"),
        ),
        air_density_kg_per_m3=Decimal("8.5"),
        darcy_friction_factor=Decimal("0.02"),
        maximum_preferred_velocity_m_per_s=Decimal("10"),
        minimum_pressure_drop_reduction_fraction=Decimal("0.20"),
    )

    branch = next(item for item in result.recommendations if item.segment_code == "P-02")

    assert branch.recommended_internal_diameter_mm in {
        Decimal("65"),
        Decimal("80"),
        Decimal("100"),
        Decimal("125"),
        Decimal("150"),
    }

    assert branch.recommended_internal_diameter_mm != Decimal("50")


def test_affected_deficient_path_is_recorded() -> None:
    network = build_network()

    hydraulic_result = solve_network(
        network=network,
        paths=(build_path(),),
        air_density_kg_per_m3=Decimal("8.5"),
        darcy_friction_factor=Decimal("0.02"),
    )

    result = optimize_distribution_network(
        network=network,
        hydraulic_result=hydraulic_result,
        candidate_internal_diameters_mm=(
            Decimal("50"),
            Decimal("65"),
            Decimal("80"),
            Decimal("100"),
        ),
        air_density_kg_per_m3=Decimal("8.5"),
        darcy_friction_factor=Decimal("0.02"),
    )

    branch = next(item for item in result.recommendations if item.segment_code == "P-02")

    assert branch.affected_deficient_paths == ("PATH-C01",)
    assert len(branch.rationale) > 0
