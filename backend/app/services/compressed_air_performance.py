from app.domain.compressed_air.performance.performance_analysis import (
    analyze_performance,
)
from app.domain.compressed_air.performance.performance_models import (
    PerformanceAnalysisInput,
    PerformanceMeasurementPoint,
)
from app.schemas.compressed_air_performance import (
    CompressedAirPerformanceAnalysisRequest,
    CompressedAirPerformanceAnalysisResponse,
    PressureEnergyPerformanceResponse,
)


class CompressedAirPerformanceService:
    """Application service for compressed-air performance analysis."""

    def analyze(
        self,
        request: CompressedAirPerformanceAnalysisRequest,
    ) -> CompressedAirPerformanceAnalysisResponse:
        result = analyze_performance(
            PerformanceAnalysisInput(
                analysis_code=request.analysis_code,
                measurements=tuple(
                    PerformanceMeasurementPoint(
                        timestamp_label=item.timestamp_label,
                        flow_nm3_per_hr=item.flow_nm3_per_hr,
                        pressure_bar_g=item.pressure_bar_g,
                        power_kw=item.power_kw,
                        operating_state=item.operating_state,
                        load_fraction=item.load_fraction,
                        production_state=item.production_state,
                        notes=item.notes,
                    )
                    for item in request.measurements
                ),
                annual_operating_hours=request.annual_operating_hours,
                electricity_tariff_per_kwh=(request.electricity_tariff_per_kwh),
                rated_capacity_nm3_per_hr=(request.rated_capacity_nm3_per_hr),
                rated_power_kw=request.rated_power_kw,
                reference_specific_power_kw_per_nm3_per_min=(
                    request.reference_specific_power_kw_per_nm3_per_min
                ),
                optimized_discharge_pressure_bar_g=(request.optimized_discharge_pressure_bar_g),
                power_penalty_fraction_per_bar=(request.power_penalty_fraction_per_bar),
                notes=request.notes,
            )
        )

        pressure_energy = None

        if result.pressure_energy is not None:
            pressure = result.pressure_energy

            pressure_energy = PressureEnergyPerformanceResponse(
                current_discharge_pressure_bar_g=(pressure.current_discharge_pressure_bar_g),
                optimized_discharge_pressure_bar_g=(pressure.optimized_discharge_pressure_bar_g),
                pressure_reduction_bar=pressure.pressure_reduction_bar,
                current_average_power_kw=pressure.current_average_power_kw,
                estimated_optimized_power_kw=(pressure.estimated_optimized_power_kw),
                estimated_power_saving_kw=(pressure.estimated_power_saving_kw),
                power_saving_fraction=pressure.power_saving_fraction,
                annual_operating_hours=pressure.annual_operating_hours,
                annual_energy_saving_kwh=(pressure.annual_energy_saving_kwh),
                electricity_tariff_per_kwh=(pressure.electricity_tariff_per_kwh),
                annual_cost_saving=pressure.annual_cost_saving,
                power_penalty_fraction_per_bar=(pressure.power_penalty_fraction_per_bar),
                power_saving_method=pressure.power_saving_method,
                pressure_reduction_is_beneficial=(pressure.pressure_reduction_is_beneficial),
            )

        return CompressedAirPerformanceAnalysisResponse(
            analysis_code=result.analysis_code,
            measurement_count=result.measurement_count,
            average_flow_nm3_per_hr=result.average_flow_nm3_per_hr,
            peak_flow_nm3_per_hr=result.peak_flow_nm3_per_hr,
            minimum_flow_nm3_per_hr=result.minimum_flow_nm3_per_hr,
            average_pressure_bar_g=result.average_pressure_bar_g,
            maximum_pressure_bar_g=result.maximum_pressure_bar_g,
            minimum_pressure_bar_g=result.minimum_pressure_bar_g,
            average_power_kw=result.average_power_kw,
            peak_power_kw=result.peak_power_kw,
            measured_specific_power_kw_per_nm3_per_min=(
                result.measured_specific_power_kw_per_nm3_per_min
            ),
            measured_specific_energy_kwh_per_1000_nm3=(
                result.measured_specific_energy_kwh_per_1000_nm3
            ),
            average_load_fraction=result.average_load_fraction,
            unloaded_measurement_fraction=(result.unloaded_measurement_fraction),
            rated_capacity_nm3_per_hr=result.rated_capacity_nm3_per_hr,
            average_capacity_utilization_fraction=(result.average_capacity_utilization_fraction),
            peak_capacity_utilization_fraction=(result.peak_capacity_utilization_fraction),
            rated_power_kw=result.rated_power_kw,
            average_power_utilization_fraction=(result.average_power_utilization_fraction),
            reference_specific_power_kw_per_nm3_per_min=(
                result.reference_specific_power_kw_per_nm3_per_min
            ),
            specific_power_deviation_fraction=(result.specific_power_deviation_fraction),
            annual_operating_hours=result.annual_operating_hours,
            annual_energy_kwh=result.annual_energy_kwh,
            electricity_tariff_per_kwh=result.electricity_tariff_per_kwh,
            annual_energy_cost=result.annual_energy_cost,
            pressure_energy=pressure_energy,
        )


compressed_air_performance_service = CompressedAirPerformanceService()
