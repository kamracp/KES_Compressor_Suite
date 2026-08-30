from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

# Standard atmosphere used to convert gauge to absolute pressure.
ATMOSPHERIC_PRESSURE_BAR = Decimal("1.01325")

# Isentropic exponent for air, k = cp/cv = 1.4 (standard thermodynamic
# property of diatomic air; consistent with the k used across the
# compression engineering modules). The adiabatic method below uses the
# ratio (k - 1) / k ~= 0.2857.
ISENTROPIC_EXPONENT_AIR = Decimal("1.4")


class PressureSavingMethod(StrEnum):
    """Method used to convert a pressure reduction into a power saving."""

    # Physics-based default: ratio of ideal isentropic compression work
    # W ~ (P_discharge/P_ambient)^((k-1)/k) - 1 before and after the
    # reduction. At 7 bar(g) this yields roughly 8% power saving per bar,
    # which is what the common "7% per bar" rule of thumb linearizes.
    ADIABATIC_ISENTROPIC = "ADIABATIC_ISENTROPIC"

    # Legacy linear rule of thumb, kept as an explicit user override
    # (saving fraction = reduction_bar x penalty_fraction_per_bar).
    LINEAR_PER_BAR = "LINEAR_PER_BAR"


class InvalidPressureEnergyInputError(ValueError):
    """Raised when pressure-energy optimization inputs are invalid."""


@dataclass(frozen=True, slots=True)
class PressureEnergyInput:
    """Input data for compressed-air pressure-energy analysis."""

    current_discharge_pressure_bar_g: Decimal
    optimized_discharge_pressure_bar_g: Decimal

    current_average_power_kw: Decimal
    annual_operating_hours: Decimal

    electricity_tariff_per_kwh: Decimal

    # None (default) selects the adiabatic isentropic-work method.
    # Providing a value selects the legacy linear per-bar override.
    power_penalty_fraction_per_bar: Decimal | None = None


@dataclass(frozen=True, slots=True)
class PressureEnergyResult:
    """Calculated energy impact of reducing compressed-air pressure."""

    current_discharge_pressure_bar_g: Decimal
    optimized_discharge_pressure_bar_g: Decimal

    pressure_reduction_bar: Decimal

    current_average_power_kw: Decimal
    estimated_optimized_power_kw: Decimal
    estimated_power_saving_kw: Decimal

    power_saving_fraction: Decimal

    annual_operating_hours: Decimal

    annual_energy_saving_kwh: Decimal

    electricity_tariff_per_kwh: Decimal
    annual_cost_saving: Decimal

    power_penalty_fraction_per_bar: Decimal | None

    power_saving_method: str

    pressure_reduction_is_beneficial: bool


