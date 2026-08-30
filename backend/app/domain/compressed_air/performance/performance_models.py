from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from app.domain.compressed_air.energy.pressure_energy import PressureEnergyResult


class PerformanceOperatingState(StrEnum):
    """Observed operating state used in performance analysis."""

    LOADED = "LOADED"
    UNLOADED = "UNLOADED"
    PART_LOAD = "PART_LOAD"
    STOPPED = "STOPPED"


@dataclass(frozen=True, slots=True)
class PerformanceMeasurementPoint:
    """One measured compressed-air system operating point."""

    timestamp_label: str

    flow_nm3_per_hr: Decimal
    pressure_bar_g: Decimal
    power_kw: Decimal

    operating_state: PerformanceOperatingState | None = None
    load_fraction: Decimal | None = None

    production_state: str | None = None
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class PerformanceAnalysisInput:
    """Input basis for standalone compressed-air performance analysis."""

    analysis_code: str

    measurements: tuple[PerformanceMeasurementPoint, ...]

    annual_operating_hours: Decimal
    electricity_tariff_per_kwh: Decimal = Decimal("0")

    rated_capacity_nm3_per_hr: Decimal | None = None
    rated_power_kw: Decimal | None = None

    reference_specific_power_kw_per_nm3_per_min: Decimal | None = None

    optimized_discharge_pressure_bar_g: Decimal | None = None
    power_penalty_fraction_per_bar: Decimal | None = None

    notes: str | None = None


@dataclass(frozen=True, slots=True)
class PerformanceAnalysisResult:
    """Calculated measured performance of a compressed-air system."""

    analysis_code: str
    measurement_count: int

    average_flow_nm3_per_hr: Decimal
    peak_flow_nm3_per_hr: Decimal
    minimum_flow_nm3_per_hr: Decimal

    average_pressure_bar_g: Decimal
    maximum_pressure_bar_g: Decimal
    minimum_pressure_bar_g: Decimal

    average_power_kw: Decimal
    peak_power_kw: Decimal

    measured_specific_power_kw_per_nm3_per_min: Decimal | None
    measured_specific_energy_kwh_per_1000_nm3: Decimal | None

    average_load_fraction: Decimal | None
    unloaded_measurement_fraction: Decimal

    rated_capacity_nm3_per_hr: Decimal | None
    average_capacity_utilization_fraction: Decimal | None
    peak_capacity_utilization_fraction: Decimal | None

    rated_power_kw: Decimal | None
    average_power_utilization_fraction: Decimal | None

    reference_specific_power_kw_per_nm3_per_min: Decimal | None
    specific_power_deviation_fraction: Decimal | None

    annual_operating_hours: Decimal
    annual_energy_kwh: Decimal

    electricity_tariff_per_kwh: Decimal
    annual_energy_cost: Decimal

    pressure_energy: PressureEnergyResult | None
