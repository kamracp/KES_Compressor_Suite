from decimal import Decimal

from pydantic import BaseModel, Field


class GasConditionInput(BaseModel):
    """Gas operating-condition input for compressor calculations."""

    suction_pressure_bar: Decimal = Field(gt=0)
    discharge_pressure_bar: Decimal = Field(gt=0)
    suction_temperature_k: Decimal = Field(gt=0)

    mass_flow_kg_per_s: Decimal = Field(gt=0)
    actual_flow_m3_per_s: Decimal = Field(gt=0)

    molecular_weight_kg_per_kmol: Decimal = Field(gt=0)

    suction_z_factor: Decimal = Field(gt=0)
    discharge_z_factor: Decimal = Field(gt=0)

    isentropic_exponent: Decimal = Field(gt=1)


class CompressionCalculationRequest(BaseModel):
    """Request payload for common compressor thermodynamic calculations."""

    gas: GasConditionInput

    number_of_stages: int = Field(ge=1)

    specific_heat_cp_kj_per_kg_k: Decimal = Field(gt=0)
    isentropic_efficiency: Decimal = Field(gt=0, le=1)
    mechanical_efficiency: Decimal = Field(gt=0, le=1)

    intercooler_outlet_temperature_k: Decimal = Field(gt=0)

    cooling_water_inlet_temperature_k: Decimal = Field(gt=0)
    cooling_water_outlet_temperature_k: Decimal = Field(gt=0)

    selected_driver_power_kw: Decimal = Field(gt=0)
    driver_service_factor: Decimal = Field(ge=0)
    motor_efficiency: Decimal | None = Field(default=None, gt=0, le=1)


class ReciprocatingCalculationRequest(BaseModel):
    """Request payload for reciprocating compressor sizing."""

    required_flow_m3_per_hr: Decimal = Field(gt=0)

    bore_mm: Decimal = Field(gt=0)
    stroke_mm: Decimal = Field(gt=0)
    rod_diameter_mm: Decimal = Field(ge=0)
    speed_rpm: Decimal = Field(gt=0)
    clearance_fraction: Decimal = Field(ge=0, lt=1)

    stage_compression_ratio: Decimal = Field(gt=1)
    suction_z_factor: Decimal = Field(gt=0)
    discharge_z_factor: Decimal = Field(gt=0)
    isentropic_exponent: Decimal = Field(gt=1)

    suction_pressure_bar: Decimal = Field(gt=0)
    discharge_pressure_bar: Decimal = Field(gt=0)

    allowable_rod_load_kn: Decimal = Field(gt=0)


class CentrifugalCalculationRequest(BaseModel):
    """Request payload for centrifugal compressor sizing."""

    gas: GasConditionInput

    polytropic_efficiency: Decimal = Field(gt=0, le=1)

    number_of_impeller_stages: int = Field(ge=1)
    head_coefficient: Decimal = Field(gt=0)
    rotational_speed_rpm: Decimal = Field(gt=0)

    mechanical_loss_fraction: Decimal = Field(ge=0)
    driver_margin_fraction: Decimal = Field(ge=0)

    selected_driver_power_kw: Decimal = Field(gt=0)
    motor_efficiency: Decimal | None = Field(default=None, gt=0, le=1)

    surge_flow_fraction: Decimal = Field(default=Decimal("0.70"), gt=0, lt=1)
    anti_surge_margin_fraction: Decimal = Field(default=Decimal("0.10"), ge=0)
    stonewall_flow_fraction: Decimal = Field(default=Decimal("1.25"), gt=1)


class CompressorSelectionRequest(BaseModel):
    """Request payload for reciprocating-versus-centrifugal selection."""

    required_flow_m3_per_hr: Decimal = Field(gt=0)
    suction_pressure_bar: Decimal = Field(gt=0)
    discharge_pressure_bar: Decimal = Field(gt=0)

    required_turndown_fraction: Decimal = Field(gt=0, le=1)

    continuous_operation: bool

    gas_molecular_weight: Decimal = Field(gt=0)
    estimated_operating_hours_per_year: Decimal = Field(ge=0)
