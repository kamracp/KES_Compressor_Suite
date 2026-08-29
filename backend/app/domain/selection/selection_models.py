from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class CompressorType(StrEnum):
    RECIPROCATING = "RECIPROCATING"
    CENTRIFUGAL = "CENTRIFUGAL"
    ROTARY_SCREW = "ROTARY_SCREW"


class SelectionRating(StrEnum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    ACCEPTABLE = "ACCEPTABLE"
    POOR = "POOR"


@dataclass(frozen=True, slots=True)
class CompressorSelectionCriteria:
    """Engineering criteria used for compressor-type selection."""

    required_flow_m3_per_hr: Decimal
    suction_pressure_bar: Decimal
    discharge_pressure_bar: Decimal
    required_turndown_fraction: Decimal
    continuous_operation: bool
    gas_molecular_weight: Decimal
    estimated_operating_hours_per_year: Decimal
    oil_free_air_required: bool = False


@dataclass(frozen=True, slots=True)
class CompressorOptionAssessment:
    """Assessment of one compressor type against selection criteria."""

    compressor_type: CompressorType
    capacity_rating: SelectionRating
    pressure_ratio_rating: SelectionRating
    turndown_rating: SelectionRating
    efficiency_rating: SelectionRating
    maintenance_rating: SelectionRating
    air_quality_rating: SelectionRating
    lifecycle_energy_rating: SelectionRating
    overall_score: Decimal
    rationale: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CompressorSelectionResult:
    """Final compressor-type selection result across evaluated technologies."""

    recommended_type: CompressorType
    reciprocating: CompressorOptionAssessment
    centrifugal: CompressorOptionAssessment
    rotary_screw: CompressorOptionAssessment
    score_difference: Decimal
    recommendation_summary: str
