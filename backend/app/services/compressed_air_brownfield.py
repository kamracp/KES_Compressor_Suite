from app.domain.compressed_air.brownfield.audit_models import (
    BrownfieldAuditCase,
    CompressorMeasurementPoint,
    ExistingCompressor,
    LeakageSurveySummary,
    SystemMeasurementPoint,
)
from app.domain.compressed_air.brownfield.system_engine import (
    BrownfieldSystemEngineInput,
    analyze_brownfield_system,
)
from app.schemas.compressed_air_brownfield import (
    BrownfieldOpportunityResponse,
    BrownfieldSystemAuditRequest,
    BrownfieldSystemAuditResponse,
)


class CompressedAirBrownfieldService:
    """Application service for brownfield compressed-air system audits."""

    def analyze(
        self,
        request: BrownfieldSystemAuditRequest,
    ) -> BrownfieldSystemAuditResponse:
        audit = BrownfieldAuditCase(
            audit_code=request.audit_code,
            project_id=request.project_id,
            compressors=tuple(
                ExistingCompressor(
                    unit_code=item.unit_code,
                    equipment_source=(item.equipment_source or item.manufacturer),
                    model=item.model,
                    technology=item.technology,
                    control_mode=item.control_mode,
                    rated_fad_nm3_per_hr=item.rated_fad_nm3_per_hr,
                    rated_discharge_pressure_bar_g=(item.rated_discharge_pressure_bar_g),
                    rated_motor_power_kw=item.rated_motor_power_kw,
                    installation_year=item.installation_year,
                    operating_hours=item.operating_hours,
                    available=item.available,
                    notes=item.notes,
                )
                for item in request.compressors
            ),
            compressor_measurements=tuple(
                CompressorMeasurementPoint(
                    unit_code=item.unit_code,
                    timestamp_label=item.timestamp_label,
                    operating_state=item.operating_state,
                    measured_flow_nm3_per_hr=item.measured_flow_nm3_per_hr,
                    measured_discharge_pressure_bar_g=(item.measured_discharge_pressure_bar_g),
                    measured_power_kw=item.measured_power_kw,
                    load_fraction=item.load_fraction,
                )
                for item in request.compressor_measurements
            ),
            system_measurements=tuple(
                SystemMeasurementPoint(
                    timestamp_label=item.timestamp_label,
                    total_flow_nm3_per_hr=item.total_flow_nm3_per_hr,
                    header_pressure_bar_g=item.header_pressure_bar_g,
                    total_power_kw=item.total_power_kw,
                    production_state=item.production_state,
                    notes=item.notes,
                )
                for item in request.system_measurements
            ),
            leakage_summary=self._build_leakage_summary(request),
            electricity_tariff_per_kwh=request.electricity_tariff_per_kwh,
            annual_operating_hours=request.annual_operating_hours,
            notes=request.notes,
        )

        result = analyze_brownfield_system(
            BrownfieldSystemEngineInput(
                audit=audit,
                optimized_discharge_pressure_bar_g=(request.optimized_discharge_pressure_bar_g),
                expected_leak_repair_fraction=(request.expected_leak_repair_fraction),
                demand_saving_control_factor=(request.demand_saving_control_factor),
                power_penalty_fraction_per_bar=(request.power_penalty_fraction_per_bar),
                condensate_drain_air_loss_nm3_per_hr=(
                    request.condensate_drain_air_loss_nm3_per_hr
                ),
                filter_excess_pressure_drop_bar=(
                    request.filter_excess_pressure_drop_bar
                ),
            )
        )

        analysis = result.audit_analysis

        opportunities = [
            BrownfieldOpportunityResponse(
                opportunity_code=item.opportunity_code,
                category=item.category.value,
                priority=item.priority.value,
                title=item.title,
                rationale=item.rationale,
                estimated_power_saving_kw=item.estimated_power_saving_kw,
                estimated_annual_energy_saving_kwh=(item.estimated_annual_energy_saving_kwh),
                estimated_annual_cost_saving=(item.estimated_annual_cost_saving),
            )
            for item in result.opportunities.opportunities
        ]

        return BrownfieldSystemAuditResponse(
            audit_code=analysis.audit_code,
            project_id=analysis.project_id,
            installed_capacity_nm3_per_hr=(analysis.installed_capacity_nm3_per_hr),
            available_capacity_nm3_per_hr=(analysis.available_capacity_nm3_per_hr),
            average_system_flow_nm3_per_hr=(analysis.average_system_flow_nm3_per_hr),
            peak_system_flow_nm3_per_hr=(analysis.peak_system_flow_nm3_per_hr),
            minimum_system_flow_nm3_per_hr=(analysis.minimum_system_flow_nm3_per_hr),
            average_system_power_kw=analysis.average_system_power_kw,
            peak_system_power_kw=analysis.peak_system_power_kw,
            average_header_pressure_bar_g=(analysis.average_header_pressure_bar_g),
            minimum_header_pressure_bar_g=(analysis.minimum_header_pressure_bar_g),
            maximum_header_pressure_bar_g=(analysis.maximum_header_pressure_bar_g),
            average_capacity_utilization_fraction=(analysis.average_capacity_utilization_fraction),
            peak_capacity_utilization_fraction=(analysis.peak_capacity_utilization_fraction),
            measured_specific_power_kw_per_nm3_per_min=(
                analysis.measured_specific_power_kw_per_nm3_per_min
            ),
            unloaded_measurement_fraction=(analysis.unloaded_measurement_fraction),
            leakage_flow_nm3_per_hr=analysis.leakage_flow_nm3_per_hr,
            leakage_fraction_of_average_demand=(analysis.leakage_fraction_of_average_demand),
            current_annual_energy_kwh=result.current_annual_energy_kwh,
            current_annual_energy_cost=result.current_annual_energy_cost,
            estimated_total_power_saving_kw=(result.estimated_total_power_saving_kw),
            estimated_total_annual_energy_saving_kwh=(
                result.estimated_total_annual_energy_saving_kwh
            ),
            estimated_total_annual_cost_saving=(result.estimated_total_annual_cost_saving),
            estimated_optimized_average_power_kw=(result.estimated_optimized_average_power_kw),
            estimated_optimized_annual_energy_kwh=(result.estimated_optimized_annual_energy_kwh),
            estimated_optimized_annual_energy_cost=(result.estimated_optimized_annual_energy_cost),
            estimated_energy_reduction_fraction=(result.estimated_energy_reduction_fraction),
            installed_capacity_is_sufficient_for_peak=(
                analysis.installed_capacity_is_sufficient_for_peak
            ),
            high_unloaded_running_detected=(analysis.high_unloaded_running_detected),
            significant_leakage_detected=(analysis.significant_leakage_detected),
            opportunities=opportunities,
        )

    def _build_leakage_summary(
        self,
        request: BrownfieldSystemAuditRequest,
    ) -> LeakageSurveySummary | None:
        item = request.leakage_summary

        if item is None:
            return None

        return LeakageSurveySummary(
            measured_leakage_flow_nm3_per_hr=(item.measured_leakage_flow_nm3_per_hr),
            survey_method=item.survey_method,
            estimated_repair_fraction=item.estimated_repair_fraction,
            survey_notes=item.survey_notes,
        )


compressed_air_brownfield_service = CompressedAirBrownfieldService()
