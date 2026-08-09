from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.compressed_air.brownfield.audit_models import (
    AuditOperatingState,
)
from app.domain.compressed_air.station.station_models import (
    CompressorControlMode,
    CompressorTechnology,
)


class ExistingCompressorInputSchema(BaseModel):
    unit_code: str

    manufacturer: str | None = None
    model: str | None = None

    technology: CompressorTechnology
    control_mode: CompressorControlMode

    rated_fad_nm3_per_hr: Decimal = Field(gt=0)
    rated_discharge_pressure_bar_g: Decimal = Field(ge=0)
    rated_motor_power_kw: Decimal = Field(gt=0)

    installation_year: int | None = None
    operating_hours: Decimal | None = Field(default=None, ge=0)

    available: bool = True
    notes: str | None = None


class CompressorMeasurementInputSchema(BaseModel):
    unit_code: str
    timestamp_label: str

    operating_state: AuditOperatingState

    measured_flow_nm3_per_hr: Decimal = Field(ge=0)
    measured_discharge_pressure_bar_g: Decimal = Field(ge=0)
    measured_power_kw: Decimal = Field(ge=0)

    load_fraction: Decimal | None = Field(
        default=None,
        ge=0,
        le=1,
    )


class SystemMeasurementInputSchema(BaseModel):
    timestamp_label: str

    total_flow_nm3_per_hr: Decimal = Field(ge=0)
    header_pressure_bar_g: Decimal = Field(ge=0)
    total_power_kw: Decimal = Field(ge=0)

    production_state: str | None = None
    notes: str | None = None


class LeakageSurveyInputSchema(BaseModel):
    measured_leakage_flow_nm3_per_hr: Decimal = Field(ge=0)

    survey_method: str

    estimated_repair_fraction: Decimal = Field(
        default=Decimal("0.80"),
        ge=0,
        le=1,
    )

    survey_notes: str | None = None


class BrownfieldSystemAuditRequest(BaseModel):
    audit_code: str
    project_id: int = Field(gt=0)

    compressors: list[ExistingCompressorInputSchema] = Field(
        min_length=1,
    )

    compressor_measurements: list[CompressorMeasurementInputSchema] = []

    system_measurements: list[SystemMeasurementInputSchema] = Field(
        min_length=1,
    )

    leakage_summary: LeakageSurveyInputSchema | None = None

    electricity_tariff_per_kwh: Decimal = Field(
        default=Decimal("0"),
        ge=0,
    )

    annual_operating_hours: Decimal = Field(gt=0)

    optimized_discharge_pressure_bar_g: Decimal | None = Field(
        default=None,
        ge=0,
    )

    expected_leak_repair_fraction: Decimal = Field(
        default=Decimal("0.80"),
        ge=0,
        le=1,
    )

    power_penalty_fraction_per_bar: Decimal = Field(
        default=Decimal("0.07"),
        ge=0,
        le=1,
    )

    notes: str | None = None


class BrownfieldOpportunityResponse(BaseModel):
    opportunity_code: str
    category: str
    priority: str

    title: str
    rationale: str

    estimated_power_saving_kw: Decimal
    estimated_annual_energy_saving_kwh: Decimal
    estimated_annual_cost_saving: Decimal


class BrownfieldSystemAuditResponse(BaseModel):
    audit_code: str
    project_id: int

    installed_capacity_nm3_per_hr: Decimal
    available_capacity_nm3_per_hr: Decimal

    average_system_flow_nm3_per_hr: Decimal
    peak_system_flow_nm3_per_hr: Decimal
    minimum_system_flow_nm3_per_hr: Decimal

    average_system_power_kw: Decimal
    peak_system_power_kw: Decimal

    average_header_pressure_bar_g: Decimal
    minimum_header_pressure_bar_g: Decimal
    maximum_header_pressure_bar_g: Decimal

    average_capacity_utilization_fraction: Decimal
    peak_capacity_utilization_fraction: Decimal

    measured_specific_power_kw_per_nm3_per_min: Decimal | None

    unloaded_measurement_fraction: Decimal

    leakage_flow_nm3_per_hr: Decimal
    leakage_fraction_of_average_demand: Decimal

    current_annual_energy_kwh: Decimal
    current_annual_energy_cost: Decimal

    estimated_total_power_saving_kw: Decimal
    estimated_total_annual_energy_saving_kwh: Decimal
    estimated_total_annual_cost_saving: Decimal

    estimated_optimized_average_power_kw: Decimal
    estimated_optimized_annual_energy_kwh: Decimal
    estimated_optimized_annual_energy_cost: Decimal

    estimated_energy_reduction_fraction: Decimal

    installed_capacity_is_sufficient_for_peak: bool
    high_unloaded_running_detected: bool
    significant_leakage_detected: bool

    opportunities: list[BrownfieldOpportunityResponse]
