from app.domain.compressed_air.advanced.advanced_registry import (
    AdvancedApplicationType,
    AdvancedEngineeringModule,
)
from app.domain.compressed_air.advanced.standard_rules import (
    RuleImplementationStatus,
    RuleSeverity,
    RuleVerificationStatus,
    StandardRule,
    StandardRuleRegistry,
    build_standard_rule_registry,
)
from app.domain.compressed_air.advanced.standards_mapping import (
    EngineeringStandard,
)


def get_standard_rule_catalog() -> tuple[StandardRule, ...]:
    """Return the controlled starter catalog of standards-backed rules."""

    return (
        StandardRule(
            rule_code="API617-CENTRIFUGAL-DESIGN-REVIEW",
            standard=EngineeringStandard.API_617,
            standard_title=("API 617 - Axial and Centrifugal Compressors and Expander-compressors"),
            clause_reference=None,
            title="Centrifugal compressor design review",
            description=(
                "Flag centrifugal process-compressor design for formal API 617 engineering review."
            ),
            severity=RuleSeverity.REQUIREMENT,
            applicable_applications=(
                AdvancedApplicationType.CENTRIFUGAL_PROCESS_COMPRESSOR,
                AdvancedApplicationType.PROCESS_GAS,
            ),
            related_modules=(
                AdvancedEngineeringModule.CENTRIFUGAL_ENGINEERING,
                AdvancedEngineeringModule.PERFORMANCE_MAP,
                AdvancedEngineeringModule.SURGE_ANALYSIS,
            ),
            verification_status=RuleVerificationStatus.UNVERIFIED,
            implementation_status=RuleImplementationStatus.NOT_IMPLEMENTED,
            source_note=(
                "Clause-level source verification is required before "
                "automatic compliance evaluation."
            ),
        ),
        StandardRule(
            rule_code="API618-RECIPROCATING-DESIGN-REVIEW",
            standard=EngineeringStandard.API_618,
            standard_title=(
                "API 618 - Reciprocating Compressors for Petroleum, "
                "Chemical, and Gas Industry Services"
            ),
            clause_reference=None,
            title="Reciprocating compressor design review",
            description=(
                "Flag reciprocating process-compressor design for formal "
                "API 618 engineering review."
            ),
            severity=RuleSeverity.REQUIREMENT,
            applicable_applications=(
                AdvancedApplicationType.RECIPROCATING_PROCESS_COMPRESSOR,
                AdvancedApplicationType.PROCESS_GAS,
                AdvancedApplicationType.HIGH_PRESSURE_AIR,
            ),
            related_modules=(
                AdvancedEngineeringModule.RECIPROCATING_ENGINEERING,
                AdvancedEngineeringModule.ROD_LOAD,
                AdvancedEngineeringModule.COMPRESSION_THERMODYNAMICS,
            ),
            verification_status=RuleVerificationStatus.UNVERIFIED,
            implementation_status=RuleImplementationStatus.NOT_IMPLEMENTED,
            source_note=(
                "Clause-level source verification is required before "
                "automatic compliance evaluation."
            ),
        ),
        StandardRule(
            rule_code="PTC10-PERFORMANCE-TEST-REVIEW",
            standard=EngineeringStandard.ASME_PTC_10,
            standard_title=("ASME PTC 10 - Performance Test Code on Compressors and Exhausters"),
            clause_reference=None,
            title="Compressor performance-test review",
            description=(
                "Flag compressor performance and acceptance calculations "
                "for formal ASME PTC 10 review."
            ),
            severity=RuleSeverity.ADVISORY,
            applicable_applications=(
                AdvancedApplicationType.FACTORY_COMPRESSED_AIR,
                AdvancedApplicationType.HIGH_PRESSURE_AIR,
                AdvancedApplicationType.PROCESS_GAS,
                AdvancedApplicationType.RECIPROCATING_PROCESS_COMPRESSOR,
                AdvancedApplicationType.CENTRIFUGAL_PROCESS_COMPRESSOR,
            ),
            related_modules=(
                AdvancedEngineeringModule.COMPRESSION_THERMODYNAMICS,
                AdvancedEngineeringModule.DRIVER_AND_POWER,
                AdvancedEngineeringModule.CENTRIFUGAL_ENGINEERING,
                AdvancedEngineeringModule.RECIPROCATING_ENGINEERING,
            ),
            verification_status=RuleVerificationStatus.UNVERIFIED,
            implementation_status=RuleImplementationStatus.NOT_IMPLEMENTED,
            source_note=(
                "Performance-test requirements must be source-verified "
                "before executable acceptance rules are added."
            ),
        ),
        StandardRule(
            rule_code="GPSA-GAS-COMPRESSION-REVIEW",
            standard=EngineeringStandard.GPSA_ENGINEERING_DATA_BOOK,
            standard_title="GPSA Engineering Data Book",
            clause_reference=None,
            title="Gas-property and compression engineering review",
            description=(
                "Flag process-gas property and compression calculations "
                "for review against the controlled engineering reference."
            ),
            severity=RuleSeverity.ADVISORY,
            applicable_applications=(
                AdvancedApplicationType.PROCESS_GAS,
                AdvancedApplicationType.HIGH_PRESSURE_AIR,
                AdvancedApplicationType.RECIPROCATING_PROCESS_COMPRESSOR,
                AdvancedApplicationType.CENTRIFUGAL_PROCESS_COMPRESSOR,
            ),
            related_modules=(
                AdvancedEngineeringModule.GAS_PROPERTIES,
                AdvancedEngineeringModule.COMPRESSION_THERMODYNAMICS,
                AdvancedEngineeringModule.COOLING_AND_INTERCOOLING,
            ),
            verification_status=RuleVerificationStatus.UNVERIFIED,
            implementation_status=RuleImplementationStatus.NOT_IMPLEMENTED,
            source_note=(
                "Controlled edition and source location must be verified "
                "before calculation rules are bound."
            ),
        ),
    )


def get_standard_rule_registry() -> StandardRuleRegistry:
    """Return the summarized controlled standards-rule registry."""

    return build_standard_rule_registry(get_standard_rule_catalog())


def get_rules_for_standard(
    standard: EngineeringStandard,
) -> tuple[StandardRule, ...]:
    """Return catalog rules associated with one standard."""

    return tuple(rule for rule in get_standard_rule_catalog() if rule.standard == standard)


def get_rules_for_application(
    application_type: AdvancedApplicationType,
) -> tuple[StandardRule, ...]:
    """Return catalog rules applicable to one application."""

    return tuple(
        rule
        for rule in get_standard_rule_catalog()
        if application_type in rule.applicable_applications
    )
