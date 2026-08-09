from dataclasses import dataclass
from enum import StrEnum

from app.domain.compressed_air.advanced.advanced_registry import (
    AdvancedApplicationType,
    AdvancedEngineeringModule,
)
from app.domain.compressed_air.advanced.standards_mapping import (
    EngineeringStandard,
)


class RuleVerificationStatus(StrEnum):
    """Verification state of one standards-backed engineering rule."""

    UNVERIFIED = "UNVERIFIED"
    SOURCE_VERIFIED = "SOURCE_VERIFIED"
    ENGINEERING_VERIFIED = "ENGINEERING_VERIFIED"
    APPROVED = "APPROVED"


class RuleImplementationStatus(StrEnum):
    """Implementation state of a standards-backed rule."""

    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    DRAFT = "DRAFT"
    IMPLEMENTED = "IMPLEMENTED"
    VALIDATED = "VALIDATED"


class RuleSeverity(StrEnum):
    """Engineering significance of one rule."""

    INFORMATION = "INFORMATION"
    ADVISORY = "ADVISORY"
    REQUIREMENT = "REQUIREMENT"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True, slots=True)
class StandardRule:
    """One traceable standards-backed engineering rule."""

    rule_code: str

    standard: EngineeringStandard
    standard_title: str

    clause_reference: str | None

    title: str
    description: str

    severity: RuleSeverity

    applicable_applications: tuple[AdvancedApplicationType, ...]
    related_modules: tuple[AdvancedEngineeringModule, ...]

    verification_status: RuleVerificationStatus
    implementation_status: RuleImplementationStatus

    source_note: str | None = None
    engineering_note: str | None = None

    calculation_binding: str | None = None

    compliance_claim_allowed: bool = False


@dataclass(frozen=True, slots=True)
class StandardRuleRegistry:
    """Registry of standards-backed rules."""

    rules: tuple[StandardRule, ...]

    total_rules: int

    verified_rules: int
    implemented_rules: int
    validated_rules: int

    compliance_claimable_rules: int


def build_standard_rule_registry(
    rules: tuple[StandardRule, ...],
) -> StandardRuleRegistry:
    """Build summary statistics for standards-backed rules."""

    rule_codes = tuple(rule.rule_code for rule in rules)

    if len(set(rule_codes)) != len(rule_codes):
        raise ValueError("Standard rule codes must be unique.")

    verified_rules = sum(
        1
        for rule in rules
        if rule.verification_status
        in {
            RuleVerificationStatus.SOURCE_VERIFIED,
            RuleVerificationStatus.ENGINEERING_VERIFIED,
            RuleVerificationStatus.APPROVED,
        }
    )

    implemented_rules = sum(
        1
        for rule in rules
        if rule.implementation_status
        in {
            RuleImplementationStatus.IMPLEMENTED,
            RuleImplementationStatus.VALIDATED,
        }
    )

    validated_rules = sum(
        1 for rule in rules if rule.implementation_status == RuleImplementationStatus.VALIDATED
    )

    compliance_claimable_rules = sum(1 for rule in rules if rule.compliance_claim_allowed)

    return StandardRuleRegistry(
        rules=rules,
        total_rules=len(rules),
        verified_rules=verified_rules,
        implemented_rules=implemented_rules,
        validated_rules=validated_rules,
        compliance_claimable_rules=compliance_claimable_rules,
    )
