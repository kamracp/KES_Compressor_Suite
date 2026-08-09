from decimal import Decimal

import pytest

from app.domain.compressed_air.distribution.network_models import (
    CompressedAirNetwork,
    NetworkNode,
    NetworkNodeType,
    NetworkPath,
    NetworkTopology,
    PipeSegment,
    PipeSegmentRole,
)
from app.domain.compressed_air.distribution.path_solver import (
    InvalidNetworkPathError,
    solve_network_path,
)


def build_network() -> CompressedAirNetwork:
    return CompressedAirNetwork(
        network_code="NET-PATH-001",
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
                name="Critical Consumer",
                node_type=NetworkNodeType.CONSUMER,
                demand_nm3_per_hr=Decimal("800"),
                minimum_pressure_bar_g=Decimal("6.0"),
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
                name="Consumer Branch",
                role=PipeSegmentRole.BRANCH,
                start_node_code="J-01",
                end_node_code="C-01",
                length_m=Decimal("60"),
                equivalent_fitting_length_m=Decimal("15"),
                internal_diameter_mm=Decimal("80"),
                roughness_mm=Decimal("0.045"),
                design_flow_nm3_per_hr=Decimal("800"),
                operating_pressure_bar_g=Decimal("6.6"),
                operating_temperature_k=Decimal("303.15"),
            ),
        ),
    )


def test_solve_network_path() -> None:
    network = build_network()

    path = NetworkPath(
        path_code="PATH-001",
        node_codes=(
            "SRC",
            "J-01",
            "C-01",
        ),
        segment_codes=(
            "P-01",
            "P-02",
        ),
    )

    result = solve_network_path(
        network=network,
        path=path,
        air_density_kg_per_m3=Decimal("8.5"),
        darcy_friction_factor=Decimal("0.02"),
    )

    assert result.path_code == "PATH-001"
    assert result.source_node_code == "SRC"
    assert result.destination_node_code == "C-01"

    assert len(result.segment_results) == 2

    assert result.total_straight_length_m == Decimal("160")
    assert result.total_equivalent_fitting_length_m == Decimal("35")
    assert result.total_equivalent_length_m == Decimal("195")

    assert result.total_pressure_drop_bar > Decimal("0")

    assert result.destination_pressure_bar_g < Decimal("6.8")

    assert result.destination_minimum_pressure_bar_g == Decimal("6.0")

    assert result.destination_pressure_margin_bar is not None
    assert result.destination_pressure_is_adequate is True


def test_smaller_branch_diameter_increases_total_pressure_drop() -> None:
    network = build_network()

    path = NetworkPath(
        path_code="PATH-002",
        node_codes=("SRC", "J-01", "C-01"),
        segment_codes=("P-01", "P-02"),
    )

    normal_result = solve_network_path(
        network=network,
        path=path,
        air_density_kg_per_m3=Decimal("8.5"),
        darcy_friction_factor=Decimal("0.02"),
    )

    smaller_branch = PipeSegment(
        segment_code="P-02",
        name="Restricted Consumer Branch",
        role=PipeSegmentRole.BRANCH,
        start_node_code="J-01",
        end_node_code="C-01",
        length_m=Decimal("60"),
        equivalent_fitting_length_m=Decimal("15"),
        internal_diameter_mm=Decimal("50"),
        roughness_mm=Decimal("0.045"),
        design_flow_nm3_per_hr=Decimal("800"),
        operating_pressure_bar_g=Decimal("6.6"),
        operating_temperature_k=Decimal("303.15"),
    )

    restricted_network = CompressedAirNetwork(
        network_code=network.network_code,
        topology=network.topology,
        nodes=network.nodes,
        segments=(
            network.segments[0],
            smaller_branch,
        ),
        design_source_pressure_bar_g=network.design_source_pressure_bar_g,
    )

    restricted_result = solve_network_path(
        network=restricted_network,
        path=path,
        air_density_kg_per_m3=Decimal("8.5"),
        darcy_friction_factor=Decimal("0.02"),
    )

    assert restricted_result.total_pressure_drop_bar > normal_result.total_pressure_drop_bar

    assert restricted_result.destination_pressure_bar_g < normal_result.destination_pressure_bar_g


