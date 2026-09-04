from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.compressed_air.allied.allied_models import (
    AftercoolerConfiguration,
    AftercoolerType,
    AlliedEquipmentAnalysisInput,
    AlliedEquipmentAnalysisResult,
    CondensateDrainConfiguration,
    CondensateDrainType,
    FilterStageConfiguration,
    FilterStageType,
    MoistureSeparatorConfiguration,
    MoistureSeparatorType,
    ReceiverConfiguration,
    RedundancyPhilosophy,
    TreatmentConfiguration,
)
from app.domain.compressed_air.consumers.consumer_models import AirQualityClass
from app.domain.compressed_air.storage.receiver_sizing import ReceiverSizingInput
from app.domain.compressed_air.treatment.air_treatment import (
    AirTreatmentInput,
    DryerType,
)
from app.schemas._bounds import (
    MAX_LINE_ITEM_QUANTITY,
    MAX_PLANT_AIR_PRESSURE_BAR_G,
    MAX_TREATMENT_UNIT_COUNT,
)


class ReceiverSizingInputRequest(BaseModel):
    peak_demand_nm3_per_hr: Decimal = Field(ge=0)
    available_compressor_flow_nm3_per_hr: Decimal = Field(ge=0)

    event_duration_seconds: Decimal = Field(
        gt=0,
        le=Decimal("86400"),
        description=(
            "A receiver demand event longer than one day is a base-load change, not an event."
        ),
    )
    receiver_high_pressure_bar_g: Decimal = Field(
        gt=0,
        le=MAX_PLANT_AIR_PRESSURE_BAR_G,
        description=(
            "Plant-air receiver ceiling. Packaged high-pressure air (PET blowing, "
            "boosters) reaches 45 bar g (MFR-ATLASCOPCO-AIR-RANGE-2026-09 DX/DN) but "
            "is reserved behind a future high-pressure-circuit flag "
            "(MAX_HIGH_PRESSURE_CIRCUIT_BAR_G); reciprocating HX/HN to 150 bar g are "
            "process machines outside this input."
        ),
    )
    receiver_low_pressure_bar_g: Decimal = Field(ge=0, le=MAX_PLANT_AIR_PRESSURE_BAR_G)

    reserve_fraction: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        le=1,
    )

    def to_domain(self) -> ReceiverSizingInput:
        return ReceiverSizingInput(
            peak_demand_nm3_per_hr=self.peak_demand_nm3_per_hr,
            available_compressor_flow_nm3_per_hr=(self.available_compressor_flow_nm3_per_hr),
            event_duration_seconds=self.event_duration_seconds,
            receiver_high_pressure_bar_g=self.receiver_high_pressure_bar_g,
            receiver_low_pressure_bar_g=self.receiver_low_pressure_bar_g,
            reserve_fraction=self.reserve_fraction,
        )


class AirTreatmentInputRequest(BaseModel):
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

    def to_domain(self) -> AirTreatmentInput:
        return AirTreatmentInput(
            required_delivered_flow_nm3_per_hr=(self.required_delivered_flow_nm3_per_hr),
            required_air_quality=self.required_air_quality,
            dryer_type=self.dryer_type,
            dryer_correction_factor=self.dryer_correction_factor,
            dryer_purge_fraction=self.dryer_purge_fraction,
            prefilter_pressure_drop_bar=self.prefilter_pressure_drop_bar,
            afterfilter_pressure_drop_bar=self.afterfilter_pressure_drop_bar,
            dryer_pressure_drop_bar=self.dryer_pressure_drop_bar,
            treatment_capacity_margin_fraction=(self.treatment_capacity_margin_fraction),
        )


class ReceiverConfigurationRequest(BaseModel):
    sizing_input: ReceiverSizingInputRequest

    selected_receiver_volume_m3: Decimal | None = Field(
        default=None,
        gt=0,
    )
    receiver_quantity: int = Field(
        le=MAX_LINE_ITEM_QUANTITY,
        default=1,
        ge=1,
    )
    design_pressure_bar_g: Decimal | None = Field(
        default=None,
        ge=0,
        le=MAX_PLANT_AIR_PRESSURE_BAR_G,
        description=(
            "Receiver vessel design pressure. Part of the plant-air circuit, so it "
            "shares the plant-air ceiling; the 45 bar g packaged high-pressure "
            "figure (MAX_HIGH_PRESSURE_CIRCUIT_BAR_G) applies only behind a future "
            "high-pressure-circuit flag (C-7, 4 Sep 2026)."
        ),
    )

    redundancy_philosophy: RedundancyPhilosophy = RedundancyPhilosophy.NONE

    equipment_reference: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    notes: str | None = Field(
        default=None,
        max_length=4000,
    )

    def to_domain(self) -> ReceiverConfiguration:
        return ReceiverConfiguration(
            sizing_input=self.sizing_input.to_domain(),
            selected_receiver_volume_m3=self.selected_receiver_volume_m3,
            receiver_quantity=self.receiver_quantity,
            design_pressure_bar_g=self.design_pressure_bar_g,
            redundancy_philosophy=self.redundancy_philosophy,
            equipment_reference=self.equipment_reference,
            notes=self.notes,
        )


