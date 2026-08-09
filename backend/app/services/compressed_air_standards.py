from app.domain.compressed_air.advanced.rule_binding import (
    build_rule_binding_registry,
)
from app.domain.compressed_air.advanced.rule_catalog import (
    get_standard_rule_catalog,
    get_standard_rule_registry,
)
from app.schemas.compressed_air_standards import (
    StandardRuleBindingResponse,
    StandardRuleResponse,
    StandardsRegistrySummaryResponse,
    StandardsRuleQueryRequest,
    StandardsRulesResponse,
)


class CompressedAirStandardsService:
    """Application service for standards-rule registry queries."""

    def query_rules(
        self,
        request: StandardsRuleQueryRequest,
    ) -> StandardsRulesResponse:
        rule_registry = get_standard_rule_registry()
        binding_registry = build_rule_binding_registry()

        rules = tuple(
            rule
            for rule in get_standard_rule_catalog()
            if self._rule_matches_query(
                rule=rule,
                request=request,
            )
        )

        selected_rule_codes = {rule.rule_code for rule in rules}

        bindings = tuple(
            binding
            for binding in binding_registry.bindings
            if binding.rule_code in selected_rule_codes
        )

        rule_responses = [
            StandardRuleResponse(
                rule_code=rule.rule_code,
                standard_code=rule.standard.value,
                standard_title=rule.standard_title,
                clause_reference=rule.clause_reference,
                title=rule.title,
                description=rule.description,
                severity=rule.severity.value,
                applicable_applications=[item.value for item in rule.applicable_applications],
                related_modules=[item.value for item in rule.related_modules],
                verification_status=rule.verification_status.value,
                implementation_status=rule.implementation_status.value,
                source_note=rule.source_note,
                engineering_note=rule.engineering_note,
                calculation_binding=rule.calculation_binding,
                compliance_claim_allowed=rule.compliance_claim_allowed,
            )
            for rule in rules
        ]

        binding_responses = [
            StandardRuleBindingResponse(
                rule_code=binding.rule_code,
                module_code=binding.module.value,
                calculation_binding=binding.calculation_binding,
                status=binding.status.value,
                source_verified=binding.source_verified,
                implementation_ready=binding.implementation_ready,
                executable=binding.executable,
                rationale=binding.rationale,
            )
            for binding in bindings
        ]

        summary = StandardsRegistrySummaryResponse(
            total_rules=rule_registry.total_rules,
            verified_rules=rule_registry.verified_rules,
            implemented_rules=rule_registry.implemented_rules,
            validated_rules=rule_registry.validated_rules,
            compliance_claimable_rules=(rule_registry.compliance_claimable_rules),
            total_bindings=binding_registry.total_bindings,
            executable_bindings=binding_registry.executable_bindings,
        )

        formal_compliance_claim_available = (
            rule_registry.compliance_claimable_rules > 0
            and binding_registry.executable_bindings > 0
        )

        return StandardsRulesResponse(
            summary=summary,
            rules=rule_responses,
            bindings=binding_responses,
            formal_compliance_claim_available=(formal_compliance_claim_available),
        )

    @staticmethod
    def _rule_matches_query(
        *,
        rule,
        request: StandardsRuleQueryRequest,
    ) -> bool:
        if (
            request.application_type is not None
            and request.application_type not in rule.applicable_applications
        ):
            return False

        if request.standard is not None and rule.standard != request.standard:
            return False

        if request.module is not None and request.module not in rule.related_modules:
            return False

        return True


compressed_air_standards_service = CompressedAirStandardsService()
