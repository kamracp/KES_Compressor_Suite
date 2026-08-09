from decimal import Decimal

import pytest

from app.domain.compressed_air.distribution.network_models import (
    CompressedAirNetwork,
    NetworkNode,
    NetworkNodeType,
    NetworkTopology,
    PipeSegment,
    PipeSegmentRole,
)
from app.domain.compressed_air.distribution.network_validation import (
    InvalidCompressedAirNetworkError,
    validate_network,
)


def build_node(
    *,
    code: str,
    node_type: NetworkNodeType,
    demand: str = "0",
    minimum_pressure: str | None = None,
) -> NetworkNode:
    return NetworkNode(
        node_code=code,
        name=code,
        node_type=node_type,
        demand_nm3_per_hr=Decimal(demand),
        minimum_pressure_bar_g=(
            Decimal(minimum_pressure) if minimum_pressure is not None else None
        ),
    )


def build_segment(
    *,
    code: str,
    start: str,
    end: str,
) -> PipeSegment:
    return PipeSegment(
        segment_code=code,
        name=code,
        role=PipeSegmentRole.MAIN_HEADER,
        start_node_code=start,
        end_node_code=end,
        length_m=Decimal("100"),
        equivalent_fitting_length_m=Decimal("20"),
        internal_diameter_mm=Decimal("125"),
        roughness_mm=Decimal("0.045"),
        design_flow_nm3_per_hr=Decimal("2000"),
        operating_pressure_bar_g=Decimal("6.8"),
        operating_temperature_k=Decimal("303.15"),
    )


def test_valid_network() -> None:
    network = CompressedAirNetwork(
        network_code="NET-001",
        topology=NetworkTopology.BRANCHED,
        design_source_pressure_bar_g=Decimal("6.8"),
        nodes=(
            build_node(
                code="SRC",
                node_type=NetworkNodeType.COMPRESSOR_STATION,
            ),
            build_node(
                code="J-01",
                node_type=NetworkNodeType.HEADER_JUNCTION,
            ),
            build_node(
                code="C-01",
                node_type=NetworkNodeType.CONSUMER,
                demand="800",
                minimum_pressure="6.0",
            ),
        ),
        segments=(
            build_segment(
                code="P-01",
                start="SRC",
                end="J-01",
            ),
            build_segment(
                code="P-02",
                start="J-01",
                end="C-01",
            ),
        ),
    )

    result = validate_network(network)

    assert result.network_code == "NET-001"
    assert result.node_count == 3
    assert result.segment_count == 2
    assert result.source_node_count == 1
    assert result.consumer_node_count == 1

    assert result.duplicate_node_codes == ()
    assert result.duplicate_segment_codes == ()
    assert result.orphan_segment_codes == ()

    assert result.is_structurally_valid is True


def test_duplicate_node_code_is_detected() -> None:
    network = CompressedAirNetwork(
        network_code="NET-002",
        topology=NetworkTopology.BRANCHED,
        design_source_pressure_bar_g=Decimal("6.8"),
        nodes=(
            build_node(
                code="SRC",
                node_type=NetworkNodeType.COMPRESSOR_STATION,
            ),
            build_node(
                code="C-01",
                node_type=NetworkNodeType.CONSUMER,
            ),
            build_node(
                code="C-01",
                node_type=NetworkNodeType.CONSUMER,
            ),
        ),
        segments=(),
    )

    result = validate_network(network)

    assert result.duplicate_node_codes == ("C-01",)
    assert result.is_structurally_valid is False


def test_duplicate_segment_code_is_detected() -> None:
    network = CompressedAirNetwork(
        network_code="NET-003",
        topology=NetworkTopology.BRANCHED,
        design_source_pressure_bar_g=Decimal("6.8"),
        nodes=(
            build_node(
                code="SRC",
                node_type=NetworkNodeType.COMPRESSOR_STATION,
            ),
            build_node(
                code="C-01",
                node_type=NetworkNodeType.CONSUMER,
            ),
        ),
        segments=(
            build_segment(
                code="P-01",
                start="SRC",
                end="C-01",
            ),
            build_segment(
                code="P-01",
                start="SRC",
                end="C-01",
            ),
        ),
    )

    result = validate_network(network)

    assert result.duplicate_segment_codes == ("P-01",)
    assert result.is_structurally_valid is False