def calculate_pressure_energy_saving(
    inputs: PressureEnergyInput,
) -> PressureEnergyResult:
    """Estimate energy savings from reducing compressor discharge pressure."""

    _validate_inputs(inputs)

    pressure_reduction_bar = (
        inputs.current_discharge_pressure_bar_g - inputs.optimized_discharge_pressure_bar_g
    )

    if inputs.power_penalty_fraction_per_bar is None:
        power_saving_method = PressureSavingMethod.ADIABATIC_ISENTROPIC
    else:
        power_saving_method = PressureSavingMethod.LINEAR_PER_BAR

    if pressure_reduction_bar <= 0:
        power_saving_fraction = Decimal("0")
    elif power_saving_method == PressureSavingMethod.ADIABATIC_ISENTROPIC:
        power_saving_fraction = _adiabatic_power_saving_fraction(
            current_pressure_bar_g=(inputs.current_discharge_pressure_bar_g),
            target_pressure_bar_g=(inputs.optimized_discharge_pressure_bar_g),
        )
    else:
        power_saving_fraction = pressure_reduction_bar * inputs.power_penalty_fraction_per_bar

    if power_saving_fraction > Decimal("1"):
        power_saving_fraction = Decimal("1")

    estimated_power_saving_kw = inputs.current_average_power_kw * power_saving_fraction

    estimated_optimized_power_kw = inputs.current_average_power_kw - estimated_power_saving_kw

    annual_energy_saving_kwh = estimated_power_saving_kw * inputs.annual_operating_hours

    annual_cost_saving = annual_energy_saving_kwh * inputs.electricity_tariff_per_kwh

    return PressureEnergyResult(
        current_discharge_pressure_bar_g=(inputs.current_discharge_pressure_bar_g),
        optimized_discharge_pressure_bar_g=(inputs.optimized_discharge_pressure_bar_g),
        pressure_reduction_bar=pressure_reduction_bar,
        current_average_power_kw=inputs.current_average_power_kw,
        estimated_optimized_power_kw=estimated_optimized_power_kw,
        estimated_power_saving_kw=estimated_power_saving_kw,
        power_saving_fraction=power_saving_fraction,
        annual_operating_hours=inputs.annual_operating_hours,
        annual_energy_saving_kwh=annual_energy_saving_kwh,
        electricity_tariff_per_kwh=inputs.electricity_tariff_per_kwh,
        annual_cost_saving=annual_cost_saving,
        power_penalty_fraction_per_bar=(inputs.power_penalty_fraction_per_bar),
        power_saving_method=power_saving_method.value,
        pressure_reduction_is_beneficial=(pressure_reduction_bar > 0),
    )


def _adiabatic_power_saving_fraction(
    current_pressure_bar_g: Decimal,
    target_pressure_bar_g: Decimal,
) -> Decimal:
    """Fraction of compressor power saved by an adiabatic pressure reduction.

    saving = 1 - (r_target^((k-1)/k) - 1) / (r_current^((k-1)/k) - 1)
    with r = absolute pressure ratio against the standard atmosphere and
    k = 1.4 for air. Ideal isentropic single-stage compression work basis.
    """

    exponent = (
        ISENTROPIC_EXPONENT_AIR - Decimal("1")
    ) / ISENTROPIC_EXPONENT_AIR

    current_ratio = (
        current_pressure_bar_g + ATMOSPHERIC_PRESSURE_BAR
    ) / ATMOSPHERIC_PRESSURE_BAR
    target_ratio = (
        target_pressure_bar_g + ATMOSPHERIC_PRESSURE_BAR
    ) / ATMOSPHERIC_PRESSURE_BAR

    current_work_term = _decimal_power(current_ratio, exponent) - Decimal("1")
    target_work_term = _decimal_power(target_ratio, exponent) - Decimal("1")

    return Decimal("1") - (target_work_term / current_work_term)


def _decimal_power(base: Decimal, exponent: Decimal) -> Decimal:
    """base ** exponent for positive Decimal base via exp(exponent * ln(base))."""

    return (exponent * base.ln()).exp()


def _validate_inputs(
    inputs: PressureEnergyInput,
) -> None:
    if inputs.current_discharge_pressure_bar_g < 0:
        raise InvalidPressureEnergyInputError("Current discharge pressure cannot be negative.")

    if inputs.optimized_discharge_pressure_bar_g < 0:
        raise InvalidPressureEnergyInputError("Optimized discharge pressure cannot be negative.")

    if inputs.current_average_power_kw <= 0:
        raise InvalidPressureEnergyInputError("Current average power must be greater than zero.")

    if inputs.annual_operating_hours <= 0:
        raise InvalidPressureEnergyInputError("Annual operating hours must be greater than zero.")

    if inputs.electricity_tariff_per_kwh < 0:
        raise InvalidPressureEnergyInputError("Electricity tariff cannot be negative.")

    if inputs.power_penalty_fraction_per_bar is not None and (
        inputs.power_penalty_fraction_per_bar < 0
        or inputs.power_penalty_fraction_per_bar > 1
    ):
        raise InvalidPressureEnergyInputError(
            "Power penalty fraction per bar must be between zero and one."
        )
