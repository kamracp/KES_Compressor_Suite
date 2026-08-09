from dataclasses import dataclass

from app.domain.compressed_air.advanced.advanced_registry import (
    AdvancedEngineeringModule,
)
from app.domain.compressed_air.advanced.application_router import (
    AdvancedRoutingInput,
    AdvancedRoutingResult,
    route_advanced_engineering,
)
from app.domain.compressed_air.advanced.compliance_engine import (
    ComplianceAssessmentResult,
    assess_standards_applicability,
)
from app.domain.compressed_air.advanced.standards_mapping import (
    EngineeringStandard,
)


@dataclass(frozen=True, slots=True)
class AdvancedEngineeringSummary:
    """Integrated advanced-engineering summary for one application."""

    routing: AdvancedRoutingResult
    compliance: ComplianceAssessmentResult

    recommended_module_codes: tuple[str, ...]

    applicable_standard_codes: tuple[str, ...]
    review_required_standard_codes: tuple[str, ...]

    advanced_engineering_required: bool
    standards_review_required: bool

    formal_compliance_claim_available: bool


def build_advanced_engineering_summary(
    inputs: AdvancedRoutingInput,
) -> AdvancedEngineeringSummary:
    """Build routing and standards summary for an advanced application."""

    routing = route_advanced_engineering(inputs)

    requested_modules = tuple(item.module for item in routing.recommended_modules)

    compliance = assess_standards_applicability(
        application_type=inputs.application_type,
        requested_modules=requested_modules,
    )

    recommended_module_codes = tuple(module.value for module in requested_modules)

    applicable_standard_codes = tuple(
        standard.value for standard in compliance.applicable_standards
    )

    review_required_standard_codes = tuple(
        standard.value for standard in compliance.review_required_standards
    )

    standards_review_required = bool(
        applicable_standard_codes
        or review_required_standard_codes
        or inputs.standards_review_required
    )

    return AdvancedEngineeringSummary(
        routing=routing,
        compliance=compliance,
        recommended_module_codes=recommended_module_codes,
        applicable_standard_codes=applicable_standard_codes,
        review_required_standard_codes=review_required_standard_codes,
        advanced_engineering_required=(routing.advanced_engineering_required),
        standards_review_required=standards_review_required,
        formal_compliance_claim_available=(compliance.compliance_claim_available),
    )


def has_advanced_module(
    summary: AdvancedEngineeringSummary,
    module: AdvancedEngineeringModule,
) -> bool:
    """Return whether one advanced engineering module is recommended."""

    return module.value in summary.recommended_module_codes


def has_applicable_standard(
    summary: AdvancedEngineeringSummary,
    standard: EngineeringStandard,
) -> bool:
    """Return whether one standard is directly applicable."""

    return standard.value in summary.applicable_standard_codes
