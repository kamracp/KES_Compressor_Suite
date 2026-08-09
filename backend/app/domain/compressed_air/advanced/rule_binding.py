from dataclasses import dataclass
from enum import StrEnum

from app.domain.compressed_air.advanced.advanced_registry import (
    AdvancedEngineeringModule,
)
from app.domain.compressed_air.advanced.rule_catalog import (
    get_standard_rule_catalog,
)
from app.domain.compressed_air.advanced.standard_rules import (
    RuleImplementationStatus,
    RuleVerificationStatus,
    StandardRule,
)


class RuleBindingStatus(StrEnum):
    """Binding status between a standards rule and calculation capability."""

    UNBOUND = "UNBOUND"
    DECLARED = "DECLARED"
    READY_FOR_IMPLEMENTATION = "READY_FOR_IMPLEMENTATION"
    EXECUTABLE = "EXECUTABLE"


@dataclass(frozen=True, slots=True)
class RuleBindingDefinition:
    """Binding metadata between one rule and an engineering calculation."""

    rule_code: str

    module: AdvancedEngineeringModule

    calculation_binding: str | None

    status: RuleBindingStatus

    source_verified: bool
    implementation_ready: bool
    executable: bool

    rationale: str


@dataclass(frozen=True, slots=True)
class RuleBindingRegistry:
    """Summary of all standards-rule calculation bindings."""

    bindings: tuple[RuleBindingDefinition, ...]

    total_bindings: int
    unbound_bindings: int
    declared_bindings: int
    ready_bindings: int
    executable_bindings: int


def build_rule_binding_registry() -> RuleBindingRegistry:
    """Build controlled calculation-binding registry for catalog rules."""

    bindings: list[RuleBindingDefinition] = []

    for rule in get_standard_rule_catalog():
        bindings.extend(_build_bindings_for_rule(rule))

    binding_tuple = tuple(bindings)

    return RuleBindingRegistry(
        bindings=binding_tuple,
        total_bindings=len(binding_tuple),
        unbound_bindings=sum(
            1 for item in binding_tuple if item.status == RuleBindingStatus.UNBOUND
        ),
        declared_bindings=sum(
            1 for item in binding_tuple if item.status == RuleBindingStatus.DECLARED
        ),
        ready_bindings=sum(
            1 for item in binding_tuple if item.status == RuleBindingStatus.READY_FOR_IMPLEMENTATION
        ),
        executable_bindings=sum(
            1 for item in binding_tuple if item.status == RuleBindingStatus.EXECUTABLE
        ),
    )


def get_bindings_for_rule(
    rule_code: str,
) -> tuple[RuleBindingDefinition, ...]:
    """Return all calculation bindings declared for one rule."""

    return tuple(
        item for item in build_rule_binding_registry().bindings if item.rule_code == rule_code
    )


def get_bindings_for_module(
    module: AdvancedEngineeringModule,
) -> tuple[RuleBindingDefinition, ...]:
    """Return all standards bindings associated with one module."""

    return tuple(item for item in build_rule_binding_registry().bindings if item.module == module)


def _build_bindings_for_rule(
    rule: StandardRule,
) -> tuple[RuleBindingDefinition, ...]:
    if not rule.related_modules:
        return (
            RuleBindingDefinition(
                rule_code=rule.rule_code,
                module=AdvancedEngineeringModule.STANDARDS_COMPLIANCE,
                calculation_binding=rule.calculation_binding,
                status=RuleBindingStatus.UNBOUND,
                source_verified=_source_is_verified(rule),
                implementation_ready=False,
                executable=False,
                rationale=("No engineering module has been mapped to this rule."),
            ),
        )

    return tuple(
        _build_binding(
            rule=rule,
            module=module,
        )
        for module in rule.related_modules
    )


def _build_binding(
    *,
    rule: StandardRule,
    module: AdvancedEngineeringModule,
) -> RuleBindingDefinition:
    source_verified = _source_is_verified(rule)

    implemented = rule.implementation_status in {
        RuleImplementationStatus.IMPLEMENTED,
        RuleImplementationStatus.VALIDATED,
    }

    has_calculation_binding = bool(rule.calculation_binding)

    if not has_calculation_binding:
        status = RuleBindingStatus.DECLARED
        implementation_ready = False
        executable = False

        rationale = (
            "Rule-to-module relationship is declared, but no calculation binding has been assigned."
        )

    elif not source_verified:
        status = RuleBindingStatus.DECLARED
        implementation_ready = False
        executable = False

        rationale = (
            "Calculation binding is declared, but source verification is "
            "not sufficient for implementation."
        )

    elif not implemented:
        status = RuleBindingStatus.READY_FOR_IMPLEMENTATION
        implementation_ready = True
        executable = False

        rationale = (
            "Source is verified and a calculation binding exists, but the "
            "rule implementation has not yet been completed."
        )

    else:
        status = RuleBindingStatus.EXECUTABLE
        implementation_ready = True
        executable = True

        rationale = (
            "Rule source is verified, calculation binding is defined, and "
            "the rule implementation is executable."
        )

    return RuleBindingDefinition(
        rule_code=rule.rule_code,
        module=module,
        calculation_binding=rule.calculation_binding,
        status=status,
        source_verified=source_verified,
        implementation_ready=implementation_ready,
        executable=executable,
        rationale=rationale,
    )


def _source_is_verified(
    rule: StandardRule,
) -> bool:
    return rule.verification_status in {
        RuleVerificationStatus.SOURCE_VERIFIED,
        RuleVerificationStatus.ENGINEERING_VERIFIED,
        RuleVerificationStatus.APPROVED,
    }
