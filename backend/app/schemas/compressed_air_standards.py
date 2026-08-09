from pydantic import BaseModel

from app.domain.compressed_air.advanced.advanced_registry import (
    AdvancedApplicationType,
    AdvancedEngineeringModule,
)
from app.domain.compressed_air.advanced.standards_mapping import (
    EngineeringStandard,
)


class StandardsRuleQueryRequest(BaseModel):
    application_type: AdvancedApplicationType | None = None
    standard: EngineeringStandard | None = None
    module: AdvancedEngineeringModule | None = None


class StandardRuleResponse(BaseModel):
    rule_code: str

    standard_code: str
    standard_title: str

    clause_reference: str | None

    title: str
    description: str

    severity: str

    applicable_applications: list[str]
    related_modules: list[str]

    verification_status: str
    implementation_status: str

    source_note: str | None
    engineering_note: str | None

    calculation_binding: str | None

    compliance_claim_allowed: bool


class StandardRuleBindingResponse(BaseModel):
    rule_code: str

    module_code: str

    calculation_binding: str | None

    status: str

    source_verified: bool
    implementation_ready: bool
    executable: bool

    rationale: str


class StandardsRegistrySummaryResponse(BaseModel):
    total_rules: int

    verified_rules: int
    implemented_rules: int
    validated_rules: int

    compliance_claimable_rules: int

    total_bindings: int
    executable_bindings: int


class StandardsRulesResponse(BaseModel):
    summary: StandardsRegistrySummaryResponse

    rules: list[StandardRuleResponse]

    bindings: list[StandardRuleBindingResponse]

    formal_compliance_claim_available: bool