class TreatmentConfigurationRequest(BaseModel):
    sizing_input: AirTreatmentInputRequest

    selected_treatment_capacity_nm3_per_hr: Decimal | None = Field(
        default=None,
        gt=0,
    )
    installed_unit_count: int = Field(
        le=MAX_TREATMENT_UNIT_COUNT,
        default=1,
        ge=1,
    )
    duty_unit_count: int = Field(
        le=MAX_TREATMENT_UNIT_COUNT,
        default=1,
        ge=1,
    )

    redundancy_philosophy: RedundancyPhilosophy = RedundancyPhilosophy.NONE

    equipment_reference: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    notes: str | None = Field(
        default=None,
        max_length=4000,
    )

    def to_domain(self) -> TreatmentConfiguration:
        return TreatmentConfiguration(
            sizing_input=self.sizing_input.to_domain(),
            selected_treatment_capacity_nm3_per_hr=(self.selected_treatment_capacity_nm3_per_hr),
            installed_unit_count=self.installed_unit_count,
            duty_unit_count=self.duty_unit_count,
            redundancy_philosophy=self.redundancy_philosophy,
            equipment_reference=self.equipment_reference,
            notes=self.notes,
        )


class AftercoolerConfigurationRequest(BaseModel):
    aftercooler_type: AftercoolerType

    selected_flow_capacity_nm3_per_hr: Decimal | None = Field(
        default=None,
        gt=0,
    )
    pressure_drop_bar: Decimal = Field(
        default=Decimal("0"),
        ge=0,
    )

    inlet_temperature_c: Decimal | None = None
    outlet_temperature_c: Decimal | None = None

    equipment_reference: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    notes: str | None = Field(
        default=None,
        max_length=4000,
    )

    def to_domain(self) -> AftercoolerConfiguration:
        return AftercoolerConfiguration(
            aftercooler_type=self.aftercooler_type,
            selected_flow_capacity_nm3_per_hr=(self.selected_flow_capacity_nm3_per_hr),
            pressure_drop_bar=self.pressure_drop_bar,
            inlet_temperature_c=self.inlet_temperature_c,
            outlet_temperature_c=self.outlet_temperature_c,
            equipment_reference=self.equipment_reference,
            notes=self.notes,
        )


class MoistureSeparatorConfigurationRequest(BaseModel):
    separator_type: MoistureSeparatorType

    selected_flow_capacity_nm3_per_hr: Decimal | None = Field(
        default=None,
        gt=0,
    )
    pressure_drop_bar: Decimal = Field(
        default=Decimal("0"),
        ge=0,
    )

    equipment_reference: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    notes: str | None = Field(
        default=None,
        max_length=4000,
    )

    def to_domain(self) -> MoistureSeparatorConfiguration:
        return MoistureSeparatorConfiguration(
            separator_type=self.separator_type,
            selected_flow_capacity_nm3_per_hr=(self.selected_flow_capacity_nm3_per_hr),
            pressure_drop_bar=self.pressure_drop_bar,
            equipment_reference=self.equipment_reference,
            notes=self.notes,
        )


class FilterStageConfigurationRequest(BaseModel):
    stage_code: str = Field(
        min_length=1,
        max_length=100,
    )
    stage_type: FilterStageType

    selected_flow_capacity_nm3_per_hr: Decimal | None = Field(
        default=None,
        gt=0,
    )
    pressure_drop_bar: Decimal = Field(
        default=Decimal("0"),
        ge=0,
    )

    equipment_reference: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    notes: str | None = Field(
        default=None,
        max_length=4000,
    )

    def to_domain(self) -> FilterStageConfiguration:
        return FilterStageConfiguration(
            stage_code=self.stage_code,
            stage_type=self.stage_type,
            selected_flow_capacity_nm3_per_hr=(self.selected_flow_capacity_nm3_per_hr),
            pressure_drop_bar=self.pressure_drop_bar,
            equipment_reference=self.equipment_reference,
            notes=self.notes,
        )


