from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from app.domain.compressed_air.storage.receiver_sizing import (
    ReceiverSizingInput,
    ReceiverSizingResult,
)
from app.domain.compressed_air.treatment.air_treatment import (
    AirTreatmentInput,
    AirTreatmentResult,
)


class EquipmentAdequacyStatus(StrEnum):
    """Engineering adequacy status for allied compressed-air equipment."""

    NOT_EVALUATED = "NOT_EVALUATED"
    NOT_REQUIRED = "NOT_REQUIRED"
    NOT_SELECTED = "NOT_SELECTED"
    ADEQUATE = "ADEQUATE"
    UNDERSIZED = "UNDERSIZED"


class RedundancyPhilosophy(StrEnum):
    """Equipment redundancy philosophy."""

    NONE = "NONE"
    DUTY_STANDBY = "DUTY_STANDBY"
    N_PLUS_1 = "N_PLUS_1"
    MULTIPLE_DUTY = "MULTIPLE_DUTY"


class AftercoolerType(StrEnum):
    """Compressed-air aftercooler arrangement."""

    AIR_COOLED = "AIR_COOLED"
    WATER_COOLED = "WATER_COOLED"
    INTEGRATED = "INTEGRATED"
    NONE = "NONE"


class MoistureSeparatorType(StrEnum):
    """Compressed-air moisture-separator arrangement."""

    CENTRIFUGAL = "CENTRIFUGAL"
    CYCLONIC = "CYCLONIC"
    DEMISTER = "DEMISTER"
    INTEGRATED = "INTEGRATED"
    NONE = "NONE"


class FilterStageType(StrEnum):
    """Functional type of compressed-air filter stage."""

    PARTICULATE = "PARTICULATE"
    COALESCING = "COALESCING"
    FINE_COALESCING = "FINE_COALESCING"
    ACTIVATED_CARBON = "ACTIVATED_CARBON"
    STERILE = "STERILE"
    OTHER = "OTHER"


class CondensateDrainType(StrEnum):
    """Condensate-drain operating principle."""

    MANUAL = "MANUAL"
    TIMER = "TIMER"
    FLOAT = "FLOAT"
    ZERO_LOSS = "ZERO_LOSS"
    OTHER = "OTHER"


class RecommendationSeverity(StrEnum):
    """Engineering recommendation severity."""

    INFORMATION = "INFORMATION"
    ADVISORY = "ADVISORY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True, slots=True)
class ReceiverConfiguration:
    """Receiver sizing basis and selected equipment configuration."""

    sizing_input: ReceiverSizingInput
    selected_receiver_volume_m3: Decimal | None = None
    receiver_quantity: int = 1
    design_pressure_bar_g: Decimal | None = None
    redundancy_philosophy: RedundancyPhilosophy = RedundancyPhilosophy.NONE
    equipment_reference: str | None = None
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class TreatmentConfiguration:
    """Air-treatment sizing basis and selected treatment equipment."""

    sizing_input: AirTreatmentInput
    selected_treatment_capacity_nm3_per_hr: Decimal | None = None
    installed_unit_count: int = 1
    duty_unit_count: int = 1
    redundancy_philosophy: RedundancyPhilosophy = RedundancyPhilosophy.NONE
    equipment_reference: str | None = None
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class AftercoolerConfiguration:
    """Aftercooler engineering configuration."""

    aftercooler_type: AftercoolerType
    selected_flow_capacity_nm3_per_hr: Decimal | None = None
    pressure_drop_bar: Decimal = Decimal("0")
    inlet_temperature_c: Decimal | None = None
    outlet_temperature_c: Decimal | None = None
    equipment_reference: str | None = None
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class MoistureSeparatorConfiguration:
    """Moisture-separator engineering configuration."""

    separator_type: MoistureSeparatorType
    selected_flow_capacity_nm3_per_hr: Decimal | None = None
    pressure_drop_bar: Decimal = Decimal("0")
    equipment_reference: str | None = None
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class FilterStageConfiguration:
    """One compressed-air filter stage."""

    stage_code: str
    stage_type: FilterStageType
    selected_flow_capacity_nm3_per_hr: Decimal | None = None
    pressure_drop_bar: Decimal = Decimal("0")
    equipment_reference: str | None = None
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class CondensateDrainConfiguration:
    """One condensate-drain installation."""

    drain_code: str
    location: str
    drain_type: CondensateDrainType
    selected_condensate_capacity_l_per_hr: Decimal | None = None
    equipment_reference: str | None = None
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class AlliedEquipmentAnalysisInput:
    """Complete input contract for allied-equipment engineering review."""

    analysis_code: str
    receiver: ReceiverConfiguration | None = None
    treatment: TreatmentConfiguration | None = None
    aftercooler: AftercoolerConfiguration | None = None
    moisture_separator: MoistureSeparatorConfiguration | None = None
    filter_stages: tuple[FilterStageConfiguration, ...] = ()
    condensate_drains: tuple[CondensateDrainConfiguration, ...] = ()
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class EquipmentCapacityEvaluation:
    """Required-versus-selected capacity engineering evaluation."""

    equipment_code: str
    required_capacity: Decimal
    selected_capacity: Decimal | None
    capacity_margin: Decimal | None
    capacity_margin_fraction: Decimal | None
    status: EquipmentAdequacyStatus


@dataclass(frozen=True, slots=True)
class EngineeringRecommendation:
    """Traceable deterministic engineering recommendation."""

    recommendation_code: str
    severity: RecommendationSeverity
    equipment_code: str
    message: str
    rationale: str


@dataclass(frozen=True, slots=True)
class AlliedEquipmentAnalysisResult:
    """Engineering result for complete allied-equipment analysis."""

    analysis_code: str
    receiver_result: ReceiverSizingResult | None
    treatment_result: AirTreatmentResult | None
    receiver_evaluation: EquipmentCapacityEvaluation | None
    treatment_evaluation: EquipmentCapacityEvaluation | None
    aftercooler_evaluation: EquipmentCapacityEvaluation | None
    moisture_separator_evaluation: EquipmentCapacityEvaluation | None
    filter_evaluations: tuple[EquipmentCapacityEvaluation, ...]
    total_additional_pressure_drop_bar: Decimal
    recommendations: tuple[EngineeringRecommendation, ...]
    notes: str | None
