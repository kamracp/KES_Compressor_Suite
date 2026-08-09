from app.domain.compressed_air.advanced.advanced_registry import (
    AdvancedApplicationType,
    AdvancedEngineeringModule,
)
from app.domain.compressed_air.advanced.rule_evaluator import (
    RuleEvaluationContext,
    RuleEvaluationStatus,
    evaluate_standard_rule,
)
from app.domain.compressed_air.advanced.standard_rules import (
    RuleImplementationStatus,
    RuleSeverity,
    RuleVerificationStatus,
    StandardRule,
)
from app.domain.compressed_air.advanced.standards_mapping import (
    EngineeringStandard,
)


def build_rule(
    *,
    verification_status: RuleVerificationStatus,
    implementation_status: RuleImplementationStatus,
    compliance_claim_allowed: bool = False,
) -> StandardRule:
    return StandardRule(
        rule_code="TEST-RULE",
        standard=EngineeringStandard.API_618,
        standard_title="API 618",
        clause_reference="TEST-CLAUSE",
        title="Test rule",
        description="Test standards-backed rule.",
        severity=RuleSeverity.REQUIREMENT,
        applicable_applications=(AdvancedApplicationType.RECIPROCATING_PROCESS_COMPRESSOR,),
        related_modules=(AdvancedEngineeringModule.RECIPROCATING_ENGINEERING,),
        verification_status=verification_status,
        implementation_status=implementation_status,
        calculation_binding="test.binding",
        compliance_claim_allowed=compliance_claim_allowed,
    )


def build_context(
    *,
    application_type: AdvancedApplicationType = (
        AdvancedApplicationType.RECIPROCATING_PROCESS_COMPRESSOR
    ),
    measured_value: int = 10,
) -> RuleEvaluationContext:
    return RuleEvaluationContext(
        application_type=application_type,
        values={
            "measured_value": measured_value,
        },
    )


def test_not_applicable_rule_is_not_executed() -> None:
    rule = build_rule(
        verification_status=RuleVerificationStatus.APPROVED,
        implementation_status=RuleImplementationStatus.VALIDATED,
        compliance_claim_allowed=True,
    )

    result = evaluate_standard_rule(
        rule=rule,
        context=build_context(application_type=AdvancedApplicationType.FACTORY_COMPRESSED_AIR),
        predicate=lambda context: True,
    )

    assert result.status == RuleEvaluationStatus.NOT_APPLICABLE
    assert result.rule_is_applicable is False
    assert result.rule_is_executable is False
    assert result.compliance_claim_allowed is False


def test_unverified_rule_requires_review() -> None:
    rule = build_rule(
        verification_status=RuleVerificationStatus.UNVERIFIED,
        implementation_status=RuleImplementationStatus.IMPLEMENTED,
    )

    result = evaluate_standard_rule(
        rule=rule,
        context=build_context(),
        predicate=lambda context: True,
    )

    assert result.status == RuleEvaluationStatus.REVIEW_REQUIRED
    assert result.rule_is_applicable is True
    assert result.rule_is_executable is False
    assert result.compliance_claim_allowed is False


def test_verified_but_unimplemented_rule_requires_review() -> None:
    rule = build_rule(
        verification_status=RuleVerificationStatus.SOURCE_VERIFIED,
        implementation_status=RuleImplementationStatus.NOT_IMPLEMENTED,
    )

    result = evaluate_standard_rule(
        rule=rule,
        context=build_context(),
        predicate=lambda context: True,
    )

    assert result.status == RuleEvaluationStatus.REVIEW_REQUIRED
    assert result.rule_is_executable is False


def test_draft_rule_requires_review() -> None:
    rule = build_rule(
        verification_status=RuleVerificationStatus.ENGINEERING_VERIFIED,
        implementation_status=RuleImplementationStatus.DRAFT,
    )

    result = evaluate_standard_rule(
        rule=rule,
        context=build_context(),
        predicate=lambda context: True,
    )

    assert result.status == RuleEvaluationStatus.REVIEW_REQUIRED
    assert result.rule_is_executable is False


