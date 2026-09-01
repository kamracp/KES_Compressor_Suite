from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.compressed_air.brownfield.audit_models import (
    AuditOperatingState,
)
from app.domain.compressed_air.station.station_models import (
    CompressorControlMode,
    CompressorTechnology,
)
from app.schemas._bounds import MAX_PLANT_AIR_PRESSURE_BAR_G


class ExistingCompressorInputSchema(BaseModel):
    unit_code: str

    equipment_source: str | None = Field(
        default=None,
        description=(
            "Vendor-neutral equipment source, make reference, "
            "or traceable equipment identification."
        ),
    )

    manufacturer: str | None = Field(
        default=None,
        description=("Legacy compatibility field. Prefer equipment_source for new integrations."),
    )

    model: str | None = None

    technology: CompressorTechnology
    control_mode: CompressorControlMode

    rated_fad_nm3_per_hr: Decimal = Field(gt=0)
    rated_discharge_pressure_bar_g: Decimal = Field(ge=0, le=MAX_PLANT_AIR_PRESSURE_BAR_G)
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
    measured_discharge_pressure_bar_g: Decimal = Field(ge=0, le=MAX_PLANT_AIR_PRESSURE_BAR_G)
    measured_power_kw: Decimal = Field(ge=0)

    load_fraction: Decimal | None = Field(
        default=None,
        ge=0,
        le=1,
    )


class SystemMeasurementInputSchema(BaseModel):
    timestamp_label: str

    total_flow_nm3_per_hr: Decimal = Field(ge=0)
    header_pressure_bar_g: Decimal = Field(ge=0, le=MAX_PLANT_AIR_PRESSURE_BAR_G)
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

    # Fraction of avoided demand converted to electrical saving by the
    # compressor controls (1 = fully effective turndown such as VSD or a
    # well-sequenced station; ~0.5 for inlet modulation without unloading).
    demand_saving_control_factor: Decimal = Field(
        default=Decimal("1"),
        ge=0,
        le=1,
        description=(
            "Fraction of avoided air demand that the compressor "
            "controls convert into electrical savings. 1 = fully "
            "effective turndown (VSD, on/off, or a well-sequenced "
            "station); load/unload typically 0.3-0.6; inlet modulation "
            "without unloading roughly 0.3. Ref: US DOE / Compressed "
            "Air Challenge, 'Improving Compressed Air System "
            "Performance: A Sourcebook for Industry'."
        ),
    )

    # None (default) selects the adiabatic isentropic-work saving method;
    # a value selects the legacy linear per-bar override.
    power_penalty_fraction_per_bar: Decimal | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    condensate_drain_air_loss_nm3_per_hr: Decimal | None = Field(
        default=None,
        ge=0,
        description=(
            "Total Nm3/hr of compressed air expelled by timed solenoid "
            "condensate drains regardless of condensate level. Replacing "
            "with zero-loss drains eliminates this waste entirely. "
            "Ref: US DOE / Compressed Air Challenge Sourcebook."
        ),
    )

    filter_excess_pressure_drop_bar: Decimal | None = Field(
        default=None,
        ge=0,
        le=1,
        description=(
            "Extra pressure drop across dirty or undersized filter "
            "elements beyond their clean design delta-p (bar). "
            "Bounded at 1 bar: a clean element runs near 0.14 bar "
            "(2 psi) and replacement is advised by roughly 0.35 bar "
            "(5 psi), so a larger figure is a data-entry error rather "
            "than a filter condition. "
            "Ref: US DOE / Compressed Air Challenge Sourcebook."
        ),
    )

    # -- Motor & power-factor measurement (C-6) --------------------
    # All four measurement fields are optional; the PF-CORRECTION
    # opportunity is raised only when voltage, current and power factor
    # are all supplied. Ref: IEEE Std 141 (Red Book), IS 15167 Part 1.
    motor_measured_voltage_v: Decimal | None = Field(
        default=None,
        gt=0,
        description=(
            "Measured line-to-line voltage at the compressor motor "
            "terminals (V, three-phase). Ref: IEEE Std 141."
        ),
    )

    motor_measured_current_a: Decimal | None = Field(
        default=None,
        ge=0,
        description=(
            "Measured line current at the compressor motor (A, three-phase). Ref: IEEE Std 141."
        ),
    )

    motor_measured_power_factor: Decimal | None = Field(
        default=None,
        gt=0,
        le=1,
        description=(
            "Measured displacement power factor at the compressor motor (0-1). Ref: IEEE Std 141."
        ),
    )

    motor_target_power_factor: Decimal = Field(
        default=Decimal("0.95"),
        gt=0,
        le=1,
        description=(
            "Target power factor after correction. Default 0.95 is the "
            "threshold above which most Indian state utility tariffs "
            "stop levying a power-factor penalty; set to the value your "
            "own tariff requires. Ref: IS 15167 Part 1."
        ),
    )

    motor_rated_power_kw: Decimal | None = Field(
        default=None,
        gt=0,
        description=(
            "Motor nameplate rated power (kW). Used only to report the "
            "deviation of measured power from nameplate."
        ),
    )

    pf_penalty_annual_cost: Decimal | None = Field(
        default=None,
        ge=0,
        description=(
            "Power-factor penalty or kVAh surcharge the utility is "
            "currently billing this site per year, in local currency. "
            "User-supplied only: penalty structures differ by state "
            "utility, so no saving is claimed without this figure."
        ),
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


class MotorPfcResponse(BaseModel):
    """
    Measured motor power and power-factor correction sizing.

    P    = sqrt3 x V x I x PF        (IEEE Std 141)
    Q_c  = P x (tan phi1 - tan phi2) (IS 15167 Part 1)
    """

    measured_voltage_v: Decimal
    measured_current_a: Decimal
    measured_power_factor: Decimal
    target_power_factor: Decimal

    measured_active_power_kw: Decimal
    measured_reactive_power_kvar: Decimal
    target_reactive_power_kvar: Decimal

    required_capacitor_kvar: Decimal

    pfc_correction_beneficial: bool

    power_deviation_from_nameplate: Decimal | None


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

    # Populated only when motor voltage, current and power factor were
    # all supplied. Power-factor correction carries no kW or kWh saving
    # (see PF-CORRECTION opportunity rationale).
    motor_pfc: MotorPfcResponse | None = None

    opportunities: list[BrownfieldOpportunityResponse]
