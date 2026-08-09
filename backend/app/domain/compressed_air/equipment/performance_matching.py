from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from app.domain.compressed_air.equipment.equipment_models import (
    CompressorCatalogModel,
    EquipmentCatalog,
)
from app.domain.compressed_air.station.station_models import (
    CompressorControlMode,
    CompressorTechnology,
)


class EquipmentMatchStatus(StrEnum):
    """Engineering suitability of one equipment option."""

    SUITABLE = "SUITABLE"
    MARGIN_LOW = "MARGIN_LOW"
    PRESSURE_INSUFFICIENT = "PRESSURE_INSUFFICIENT"
    CAPACITY_INSUFFICIENT = "CAPACITY_INSUFFICIENT"
    TECHNOLOGY_MISMATCH = "TECHNOLOGY_MISMATCH"


@dataclass(frozen=True, slots=True)
class EquipmentMatchingInput:
    """Engineering requirements used for equipment matching."""

    required_fad_nm3_per_hr: Decimal
    required_discharge_pressure_bar_g: Decimal

    minimum_capacity_margin_fraction: Decimal = Decimal("0.10")

    preferred_technology: CompressorTechnology | None = None
    preferred_control_mode: CompressorControlMode | None = None


@dataclass(frozen=True, slots=True)
class EquipmentMatchResult:
    """Engineering match result for one equipment option."""

    model_code: str

    technology: CompressorTechnology
    control_mode: CompressorControlMode

    rated_fad_nm3_per_hr: Decimal
    rated_discharge_pressure_bar_g: Decimal
    rated_motor_power_kw: Decimal

    required_fad_nm3_per_hr: Decimal
    required_discharge_pressure_bar_g: Decimal

    capacity_margin_nm3_per_hr: Decimal
    capacity_margin_fraction: Decimal

    pressure_margin_bar: Decimal

    technology_preference_met: bool
    control_preference_met: bool

    status: EquipmentMatchStatus

    engineering_score: Decimal

    reasons: tuple[str, ...]


def match_equipment(
    *,
    catalog: EquipmentCatalog,
    requirements: EquipmentMatchingInput,
) -> tuple[EquipmentMatchResult, ...]:
    """Rank vendor-neutral equipment options against engineering requirements."""

    _validate_requirements(requirements)

    results = tuple(
        _evaluate_model(
            model=model,
            requirements=requirements,
        )
        for model in catalog.models
    )

    return tuple(
        sorted(
            results,
            key=lambda item: (
                -item.engineering_score,
                item.rated_motor_power_kw,
                item.model_code.casefold(),
            ),
        )
    )


def get_suitable_equipment(
    *,
    catalog: EquipmentCatalog,
    requirements: EquipmentMatchingInput,
) -> tuple[EquipmentMatchResult, ...]:
    """Return only technically suitable equipment options."""

    return tuple(
        result
        for result in match_equipment(
            catalog=catalog,
            requirements=requirements,
        )
        if result.status == EquipmentMatchStatus.SUITABLE
    )


def _evaluate_model(
    *,
    model: CompressorCatalogModel,
    requirements: EquipmentMatchingInput,
) -> EquipmentMatchResult:
    capacity_margin = model.rated_fad_nm3_per_hr - requirements.required_fad_nm3_per_hr

    capacity_margin_fraction = capacity_margin / requirements.required_fad_nm3_per_hr

    pressure_margin = (
        model.rated_discharge_pressure_bar_g - requirements.required_discharge_pressure_bar_g
    )

    technology_preference_met = (
        requirements.preferred_technology is None
        or model.technology == requirements.preferred_technology
    )

    control_preference_met = (
        requirements.preferred_control_mode is None
        or model.control_mode == requirements.preferred_control_mode
    )

    reasons: list[str] = []

    if pressure_margin < 0:
        status = EquipmentMatchStatus.PRESSURE_INSUFFICIENT
        reasons.append("Rated discharge pressure is below the required pressure.")

    elif capacity_margin < 0:
        status = EquipmentMatchStatus.CAPACITY_INSUFFICIENT
        reasons.append("Rated free-air delivery is below the required capacity.")

    elif not technology_preference_met:
        status = EquipmentMatchStatus.TECHNOLOGY_MISMATCH
        reasons.append("Equipment technology does not match the preferred technology.")

    elif capacity_margin_fraction < requirements.minimum_capacity_margin_fraction:
        status = EquipmentMatchStatus.MARGIN_LOW
        reasons.append("Available capacity margin is below the specified minimum.")

    else:
        status = EquipmentMatchStatus.SUITABLE
        reasons.append("Equipment satisfies the primary capacity and pressure requirements.")

    if control_preference_met:
        if requirements.preferred_control_mode is not None:
            reasons.append("Preferred control mode is satisfied.")
    else:
        reasons.append("Preferred control mode is not satisfied.")

    score = _calculate_engineering_score(
        status=status,
        capacity_margin_fraction=capacity_margin_fraction,
        pressure_margin_bar=pressure_margin,
        technology_preference_met=technology_preference_met,
        control_preference_met=control_preference_met,
    )

    return EquipmentMatchResult(
        model_code=model.model_code,
        technology=model.technology,
        control_mode=model.control_mode,
        rated_fad_nm3_per_hr=model.rated_fad_nm3_per_hr,
        rated_discharge_pressure_bar_g=(model.rated_discharge_pressure_bar_g),
        rated_motor_power_kw=model.rated_motor_power_kw,
        required_fad_nm3_per_hr=requirements.required_fad_nm3_per_hr,
        required_discharge_pressure_bar_g=(requirements.required_discharge_pressure_bar_g),
        capacity_margin_nm3_per_hr=capacity_margin,
        capacity_margin_fraction=capacity_margin_fraction,
        pressure_margin_bar=pressure_margin,
        technology_preference_met=technology_preference_met,
        control_preference_met=control_preference_met,
        status=status,
        engineering_score=score,
        reasons=tuple(reasons),
    )


def _calculate_engineering_score(
    *,
    status: EquipmentMatchStatus,
    capacity_margin_fraction: Decimal,
    pressure_margin_bar: Decimal,
    technology_preference_met: bool,
    control_preference_met: bool,
) -> Decimal:
    score = Decimal("100")

    if status == EquipmentMatchStatus.PRESSURE_INSUFFICIENT:
        score -= Decimal("60")

    elif status == EquipmentMatchStatus.CAPACITY_INSUFFICIENT:
        score -= Decimal("50")

    elif status == EquipmentMatchStatus.TECHNOLOGY_MISMATCH:
        score -= Decimal("30")

    elif status == EquipmentMatchStatus.MARGIN_LOW:
        score -= Decimal("20")

    if not technology_preference_met:
        score -= Decimal("10")

    if not control_preference_met:
        score -= Decimal("5")

    if capacity_margin_fraction < 0:
        score += capacity_margin_fraction * Decimal("20")

    if pressure_margin_bar < 0:
        score += pressure_margin_bar * Decimal("2")

    return max(score, Decimal("0"))


def _validate_requirements(
    requirements: EquipmentMatchingInput,
) -> None:
    if requirements.required_fad_nm3_per_hr <= 0:
        raise ValueError("Required FAD must be greater than zero.")

    if requirements.required_discharge_pressure_bar_g < 0:
        raise ValueError("Required discharge pressure cannot be negative.")

    if (
        requirements.minimum_capacity_margin_fraction < 0
        or requirements.minimum_capacity_margin_fraction >= 1
    ):
        raise ValueError("Minimum capacity margin fraction must be between zero and one.")
