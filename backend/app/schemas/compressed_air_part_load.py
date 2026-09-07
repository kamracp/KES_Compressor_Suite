"""Request / response schemas for the C-8 part-load comparison endpoint."""

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, Field, model_validator

from app.domain.compressed_air.performance.part_load import BelowTurndownMode, PartLoadMode
from app.schemas._bounds import (
    MAX_CENTRIFUGAL_TURNDOWN_FRACTION,
    MAX_ELECTRICITY_TARIFF_INR_PER_KWH,
    MAX_MODULATION_FLOOR_CAPACITY_FRACTION,
    MIN_CENTRIFUGAL_POWER_FRACTION_AT_TURNDOWN,
    MIN_CENTRIFUGAL_TURNDOWN_FRACTION,
    MIN_ELECTRICITY_TARIFF_INR_PER_KWH,
    MIN_MODULATION_FLOOR_CAPACITY_FRACTION,
    MIN_VSD_MINIMUM_FLOW_FRACTION,
)


class PartLoadCandidateRequest(BaseModel):
    """One control mode to evaluate. Mode rules are enforced by part_load.validate_curve."""

    label: str = Field(min_length=1, max_length=48)
    mode: PartLoadMode
    unload_power_fraction: Decimal | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Screw 0.15-0.35 (DOE-CAC-SOURCEBOOK-2003); centrifugal auto-dual 0.05-0.35.",
    )
    modulation_floor_capacity_fraction: Decimal | None = Field(
        default=None,
        ge=MIN_MODULATION_FLOOR_CAPACITY_FRACTION,
        le=MAX_MODULATION_FLOOR_CAPACITY_FRACTION,
    )
    minimum_flow_fraction: Decimal | None = Field(
        default=None, ge=MIN_VSD_MINIMUM_FLOW_FRACTION, le=1
    )
    minimum_flow_power_fraction: Decimal | None = Field(default=None, gt=0, le=1)
    turndown_flow_fraction: Decimal | None = Field(
        default=None,
        ge=MIN_CENTRIFUGAL_TURNDOWN_FRACTION,
        le=MAX_CENTRIFUGAL_TURNDOWN_FRACTION,
    )
    power_fraction_at_turndown: Decimal | None = Field(
        default=None, ge=MIN_CENTRIFUGAL_POWER_FRACTION_AT_TURNDOWN, le=1
    )
    below_turndown: BelowTurndownMode | None = None


class LoadDurationBinRequest(BaseModel):
    capacity_fraction: Decimal = Field(ge=0, le=1)
    hours: Decimal = Field(gt=0, le=Decimal("8784"))


class PartLoadComparisonRequest(BaseModel):
    analysis_code: str = Field(min_length=1, max_length=64)
    rated_fad_nm3_per_hr: Decimal = Field(gt=0, le=Decimal("36000"))
    rated_power_kw: Decimal = Field(gt=0, le=Decimal("3150"))
    candidates: list[PartLoadCandidateRequest] = Field(min_length=1, max_length=8)
    capacity_fractions: list[Decimal] = Field(
        default=[Decimal("0.25"), Decimal("0.5"), Decimal("0.75"), Decimal("1")],
        min_length=1,
        max_length=21,
    )
    load_duration: list[LoadDurationBinRequest] = Field(default=[], max_length=24)
    electricity_tariff_per_kwh: Decimal | None = Field(
        default=None,
        ge=MIN_ELECTRICITY_TARIFF_INR_PER_KWH,
        le=MAX_ELECTRICITY_TARIFF_INR_PER_KWH,
    )

    @model_validator(mode="after")
    def _unique_labels(self) -> Self:
        labels = [c.label for c in self.candidates]
        if len(set(labels)) != len(labels):
            raise ValueError("Candidate labels must be unique.")
        return self


class CandidatePointResponse(BaseModel):
    capacity_fraction: Decimal
    power_fraction: Decimal
    power_kw: Decimal
    specific_power_kw_per_nm3_per_min: Decimal | None
    wasted_flow_nm3_per_hr: Decimal
    regime: str


class CandidateResponse(BaseModel):
    label: str
    mode: PartLoadMode
    points: list[CandidatePointResponse]
    annual_energy_kwh: Decimal | None
    annual_energy_cost: Decimal | None
    annual_blow_off_volume_nm3: Decimal | None


class PointWinnerResponse(BaseModel):
    capacity_fraction: Decimal
    label: str
    power_kw: Decimal


class PartLoadComparisonResponse(BaseModel):
    analysis_code: str
    rated_fad_nm3_per_hr: Decimal
    rated_power_kw: Decimal
    candidates: list[CandidateResponse]
    lowest_power_per_point: list[PointWinnerResponse]
    lowest_annual_energy_label: str | None
    profile_hours: Decimal
