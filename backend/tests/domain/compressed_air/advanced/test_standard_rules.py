import pytest

from app.domain.compressed_air.advanced.advanced_registry import (
    AdvancedApplicationType,
    AdvancedEngineeringModule,
)
from app.domain.compressed_air.advanced.standard_rules import (
    RuleImplementationStatus,
    RuleSeverity,
    RuleVerificationStatus,
    StandardRule,
    build_standard_rule_registry,
)
from app.domain.compressed_air.advanced.standards_mapping import (
    EngineeringStandard,
)


def build_rule(
    *,
    rule_code: str,
    verification_status: RuleVerificationStatus,
    implementation_status: RuleImplementationStatus,
    compliance_claim_allowed: bool = False,
) -> StandardRule:
    return StandardRule(
        rule_code=rule_code,
        standard=EngineeringStandard.API_618,
        standard_title="API 618",
        clause_reference=None,
        title=rule_code,
        description="Test standards-backed engineering rule.",
        severity=RuleSeverity.REQUIREMENT,
        applicable_applications=(AdvancedApplicationType.RECIPROCATING_PROCESS_COMPRESSOR,),
        related_modules=(AdvancedEngineeringModule.RECIPROCATING_ENGINEERING,),
        verification_status=verification_status,
        implementation_status=implementation_status,
        compliance_claim_allowed=compliance_claim_allowed,
    )


def test_empty_registry_has_zero_counts() -> None:
    registry = build_standard_rule_registry(())

    assert registry.total_rules == 0
    assert registry.verified_rules == 0
    assert registry.implemented_rules == 0
    assert registry.validated_rules == 0
    assert registry.compliance_claimable_rules == 0


def test_registry_counts_verified_rules() -> None:
    registry = build_standard_rule_registry(
        (
            build_rule(
                rule_code="R-01",
                verification_status=RuleVerificationStatus.UNVERIFIED,
                implementation_status=RuleImplementationStatus.NOT_IMPLEMENTED,
            ),
            build_rule(
                rule_code="R-02",
                verification_status=RuleVerificationStatus.SOURCE_VERIFIED,
                implementation_status=RuleImplementationStatus.NOT_IMPLEMENTED,
            ),
            build_rule(
                rule_code="R-03",
                verification_status=RuleVerificationStatus.ENGINEERING_VERIFIED,
                implementation_status=RuleImplementationStatus.DRAFT,
            ),
            build_rule(
                rule_code="R-04",
                verification_status=RuleVerificationStatus.APPROVED,
                implementation_status=RuleImplementationStatus.IMPLEMENTED,
            ),
        )
    )

    assert registry.total_rules == 4
    assert registry.verified_rules == 3


def test_registry_counts_implemented_rules() -> None:
    registry = build_standard_rule_registry(
        (
            build_rule(
                rule_code="R-01",
                verification_status=RuleVerificationStatus.SOURCE_VERIFIED,
                implementation_status=RuleImplementationStatus.NOT_IMPLEMENTED,
            ),
            build_rule(
                rule_code="R-02",
                verification_status=RuleVerificationStatus.SOURCE_VERIFIED,
                implementation_status=RuleImplementationStatus.DRAFT,
            ),
            build_rule(
                rule_code="R-03",
                verification_status=RuleVerificationStatus.SOURCE_VERIFIED,
                implementation_status=RuleImplementationStatus.IMPLEMENTED,
            ),
            build_rule(
                rule_code="R-04",
                verification_status=RuleVerificationStatus.APPROVED,
                implementation_status=RuleImplementationStatus.VALIDATED,
            ),
        )
    )

    assert registry.implemented_rules == 2
    assert registry.validated_rules == 1


def test_registry_counts_claimable_rules_explicitly() -> None:
    registry = build_standard_rule_registry(
        (
            build_rule(
                rule_code="R-01",
                verification_status=RuleVerificationStatus.APPROVED,
                implementation_status=RuleImplementationStatus.VALIDATED,
                compliance_claim_allowed=True,
            ),
            build_rule(
                rule_code="R-02",
                verification_status=RuleVerificationStatus.APPROVED,
                implementation_status=RuleImplementationStatus.VALIDATED,
                compliance_claim_allowed=False,
            ),
        )
    )

    assert registry.compliance_claimable_rules == 1


def test_duplicate_rule_codes_are_rejected() -> None:
    rule_one = build_rule(
        rule_code="DUPLICATE",
        verification_status=RuleVerificationStatus.SOURCE_VERIFIED,
        implementation_status=RuleImplementationStatus.DRAFT,
    )

    rule_two = build_rule(
        rule_code="DUPLICATE",
        verification_status=RuleVerificationStatus.APPROVED,
        implementation_status=RuleImplementationStatus.VALIDATED,
    )

    with pytest.raises(
        ValueError,
        match="Standard rule codes must be unique",
    ):
        build_standard_rule_registry(
            (
                rule_one,
                rule_two,
            )
        )


def test_unverified_rule_is_not_counted_as_verified() -> None:
    registry = build_standard_rule_registry(
        (
            build_rule(
                rule_code="R-UNVERIFIED",
                verification_status=RuleVerificationStatus.UNVERIFIED,
                implementation_status=RuleImplementationStatus.NOT_IMPLEMENTED,
            ),
        )
    )

    assert registry.verified_rules == 0


def test_draft_rule_is_not_counted_as_implemented() -> None:
    registry = build_standard_rule_registry(
        (
            build_rule(
                rule_code="R-DRAFT",
                verification_status=RuleVerificationStatus.SOURCE_VERIFIED,
                implementation_status=RuleImplementationStatus.DRAFT,
            ),
        )
    )

    assert registry.implemented_rules == 0


def test_validated_rule_is_counted_as_implemented_and_validated() -> None:
    registry = build_standard_rule_registry(
        (
            build_rule(
                rule_code="R-VALIDATED",
                verification_status=RuleVerificationStatus.APPROVED,
                implementation_status=RuleImplementationStatus.VALIDATED,
            ),
        )
    )

    assert registry.implemented_rules == 1
    assert registry.validated_rules == 1


def test_claimability_is_not_inferred_from_validation_status() -> None:
    registry = build_standard_rule_registry(
        (
            build_rule(
                rule_code="R-NO-CLAIM",
                verification_status=RuleVerificationStatus.APPROVED,
                implementation_status=RuleImplementationStatus.VALIDATED,
                compliance_claim_allowed=False,
            ),
        )
    )

    assert registry.validated_rules == 1
    assert registry.compliance_claimable_rules == 0
