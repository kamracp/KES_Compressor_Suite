from app.domain.compressed_air.performance.part_load import BelowTurndownMode, PartLoadCurve
from app.domain.compressed_air.performance.part_load_comparison import (
    LoadDurationBin,
    PartLoadCandidate,
    PartLoadComparisonInput,
    PartLoadComparisonResult,
    compare_part_load,
)
from app.schemas._bounds import DEFAULT_MODULATION_FLOOR_CAPACITY_FRACTION
from app.schemas.compressed_air_part_load import (
    CandidatePointResponse,
    CandidateResponse,
    PartLoadCandidateRequest,
    PartLoadComparisonRequest,
    PartLoadComparisonResponse,
    PointWinnerResponse,
)


def _curve(item: PartLoadCandidateRequest) -> PartLoadCurve:
    return PartLoadCurve(
        mode=item.mode,
        unload_power_fraction=item.unload_power_fraction,
        modulation_floor_capacity_fraction=(
            item.modulation_floor_capacity_fraction
            if item.modulation_floor_capacity_fraction is not None
            else DEFAULT_MODULATION_FLOOR_CAPACITY_FRACTION
        ),
        minimum_flow_fraction=item.minimum_flow_fraction,
        minimum_flow_power_fraction=item.minimum_flow_power_fraction,
        turndown_flow_fraction=item.turndown_flow_fraction,
        power_fraction_at_turndown=item.power_fraction_at_turndown,
        below_turndown=(
            item.below_turndown if item.below_turndown is not None else BelowTurndownMode.BLOW_OFF
        ),
    )


def _response(result: PartLoadComparisonResult) -> PartLoadComparisonResponse:
    return PartLoadComparisonResponse(
        analysis_code=result.analysis_code,
        rated_fad_nm3_per_hr=result.rated_fad_nm3_per_hr,
        rated_power_kw=result.rated_power_kw,
        candidates=[
            CandidateResponse(
                label=c.label,
                mode=c.mode,
                points=[
                    CandidatePointResponse(
                        capacity_fraction=p.capacity_fraction,
                        power_fraction=p.power_fraction,
                        power_kw=p.power_kw,
                        specific_power_kw_per_nm3_per_min=p.specific_power_kw_per_nm3_per_min,
                        wasted_flow_nm3_per_hr=p.wasted_flow_nm3_per_hr,
                        regime=p.regime,
                    )
                    for p in c.points
                ],
                annual_energy_kwh=c.annual_energy_kwh,
                annual_energy_cost=c.annual_energy_cost,
                annual_blow_off_volume_nm3=c.annual_blow_off_volume_nm3,
            )
            for c in result.candidates
        ],
        lowest_power_per_point=[
            PointWinnerResponse(
                capacity_fraction=w.capacity_fraction, label=w.label, power_kw=w.power_kw
            )
            for w in result.lowest_power_per_point
        ],
        lowest_annual_energy_label=result.lowest_annual_energy_label,
        profile_hours=result.profile_hours,
    )


class CompressedAirPartLoadService:
    def compare(self, request: PartLoadComparisonRequest) -> PartLoadComparisonResponse:
        inputs = PartLoadComparisonInput(
            analysis_code=request.analysis_code,
            rated_fad_nm3_per_hr=request.rated_fad_nm3_per_hr,
            rated_power_kw=request.rated_power_kw,
            candidates=tuple(
                PartLoadCandidate(label=c.label, curve=_curve(c)) for c in request.candidates
            ),
            capacity_fractions=tuple(request.capacity_fractions),
            load_duration=tuple(
                LoadDurationBin(capacity_fraction=b.capacity_fraction, hours=b.hours)
                for b in request.load_duration
            ),
            electricity_tariff_per_kwh=request.electricity_tariff_per_kwh,
        )
        return _response(compare_part_load(inputs))


compressed_air_part_load_service = CompressedAirPartLoadService()
