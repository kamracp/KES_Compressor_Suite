from app.domain.compressed_air.leakage.leakage_analysis import (
    analyze_leakage_management,
)
from app.domain.compressed_air.leakage.leakage_models import (
    LeakageManagementInput,
    LeakRegisterItem,
)
from app.schemas.compressed_air_leakage import (
    CompressedAirLeakageManagementRequest,
    CompressedAirLeakageManagementResponse,
    LeakageEnergyResponse,
    LeakageRegisterItemResultResponse,
)


class CompressedAirLeakageService:
    """Application service for compressed-air leakage management."""

    def analyze(
        self,
        request: CompressedAirLeakageManagementRequest,
    ) -> CompressedAirLeakageManagementResponse:
        result = analyze_leakage_management(
            LeakageManagementInput(
                analysis_code=request.analysis_code,
                leaks=tuple(
                    LeakRegisterItem(
                        leak_code=item.leak_code,
                        location=item.location,
                        baseline_leakage_flow_nm3_per_hr=(item.baseline_leakage_flow_nm3_per_hr),
                        quantification_basis=item.quantification_basis,
                        source_category=item.source_category,
                        area=item.area,
                        equipment_tag=item.equipment_tag,
                        component_description=item.component_description,
                        survey_pressure_bar_g=item.survey_pressure_bar_g,
                        expected_repair_fraction=(item.expected_repair_fraction),
                        repair_status=item.repair_status,
                        estimated_repair_cost=item.estimated_repair_cost,
                        verified_post_repair_flow_nm3_per_hr=(
                            item.verified_post_repair_flow_nm3_per_hr
                        ),
                        survey_method_reference=(item.survey_method_reference),
                        notes=item.notes,
                    )
                    for item in request.leaks
                ),
                specific_power_kw_per_nm3_per_min=(request.specific_power_kw_per_nm3_per_min),
                annual_operating_hours=request.annual_operating_hours,
                electricity_tariff_per_kwh=(request.electricity_tariff_per_kwh),
                demand_saving_control_factor=(request.demand_saving_control_factor),
                average_system_demand_nm3_per_hr=(request.average_system_demand_nm3_per_hr),
                notes=request.notes,
            )
        )

        return CompressedAirLeakageManagementResponse(
            analysis_code=result.analysis_code,
            leak_count=result.leak_count,
            total_registered_leakage_flow_nm3_per_hr=(
                result.total_registered_leakage_flow_nm3_per_hr
            ),
            leakage_fraction_of_average_system_demand=(
                result.leakage_fraction_of_average_system_demand
            ),
            total_wasted_power_kw=result.total_wasted_power_kw,
            total_annual_wasted_energy_kwh=(result.total_annual_wasted_energy_kwh),
            total_annual_wasted_energy_cost=(result.total_annual_wasted_energy_cost),
            total_recoverable_leakage_flow_nm3_per_hr=(
                result.total_recoverable_leakage_flow_nm3_per_hr
            ),
            total_recoverable_power_kw=(result.total_recoverable_power_kw),
            total_annual_energy_saving_kwh=(result.total_annual_energy_saving_kwh),
            total_annual_cost_saving=result.total_annual_cost_saving,
            total_residual_leakage_flow_nm3_per_hr=(result.total_residual_leakage_flow_nm3_per_hr),
            verified_leak_count=result.verified_leak_count,
            verified_flow_reduction_nm3_per_hr=(result.verified_flow_reduction_nm3_per_hr),
            items=[
                LeakageRegisterItemResultResponse(
                    leak_code=item.leak_code,
                    location=item.location,
                    source_category=item.source_category,
                    quantification_basis=item.quantification_basis,
                    repair_status=item.repair_status,
                    priority=item.priority,
                    baseline_leakage_flow_nm3_per_hr=(item.baseline_leakage_flow_nm3_per_hr),
                    fraction_of_total_registered_leakage=(
                        item.fraction_of_total_registered_leakage
                    ),
                    energy=LeakageEnergyResponse(
                        leakage_flow_nm3_per_hr=(item.energy.leakage_flow_nm3_per_hr),
                        leakage_flow_nm3_per_min=(item.energy.leakage_flow_nm3_per_min),
                        wasted_power_kw=item.energy.wasted_power_kw,
                        annual_wasted_energy_kwh=(item.energy.annual_wasted_energy_kwh),
                        annual_wasted_energy_cost=(item.energy.annual_wasted_energy_cost),
                        expected_repair_fraction=(item.energy.expected_repair_fraction),
                        demand_saving_control_factor=(item.energy.demand_saving_control_factor),
                        recoverable_leakage_flow_nm3_per_hr=(
                            item.energy.recoverable_leakage_flow_nm3_per_hr
                        ),
                        recoverable_power_kw=(item.energy.recoverable_power_kw),
                        annual_energy_saving_kwh=(item.energy.annual_energy_saving_kwh),
                        annual_cost_saving=(item.energy.annual_cost_saving),
                        residual_leakage_flow_nm3_per_hr=(
                            item.energy.residual_leakage_flow_nm3_per_hr
                        ),
                    ),
                    estimated_repair_cost=item.estimated_repair_cost,
                    simple_payback_years=item.simple_payback_years,
                    verified_post_repair_flow_nm3_per_hr=(
                        item.verified_post_repair_flow_nm3_per_hr
                    ),
                    verified_flow_reduction_nm3_per_hr=(item.verified_flow_reduction_nm3_per_hr),
                    verified_repair_fraction=(item.verified_repair_fraction),
                    notes=item.notes,
                )
                for item in result.items
            ],
        )


compressed_air_leakage_service = CompressedAirLeakageService()
