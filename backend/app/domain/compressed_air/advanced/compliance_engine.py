from dataclasses import dataclass
from enum import StrEnum

from app.domain.compressed_air.advanced.advanced_registry import (
    AdvancedApplicationType,
    AdvancedEngineeringModule,
)
from app.domain.compressed_air.advanced.standards_mapping import (
    EngineeringStandard,
    StandardMapping,
    get_standards_mapping,
)


class StandardApplicabilityStatus(StrEnum):
    APPLICABLE = "APPLICABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


@dataclass(frozen=True, slots=True)
class StandardApplicabilityResult:
    """Applicability assessment for one engineering standard."""

    standard: EngineeringStandard

    status: StandardApplicabilityStatus

    title: str
    rationale: str

    related_modules: tuple[AdvancedEngineeringModule, ...]

    clause_rules_implemented: bool

    formal_compliance_claim_allowed: bool


@dataclass(frozen=True, slots=True)
class ComplianceAssessmentResult:
    """Standards applicability assessment for one compressor application."""

    application_type: AdvancedApplicationType

    assessments: tuple[StandardApplicabilityResult, ...]

    applicable_standards: tuple[EngineeringStandard, ...]

    review_required_standards: tuple[EngineeringStandard, ...]

    compliance_claim_available: bool


def assess_standards_applicability(
    *,
    application_type: AdvancedApplicationType,
    requested_modules: tuple[AdvancedEngineeringModule, ...] = (),
) -> ComplianceAssessmentResult:
    """Assess which engineering references apply to one application."""

    mappings = get_standards_mapping()

    assessments = tuple(
        _assess_mapping(
            mapping=mapping,
            application_type=application_type,
            requested_modules=requested_modules,
        )
        for mapping in mappings
    )

    applicable_standards = tuple(
        assessment.standard
        for assessment in assessments
        if assessment.status == StandardApplicabilityStatus.APPLICABLE
    )

    review_required_standards = tuple(
        assessment.standard
        for assessment in assessments
        if assessment.status == StandardApplicabilityStatus.REVIEW_REQUIRED
    )

    compliance_claim_available = bool(applicable_standards) and all(
        assessment.formal_compliance_claim_allowed
        for assessment in assessments
        if assessment.status == StandardApplicabilityStatus.APPLICABLE
    )

    return ComplianceAssessmentResult(
        application_type=application_type,
        assessments=assessments,
        applicable_standards=applicable_standards,
        review_required_standards=review_required_standards,
        compliance_claim_available=compliance_claim_available,
    )


def _assess_mapping(
    *,
    mapping: StandardMapping,
    application_type: AdvancedApplicationType,
    requested_modules: tuple[AdvancedEngineeringModule, ...],
) -> StandardApplicabilityResult:
    application_matches = application_type in mapping.applicable_applications

    module_matches = bool(set(requested_modules).intersection(mapping.related_modules))

    if application_matches:
        status = StandardApplicabilityStatus.APPLICABLE

        rationale = (
            "The selected application type is explicitly mapped to this engineering reference."
        )

    elif module_matches:
        status = StandardApplicabilityStatus.REVIEW_REQUIRED

        rationale = (
            "The selected application is not directly mapped, but one or "
            "more requested advanced modules reference this standard."
        )

    else:
        status = StandardApplicabilityStatus.NOT_APPLICABLE

        rationale = (
            "Neither the selected application nor the requested advanced "
            "modules map to this engineering reference."
        )

    formal_compliance_claim_allowed = (
        status == StandardApplicabilityStatus.APPLICABLE and mapping.clause_rules_implemented
    )

    return StandardApplicabilityResult(
        standard=mapping.standard,
        status=status,
        title=mapping.title,
        rationale=rationale,
        related_modules=mapping.related_modules,
        clause_rules_implemented=mapping.clause_rules_implemented,
        formal_compliance_claim_allowed=formal_compliance_claim_allowed,
    )