class CondensateDrainConfigurationRequest(BaseModel):
    drain_code: str = Field(
        min_length=1,
        max_length=100,
    )
    location: str = Field(
        min_length=1,
        max_length=255,
    )
    drain_type: CondensateDrainType

    selected_condensate_capacity_l_per_hr: Decimal | None = Field(
        default=None,
        gt=0,
    )

    equipment_reference: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    notes: str | None = Field(
        default=None,
        max_length=4000,
    )

    def to_domain(self) -> CondensateDrainConfiguration:
        return CondensateDrainConfiguration(
            drain_code=self.drain_code,
            location=self.location,
            drain_type=self.drain_type,
            selected_condensate_capacity_l_per_hr=(self.selected_condensate_capacity_l_per_hr),
            equipment_reference=self.equipment_reference,
            notes=self.notes,
        )


class AlliedEquipmentAnalysisRequest(BaseModel):
    analysis_code: str = Field(
        min_length=1,
        max_length=100,
    )

    receiver: ReceiverConfigurationRequest | None = None
    treatment: TreatmentConfigurationRequest | None = None
    aftercooler: AftercoolerConfigurationRequest | None = None
    moisture_separator: MoistureSeparatorConfigurationRequest | None = None

    filter_stages: list[FilterStageConfigurationRequest] = Field(
        default_factory=list,
        max_length=20,
    )
    condensate_drains: list[CondensateDrainConfigurationRequest] = Field(
        default_factory=list,
        max_length=100,
    )

    notes: str | None = Field(
        default=None,
        max_length=4000,
    )

    def to_domain(self) -> AlliedEquipmentAnalysisInput:
        return AlliedEquipmentAnalysisInput(
            analysis_code=self.analysis_code,
            receiver=self.receiver.to_domain() if self.receiver else None,
            treatment=self.treatment.to_domain() if self.treatment else None,
            aftercooler=self.aftercooler.to_domain() if self.aftercooler else None,
            moisture_separator=(
                self.moisture_separator.to_domain() if self.moisture_separator else None
            ),
            filter_stages=tuple(item.to_domain() for item in self.filter_stages),
            condensate_drains=tuple(item.to_domain() for item in self.condensate_drains),
            notes=self.notes,
        )


class ReceiverSizingResultResponse(BaseModel):
    peak_demand_nm3_per_hr: Decimal
    available_compressor_flow_nm3_per_hr: Decimal
    flow_deficit_nm3_per_hr: Decimal

    event_duration_seconds: Decimal

    receiver_high_pressure_bar_g: Decimal
    receiver_low_pressure_bar_g: Decimal
    pressure_band_bar: Decimal

    base_receiver_volume_m3: Decimal
    reserve_fraction: Decimal
    recommended_receiver_volume_m3: Decimal

    storage_required: bool

    model_config = {
        "from_attributes": True,
    }


class AirTreatmentResultResponse(BaseModel):
    required_delivered_flow_nm3_per_hr: Decimal

    dryer_purge_loss_nm3_per_hr: Decimal
    gross_flow_before_purge_nm3_per_hr: Decimal

    corrected_required_treatment_capacity_nm3_per_hr: Decimal
    recommended_treatment_capacity_nm3_per_hr: Decimal

    total_treatment_pressure_drop_bar: Decimal

    dryer_type: str
    required_air_quality: str

    purge_loss_fraction: Decimal
    correction_factor: Decimal
    treatment_capacity_margin_fraction: Decimal

    model_config = {
        "from_attributes": True,
    }


class EquipmentCapacityEvaluationResponse(BaseModel):
    equipment_code: str

    required_capacity: Decimal
    selected_capacity: Decimal | None

    capacity_margin: Decimal | None
    capacity_margin_fraction: Decimal | None

    status: str

    model_config = {
        "from_attributes": True,
    }


class EngineeringRecommendationResponse(BaseModel):
    recommendation_code: str
    severity: str

    equipment_code: str
    message: str
    rationale: str

    model_config = {
        "from_attributes": True,
    }


class AlliedEquipmentAnalysisResponse(BaseModel):
    analysis_code: str

    receiver_result: ReceiverSizingResultResponse | None
    treatment_result: AirTreatmentResultResponse | None

    receiver_evaluation: EquipmentCapacityEvaluationResponse | None
    treatment_evaluation: EquipmentCapacityEvaluationResponse | None
    aftercooler_evaluation: EquipmentCapacityEvaluationResponse | None
    moisture_separator_evaluation: EquipmentCapacityEvaluationResponse | None

    filter_evaluations: list[EquipmentCapacityEvaluationResponse]

    total_additional_pressure_drop_bar: Decimal

    recommendations: list[EngineeringRecommendationResponse]

    notes: str | None

    model_config = {
        "from_attributes": True,
    }

    @classmethod
    def from_domain(
        cls,
        result: AlliedEquipmentAnalysisResult,
    ) -> "AlliedEquipmentAnalysisResponse":
        return cls.model_validate(result)
