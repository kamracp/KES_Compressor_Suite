from collections import Counter

from app.domain.compressed_air.distribution.network_models import (
    CompressedAirNetwork,
    NetworkNodeType,
    NetworkValidationResult,
)


class InvalidCompressedAirNetworkError(ValueError):
    """Raised when a compressed-air network definition is invalid."""


def validate_network(
    network: CompressedAirNetwork,
) -> NetworkValidationResult:
    """Validate compressed-air network structure."""

    if not network.network_code.strip():
        raise InvalidCompressedAirNetworkError("Network code cannot be empty.")

    if network.design_source_pressure_bar_g < 0:
        raise InvalidCompressedAirNetworkError("Design source pressure cannot be negative.")

    if not network.nodes:
        raise InvalidCompressedAirNetworkError("At least one network node is required.")

    node_codes = tuple(node.node_code for node in network.nodes)

    segment_codes = tuple(segment.segment_code for segment in network.segments)

    duplicate_node_codes = tuple(
        sorted(code for code, count in Counter(node_codes).items() if count > 1)
    )

    duplicate_segment_codes = tuple(
        sorted(code for code, count in Counter(segment_codes).items() if count > 1)
    )

    node_code_set = set(node_codes)

    orphan_segment_codes = tuple(
        sorted(
            segment.segment_code
            for segment in network.segments
            if (
                segment.start_node_code not in node_code_set
                or segment.end_node_code not in node_code_set
            )
        )
    )

    for node in network.nodes:
        _validate_node(node)

    for segment in network.segments:
        _validate_segment(segment)

    source_node_count = sum(
        1 for node in network.nodes if node.node_type == NetworkNodeType.COMPRESSOR_STATION
    )

    consumer_node_count = sum(
        1 for node in network.nodes if node.node_type == NetworkNodeType.CONSUMER
    )

    is_structurally_valid = (
        not duplicate_node_codes
        and not duplicate_segment_codes
        and not orphan_segment_codes
        and source_node_count >= 1
        and consumer_node_count >= 1
    )

    return NetworkValidationResult(
        network_code=network.network_code,
        node_count=len(network.nodes),
        segment_count=len(network.segments),
        source_node_count=source_node_count,
        consumer_node_count=consumer_node_count,
        duplicate_node_codes=duplicate_node_codes,
        duplicate_segment_codes=duplicate_segment_codes,
        orphan_segment_codes=orphan_segment_codes,
        is_structurally_valid=is_structurally_valid,
    )


def _validate_node(node) -> None:
    if not node.node_code.strip():
        raise InvalidCompressedAirNetworkError("Network node code cannot be empty.")

    if not node.name.strip():
        raise InvalidCompressedAirNetworkError("Network node name cannot be empty.")

    if node.demand_nm3_per_hr < 0:
        raise InvalidCompressedAirNetworkError("Node demand cannot be negative.")

    if node.minimum_pressure_bar_g is not None and node.minimum_pressure_bar_g < 0:
        raise InvalidCompressedAirNetworkError("Node minimum pressure cannot be negative.")


def _validate_segment(segment) -> None:
    if not segment.segment_code.strip():
        raise InvalidCompressedAirNetworkError("Pipe segment code cannot be empty.")

    if not segment.name.strip():
        raise InvalidCompressedAirNetworkError("Pipe segment name cannot be empty.")

    if not segment.start_node_code.strip():
        raise InvalidCompressedAirNetworkError("Pipe segment start node code cannot be empty.")

    if not segment.end_node_code.strip():
        raise InvalidCompressedAirNetworkError("Pipe segment end node code cannot be empty.")

    if segment.start_node_code == segment.end_node_code:
        raise InvalidCompressedAirNetworkError("Pipe segment cannot connect a node to itself.")

    if segment.length_m < 0:
        raise InvalidCompressedAirNetworkError("Pipe segment length cannot be negative.")

    if segment.equivalent_fitting_length_m < 0:
        raise InvalidCompressedAirNetworkError("Equivalent fitting length cannot be negative.")

    if segment.internal_diameter_mm <= 0:
        raise InvalidCompressedAirNetworkError("Pipe internal diameter must be greater than zero.")

    if segment.roughness_mm < 0:
        raise InvalidCompressedAirNetworkError("Pipe roughness cannot be negative.")

    if segment.design_flow_nm3_per_hr < 0:
        raise InvalidCompressedAirNetworkError("Pipe design flow cannot be negative.")

    if segment.operating_pressure_bar_g < 0:
        raise InvalidCompressedAirNetworkError("Pipe operating pressure cannot be negative.")

    if segment.operating_temperature_k <= 0:
        raise InvalidCompressedAirNetworkError(
            "Pipe operating temperature must be greater than zero."
        )
