from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.compressed_air.consumers.consumer_models import (
    AirConsumerCategory,
    AirConsumptionBasis,
    AirQualityClass,
    ConsumerCriticality,
)
from app.domain.compressed_air.station.station_models import (
    CompressorControlMode,
    CompressorDutyRole,
    CompressorTechnology,
    RedundancyPhilosophy,
)
from app.domain.compressed_air.treatment.air_treatment import DryerType
from app.schemas._bounds import MAX_PLANT_AIR_PRESSURE_BAR_G


class AirConsumerInputSchema(BaseModel):
    consumer_code: str
    name: str
    category: AirConsumerCategory

    quantity: int = Field(gt=0)

    required_pressure_bar_g: Decimal = Field(ge=0, le=MAX_PLANT_AIR_PRESSURE_BAR_G)
    air_quality_class: AirQualityClass

    consumption_basis: AirConsumptionBasis

    flow_per_unit_nm3_per_hr: Decimal | None = Field(
        default=None,
        ge=0,
    )

    air_per_cycle_nl: Decimal | None = Field(
        default=None,
        ge=0,
    )

    cycles_per_minute: Decimal | None = Field(
        default=None,
        ge=0,
    )

    duty_factor: Decimal = Field(
        default=Decimal("1"),
        ge=0,
        le=1,
    )

    simultaneity_factor: Decimal = Field(
        default=Decimal("1"),
        ge=0,
        le=1,
    )

    operating_hours_per_day: Decimal = Field(
        default=Decimal("24"),
        ge=0,
        le=24,
    )

    operating_days_per_year: Decimal = Field(
        default=Decimal("365"),
        ge=0,
        le=366,
    )

    criticality: ConsumerCriticality = ConsumerCriticality.NORMAL

    area: str | None = None
    production_line: str | None = None
    notes: str | None = None


class DemandProfilePointInputSchema(BaseModel):
    period_index: int = Field(ge=0)
    label: str

    demand_nm3_per_hr: Decimal = Field(ge=0)
    required_pressure_bar_g: Decimal = Field(ge=0, le=MAX_PLANT_AIR_PRESSURE_BAR_G)

    duration_hours: Decimal = Field(gt=0)


class PressureLossComponentInputSchema(BaseModel):
    component_code: str
    name: str

    pressure_drop_bar: Decimal = Field(ge=0)

    category: str

    notes: str | None = None


class AirTreatmentInputSchema(BaseModel):
    required_delivered_flow_nm3_per_hr: Decimal = Field(gt=0)

    required_air_quality: AirQualityClass
    dryer_type: DryerType

    dryer_correction_factor: Decimal = Field(
        default=Decimal("1"),
        gt=0,
    )

    dryer_purge_fraction: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        lt=1,
    )

    prefilter_pressure_drop_bar: Decimal = Field(
        default=Decimal("0"),
        ge=0,
    )

    afterfilter_pressure_drop_bar: Decimal = Field(
        default=Decimal("0"),
        ge=0,
    )

    dryer_pressure_drop_bar: Decimal = Field(
        default=Decimal("0"),
        ge=0,
    )

    treatment_capacity_margin_fraction: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        le=1,
    )


class CompressorUnitInputSchema(BaseModel):
    unit_code: str

    technology: CompressorTechnology
    control_mode: CompressorControlMode
    duty_role: CompressorDutyRole

    rated_fad_nm3_per_hr: Decimal = Field(gt=0)

    minimum_stable_flow_fraction: Decimal = Field(
        ge=0,
        le=1,
    )

    rated_discharge_pressure_bar_g: Decimal = Field(ge=0, le=MAX_PLANT_AIR_PRESSURE_BAR_G)

    rated_motor_power_kw: Decimal | None = Field(
        default=None,
        gt=0,
    )

    specific_power_kw_per_nm3_per_min: Decimal | None = Field(
        default=None,
        gt=0,
    )

    available: bool = True
    notes: str | None = None


class CompressorStationInputSchema(BaseModel):
    station_code: str

    units: list[CompressorUnitInputSchema] = Field(
        min_length=1,
    )

    redundancy_philosophy: RedundancyPhilosophy

    minimum_required_pressure_bar_g: Decimal = Field(ge=0, le=MAX_PLANT_AIR_PRESSURE_BAR_G)
    design_flow_nm3_per_hr: Decimal = Field(gt=0)

    master_control_enabled: bool = False


class ReceiverSizingInputSchema(BaseModel):
    peak_demand_nm3_per_hr: Decimal = Field(ge=0)

    available_compressor_flow_nm3_per_hr: Decimal = Field(ge=0)

    event_duration_seconds: Decimal = Field(gt=0)

    receiver_high_pressure_bar_g: Decimal = Field(ge=0, le=MAX_PLANT_AIR_PRESSURE_BAR_G)
    receiver_low_pressure_bar_g: Decimal = Field(ge=0, le=MAX_PLANT_AIR_PRESSURE_BAR_G)

    reserve_fraction: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        le=1,
    )


class GreenfieldSystemDesignRequest(BaseModel):
    consumers: list[AirConsumerInputSchema] = Field(
        min_length=1,
    )

    demand_profile_points: list[DemandProfilePointInputSchema] = Field(
        min_length=1,
    )

    leakage_fraction: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        le=1,
    )

    future_expansion_fraction: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        le=1,
    )

    other_allowance_fraction: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        le=1,
    )

    minimum_point_of_use_pressure_bar_g: Decimal = Field(
        default=Decimal("6"),
        ge=0,
    )

    pressure_loss_components: list[PressureLossComponentInputSchema] = []

    control_margin_bar: Decimal = Field(
        default=Decimal("0"),
        ge=0,
    )

    treatment: AirTreatmentInputSchema | None = None

    station: CompressorStationInputSchema | None = None

    receiver: ReceiverSizingInputSchema | None = None

    specific_power_kw_per_nm3_per_min: Decimal | None = Field(
        default=None,
        gt=0,
    )

    annual_operating_days: Decimal | None = Field(
        default=None,
        gt=0,
    )

    electricity_tariff_per_kwh: Decimal = Field(
        default=Decimal("0"),
        ge=0,
    )


class GreenfieldSystemDesignResponse(BaseModel):
    required_design_flow_nm3_per_hr: Decimal

    required_compressor_discharge_pressure_bar_g: Decimal

    simultaneous_demand_nm3_per_hr: Decimal
    peak_profile_demand_nm3_per_hr: Decimal

    leakage_allowance_nm3_per_hr: Decimal
    future_expansion_allowance_nm3_per_hr: Decimal

    treatment_capacity_nm3_per_hr: Decimal | None

    station_available_capacity_nm3_per_hr: Decimal | None
    station_capacity_is_adequate: bool | None

    receiver_volume_m3: Decimal | None
    receiver_storage_required: bool | None

    annual_energy_kwh: Decimal | None
    annual_energy_cost: Decimal | None

    system_design_is_feasible: bool

    engineering_messages: list[str]
