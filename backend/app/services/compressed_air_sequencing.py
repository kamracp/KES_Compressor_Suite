from app.domain.compressed_air.profiles.demand_profile import DemandProfilePoint
from app.domain.compressed_air.sequencing.sequencing_assessment import (
    SequencingAssessmentInput,
    SequencingAssessmentResult,
    assess_sequencing,
)
from app.domain.compressed_air.sequencing.sequencing_models import (
    PressureBand,
    SequencedMachine,
    SequencingResult,
)
from app.schemas.compressed_air_sequencing import (
    MachinePeriodResponse,
    PeriodResponse,
    PressureBandSchema,
    ProposedMachineResponse,
    SequencedMachineRequest,
    SequencingAssessmentRequest,
    SequencingAssessmentResponse,
    SequencingRunResponse,
)


def _machine(item: SequencedMachineRequest) -> SequencedMachine:
    return SequencedMachine(
        unit_code=item.unit_code,
        control_mode=item.control_mode,
        rated_fad_nm3_per_hr=item.rated_fad_nm3_per_hr,
        rated_power_kw=item.rated_power_kw,
        band=PressureBand(item.band.load_pressure_bar_g, item.band.unload_pressure_bar_g),
        unload_power_fraction=item.unload_power_fraction,
        minimum_flow_fraction=item.minimum_flow_fraction,
        minimum_flow_power_fraction=item.minimum_flow_power_fraction,
        standby_runs_unloaded=item.standby_runs_unloaded,
    )


def _run(result: SequencingResult) -> SequencingRunResponse:
    return SequencingRunResponse(
        periods=[
            PeriodResponse(
                period_index=p.period_index,
                label=p.label,
                demand_nm3_per_hr=p.demand_nm3_per_hr,
                duration_hours=p.duration_hours,
                supplied_flow_nm3_per_hr=p.supplied_flow_nm3_per_hr,
                shortfall_nm3_per_hr=p.shortfall_nm3_per_hr,
                average_header_pressure_bar_g=p.average_header_pressure_bar_g,
                total_power_kw=p.total_power_kw,
                energy_kwh=p.energy_kwh,
                machines=[
                    MachinePeriodResponse(
                        unit_code=m.unit_code,
                        period_index=m.period_index,
                        duty_role=m.duty_role,
                        delivered_flow_nm3_per_hr=m.delivered_flow_nm3_per_hr,
                        load_fraction=m.load_fraction,
                        cycles_per_hour=m.cycles_per_hour,
                        average_power_kw=m.average_power_kw,
                        energy_kwh=m.energy_kwh,
                    )
                    for m in p.machines
                ],
            )
            for p in result.periods
        ],
        total_energy_kwh=result.total_energy_kwh,
        total_energy_cost=result.total_energy_cost,
        specific_power_kw_per_nm3_per_min=result.specific_power_kw_per_nm3_per_min,
        unload_energy_kwh=result.unload_energy_kwh,
        standby_energy_kwh=result.standby_energy_kwh,
        unmet_demand_hours=result.unmet_demand_hours,
    )


def _response(result: SequencingAssessmentResult) -> SequencingAssessmentResponse:
    return SequencingAssessmentResponse(
        analysis_code=result.analysis_code,
        baseline=_run(result.baseline),
        proposed=_run(result.proposed),
        proposed_machines=[
            ProposedMachineResponse(
                unit_code=m.unit_code,
                control_mode=m.control_mode,
                priority=m.priority if m.priority is not None else 0,
                band=PressureBandSchema(
                    load_pressure_bar_g=m.band.load_pressure_bar_g,
                    unload_pressure_bar_g=m.band.unload_pressure_bar_g,
                ),
            )
            for m in result.proposed_machines
        ],
        profile_hours=result.profile_hours,
        annualisation_factor=result.annualisation_factor,
        baseline_average_header_pressure_bar_g=result.baseline_average_header_pressure_bar_g,
        proposed_average_header_pressure_bar_g=result.proposed_average_header_pressure_bar_g,
        standby_saving_kwh=result.standby_saving_kwh,
        trim_saving_kwh=result.trim_saving_kwh,
        pressure_saving_kwh=result.pressure_saving_kwh,
        total_annual_saving_kwh=result.total_annual_saving_kwh,
        total_annual_cost_saving=result.total_annual_cost_saving,
        saving_claimed=result.saving_claimed,
        note=result.note,
    )


class CompressedAirSequencingService:
    def assess(self, request: SequencingAssessmentRequest) -> SequencingAssessmentResponse:
        result = assess_sequencing(
            SequencingAssessmentInput(
                analysis_code=request.analysis_code,
                baseline_machines=tuple(_machine(m) for m in request.baseline_machines),
                demand_profile=tuple(
                    DemandProfilePoint(
                        period_index=p.period_index,
                        label=p.label,
                        demand_nm3_per_hr=p.demand_nm3_per_hr,
                        required_pressure_bar_g=p.required_pressure_bar_g,
                        duration_hours=p.duration_hours,
                    )
                    for p in request.demand_profile
                ),
                receiver_volume_m3=request.receiver_volume_m3,
                electricity_tariff_per_kwh=request.electricity_tariff_per_kwh,
                proposed_band=PressureBand(
                    request.proposed_band.load_pressure_bar_g,
                    request.proposed_band.unload_pressure_bar_g,
                ),
                annual_operating_hours=request.annual_operating_hours,
            )
        )
        return _response(result)


compressed_air_sequencing_service = CompressedAirSequencingService()
