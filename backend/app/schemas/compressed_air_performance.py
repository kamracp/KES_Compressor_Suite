from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.compressed_air.performance.performance_models import (
    PerformanceOperatingState,
)


class PerformanceMeasurementInputSchema(BaseModel):
    """One measured compressed-air operating point."""

    timestamp_label: str

    flow_nm3_per_hr: Decimal = Field(ge=0)
    pressure_bar_g: Decimal = Field(ge=0)
    power_kw: Decimal = Field(ge=0)

    operating_state: PerformanceOperatingState | None = None

    load_fraction: Decimal | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    production_state: str | None = None
    notes: str | None = None


class CompressedAirPerformanceAnalysisRequest(BaseModel):
    """Request for standalone compressed-air performance analysis."""

    analysis_code: str

    measurements: list[PerformanceMeasurementInputSchema] = Field(
        min_length=1,
    )

    annual_operating_hours: Decimal = Field(gt=0)

    electricity_tariff_per_kwh: Decimal = Field(
        default=Decimal("0"),
        ge=0,
    )

    rated_capacity_nm3_per_hr: Decimal | None = Field(
        default=None,
        gt=0,
    )

    rated_power_kw: Decimal | None = Field(
        default=None,
        gt=0,
    )

    reference_specific_power_kw_per_nm3_per_min: Decimal | None = Field(
        default=None,
        gt=0,
    )

    optimized_discharge_pressure_bar_g: Decimal | None = Field(
        default=None,
        ge=0,
    )

    power_penalty_fraction_per_bar: Decimal = Field(
        default=Decimal("0.07"),
        ge=0,
        le=1,
    )

    notes: str | None = None


class PressureEnergyPerformanceResponse(BaseModel):
    """Pressure-reduction energy result within performance analysis."""

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

    power_penalty_fraction_per_bar: Decimal

    pressure_reduction_is_beneficial: bool


class CompressedAirPerformanceAnalysisResponse(BaseModel):
    """Measured compressed-air performance and energy result."""

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

    pressure_energy: PressureEnergyPerformanceResponse | None
