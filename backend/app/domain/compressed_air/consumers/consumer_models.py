from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class AirConsumerCategory(StrEnum):
    """Industrial compressed-air consumer categories."""

    PRODUCTION_MACHINE = "PRODUCTION_MACHINE"
    PNEUMATIC_CYLINDER = "PNEUMATIC_CYLINDER"
    AIR_TOOL = "AIR_TOOL"
    BAG_FILTER = "BAG_FILTER"
    PNEUMATIC_CONVEYING = "PNEUMATIC_CONVEYING"
    PACKAGING_MACHINE = "PACKAGING_MACHINE"
    CONTROL_VALVE = "CONTROL_VALVE"
    INSTRUMENT_AIR = "INSTRUMENT_AIR"
    PROCESS_AIR = "PROCESS_AIR"
    AIR_CLEANING = "AIR_CLEANING"
    OTHER = "OTHER"


class AirConsumptionBasis(StrEnum):
    """Basis used to define compressed-air consumption."""

    CONTINUOUS_FLOW = "CONTINUOUS_FLOW"
    FLOW_WHEN_OPERATING = "FLOW_WHEN_OPERATING"
    PER_CYCLE = "PER_CYCLE"


class AirQualityClass(StrEnum):
    """High-level compressed-air quality requirement."""

    GENERAL_PLANT_AIR = "GENERAL_PLANT_AIR"
    INSTRUMENT_AIR = "INSTRUMENT_AIR"
    OIL_FREE_PROCESS_AIR = "OIL_FREE_PROCESS_AIR"
    CRITICAL_PROCESS_AIR = "CRITICAL_PROCESS_AIR"


class ConsumerCriticality(StrEnum):
    """Operational criticality of an air consumer."""

    CRITICAL = "CRITICAL"
    ESSENTIAL = "ESSENTIAL"
    NORMAL = "NORMAL"
    NON_CRITICAL = "NON_CRITICAL"


@dataclass(frozen=True, slots=True)
class AirConsumer:
    """One compressed-air consuming equipment item or equipment group."""

    consumer_code: str
    name: str
    category: AirConsumerCategory

    quantity: int

    required_pressure_bar_g: Decimal
    air_quality_class: AirQualityClass

    consumption_basis: AirConsumptionBasis

    flow_per_unit_nm3_per_hr: Decimal | None = None

    air_per_cycle_nl: Decimal | None = None
    cycles_per_minute: Decimal | None = None

    duty_factor: Decimal = Decimal("1")
    simultaneity_factor: Decimal = Decimal("1")

    operating_hours_per_day: Decimal = Decimal("24")
    operating_days_per_year: Decimal = Decimal("365")

    criticality: ConsumerCriticality = ConsumerCriticality.NORMAL

    area: str | None = None
    production_line: str | None = None
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class AirConsumerDemandResult:
    """Calculated demand result for one compressed-air consumer."""

    consumer_code: str
    name: str
    category: AirConsumerCategory

    quantity: int
    required_pressure_bar_g: Decimal
    air_quality_class: AirQualityClass

    theoretical_flow_nm3_per_hr: Decimal
    duty_adjusted_flow_nm3_per_hr: Decimal
    simultaneous_flow_nm3_per_hr: Decimal

    annual_air_volume_nm3: Decimal

    criticality: ConsumerCriticality
