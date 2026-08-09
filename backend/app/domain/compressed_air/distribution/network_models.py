from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class NetworkNodeType(StrEnum):
    """Compressed-air distribution node type."""

    COMPRESSOR_STATION = "COMPRESSOR_STATION"
    RECEIVER = "RECEIVER"
    HEADER_JUNCTION = "HEADER_JUNCTION"
    BRANCH_JUNCTION = "BRANCH_JUNCTION"
    CONSUMER = "CONSUMER"
    RING_CONNECTION = "RING_CONNECTION"


class PipeSegmentRole(StrEnum):
    """Functional role of a compressed-air pipe segment."""

    MAIN_HEADER = "MAIN_HEADER"
    RING_MAIN = "RING_MAIN"
    SUB_HEADER = "SUB_HEADER"
    BRANCH = "BRANCH"
    DROP_LEG = "DROP_LEG"
    EQUIPMENT_CONNECTION = "EQUIPMENT_CONNECTION"


class NetworkTopology(StrEnum):
    """Compressed-air distribution topology."""

    DEAD_END = "DEAD_END"
    BRANCHED = "BRANCHED"
    RING_MAIN = "RING_MAIN"
    MULTIPLE_RING = "MULTIPLE_RING"
    HYBRID = "HYBRID"


@dataclass(frozen=True, slots=True)
class NetworkNode:
    """One node in a compressed-air distribution network."""

    node_code: str
    name: str
    node_type: NetworkNodeType

    elevation_m: Decimal = Decimal("0")

    demand_nm3_per_hr: Decimal = Decimal("0")
    minimum_pressure_bar_g: Decimal | None = None

    area: str | None = None
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class PipeSegment:
    """One pipe segment connecting two network nodes."""

    segment_code: str
    name: str
    role: PipeSegmentRole

    start_node_code: str
    end_node_code: str

    length_m: Decimal
    equivalent_fitting_length_m: Decimal

    internal_diameter_mm: Decimal

    roughness_mm: Decimal

    design_flow_nm3_per_hr: Decimal

    operating_pressure_bar_g: Decimal
    operating_temperature_k: Decimal

    material: str | None = None
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class CompressedAirNetwork:
    """Compressed-air distribution network definition."""

    network_code: str
    topology: NetworkTopology

    nodes: tuple[NetworkNode, ...]
    segments: tuple[PipeSegment, ...]

    design_source_pressure_bar_g: Decimal

    description: str | None = None


@dataclass(frozen=True, slots=True)
class NetworkPath:
    """One flow path from source to a downstream node."""

    path_code: str
    node_codes: tuple[str, ...]
    segment_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class NetworkValidationResult:
    """Structural validation result for a compressed-air network."""

    network_code: str

    node_count: int
    segment_count: int

    source_node_count: int
    consumer_node_count: int

    duplicate_node_codes: tuple[str, ...]
    duplicate_segment_codes: tuple[str, ...]

    orphan_segment_codes: tuple[str, ...]

    is_structurally_valid: bool
