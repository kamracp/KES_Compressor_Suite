from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from app.domain.compressed_air.advanced.advanced_registry import (
    AdvancedApplicationType,
)
from app.domain.compressed_air.advanced.standard_rules import (
    RuleImplementationStatus,
    RuleVerificationStatus,
    StandardRule,
)


class RuleEvaluationStatus(StrEnum):
    """Evaluation result for one standards-backed engineering rule."""

    PASS = "PASS"
    FAIL = "FAIL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass(frozen=True, slots=True)
class RuleEvaluationContext:
    """Runtime context used to evaluate a standards-backed rule."""

    application_type: AdvancedApplicationType

    values: dict[str, Any]


@dataclass(frozen=True, slots=True)
class RuleEvaluationResult:
    """Result of evaluating one standards-backed engineering rule."""

    rule_code: str

    status: RuleEvaluationStatus

    message: str

    rule_is_applicable: bool
    rule_is_executable: bool

    compliance_claim_allowed: bool


RulePredicate = Callable[[RuleEvaluationContext], bool]


def evaluate_standard_rule(
    *,
    rule: StandardRule,
    context: RuleEvaluationContext,
    predicate: RulePredicate | None = None,
) -> RuleEvaluationResult:
    """Evaluate one standards-backed engineering rule safely."""

    if context.application_type not in rule.applicable_applications:
        return RuleEvaluationResult(
            rule_code=rule.rule_code,
            status=RuleEvaluationStatus.NOT_APPLICABLE,
            message=("Rule is not applicable to the selected application type."),
            rule_is_applicable=False,
            rule_is_executable=False,
            compliance_claim_allowed=False,
        )

    if not _rule_is_verified(rule):
        return RuleEvaluationResult(
            rule_code=rule.rule_code,
            status=RuleEvaluationStatus.REVIEW_REQUIRED,
            message=(
                "Rule source or engineering interpretation has not been "
                "sufficiently verified for automatic evaluation."
            ),
            rule_is_applicable=True,
            rule_is_executable=False,
            compliance_claim_allowed=False,
        )

    if not _rule_is_implemented(rule):
        return RuleEvaluationResult(
            rule_code=rule.rule_code,
            status=RuleEvaluationStatus.REVIEW_REQUIRED,
            message=(
                "Rule is applicable and verified but has not yet been "
                "implemented as an executable calculation rule."
            ),
            rule_is_applicable=True,
            rule_is_executable=False,
            compliance_claim_allowed=False,
        )

    if predicate is None:
        return RuleEvaluationResult(
            rule_code=rule.rule_code,
            status=RuleEvaluationStatus.REVIEW_REQUIRED,
            message=("Rule is executable in principle but no evaluation predicate was supplied."),
            rule_is_applicable=True,
            rule_is_executable=True,
            compliance_claim_allowed=False,
        )

    passed = predicate(context)

    if passed:
        status = RuleEvaluationStatus.PASS
        message = "Engineering rule evaluation passed."
    else:
        status = RuleEvaluationStatus.FAIL
        message = "Engineering rule evaluation failed."

    compliance_claim_allowed = (
        passed
        and rule.compliance_claim_allowed
        and rule.implementation_status == RuleImplementationStatus.VALIDATED
        and rule.verification_status
        in {
            RuleVerificationStatus.ENGINEERING_VERIFIED,
            RuleVerificationStatus.APPROVED,
        }
    )

    return RuleEvaluationResult(
        rule_code=rule.rule_code,
        status=status,
        message=message,
        rule_is_applicable=True,
        rule_is_executable=True,
        compliance_claim_allowed=compliance_claim_allowed,
    )


def _rule_is_verified(
    rule: StandardRule,
) -> bool:
    return rule.verification_status in {
        RuleVerificationStatus.SOURCE_VERIFIED,
        RuleVerificationStatus.ENGINEERING_VERIFIED,
        RuleVerificationStatus.APPROVED,
    }


def _rule_is_implemented(
    rule: StandardRule,
) -> bool:
    return rule.implementation_status in {
        RuleImplementationStatus.IMPLEMENTED,
        RuleImplementationStatus.VALIDATED,
    }
