from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class RotaryScrewOilType(StrEnum):
    """Lubrication method of the screw compressor rotor set."""

    OIL_INJECTED = "OIL_INJECTED"
    OIL_FREE = "OIL_FREE"


class RotaryScrewControlType(StrEnum):
    """Capacity control method for the screw compressor."""

    FIXED_SPEED_LOAD_UNLOAD = "FIXED_SPEED_LOAD_UNLOAD"
    VARIABLE_SPEED_DRIVE = "VARIABLE_SPEED_DRIVE"


class RotaryScrewStageCount(StrEnum):
    """Number of compression stages in the screw compressor package."""

    SINGLE_STAGE = "SINGLE_STAGE"
    TWO_STAGE = "TWO_STAGE"


@dataclass(frozen=True, slots=True)
class RotaryScrewOperatingPoint:
    """Site operating conditions at which a rotary screw compressor is evaluated."""

    inlet_pressure_bar_a: Decimal
    inlet_temperature_k: Decimal
    discharge_pressure_bar_g: Decimal
    rotational_speed_rpm: Decimal
    oil_type: RotaryScrewOilType
    control_type: RotaryScrewControlType
    stage_count: RotaryScrewStageCount = RotaryScrewStageCount.SINGLE_STAGE


@dataclass(frozen=True, slots=True)
class RotaryScrewRotorGeometry:
    """Male rotor geometry used for a theoretical (ideal) displacement estimate.

    ``area_utilisation_coefficient`` is the rotor-profile area utilisation
    factor (commonly denoted C-theta in screw compressor literature). It is
    profile-specific to each manufacturer's rotor design and therefore must
    be supplied by the user (from the manufacturer's published data or a
    documented textbook range) rather than assumed internally.
    """

    male_rotor_diameter_mm: Decimal
    rotor_length_mm: Decimal
    area_utilisation_coefficient: Decimal


@dataclass(frozen=True, slots=True)
class RotaryScrewDisplacementResult:
    """Theoretical (ideal) displacement of the rotor set, before losses."""

    theoretical_displacement_m3_per_min: Decimal


@dataclass(frozen=True, slots=True)
class RotaryScrewStandardAirCorrectionResult:
    """ISO 1217 style correction of a rated FAD to site inlet conditions."""

    reference_pressure_bar_a: Decimal
    reference_temperature_k: Decimal
    corrected_fad_m3_per_min: Decimal


@dataclass(frozen=True, slots=True)
class RotaryScrewPerformanceResult:
    """Performance figures derived from manufacturer-verified package data.

    These figures are computed from data the user supplies from an actual
    CAGI-tested manufacturer datasheet (rated FAD and package input power) --
    this module verifies and benchmarks that data, it does not invent it.
    """

    rated_fad_m3_per_min: Decimal
    package_input_power_kw: Decimal
    specific_power_kw_per_m3_min: Decimal


@dataclass(frozen=True, slots=True)
class RotaryScrewSizingResult:
    """Combined rotary screw compressor evaluation result."""

    operating_point: RotaryScrewOperatingPoint
    displacement: RotaryScrewDisplacementResult | None
    standard_air_correction: RotaryScrewStandardAirCorrectionResult | None
    performance: RotaryScrewPerformanceResult
