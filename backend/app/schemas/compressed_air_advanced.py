from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.compressed_air.advanced.advanced_registry import (
    AdvancedApplicationType,
)
from app.domain.compressed_air.station.station_models import (
    CompressorTechnology,
)


class AdvancedEngineeringRequest(BaseModel):
    application_type: AdvancedApplicationType

    compressor_technology: CompressorTechnology | None = None

    discharge_pressure_bar_g: Decimal | None = Field(
        default=None,
        ge=0,
    )

    process_gas_service: bool = False
    high_pressure_service: bool = False

    standards_review_required: bool = False


class AdvancedModuleResponse(BaseModel):
    module_code: str
    title: str
    description: str
    source_package: str


class StandardAssessmentResponse(BaseModel):
    standard_code: str
    title: str

    status: str
    rationale: str

    clause_rules_implemented: bool
    formal_compliance_claim_allowed: bool


class AdvancedEngineeringResponse(BaseModel):
    application_type: str

    advanced_engineering_required: bool
    standards_review_required: bool

    recommended_modules: list[AdvancedModuleResponse]

    applicable_standard_codes: list[str]
    review_required_standard_codes: list[str]

    standard_assessments: list[StandardAssessmentResponse]

    formal_compliance_claim_available: bool

    routing_reasons: list[str]
