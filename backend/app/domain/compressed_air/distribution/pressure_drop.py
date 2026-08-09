from dataclasses import dataclass
from decimal import Decimal

from app.domain.compressed_air.distribution.pipe_sizing import (
    PipeSizingInput,
    PipeSizingResult,
    calculate_pipe_velocity,
)


class InvalidPressureDropInputError(ValueError):
    """Raised when compressed-air pressure-drop inputs are invalid."""


PA_PER_BAR = Decimal("100000")


@dataclass(frozen=True, slots=True)
class PressureDropInput:
    """Input data for compressed-air pipe pressure-drop calculation."""

    pipe: PipeSizingInput

    straight_length_m: Decimal
    equivalent_fitting_length_m: Decimal

    air_density_kg_per_m3: Decimal
    darcy_friction_factor: Decimal


@dataclass(frozen=True, slots=True)
class PressureDropResult:
    """Calculated compressed-air pipe pressure-drop result."""

    pipe_result: PipeSizingResult

    straight_length_m: Decimal
    equivalent_fitting_length_m: Decimal
    total_equivalent_length_m: Decimal

    air_density_kg_per_m3: Decimal
    darcy_friction_factor: Decimal

    pressure_drop_pa: Decimal
    pressure_drop_bar: Decimal
    pressure_drop_bar_per_100m: Decimal


def calculate_pressure_drop(
    inputs: PressureDropInput,
) -> PressureDropResult:
    """Calculate compressed-air pipe pressure drop using Darcy-Weisbach."""

    _validate_inputs(inputs)

    pipe_result = calculate_pipe_velocity(inputs.pipe)

    total_equivalent_length_m = inputs.straight_length_m + inputs.equivalent_fitting_length_m

    diameter_m = inputs.pipe.pipe_internal_diameter_mm / Decimal("1000")

    velocity_squared = pipe_result.air_velocity_m_per_s * pipe_result.air_velocity_m_per_s

    pressure_drop_pa = (
        inputs.darcy_friction_factor
        * (total_equivalent_length_m / diameter_m)
        * (inputs.air_density_kg_per_m3 * velocity_squared / Decimal("2"))
    )

    pressure_drop_bar = pressure_drop_pa / PA_PER_BAR

    if total_equivalent_length_m > 0:
        pressure_drop_bar_per_100m = pressure_drop_bar * Decimal("100") / total_equivalent_length_m
    else:
        pressure_drop_bar_per_100m = Decimal("0")

    return PressureDropResult(
        pipe_result=pipe_result,
        straight_length_m=inputs.straight_length_m,
        equivalent_fitting_length_m=inputs.equivalent_fitting_length_m,
        total_equivalent_length_m=total_equivalent_length_m,
        air_density_kg_per_m3=inputs.air_density_kg_per_m3,
        darcy_friction_factor=inputs.darcy_friction_factor,
        pressure_drop_pa=pressure_drop_pa,
        pressure_drop_bar=pressure_drop_bar,
        pressure_drop_bar_per_100m=pressure_drop_bar_per_100m,
    )


def _validate_inputs(
    inputs: PressureDropInput,
) -> None:
    if inputs.straight_length_m < 0:
        raise InvalidPressureDropInputError("Straight pipe length cannot be negative.")

    if inputs.equivalent_fitting_length_m < 0:
        raise InvalidPressureDropInputError("Equivalent fitting length cannot be negative.")

    if inputs.straight_length_m + inputs.equivalent_fitting_length_m <= 0:
        raise InvalidPressureDropInputError(
            "Total equivalent pipe length must be greater than zero."
        )

    if inputs.air_density_kg_per_m3 <= 0:
        raise InvalidPressureDropInputError("Air density must be greater than zero.")

    if inputs.darcy_friction_factor <= 0:
        raise InvalidPressureDropInputError("Darcy friction factor must be greater than zero.")

    if inputs.darcy_friction_factor >= 1:
        raise InvalidPressureDropInputError("Darcy friction factor must be less than one.")
