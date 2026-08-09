from dataclasses import dataclass
from decimal import Decimal

BAR_TO_PA = Decimal("100000")
N_TO_KN = Decimal("0.001")


class InvalidRodLoadInputError(ValueError):
    """Raised when reciprocating rod-load inputs are invalid."""


@dataclass(frozen=True, slots=True)
class RodLoadResult:
    """Static gas rod-load calculation result."""

    compression_load_kn: Decimal
    tension_load_kn: Decimal
    maximum_absolute_load_kn: Decimal
    allowable_rod_load_kn: Decimal
    rod_load_is_adequate: bool


def calculate_rod_load(
    piston_area_m2: Decimal,
    rod_area_m2: Decimal,
    suction_pressure_bar: Decimal,
    discharge_pressure_bar: Decimal,
    allowable_rod_load_kn: Decimal,
) -> RodLoadResult:
    """Calculate simplified static gas rod loads."""

    if piston_area_m2 <= 0:
        raise InvalidRodLoadInputError("Piston area must be greater than zero.")

    if rod_area_m2 < 0:
        raise InvalidRodLoadInputError("Rod area cannot be negative.")

    if rod_area_m2 >= piston_area_m2:
        raise InvalidRodLoadInputError("Rod area must be smaller than piston area.")

    if suction_pressure_bar <= 0:
        raise InvalidRodLoadInputError("Suction absolute pressure must be greater than zero.")

    if discharge_pressure_bar <= suction_pressure_bar:
        raise InvalidRodLoadInputError("Discharge pressure must be greater than suction pressure.")

    if allowable_rod_load_kn <= 0:
        raise InvalidRodLoadInputError("Allowable rod load must be greater than zero.")

    pressure_difference_pa = (discharge_pressure_bar - suction_pressure_bar) * BAR_TO_PA

    compression_force_n = pressure_difference_pa * piston_area_m2
    tension_effective_area_m2 = piston_area_m2 - rod_area_m2
    tension_force_n = pressure_difference_pa * tension_effective_area_m2

    compression_load_kn = compression_force_n * N_TO_KN
    tension_load_kn = tension_force_n * N_TO_KN

    maximum_absolute_load_kn = max(
        abs(compression_load_kn),
        abs(tension_load_kn),
    )

    rod_load_is_adequate = maximum_absolute_load_kn <= allowable_rod_load_kn

    return RodLoadResult(
        compression_load_kn=compression_load_kn,
        tension_load_kn=tension_load_kn,
        maximum_absolute_load_kn=maximum_absolute_load_kn,
        allowable_rod_load_kn=allowable_rod_load_kn,
        rod_load_is_adequate=rod_load_is_adequate,
    )
