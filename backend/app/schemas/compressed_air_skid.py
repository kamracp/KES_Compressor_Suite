from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.compressed_air.skid.skid_models import (
    AirSkidAssessmentResult,
    AirSkidConfiguration,
    SkidArrangement,
    SkidComponent,
    SkidComponentType,
)
from app.domain.compressed_air.treatment.air_treatment import DryerType


class SkidComponentRequest(BaseModel):
    component_code: str = Field(
        min_length=1,
        max_length=100,
    )
    name: str = Field(
        min_length=1,
        max_length=255,
    )
    component_type: SkidComponentType

    rated_flow_nm3_per_hr: Decimal | None = Field(
        default=None,
        gt=0,
    )
    rated_pressure_bar_g: Decimal | None = Field(
        default=None,
        gt=0,
    )
    pressure_drop_bar: Decimal = Field(
        default=Decimal("0"),
        ge=0,
    )

    quantity: int = Field(
        default=1,
        ge=1,
    )

    equipment_source: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    model: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    notes: str | None = Field(
        default=None,
        max_length=4000,
    )

    def to_domain(self) -> SkidComponent:
        return SkidComponent(
            component_code=self.component_code,
            name=self.name,
            component_type=self.component_type,
            rated_flow_nm3_per_hr=self.rated_flow_nm3_per_hr,
            rated_pressure_bar_g=self.rated_pressure_bar_g,
            pressure_drop_bar=self.pressure_drop_bar,
            quantity=self.quantity,
            equipment_source=self.equipment_source,
            model=self.model,
            notes=self.notes,
        )


class AirSkidAssessmentRequest(BaseModel):
    skid_code: str = Field(
        min_length=1,
        max_length=100,
    )
    arrangement: SkidArrangement

    design_flow_nm3_per_hr: Decimal = Field(gt=0)
    design_pressure_bar_g: Decimal = Field(
        gt=0,
        le=Decimal("45"),
        description=(
            "Packaged industrial high-pressure air (PET blowing, boosters) reaches 45 "
            "bar g (MFR-ATLASCOPCO-AIR-RANGE-2026-09 DX/DN); reciprocating HX/HN to "
            "150 bar g are process machines outside this input."
        ),
    )
    dryer_type: DryerType

    components: list[SkidComponentRequest] = Field(
        min_length=1,
        max_length=100,
    )

    has_wet_receiver: bool
    has_dry_receiver: bool

    has_flow_metering: bool
    has_pressure_monitoring: bool
    has_dew_point_monitoring: bool

    master_control_enabled: bool

    description: str | None = Field(
        default=None,
        max_length=4000,
    )

    def to_domain(self) -> AirSkidConfiguration:
        return AirSkidConfiguration(
            skid_code=self.skid_code,
            arrangement=self.arrangement,
            design_flow_nm3_per_hr=self.design_flow_nm3_per_hr,
            design_pressure_bar_g=self.design_pressure_bar_g,
            dryer_type=self.dryer_type,
            components=tuple(component.to_domain() for component in self.components),
            has_wet_receiver=self.has_wet_receiver,
            has_dry_receiver=self.has_dry_receiver,
            has_flow_metering=self.has_flow_metering,
            has_pressure_monitoring=self.has_pressure_monitoring,
            has_dew_point_monitoring=self.has_dew_point_monitoring,
            master_control_enabled=self.master_control_enabled,
            description=self.description,
        )


class AirSkidAssessmentResponse(BaseModel):
    skid_code: str

    design_flow_nm3_per_hr: Decimal
    design_pressure_bar_g: Decimal

    total_component_count: int

    total_pressure_drop_bar: Decimal

    minimum_component_flow_capacity_nm3_per_hr: Decimal | None
    minimum_component_pressure_rating_bar_g: Decimal | None

    flow_capacity_is_adequate: bool
    pressure_rating_is_adequate: bool

    has_wet_receiver: bool
    has_dry_receiver: bool

    has_flow_metering: bool
    has_pressure_monitoring: bool
    has_dew_point_monitoring: bool

    master_control_enabled: bool

    instrumentation_is_complete: bool
    skid_is_adequate: bool

    model_config = {
        "from_attributes": True,
    }

    @classmethod
    def from_domain(
        cls,
        result: AirSkidAssessmentResult,
    ) -> "AirSkidAssessmentResponse":
        return cls.model_validate(result)
