from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class CylinderAction(StrEnum):
    SINGLE_ACTING = "SINGLE_ACTING"
    DOUBLE_ACTING = "DOUBLE_ACTING"


@dataclass(frozen=True, slots=True)
class ReciprocatingCylinderGeometry:
    """Reciprocating compressor cylinder geometry."""

    bore_mm: Decimal
    stroke_mm: Decimal
    rod_diameter_mm: Decimal
    speed_rpm: Decimal
    clearance_fraction: Decimal
    action: CylinderAction = CylinderAction.DOUBLE_ACTING


@dataclass(frozen=True, slots=True)
class ReciprocatingDisplacementResult:
    """Calculated reciprocating compressor displacement."""

    piston_area_m2: Decimal
    rod_area_m2: Decimal
    head_end_displacement_m3_per_min: Decimal
    crank_end_displacement_m3_per_min: Decimal
    total_displacement_m3_per_min: Decimal
    total_displacement_m3_per_hr: Decimal


@dataclass(frozen=True, slots=True)
class VolumetricEfficiencyResult:
    """Calculated volumetric efficiency and delivered capacity."""

    volumetric_efficiency: Decimal
    delivered_flow_m3_per_hr: Decimal


@dataclass(frozen=True, slots=True)
class ReciprocatingCapacityResult:
    """Combined reciprocating compressor capacity result."""

    geometry: ReciprocatingCylinderGeometry
    displacement: ReciprocatingDisplacementResult
    volumetric_efficiency: VolumetricEfficiencyResult
