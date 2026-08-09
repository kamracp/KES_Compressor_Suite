from app.domain.compressed_air.advanced.advanced_registry import (
    AdvancedApplicationType,
    AdvancedEngineeringModule,
)
from app.domain.compressed_air.advanced.compliance_engine import (
    StandardApplicabilityStatus,
    assess_standards_applicability,
)
from app.domain.compressed_air.advanced.standards_mapping import (
    EngineeringStandard,
)


def assessment_map(result):
    return {item.standard: item for item in result.assessments}


def test_reciprocating_process_compressor_applicability() -> None:
    result = assess_standards_applicability(
        application_type=(AdvancedApplicationType.RECIPROCATING_PROCESS_COMPRESSOR)
    )

    assessments = assessment_map(result)

    assert assessments[EngineeringStandard.API_618].status == StandardApplicabilityStatus.APPLICABLE

    assert (
        assessments[EngineeringStandard.ASME_PTC_10].status
        == StandardApplicabilityStatus.APPLICABLE
    )

    assert (
        assessments[EngineeringStandard.GPSA_ENGINEERING_DATA_BOOK].status
        == StandardApplicabilityStatus.APPLICABLE
    )

    assert (
        assessments[EngineeringStandard.API_617].status
        == StandardApplicabilityStatus.NOT_APPLICABLE
    )


def test_centrifugal_process_compressor_applicability() -> None:
    result = assess_standards_applicability(
        application_type=(AdvancedApplicationType.CENTRIFUGAL_PROCESS_COMPRESSOR)
    )

    assessments = assessment_map(result)

    assert assessments[EngineeringStandard.API_617].status == StandardApplicabilityStatus.APPLICABLE

    assert (
        assessments[EngineeringStandard.ASME_PTC_10].status
        == StandardApplicabilityStatus.APPLICABLE
    )

    assert (
        assessments[EngineeringStandard.GPSA_ENGINEERING_DATA_BOOK].status
        == StandardApplicabilityStatus.APPLICABLE
    )

    assert (
        assessments[EngineeringStandard.API_618].status
        == StandardApplicabilityStatus.NOT_APPLICABLE
    )


def test_factory_air_maps_to_ptc_10_only() -> None:
    result = assess_standards_applicability(
        application_type=AdvancedApplicationType.FACTORY_COMPRESSED_AIR
    )

    assessments = assessment_map(result)

    assert (
        assessments[EngineeringStandard.ASME_PTC_10].status
        == StandardApplicabilityStatus.APPLICABLE
    )

    assert (
        assessments[EngineeringStandard.API_617].status
        == StandardApplicabilityStatus.NOT_APPLICABLE
    )

    assert (
        assessments[EngineeringStandard.API_618].status
        == StandardApplicabilityStatus.NOT_APPLICABLE
    )

    assert (
        assessments[EngineeringStandard.GPSA_ENGINEERING_DATA_BOOK].status
        == StandardApplicabilityStatus.NOT_APPLICABLE
    )


def test_module_can_trigger_review_required() -> None:
    result = assess_standards_applicability(
        application_type=AdvancedApplicationType.FACTORY_COMPRESSED_AIR,
        requested_modules=(AdvancedEngineeringModule.ROD_LOAD,),
    )

    assessments = assessment_map(result)

    assert (
        assessments[EngineeringStandard.API_618].status
        == StandardApplicabilityStatus.REVIEW_REQUIRED
    )


def test_surge_module_can_trigger_api_617_review() -> None:
    result = assess_standards_applicability(
        application_type=AdvancedApplicationType.HIGH_PRESSURE_AIR,
        requested_modules=(AdvancedEngineeringModule.SURGE_ANALYSIS,),
    )

    assessments = assessment_map(result)

    assert (
        assessments[EngineeringStandard.API_617].status
        == StandardApplicabilityStatus.REVIEW_REQUIRED
    )


def test_applicable_standard_does_not_allow_compliance_claim_yet() -> None:
    result = assess_standards_applicability(
        application_type=(AdvancedApplicationType.RECIPROCATING_PROCESS_COMPRESSOR)
    )

    assessments = assessment_map(result)

    assert assessments[EngineeringStandard.API_618].formal_compliance_claim_allowed is False

    assert result.compliance_claim_available is False


def test_all_clause_rules_are_still_unimplemented() -> None:
    result = assess_standards_applicability(application_type=AdvancedApplicationType.PROCESS_GAS)

    assert all(item.clause_rules_implemented is False for item in result.assessments)


def test_applicable_standards_summary_is_populated() -> None:
    result = assess_standards_applicability(
        application_type=(AdvancedApplicationType.CENTRIFUGAL_PROCESS_COMPRESSOR)
    )

    assert EngineeringStandard.API_617 in result.applicable_standards
    assert EngineeringStandard.ASME_PTC_10 in result.applicable_standards
    assert EngineeringStandard.GPSA_ENGINEERING_DATA_BOOK in result.applicable_standards


def test_review_required_summary_is_populated() -> None:
    result = assess_standards_applicability(
        application_type=AdvancedApplicationType.FACTORY_COMPRESSED_AIR,
        requested_modules=(AdvancedEngineeringModule.ROD_LOAD,),
    )

    assert EngineeringStandard.API_618 in result.review_required_standards
