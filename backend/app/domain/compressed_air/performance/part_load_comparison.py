"""Side-by-side part-load comparison of control modes for one machine (C-8).

Answers the Section 8 question directly: "this rated FAD / rated power, in
modulation vs load/unload vs VSD vs IGV - what does it draw at 25, 50, 75,
100 % load, and over my load-duration profile?" Every curve comes from
performance/part_load.py; nothing here adds constants.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from app.domain.compressed_air.performance.part_load import (
    InvalidPartLoadInputError,
    PartLoadCurve,
    PartLoadMode,
    part_load_point,
    validate_curve,
)

_ZERO = Decimal("0")
_ONE = Decimal("1")
_Q4 = Decimal("0.0001")


def _q(value: Decimal) -> Decimal:
    return value.quantize(_Q4, rounding=ROUND_HALF_UP)


class InvalidPartLoadComparisonInputError(ValueError):
    """Raised when the comparison request is not self-consistent."""


@dataclass(frozen=True, slots=True)
class PartLoadCandidate:
    label: str
    curve: PartLoadCurve


@dataclass(frozen=True, slots=True)
class LoadDurationBin:
    """Hours per year spent at a given capacity fraction."""

    capacity_fraction: Decimal
    hours: Decimal


@dataclass(frozen=True, slots=True)
class PartLoadComparisonInput:
    analysis_code: str
    rated_fad_nm3_per_hr: Decimal
    rated_power_kw: Decimal
    candidates: tuple[PartLoadCandidate, ...]
    capacity_fractions: tuple[Decimal, ...]
    load_duration: tuple[LoadDurationBin, ...] = ()
    electricity_tariff_per_kwh: Decimal | None = None


@dataclass(frozen=True, slots=True)
class CandidatePoint:
    capacity_fraction: Decimal
    power_fraction: Decimal
    power_kw: Decimal
    # kW per Nm3/min delivered; None at zero flow (undefined, not zero).
    specific_power_kw_per_nm3_per_min: Decimal | None
    wasted_flow_nm3_per_hr: Decimal
    regime: str


@dataclass(frozen=True, slots=True)
class CandidateResult:
    label: str
    mode: PartLoadMode
    points: tuple[CandidatePoint, ...]
    annual_energy_kwh: Decimal | None
    annual_energy_cost: Decimal | None
    annual_blow_off_volume_nm3: Decimal | None


@dataclass(frozen=True, slots=True)
class PointWinner:
    capacity_fraction: Decimal
    label: str
    power_kw: Decimal


@dataclass(frozen=True, slots=True)
class PartLoadComparisonResult:
    analysis_code: str
    rated_fad_nm3_per_hr: Decimal
    rated_power_kw: Decimal
    candidates: tuple[CandidateResult, ...]
    lowest_power_per_point: tuple[PointWinner, ...]
    lowest_annual_energy_label: str | None
    profile_hours: Decimal


def _validate(inputs: PartLoadComparisonInput) -> None:
    if inputs.rated_fad_nm3_per_hr <= _ZERO or inputs.rated_power_kw <= _ZERO:
        raise InvalidPartLoadComparisonInputError("Rated FAD and rated power must be positive.")
    if not inputs.candidates:
        raise InvalidPartLoadComparisonInputError(
            "At least one control-mode candidate is required."
        )
    labels = [c.label for c in inputs.candidates]
    if len(set(labels)) != len(labels):
        raise InvalidPartLoadComparisonInputError("Candidate labels must be unique.")
    for candidate in inputs.candidates:
        try:
            validate_curve(candidate.curve)
        except InvalidPartLoadInputError as exc:
            raise InvalidPartLoadComparisonInputError(f"{candidate.label}: {exc}") from exc
    if not inputs.capacity_fractions:
        raise InvalidPartLoadComparisonInputError("At least one capacity fraction is required.")
    for q in inputs.capacity_fractions:
        if not (_ZERO <= q <= _ONE):
            raise InvalidPartLoadComparisonInputError("Capacity fractions must be within 0 and 1.")
    if len(set(inputs.capacity_fractions)) != len(inputs.capacity_fractions):
        raise InvalidPartLoadComparisonInputError("Capacity fractions must be unique.")
    for item in inputs.load_duration:
        if not (_ZERO <= item.capacity_fraction <= _ONE) or item.hours <= _ZERO:
            raise InvalidPartLoadComparisonInputError(
                "Load-duration bins need a capacity fraction within 0..1 and positive hours."
            )
    if sum((b.hours for b in inputs.load_duration), _ZERO) > Decimal("8784"):
        raise InvalidPartLoadComparisonInputError("Load-duration hours exceed a calendar year.")
    if inputs.electricity_tariff_per_kwh is not None and inputs.electricity_tariff_per_kwh <= _ZERO:
        raise InvalidPartLoadComparisonInputError("Electricity tariff must be positive.")


def _point(inputs: PartLoadComparisonInput, curve: PartLoadCurve, q: Decimal) -> CandidatePoint:
    point = part_load_point(curve, q)
    power_kw = inputs.rated_power_kw * point.power_fraction
    delivered_nm3_per_min = inputs.rated_fad_nm3_per_hr * q / Decimal("60")
    specific = None if delivered_nm3_per_min == _ZERO else power_kw / delivered_nm3_per_min
    return CandidatePoint(
        capacity_fraction=_q(q),
        power_fraction=point.power_fraction,
        power_kw=_q(power_kw),
        specific_power_kw_per_nm3_per_min=None if specific is None else _q(specific),
        wasted_flow_nm3_per_hr=_q(inputs.rated_fad_nm3_per_hr * point.wasted_flow_fraction),
        regime=point.regime,
    )


def compare_part_load(inputs: PartLoadComparisonInput) -> PartLoadComparisonResult:
    _validate(inputs)
    fractions = tuple(sorted(inputs.capacity_fractions))
    profile_hours = sum((b.hours for b in inputs.load_duration), _ZERO)

    results: list[CandidateResult] = []
    for candidate in inputs.candidates:
        points = tuple(_point(inputs, candidate.curve, q) for q in fractions)
        energy = cost = blow_off = None
        if inputs.load_duration:
            energy = _ZERO
            blow_off = _ZERO
            for item in inputs.load_duration:
                p = _point(inputs, candidate.curve, item.capacity_fraction)
                energy += p.power_kw * item.hours
                blow_off += p.wasted_flow_nm3_per_hr * item.hours
            energy = _q(energy)
            blow_off = _q(blow_off)
            if inputs.electricity_tariff_per_kwh is not None:
                cost = _q(energy * inputs.electricity_tariff_per_kwh)
        results.append(
            CandidateResult(
                label=candidate.label,
                mode=candidate.curve.mode,
                points=points,
                annual_energy_kwh=energy,
                annual_energy_cost=cost,
                annual_blow_off_volume_nm3=blow_off,
            )
        )

    winners = []
    for index, q in enumerate(fractions):
        best = min(results, key=lambda r: (r.points[index].power_kw, r.label))
        winners.append(
            PointWinner(
                capacity_fraction=_q(q), label=best.label, power_kw=best.points[index].power_kw
            )
        )

    annual_winner = None
    if inputs.load_duration:
        annual_winner = min(
            results,
            key=lambda r: (
                r.annual_energy_kwh if r.annual_energy_kwh is not None else _ZERO,
                r.label,
            ),
        ).label

    return PartLoadComparisonResult(
        analysis_code=inputs.analysis_code,
        rated_fad_nm3_per_hr=inputs.rated_fad_nm3_per_hr,
        rated_power_kw=inputs.rated_power_kw,
        candidates=tuple(results),
        lowest_power_per_point=tuple(winners),
        lowest_annual_energy_label=annual_winner,
        profile_hours=_q(profile_hours),
    )
