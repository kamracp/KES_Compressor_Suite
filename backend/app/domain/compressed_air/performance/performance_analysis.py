from decimal import Decimal

from app.domain.compressed_air.energy.pressure_energy import (
    PressureEnergyInput,
    calculate_pressure_energy_saving,
)
from app.domain.compressed_air.performance.performance_models import (
    PerformanceAnalysisInput,
    PerformanceAnalysisResult,
    PerformanceOperatingState,
)

MINUTES_PER_HOUR = Decimal("60")
NM3_PER_1000_NM3 = Decimal("1000")


class InvalidPerformanceAnalysisInputError(ValueError):
    """Raised when standalone compressed-air performance inputs are invalid."""


def analyze_performance(
    inputs: PerformanceAnalysisInput,
) -> PerformanceAnalysisResult:
    """Analyze measured compressed-air system performance."""

    _validate_inputs(inputs)

    measurements = inputs.measurements

    average_flow = _average(tuple(point.flow_nm3_per_hr for point in measurements))
    peak_flow = max(point.flow_nm3_per_hr for point in measurements)
    minimum_flow = min(point.flow_nm3_per_hr for point in measurements)

    average_pressure = _average(tuple(point.pressure_bar_g for point in measurements))
    maximum_pressure = max(point.pressure_bar_g for point in measurements)
    minimum_pressure = min(point.pressure_bar_g for point in measurements)

    average_power = _average(tuple(point.power_kw for point in measurements))
    peak_power = max(point.power_kw for point in measurements)

    measured_specific_power = _calculate_specific_power(
        average_flow_nm3_per_hr=average_flow,
        average_power_kw=average_power,
    )

    measured_specific_energy = _calculate_specific_energy(
        average_flow_nm3_per_hr=average_flow,
        average_power_kw=average_power,
    )

    load_fractions = tuple(
        point.load_fraction for point in measurements if point.load_fraction is not None
    )

    average_load_fraction = _average(load_fractions) if load_fractions else None

    unloaded_count = sum(
        1 for point in measurements if point.operating_state == PerformanceOperatingState.UNLOADED
    )

    unloaded_measurement_fraction = Decimal(unloaded_count) / Decimal(len(measurements))

    average_capacity_utilization = None
    peak_capacity_utilization = None

    if inputs.rated_capacity_nm3_per_hr is not None:
        average_capacity_utilization = average_flow / inputs.rated_capacity_nm3_per_hr
        peak_capacity_utilization = peak_flow / inputs.rated_capacity_nm3_per_hr

    average_power_utilization = None

    if inputs.rated_power_kw is not None:
        average_power_utilization = average_power / inputs.rated_power_kw

    specific_power_deviation = None

    if (
        inputs.reference_specific_power_kw_per_nm3_per_min is not None
        and measured_specific_power is not None
    ):
        reference_specific_power = inputs.reference_specific_power_kw_per_nm3_per_min

        specific_power_deviation = (
            measured_specific_power - reference_specific_power
        ) / reference_specific_power

    annual_energy_kwh = average_power * inputs.annual_operating_hours

    annual_energy_cost = annual_energy_kwh * inputs.electricity_tariff_per_kwh

    pressure_energy = None

    if inputs.optimized_discharge_pressure_bar_g is not None:
        if average_power <= 0:
            raise InvalidPerformanceAnalysisInputError(
                "Pressure optimization requires average measured power greater than zero."
            )

        pressure_energy = calculate_pressure_energy_saving(
            PressureEnergyInput(
                current_discharge_pressure_bar_g=average_pressure,
                optimized_discharge_pressure_bar_g=(inputs.optimized_discharge_pressure_bar_g),
                current_average_power_kw=average_power,
                annual_operating_hours=inputs.annual_operating_hours,
                electricity_tariff_per_kwh=(inputs.electricity_tariff_per_kwh),
                power_penalty_fraction_per_bar=(inputs.power_penalty_fraction_per_bar),
            )
        )

    return PerformanceAnalysisResult(
        analysis_code=inputs.analysis_code,
        measurement_count=len(measurements),
        average_flow_nm3_per_hr=average_flow,
        peak_flow_nm3_per_hr=peak_flow,
        minimum_flow_nm3_per_hr=minimum_flow,
        average_pressure_bar_g=average_pressure,
        maximum_pressure_bar_g=maximum_pressure,
        minimum_pressure_bar_g=minimum_pressure,
        average_power_kw=average_power,
        peak_power_kw=peak_power,
        measured_specific_power_kw_per_nm3_per_min=(measured_specific_power),
        measured_specific_energy_kwh_per_1000_nm3=(measured_specific_energy),
        average_load_fraction=average_load_fraction,
        unloaded_measurement_fraction=(unloaded_measurement_fraction),
        rated_capacity_nm3_per_hr=inputs.rated_capacity_nm3_per_hr,
        average_capacity_utilization_fraction=(average_capacity_utilization),
        peak_capacity_utilization_fraction=(peak_capacity_utilization),
        rated_power_kw=inputs.rated_power_kw,
        average_power_utilization_fraction=(average_power_utilization),
        reference_specific_power_kw_per_nm3_per_min=(
            inputs.reference_specific_power_kw_per_nm3_per_min
        ),
        specific_power_deviation_fraction=(specific_power_deviation),
        annual_operating_hours=inputs.annual_operating_hours,
        annual_energy_kwh=annual_energy_kwh,
        electricity_tariff_per_kwh=(inputs.electricity_tariff_per_kwh),
        annual_energy_cost=annual_energy_cost,
        pressure_energy=pressure_energy,
    )


