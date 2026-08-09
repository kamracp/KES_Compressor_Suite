from dataclasses import dataclass
from decimal import Decimal

from app.domain.compressed_air.distribution.network_models import (
    CompressedAirNetwork,
    NetworkPath,
)
from app.domain.compressed_air.distribution.pipe_sizing import PipeSizingInput
from app.domain.compressed_air.distribution.pressure_drop import (
    PressureDropInput,
    calculate_pressure_drop,
)


class InvalidNetworkPathError(ValueError):
    """Raised when a compressed-air network path is invalid."""


@dataclass(frozen=True, slots=True)
class PathSegmentResult:
    """Calculated result for one segment in a network path."""

    segment_code: str
    start_node_code: str
    end_node_code: str

    design_flow_nm3_per_hr: Decimal

    length_m: Decimal
    equivalent_fitting_length_m: Decimal
    total_equivalent_length_m: Decimal

    velocity_m_per_s: Decimal
    pressure_drop_bar: Decimal


@dataclass(frozen=True, slots=True)
class NetworkPathResult:
    """Calculated hydraulic result for one compressed-air network path."""

    path_code: str

    source_node_code: str
    destination_node_code: str

    segment_results: tuple[PathSegmentResult, ...]

    total_straight_length_m: Decimal
    total_equivalent_fitting_length_m: Decimal
    total_equivalent_length_m: Decimal

    total_pressure_drop_bar: Decimal

    source_pressure_bar_g: Decimal
    destination_pressure_bar_g: Decimal

    destination_minimum_pressure_bar_g: Decimal | None
    destination_pressure_margin_bar: Decimal | None

    destination_pressure_is_adequate: bool | None


def solve_network_path(
    *,
    network: CompressedAirNetwork,
    path: NetworkPath,
    air_density_kg_per_m3: Decimal,
    darcy_friction_factor: Decimal,
) -> NetworkPathResult:
    """Calculate cumulative pressure drop along one defined network path."""

    _validate_path(
        network=network,
        path=path,
    )

    if air_density_kg_per_m3 <= 0:
        raise InvalidNetworkPathError("Air density must be greater than zero.")

    if darcy_friction_factor <= 0 or darcy_friction_factor >= 1:
        raise InvalidNetworkPathError(
            "Darcy friction factor must be greater than zero and less than one."
        )

    segment_lookup = {segment.segment_code: segment for segment in network.segments}

    node_lookup = {node.node_code: node for node in network.nodes}

    segment_results: list[PathSegmentResult] = []

    total_straight_length_m = Decimal("0")
    total_equivalent_fitting_length_m = Decimal("0")
    total_pressure_drop_bar = Decimal("0")

    for segment_code in path.segment_codes:
        segment = segment_lookup[segment_code]

        pressure_drop_result = calculate_pressure_drop(
            PressureDropInput(
                pipe=PipeSizingInput(
                    normal_flow_nm3_per_hr=segment.design_flow_nm3_per_hr,
                    operating_pressure_bar_g=segment.operating_pressure_bar_g,
                    operating_temperature_k=segment.operating_temperature_k,
                    pipe_internal_diameter_mm=segment.internal_diameter_mm,
                ),
                straight_length_m=segment.length_m,
                equivalent_fitting_length_m=(segment.equivalent_fitting_length_m),
                air_density_kg_per_m3=air_density_kg_per_m3,
                darcy_friction_factor=darcy_friction_factor,
            )
        )

        segment_results.append(
            PathSegmentResult(
                segment_code=segment.segment_code,
                start_node_code=segment.start_node_code,
                end_node_code=segment.end_node_code,
                design_flow_nm3_per_hr=segment.design_flow_nm3_per_hr,
                length_m=segment.length_m,
                equivalent_fitting_length_m=(segment.equivalent_fitting_length_m),
                total_equivalent_length_m=(pressure_drop_result.total_equivalent_length_m),
                velocity_m_per_s=(pressure_drop_result.pipe_result.air_velocity_m_per_s),
                pressure_drop_bar=pressure_drop_result.pressure_drop_bar,
            )
        )

        total_straight_length_m += segment.length_m
        total_equivalent_fitting_length_m += segment.equivalent_fitting_length_m
        total_pressure_drop_bar += pressure_drop_result.pressure_drop_bar

    source_pressure_bar_g = network.design_source_pressure_bar_g

    destination_pressure_bar_g = source_pressure_bar_g - total_pressure_drop_bar

    destination_node_code = path.node_codes[-1]
    destination_node = node_lookup[destination_node_code]

    minimum_pressure = destination_node.minimum_pressure_bar_g

    if minimum_pressure is None:
        destination_pressure_margin_bar = None
        destination_pressure_is_adequate = None
    else:
        destination_pressure_margin_bar = destination_pressure_bar_g - minimum_pressure
        destination_pressure_is_adequate = destination_pressure_bar_g >= minimum_pressure

    return NetworkPathResult(
        path_code=path.path_code,
        source_node_code=path.node_codes[0],
        destination_node_code=destination_node_code,
        segment_results=tuple(segment_results),
        total_straight_length_m=total_straight_length_m,
        total_equivalent_fitting_length_m=(total_equivalent_fitting_length_m),
        total_equivalent_length_m=(total_straight_length_m + total_equivalent_fitting_length_m),
        total_pressure_drop_bar=total_pressure_drop_bar,
        source_pressure_bar_g=source_pressure_bar_g,
        destination_pressure_bar_g=destination_pressure_bar_g,
        destination_minimum_pressure_bar_g=minimum_pressure,
        destination_pressure_margin_bar=destination_pressure_margin_bar,
        destination_pressure_is_adequate=destination_pressure_is_adequate,
    )


def _validate_path(
    *,
    network: CompressedAirNetwork,
    path: NetworkPath,
) -> None:
    if not path.path_code.strip():
        raise InvalidNetworkPathError("Path code cannot be empty.")

    if len(path.node_codes) < 2:
        raise InvalidNetworkPathError("A network path must contain at least two nodes.")

    if not path.segment_codes:
        raise InvalidNetworkPathError("A network path must contain at least one segment.")

    if len(path.segment_codes) != len(path.node_codes) - 1:
        raise InvalidNetworkPathError("Segment count must be one less than node count.")

    node_codes = {node.node_code for node in network.nodes}

    segment_lookup = {segment.segment_code: segment for segment in network.segments}

    for node_code in path.node_codes:
        if node_code not in node_codes:
            raise InvalidNetworkPathError(f"Path references unknown node '{node_code}'.")

    for index, segment_code in enumerate(path.segment_codes):
        if segment_code not in segment_lookup:
            raise InvalidNetworkPathError(f"Path references unknown segment '{segment_code}'.")

        segment = segment_lookup[segment_code]

        expected_start = path.node_codes[index]
        expected_end = path.node_codes[index + 1]

        if segment.start_node_code != expected_start or segment.end_node_code != expected_end:
            raise InvalidNetworkPathError(
                f"Segment '{segment_code}' does not match the defined node path."
            )
