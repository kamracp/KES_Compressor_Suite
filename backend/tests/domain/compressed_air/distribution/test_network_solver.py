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
from app.domain.compressed_air.distribution.network_solver import solve_network


def build_network() -> CompressedAirNetwork:
    return CompressedAirNetwork(
        network_code="NET-SOLVE-001",
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
                name="Machine Shop",
                node_type=NetworkNodeType.CONSUMER,
                demand_nm3_per_hr=Decimal("700"),
                minimum_pressure_bar_g=Decimal("6.0"),
            ),
            NetworkNode(
                node_code="C-02",
                name="Packing Area",
                node_type=NetworkNodeType.CONSUMER,
                demand_nm3_per_hr=Decimal("500"),
                minimum_pressure_bar_g=Decimal("6.6"),
            ),
        ),
        segments=(
            PipeSegment(
                segment_code="P-01",
                name="Main Header",
                role=PipeSegmentRole.MAIN_HEADER,
                start_node_code="SRC",
                end_node_code="J-01",
                length_m=Decimal("100"),
                equivalent_fitting_length_m=Decimal("20"),
                internal_diameter_mm=Decimal("125"),
                roughness_mm=Decimal("0.045"),
                design_flow_nm3_per_hr=Decimal("2000"),
                operating_pressure_bar_g=Decimal("6.8"),
                operating_temperature_k=Decimal("303.15"),
            ),
            PipeSegment(
                segment_code="P-02",
                name="Machine Shop Branch",
                role=PipeSegmentRole.BRANCH,
                start_node_code="J-01",
                end_node_code="C-01",
                length_m=Decimal("40"),
                equivalent_fitting_length_m=Decimal("10"),
                internal_diameter_mm=Decimal("80"),
                roughness_mm=Decimal("0.045"),
                design_flow_nm3_per_hr=Decimal("700"),
                operating_pressure_bar_g=Decimal("6.6"),
                operating_temperature_k=Decimal("303.15"),
            ),
            PipeSegment(
                segment_code="P-03",
                name="Packing Area Branch",
                role=PipeSegmentRole.BRANCH,
                start_node_code="J-01",
                end_node_code="C-02",
                length_m=Decimal("120"),
                equivalent_fitting_length_m=Decimal("30"),
                internal_diameter_mm=Decimal("50"),
                roughness_mm=Decimal("0.045"),
                design_flow_nm3_per_hr=Decimal("500"),
                operating_pressure_bar_g=Decimal("6.6"),
                operating_temperature_k=Decimal("303.15"),
            ),
        ),
    )


def build_paths() -> tuple[NetworkPath, ...]:
    return (
        NetworkPath(
            path_code="PATH-C01",
            node_codes=("SRC", "J-01", "C-01"),
            segment_codes=("P-01", "P-02"),
        ),
        NetworkPath(
            path_code="PATH-C02",
            node_codes=("SRC", "J-01", "C-02"),
            segment_codes=("P-01", "P-03"),
        ),
    )


def test_solve_multi_consumer_network() -> None:
    result = solve_network(
        network=build_network(),
        paths=build_paths(),
        air_density_kg_per_m3=Decimal("8.5"),
        darcy_friction_factor=Decimal("0.02"),
    )

    assert result.network_code == "NET-SOLVE-001"
    assert result.total_paths == 2
    assert len(result.path_results) == 2

    assert result.maximum_path_pressure_drop_bar > Decimal("0")
    assert result.minimum_destination_pressure_bar_g < Decimal("6.8")


def test_restricted_consumer_path_is_worst_pressure_path() -> None:
    result = solve_network(
        network=build_network(),
        paths=build_paths(),
        air_density_kg_per_m3=Decimal("8.5"),
        darcy_friction_factor=Decimal("0.02"),
    )

    assert result.worst_pressure_path_code == "PATH-C02"
    assert result.highest_pressure_drop_path_code == "PATH-C02"


def test_pressure_deficient_consumer_is_detected() -> None:
    result = solve_network(
        network=build_network(),
        paths=build_paths(),
        air_density_kg_per_m3=Decimal("8.5"),
        darcy_friction_factor=Decimal("0.02"),
    )

    assert "PATH-C02" in result.pressure_deficient_path_codes
    assert result.deficient_paths >= 1
    assert result.network_pressure_is_adequate is False


def test_network_can_be_adequate_when_consumer_requirements_are_lower() -> None:
    network = build_network()

    relaxed_consumer = NetworkNode(
        node_code="C-02",
        name="Packing Area",
        node_type=NetworkNodeType.CONSUMER,
        demand_nm3_per_hr=Decimal("500"),
        minimum_pressure_bar_g=Decimal("5.5"),
    )

    relaxed_network = CompressedAirNetwork(
        network_code=network.network_code,
        topology=network.topology,
        nodes=(
            network.nodes[0],
            network.nodes[1],
            network.nodes[2],
            relaxed_consumer,
        ),
        segments=network.segments,
        design_source_pressure_bar_g=network.design_source_pressure_bar_g,
    )

    result = solve_network(
        network=relaxed_network,
        paths=build_paths(),
        air_density_kg_per_m3=Decimal("8.5"),
        darcy_friction_factor=Decimal("0.02"),
    )

    assert result.deficient_paths == 0
    assert result.network_pressure_is_adequate is True


def test_duplicate_path_codes_are_rejected() -> None:
    paths = (
        NetworkPath(
            path_code="DUPLICATE",
            node_codes=("SRC", "J-01", "C-01"),
            segment_codes=("P-01", "P-02"),
        ),
        NetworkPath(
            path_code="DUPLICATE",
            node_codes=("SRC", "J-01", "C-02"),
            segment_codes=("P-01", "P-03"),
        ),
    )

    try:
        solve_network(
            network=build_network(),
            paths=paths,
            air_density_kg_per_m3=Decimal("8.5"),
            darcy_friction_factor=Decimal("0.02"),
        )
    except ValueError as exc:
        assert "Network path codes must be unique" in str(exc)
    else:
        raise AssertionError("Expected duplicate path code validation error.")


def test_empty_path_collection_is_rejected() -> None:
    try:
        solve_network(
            network=build_network(),
            paths=(),
            air_density_kg_per_m3=Decimal("8.5"),
            darcy_friction_factor=Decimal("0.02"),
        )
    except ValueError as exc:
        assert "At least one network path is required" in str(exc)
    else:
        raise AssertionError("Expected empty path validation error.")