def test_missing_predicate_requires_review() -> None:
    rule = build_rule(
        verification_status=RuleVerificationStatus.SOURCE_VERIFIED,
        implementation_status=RuleImplementationStatus.IMPLEMENTED,
    )

    result = evaluate_standard_rule(
        rule=rule,
        context=build_context(),
        predicate=None,
    )

    assert result.status == RuleEvaluationStatus.REVIEW_REQUIRED
    assert result.rule_is_applicable is True
    assert result.rule_is_executable is True
    assert result.compliance_claim_allowed is False


def test_implemented_verified_rule_can_pass() -> None:
    rule = build_rule(
        verification_status=RuleVerificationStatus.ENGINEERING_VERIFIED,
        implementation_status=RuleImplementationStatus.IMPLEMENTED,
    )

    result = evaluate_standard_rule(
        rule=rule,
        context=build_context(
            measured_value=10,
        ),
        predicate=lambda context: context.values["measured_value"] <= 10,
    )

    assert result.status == RuleEvaluationStatus.PASS
    assert result.rule_is_applicable is True
    assert result.rule_is_executable is True
    assert result.compliance_claim_allowed is False


def test_implemented_verified_rule_can_fail() -> None:
    rule = build_rule(
        verification_status=RuleVerificationStatus.ENGINEERING_VERIFIED,
        implementation_status=RuleImplementationStatus.IMPLEMENTED,
    )

    result = evaluate_standard_rule(
        rule=rule,
        context=build_context(
            measured_value=15,
        ),
        predicate=lambda context: context.values["measured_value"] <= 10,
    )

    assert result.status == RuleEvaluationStatus.FAIL
    assert result.rule_is_executable is True
    assert result.compliance_claim_allowed is False


def test_pass_does_not_automatically_allow_compliance_claim() -> None:
    rule = build_rule(
        verification_status=RuleVerificationStatus.APPROVED,
        implementation_status=RuleImplementationStatus.VALIDATED,
        compliance_claim_allowed=False,
    )

    result = evaluate_standard_rule(
        rule=rule,
        context=build_context(),
        predicate=lambda context: True,
    )

    assert result.status == RuleEvaluationStatus.PASS
    assert result.compliance_claim_allowed is False


def test_validated_approved_rule_can_allow_compliance_claim() -> None:
    rule = build_rule(
        verification_status=RuleVerificationStatus.APPROVED,
        implementation_status=RuleImplementationStatus.VALIDATED,
        compliance_claim_allowed=True,
    )

    result = evaluate_standard_rule(
        rule=rule,
        context=build_context(),
        predicate=lambda context: True,
    )

    assert result.status == RuleEvaluationStatus.PASS
    assert result.compliance_claim_allowed is True


def test_failed_rule_never_allows_compliance_claim() -> None:
    rule = build_rule(
        verification_status=RuleVerificationStatus.APPROVED,
        implementation_status=RuleImplementationStatus.VALIDATED,
        compliance_claim_allowed=True,
    )

    result = evaluate_standard_rule(
        rule=rule,
        context=build_context(),
        predicate=lambda context: False,
    )

    assert result.status == RuleEvaluationStatus.FAIL
    assert result.compliance_claim_allowed is False


def test_source_verified_validated_rule_does_not_allow_formal_claim() -> None:
    rule = build_rule(
        verification_status=RuleVerificationStatus.SOURCE_VERIFIED,
        implementation_status=RuleImplementationStatus.VALIDATED,
        compliance_claim_allowed=True,
    )

    result = evaluate_standard_rule(
        rule=rule,
        context=build_context(),
        predicate=lambda context: True,
    )

    assert result.status == RuleEvaluationStatus.PASS
    assert result.compliance_claim_allowed is False