def _calculate_specific_power(
    *,
    average_flow_nm3_per_hr: Decimal,
    average_power_kw: Decimal,
) -> Decimal | None:
    if average_flow_nm3_per_hr <= 0:
        return None

    average_flow_nm3_per_min = average_flow_nm3_per_hr / MINUTES_PER_HOUR

    return average_power_kw / average_flow_nm3_per_min


def _calculate_specific_energy(
    *,
    average_flow_nm3_per_hr: Decimal,
    average_power_kw: Decimal,
) -> Decimal | None:
    if average_flow_nm3_per_hr <= 0:
        return None

    return average_power_kw / average_flow_nm3_per_hr * NM3_PER_1000_NM3


def _average(
    values: tuple[Decimal, ...],
) -> Decimal:
    if not values:
        raise InvalidPerformanceAnalysisInputError("At least one measurement value is required.")

    return sum(
        values,
        start=Decimal("0"),
    ) / Decimal(len(values))


def _validate_inputs(
    inputs: PerformanceAnalysisInput,
) -> None:
    if not inputs.analysis_code.strip():
        raise InvalidPerformanceAnalysisInputError("Analysis code cannot be empty.")

    if not inputs.measurements:
        raise InvalidPerformanceAnalysisInputError(
            "At least one performance measurement is required."
        )

    if inputs.annual_operating_hours <= 0:
        raise InvalidPerformanceAnalysisInputError(
            "Annual operating hours must be greater than zero."
        )

    if inputs.electricity_tariff_per_kwh < 0:
        raise InvalidPerformanceAnalysisInputError("Electricity tariff cannot be negative.")

    if inputs.rated_capacity_nm3_per_hr is not None and inputs.rated_capacity_nm3_per_hr <= 0:
        raise InvalidPerformanceAnalysisInputError("Rated capacity must be greater than zero.")

    if inputs.rated_power_kw is not None and inputs.rated_power_kw <= 0:
        raise InvalidPerformanceAnalysisInputError("Rated power must be greater than zero.")

    if (
        inputs.reference_specific_power_kw_per_nm3_per_min is not None
        and inputs.reference_specific_power_kw_per_nm3_per_min <= 0
    ):
        raise InvalidPerformanceAnalysisInputError(
            "Reference specific power must be greater than zero."
        )

    if (
        inputs.optimized_discharge_pressure_bar_g is not None
        and inputs.optimized_discharge_pressure_bar_g < 0
    ):
        raise InvalidPerformanceAnalysisInputError(
            "Optimized discharge pressure cannot be negative."
        )

    if inputs.power_penalty_fraction_per_bar is not None and (
        inputs.power_penalty_fraction_per_bar < 0
        or inputs.power_penalty_fraction_per_bar > 1
    ):
        raise InvalidPerformanceAnalysisInputError(
            "Power penalty fraction per bar must be between zero and one."
        )

    for index, point in enumerate(inputs.measurements, start=1):
        if not point.timestamp_label.strip():
            raise InvalidPerformanceAnalysisInputError(
                f"Measurement {index} timestamp label cannot be empty."
            )

        if point.flow_nm3_per_hr < 0:
            raise InvalidPerformanceAnalysisInputError(
                f"Measurement {index} flow cannot be negative."
            )

        if point.pressure_bar_g < 0:
            raise InvalidPerformanceAnalysisInputError(
                f"Measurement {index} pressure cannot be negative."
            )

        if point.power_kw < 0:
            raise InvalidPerformanceAnalysisInputError(
                f"Measurement {index} power cannot be negative."
            )

        if point.load_fraction is not None and (point.load_fraction < 0 or point.load_fraction > 1):
            raise InvalidPerformanceAnalysisInputError(
                f"Measurement {index} load fraction must be between zero and one."
            )
