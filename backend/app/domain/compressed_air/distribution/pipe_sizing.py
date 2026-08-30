from dataclasses import dataclass
from decimal import Decimal, getcontext

getcontext().prec = 28


class InvalidPipeSizingInputError(ValueError):
    """Raised when compressed-air pipe sizing inputs are invalid."""


PI = Decimal("3.141592653589793238462643383")
SECONDS_PER_HOUR = Decimal("3600")
ATMOSPHERIC_PRESSURE_BAR = Decimal("1.01325")

# Velocity screening thresholds calibrated to published industry guidance.
#
# - CAGI Pressure Drop technical brief / Compressed Air and Gas Handbook
#   (7th Edition, 2016): keep piping velocity at or below 20 ft/s
#   (~6.1 m/s) to minimize turbulence and pressure drop.
# - BCAS (Best Practice Guide 101, Installation): <= 6 m/s prevents
#   moisture/debris being carried past drain legs; > 9 m/s transports
#   water and debris in the air stream; design mains at 6-7 m/s and
#   never exceed 9 m/s.
#
# Standards registry references: CAGI-CAGH, BCAS-BPG-101.
VELOCITY_RECOMMENDED_LIMIT_M_PER_S = Decimal("6")
VELOCITY_ABSOLUTE_LIMIT_M_PER_S = Decimal("9")


@dataclass(frozen=True, slots=True)
class PipeSizingInput:
    """Input data for preliminary compressed-air pipe sizing."""

    normal_flow_nm3_per_hr: Decimal

    operating_pressure_bar_g: Decimal
    operating_temperature_k: Decimal

    pipe_internal_diameter_mm: Decimal

    normal_temperature_k: Decimal = Decimal("273.15")
    normal_pressure_bar_abs: Decimal = ATMOSPHERIC_PRESSURE_BAR


@dataclass(frozen=True, slots=True)
class PipeSizingResult:
    """Calculated compressed-air pipe-flow result."""

    normal_flow_nm3_per_hr: Decimal
    actual_flow_m3_per_hr: Decimal
    actual_flow_m3_per_s: Decimal

    pipe_internal_diameter_mm: Decimal
    pipe_cross_section_area_m2: Decimal

    air_velocity_m_per_s: Decimal

    operating_pressure_bar_g: Decimal
    operating_pressure_bar_abs: Decimal

    operating_temperature_k: Decimal

    velocity_screening_status: str


def calculate_pipe_velocity(
    inputs: PipeSizingInput,
) -> PipeSizingResult:
    """Convert normal flow to actual flow and calculate pipe velocity."""

    _validate_inputs(inputs)

    operating_pressure_bar_abs = inputs.operating_pressure_bar_g + ATMOSPHERIC_PRESSURE_BAR

    actual_flow_m3_per_hr = (
        inputs.normal_flow_nm3_per_hr
        * inputs.operating_temperature_k
        / inputs.normal_temperature_k
        * inputs.normal_pressure_bar_abs
        / operating_pressure_bar_abs
    )

    actual_flow_m3_per_s = actual_flow_m3_per_hr / SECONDS_PER_HOUR

    diameter_m = inputs.pipe_internal_diameter_mm / Decimal("1000")

    pipe_cross_section_area_m2 = PI * diameter_m * diameter_m / Decimal("4")

    air_velocity_m_per_s = actual_flow_m3_per_s / pipe_cross_section_area_m2

    velocity_screening_status = _screen_velocity(air_velocity_m_per_s)

    return PipeSizingResult(
        normal_flow_nm3_per_hr=inputs.normal_flow_nm3_per_hr,
        actual_flow_m3_per_hr=actual_flow_m3_per_hr,
        actual_flow_m3_per_s=actual_flow_m3_per_s,
        pipe_internal_diameter_mm=inputs.pipe_internal_diameter_mm,
        pipe_cross_section_area_m2=pipe_cross_section_area_m2,
        air_velocity_m_per_s=air_velocity_m_per_s,
        operating_pressure_bar_g=inputs.operating_pressure_bar_g,
        operating_pressure_bar_abs=operating_pressure_bar_abs,
        operating_temperature_k=inputs.operating_temperature_k,
        velocity_screening_status=velocity_screening_status,
    )


def _screen_velocity(
    velocity_m_per_s: Decimal,
) -> str:
    if velocity_m_per_s <= VELOCITY_RECOMMENDED_LIMIT_M_PER_S:
        return "RECOMMENDED"

    if velocity_m_per_s <= VELOCITY_ABSOLUTE_LIMIT_M_PER_S:
        return "CAUTION"

    return "EXCESSIVE"


def _validate_inputs(
    inputs: PipeSizingInput,
) -> None:
    if inputs.normal_flow_nm3_per_hr <= 0:
        raise InvalidPipeSizingInputError("Normal flow must be greater than zero.")

    if inputs.operating_pressure_bar_g < 0:
        raise InvalidPipeSizingInputError("Operating gauge pressure cannot be negative.")

    if inputs.operating_temperature_k <= 0:
        raise InvalidPipeSizingInputError("Operating temperature must be greater than zero.")

    if inputs.pipe_internal_diameter_mm <= 0:
        raise InvalidPipeSizingInputError("Pipe internal diameter must be greater than zero.")

    if inputs.normal_temperature_k <= 0:
        raise InvalidPipeSizingInputError("Normal temperature must be greater than zero.")

    if inputs.normal_pressure_bar_abs <= 0:
        raise InvalidPipeSizingInputError("Normal absolute pressure must be greater than zero.")