def test_orphan_segment_is_detected() -> None:
    network = CompressedAirNetwork(
        network_code="NET-004",
        topology=NetworkTopology.BRANCHED,
        design_source_pressure_bar_g=Decimal("6.8"),
        nodes=(
            build_node(
                code="SRC",
                node_type=NetworkNodeType.COMPRESSOR_STATION,
            ),
            build_node(
                code="C-01",
                node_type=NetworkNodeType.CONSUMER,
            ),
        ),
        segments=(
            build_segment(
                code="P-ORPHAN",
                start="SRC",
                end="MISSING",
            ),
        ),
    )

    result = validate_network(network)

    assert result.orphan_segment_codes == ("P-ORPHAN",)
    assert result.is_structurally_valid is False


def test_missing_source_node_is_invalid() -> None:
    network = CompressedAirNetwork(
        network_code="NET-005",
        topology=NetworkTopology.BRANCHED,
        design_source_pressure_bar_g=Decimal("6.8"),
        nodes=(
            build_node(
                code="J-01",
                node_type=NetworkNodeType.HEADER_JUNCTION,
            ),
            build_node(
                code="C-01",
                node_type=NetworkNodeType.CONSUMER,
            ),
        ),
        segments=(
            build_segment(
                code="P-01",
                start="J-01",
                end="C-01",
            ),
        ),
    )

    result = validate_network(network)

    assert result.source_node_count == 0
    assert result.is_structurally_valid is False


def test_missing_consumer_node_is_invalid() -> None:
    network = CompressedAirNetwork(
        network_code="NET-006",
        topology=NetworkTopology.BRANCHED,
        design_source_pressure_bar_g=Decimal("6.8"),
        nodes=(
            build_node(
                code="SRC",
                node_type=NetworkNodeType.COMPRESSOR_STATION,
            ),
            build_node(
                code="J-01",
                node_type=NetworkNodeType.HEADER_JUNCTION,
            ),
        ),
        segments=(
            build_segment(
                code="P-01",
                start="SRC",
                end="J-01",
            ),
        ),
    )

    result = validate_network(network)

    assert result.consumer_node_count == 0
    assert result.is_structurally_valid is False


def test_empty_network_code_is_rejected() -> None:
    network = CompressedAirNetwork(
        network_code="",
        topology=NetworkTopology.BRANCHED,
        design_source_pressure_bar_g=Decimal("6.8"),
        nodes=(
            build_node(
                code="SRC",
                node_type=NetworkNodeType.COMPRESSOR_STATION,
            ),
        ),
        segments=(),
    )

    with pytest.raises(
        InvalidCompressedAirNetworkError,
        match="Network code cannot be empty",
    ):
        validate_network(network)


def test_negative_source_pressure_is_rejected() -> None:
    network = CompressedAirNetwork(
        network_code="NET-007",
        topology=NetworkTopology.BRANCHED,
        design_source_pressure_bar_g=Decimal("-0.1"),
        nodes=(
            build_node(
                code="SRC",
                node_type=NetworkNodeType.COMPRESSOR_STATION,
            ),
        ),
        segments=(),
    )

    with pytest.raises(
        InvalidCompressedAirNetworkError,
        match="Design source pressure cannot be negative",
    ):
        validate_network(network)


def test_self_connected_segment_is_rejected() -> None:
    network = CompressedAirNetwork(
        network_code="NET-008",
        topology=NetworkTopology.BRANCHED,
        design_source_pressure_bar_g=Decimal("6.8"),
        nodes=(
            build_node(
                code="SRC",
                node_type=NetworkNodeType.COMPRESSOR_STATION,
            ),
            build_node(
                code="C-01",
                node_type=NetworkNodeType.CONSUMER,
            ),
        ),
        segments=(
            build_segment(
                code="P-SELF",
                start="SRC",
                end="SRC",
            ),
        ),
    )

    with pytest.raises(
        InvalidCompressedAirNetworkError,
        match="Pipe segment cannot connect a node to itself",
    ):
        validate_network(network)
