from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from app.domain.compressed_air.treatment.air_treatment import DryerType


class SkidComponentType(StrEnum):
    """Compressed-air skid component type."""

    COMPRESSOR = "COMPRESSOR"
    AFTERCOOLER = "AFTERCOOLER"
    MOISTURE_SEPARATOR = "MOISTURE_SEPARATOR"
    WET_RECEIVER = "WET_RECEIVER"
    PREFILTER = "PREFILTER"
    DRYER = "DRYER"
    AFTERFILTER = "AFTERFILTER"
    DRY_RECEIVER = "DRY_RECEIVER"
    CONDENSATE_DRAIN = "CONDENSATE_DRAIN"
    OIL_WATER_SEPARATOR = "OIL_WATER_SEPARATOR"
    FLOW_METER = "FLOW_METER"
    PRESSURE_SENSOR = "PRESSURE_SENSOR"
    DEW_POINT_SENSOR = "DEW_POINT_SENSOR"
    MASTER_CONTROLLER = "MASTER_CONTROLLER"
    ISOLATION_VALVE = "ISOLATION_VALVE"
    CHECK_VALVE = "CHECK_VALVE"
    OTHER = "OTHER"


class SkidArrangement(StrEnum):
    """Overall compressed-air station/skid arrangement."""

    CENTRALIZED = "CENTRALIZED"
    DECENTRALIZED = "DECENTRALIZED"
    HYBRID = "HYBRID"


@dataclass(frozen=True, slots=True)
class SkidComponent:
    """One component installed in a compressed-air skid/system."""

    component_code: str
    name: str
    component_type: SkidComponentType

    rated_flow_nm3_per_hr: Decimal | None = None
    rated_pressure_bar_g: Decimal | None = None
    pressure_drop_bar: Decimal = Decimal("0")

    quantity: int = 1

    manufacturer: str | None = None
    model: str | None = None

    notes: str | None = None


@dataclass(frozen=True, slots=True)
class AirSkidConfiguration:
    """Integrated compressed-air skid/system configuration."""

    skid_code: str
    arrangement: SkidArrangement

    design_flow_nm3_per_hr: Decimal
    design_pressure_bar_g: Decimal

    dryer_type: DryerType

    components: tuple[SkidComponent, ...]

    has_wet_receiver: bool
    has_dry_receiver: bool

    has_flow_metering: bool
    has_pressure_monitoring: bool
    has_dew_point_monitoring: bool

    master_control_enabled: bool

    description: str | None = None


@dataclass(frozen=True, slots=True)
class AirSkidAssessmentResult:
    """Engineering assessment of a compressed-air skid configuration."""

    skid_code: str

    design_flow_nm3_per_hr: Decimal
    design_pressure_bar_g: Decimal

    total_component_count: int

    total_pressure_drop_bar: Decimal

    minimum_component_flow_capacity_nm3_per_hr: Decimal | None
    minimum_component_pressure_rating_bar_g: Decimal | None

    flow_capacity_is_adequate: bool
    pressure_rating_is_adequate: bool

    has_wet_receiver: bool
    has_dry_receiver: bool

    has_flow_metering: bool
    has_pressure_monitoring: bool
    has_dew_point_monitoring: bool

    master_control_enabled: bool

    instrumentation_is_complete: bool
    skid_is_adequate: bool
