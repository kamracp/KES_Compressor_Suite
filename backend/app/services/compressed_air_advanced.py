from app.domain.compressed_air.advanced.advanced_summary import (
    build_advanced_engineering_summary,
)
from app.domain.compressed_air.advanced.application_router import (
    AdvancedRoutingInput,
)
from app.schemas.compressed_air_advanced import (
    AdvancedEngineeringRequest,
    AdvancedEngineeringResponse,
    AdvancedModuleResponse,
    StandardAssessmentResponse,
)


class CompressedAirAdvancedService:
    """Application service for compressed-air advanced engineering."""

    def assess(
        self,
        request: AdvancedEngineeringRequest,
    ) -> AdvancedEngineeringResponse:
        summary = build_advanced_engineering_summary(
            AdvancedRoutingInput(
                application_type=request.application_type,
                compressor_technology=request.compressor_technology,
                discharge_pressure_bar_g=request.discharge_pressure_bar_g,
                process_gas_service=request.process_gas_service,
                high_pressure_service=request.high_pressure_service,
                standards_review_required=request.standards_review_required,
            )
        )

        recommended_modules = [
            AdvancedModuleResponse(
                module_code=item.module.value,
                title=item.title,
                description=item.description,
                source_package=item.source_package,
            )
            for item in summary.routing.recommended_modules
        ]

        standard_assessments = [
            StandardAssessmentResponse(
                standard_code=item.standard.value,
                title=item.title,
                status=item.status.value,
                rationale=item.rationale,
                clause_rules_implemented=item.clause_rules_implemented,
                formal_compliance_claim_allowed=(item.formal_compliance_claim_allowed),
            )
            for item in summary.compliance.assessments
        ]

        return AdvancedEngineeringResponse(
            application_type=summary.routing.application_type.value,
            advanced_engineering_required=(summary.advanced_engineering_required),
            standards_review_required=summary.standards_review_required,
            recommended_modules=recommended_modules,
            applicable_standard_codes=list(summary.applicable_standard_codes),
            review_required_standard_codes=list(summary.review_required_standard_codes),
            standard_assessments=standard_assessments,
            formal_compliance_claim_available=(summary.formal_compliance_claim_available),
            routing_reasons=list(summary.routing.reasons),
        )


compressed_air_advanced_service = CompressedAirAdvancedService()