def test_pressure_adequacy_can_fail() -> None:
    network = build_network()

    high_pressure_consumer = NetworkNode(
        node_code="C-01",
        name="High Pressure Consumer",
        node_type=NetworkNodeType.CONSUMER,
        demand_nm3_per_hr=Decimal("800"),
        minimum_pressure_bar_g=Decimal("6.79"),
    )

    modified_network = CompressedAirNetwork(
        network_code=network.network_code,
        topology=network.topology,
        nodes=(
            network.nodes[0],
            network.nodes[1],
            high_pressure_consumer,
        ),
        segments=network.segments,
        design_source_pressure_bar_g=network.design_source_pressure_bar_g,
    )

    path = NetworkPath(
        path_code="PATH-003",
        node_codes=("SRC", "J-01", "C-01"),
        segment_codes=("P-01", "P-02"),
    )

    result = solve_network_path(
        network=modified_network,
        path=path,
        air_density_kg_per_m3=Decimal("8.5"),
        darcy_friction_factor=Decimal("0.02"),
    )

    assert result.destination_pressure_is_adequate is False
    assert result.destination_pressure_margin_bar is not None
    assert result.destination_pressure_margin_bar < Decimal("0")


def test_destination_without_minimum_pressure_returns_none_adequacy() -> None:
    network = build_network()

    consumer = NetworkNode(
        node_code="C-01",
        name="Consumer Without Pressure Requirement",
        node_type=NetworkNodeType.CONSUMER,
        demand_nm3_per_hr=Decimal("800"),
        minimum_pressure_bar_g=None,
    )

    modified_network = CompressedAirNetwork(
        network_code=network.network_code,
        topology=network.topology,
        nodes=(
            network.nodes[0],
            network.nodes[1],
            consumer,
        ),
        segments=network.segments,
        design_source_pressure_bar_g=network.design_source_pressure_bar_g,
    )

    path = NetworkPath(
        path_code="PATH-004",
        node_codes=("SRC", "J-01", "C-01"),
        segment_codes=("P-01", "P-02"),
    )

    result = solve_network_path(
        network=modified_network,
        path=path,
        air_density_kg_per_m3=Decimal("8.5"),
        darcy_friction_factor=Decimal("0.02"),
    )

    assert result.destination_minimum_pressure_bar_g is None
    assert result.destination_pressure_margin_bar is None
    assert result.destination_pressure_is_adequate is None


def test_unknown_node_is_rejected() -> None:
    network = build_network()

    path = NetworkPath(
        path_code="PATH-BAD-NODE",
        node_codes=("SRC", "MISSING"),
        segment_codes=("P-01",),
    )

    with pytest.raises(
        InvalidNetworkPathError,
        match="Path references unknown node",
    ):
        solve_network_path(
            network=network,
            path=path,
            air_density_kg_per_m3=Decimal("8.5"),
            darcy_friction_factor=Decimal("0.02"),
        )


def test_unknown_segment_is_rejected() -> None:
    network = build_network()

    path = NetworkPath(
        path_code="PATH-BAD-SEGMENT",
        node_codes=("SRC", "J-01"),
        segment_codes=("MISSING",),
    )

    with pytest.raises(
        InvalidNetworkPathError,
        match="Path references unknown segment",
    ):
        solve_network_path(
            network=network,
            path=path,
            air_density_kg_per_m3=Decimal("8.5"),
            darcy_friction_factor=Decimal("0.02"),
        )


def test_segment_direction_mismatch_is_rejected() -> None:
    network = build_network()

    path = NetworkPath(
        path_code="PATH-BAD-DIRECTION",
        node_codes=("J-01", "SRC"),
        segment_codes=("P-01",),
    )

    with pytest.raises(
        InvalidNetworkPathError,
        match="does not match the defined node path",
    ):
        solve_network_path(
            network=network,
            path=path,
            air_density_kg_per_m3=Decimal("8.5"),
            darcy_friction_factor=Decimal("0.02"),
        )


def test_invalid_friction_factor_is_rejected() -> None:
    network = build_network()

    path = NetworkPath(
        path_code="PATH-BAD-FRICTION",
        node_codes=("SRC", "J-01"),
        segment_codes=("P-01",),
    )

    with pytest.raises(
        InvalidNetworkPathError,
        match=("Darcy friction factor must be greater than zero and less than one"),
    ):
        solve_network_path(
            network=network,
            path=path,
            air_density_kg_per_m3=Decimal("8.5"),
            darcy_friction_factor=Decimal("1"),
        )
