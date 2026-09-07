"""Request and response schemas for the C-7 sequencing assessment."""

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, Field, model_validator

from app.domain.compressed_air.performance.part_load import BelowTurndownMode
from app.domain.compressed_air.sequencing.sequencing_models import ControlMode, DutyRole
from app.schemas._bounds import (
    MAX_CENTRIFUGAL_TURNDOWN_FRACTION,
    MAX_CENTRIFUGAL_UNLOAD_POWER_FRACTION,
    MAX_ELECTRICITY_TARIFF_INR_PER_KWH,
    MAX_FIXED_SPEED_UNLOAD_POWER_FRACTION,
    MAX_MODULATION_FLOOR_CAPACITY_FRACTION,
    MAX_PLANT_AIR_PRESSURE_BAR_G,
    MIN_CENTRIFUGAL_POWER_FRACTION_AT_TURNDOWN,
    MIN_CENTRIFUGAL_TURNDOWN_FRACTION,
    MIN_CENTRIFUGAL_UNLOAD_POWER_FRACTION,
    MIN_ELECTRICITY_TARIFF_INR_PER_KWH,
    MIN_FIXED_SPEED_UNLOAD_POWER_FRACTION,
    MIN_MODULATION_FLOOR_CAPACITY_FRACTION,
    MIN_VSD_MINIMUM_FLOW_FRACTION,
)
from app.schemas.compressed_air_greenfield import DemandProfilePointInputSchema


class PressureBandSchema(BaseModel):
    load_pressure_bar_g: Decimal = Field(ge=0, le=MAX_PLANT_AIR_PRESSURE_BAR_G)
    unload_pressure_bar_g: Decimal = Field(gt=0, le=MAX_PLANT_AIR_PRESSURE_BAR_G)

    @model_validator(mode="after")
    def _ordered(self) -> Self:
        if self.unload_pressure_bar_g <= self.load_pressure_bar_g:
            raise ValueError("unload_pressure_bar_g must exceed load_pressure_bar_g.")
        return self


class SequencedMachineRequest(BaseModel):
    unit_code: str = Field(min_length=1, max_length=32)
    control_mode: ControlMode
    rated_fad_nm3_per_hr: Decimal = Field(
        gt=0,
        le=Decimal("36000"),
        description="Largest single plant-air package (MFR-ATLASCOPCO-AIR-RANGE-2026-09).",
    )
    rated_power_kw: Decimal = Field(
        gt=0,
        le=Decimal("3150"),
        description="Largest single plant-air motor (MFR-ATLASCOPCO-AIR-RANGE-2026-09).",
    )
    band: PressureBandSchema
    unload_power_fraction: Decimal | None = Field(
        default=None,
        ge=0,
        le=1,
        description=(
            "Unloaded draw as a fraction of rated power, from nameplate or measurement. "
            "Screw units (DOE-CAC-SOURCEBOOK-2003): 15-35 %, required. Centrifugal "
            "auto-dual (ATLASCOPCO-CAM-9ED-2019, ~20 %): 5-35 %, required only when "
            "below_turndown is UNLOAD."
        ),
    )
    modulation_floor_capacity_fraction: Decimal | None = Field(
        default=None,
        ge=MIN_MODULATION_FLOOR_CAPACITY_FRACTION,
        le=MAX_MODULATION_FLOOR_CAPACITY_FRACTION,
        description=(
            "MODULATION only: capacity where throttling ends and the unit unloads; "
            "default 0.40 (DOE Fig. 2.6)."
        ),
    )
    turndown_flow_fraction: Decimal | None = Field(
        default=None,
        ge=MIN_CENTRIFUGAL_TURNDOWN_FRACTION,
        le=MAX_CENTRIFUGAL_TURNDOWN_FRACTION,
        description=(
            "INLET_GUIDE_VANE only: turndown before blow-off / unload as a fraction of "
            "rated FAD (CAGI 30-40 % typical)."
        ),
    )
    power_fraction_at_turndown: Decimal | None = Field(
        default=None,
        ge=MIN_CENTRIFUGAL_POWER_FRACTION_AT_TURNDOWN,
        le=1,
        description="INLET_GUIDE_VANE only: power at full turndown / rated power (machine curve).",
    )
    below_turndown: BelowTurndownMode | None = Field(
        default=None,
        description="INLET_GUIDE_VANE only: BLOW_OFF (default) or UNLOAD (auto-dual).",
    )
    unload_blowdown_seconds: Decimal | None = Field(
        default=None,
        ge=0,
        le=Decimal("600"),
        description=(
            "FIXED_SPEED_LOAD_UNLOAD only, manufacturer figure: sump blowdown time; "
            "enables the storage-dependent penalty."
        ),
    )
    minimum_flow_fraction: Decimal | None = Field(
        default=None,
        ge=MIN_VSD_MINIMUM_FLOW_FRACTION,
        le=1,
        description="VSD only: minimum stable flow / rated FAD (turndown <= 86 %).",
    )
    minimum_flow_power_fraction: Decimal | None = Field(
        default=None, gt=0, le=1, description="VSD only: power at minimum flow / rated power."
    )
    standby_runs_unloaded: bool = Field(
        default=False,
        description="As-found: unit below the trim keeps running unloaded (no auto-stop).",
    )

    @model_validator(mode="after")
    def _mode_fields(self) -> Self:
        mode = self.control_mode
        is_vsd = mode is ControlMode.VARIABLE_SPEED
        is_igv = mode is ControlMode.INLET_GUIDE_VANE

        has_vsd_fields = (
            self.minimum_flow_fraction is not None and self.minimum_flow_power_fraction is not None
        )
        if is_vsd and not has_vsd_fields:
            raise ValueError(
                "VSD units need minimum_flow_fraction and minimum_flow_power_fraction."
            )
        if not is_vsd and (
            self.minimum_flow_fraction is not None or self.minimum_flow_power_fraction is not None
        ):
            raise ValueError("Only VSD units take minimum-flow fields.")

        if is_igv:
            if self.turndown_flow_fraction is None or self.power_fraction_at_turndown is None:
                raise ValueError(
                    "INLET_GUIDE_VANE units need turndown_flow_fraction "
                    "and power_fraction_at_turndown."
                )
            needs_unload = (
                self.below_turndown is BelowTurndownMode.UNLOAD or self.standby_runs_unloaded
            )
            if needs_unload and self.unload_power_fraction is None:
                raise ValueError(
                    "Centrifugal auto-dual / unloaded standby needs unload_power_fraction."
                )
            if self.unload_power_fraction is not None and not (
                MIN_CENTRIFUGAL_UNLOAD_POWER_FRACTION
                <= self.unload_power_fraction
                <= MAX_CENTRIFUGAL_UNLOAD_POWER_FRACTION
            ):
                raise ValueError(
                    "Centrifugal unload_power_fraction must be "
                    f"{MIN_CENTRIFUGAL_UNLOAD_POWER_FRACTION}-"
                    f"{MAX_CENTRIFUGAL_UNLOAD_POWER_FRACTION} (ATLASCOPCO-CAM-9ED-2019 ~0.20)."
                )
        else:
            if self.unload_power_fraction is None:
                raise ValueError("unload_power_fraction is required for screw control modes.")
            if not (
                MIN_FIXED_SPEED_UNLOAD_POWER_FRACTION
                <= self.unload_power_fraction
                <= MAX_FIXED_SPEED_UNLOAD_POWER_FRACTION
            ):
                raise ValueError(
                    f"unload_power_fraction must be {MIN_FIXED_SPEED_UNLOAD_POWER_FRACTION}-"
                    f"{MAX_FIXED_SPEED_UNLOAD_POWER_FRACTION} (DOE-CAC-SOURCEBOOK-2003)."
                )
            if (
                self.turndown_flow_fraction is not None
                or self.power_fraction_at_turndown is not None
                or self.below_turndown is not None
            ):
                raise ValueError("Only INLET_GUIDE_VANE units take turndown fields.")

        if (
            mode is not ControlMode.MODULATION
            and self.modulation_floor_capacity_fraction is not None
        ):
            raise ValueError("Only MODULATION units take modulation_floor_capacity_fraction.")
        if (
            mode is not ControlMode.FIXED_SPEED_LOAD_UNLOAD
            and self.unload_blowdown_seconds is not None
        ):
            raise ValueError("Only FIXED_SPEED_LOAD_UNLOAD units take unload_blowdown_seconds.")
        return self


class SequencingAssessmentRequest(BaseModel):
    analysis_code: str = Field(min_length=1, max_length=64)
    baseline_machines: list[SequencedMachineRequest] = Field(min_length=1, max_length=20)
    demand_profile: list[DemandProfilePointInputSchema] = Field(min_length=1, max_length=8784)
    receiver_volume_m3: Decimal = Field(gt=0)
    electricity_tariff_per_kwh: Decimal = Field(
        ge=MIN_ELECTRICITY_TARIFF_INR_PER_KWH, le=MAX_ELECTRICITY_TARIFF_INR_PER_KWH
    )
    proposed_band: PressureBandSchema
    annual_operating_hours: Decimal = Field(
        gt=0, le=Decimal("8784"), description="Calendar limit: 366 days x 24 h."
    )

    @model_validator(mode="after")
    def _unique_codes(self) -> Self:
        codes = [m.unit_code for m in self.baseline_machines]
        if len(set(codes)) != len(codes):
            raise ValueError("Machine unit codes must be unique.")
        return self


class MachinePeriodResponse(BaseModel):
    unit_code: str
    period_index: int
    duty_role: DutyRole
    delivered_flow_nm3_per_hr: Decimal
    load_fraction: Decimal
    cycles_per_hour: Decimal | None
    average_power_kw: Decimal
    energy_kwh: Decimal
    wasted_flow_nm3_per_hr: Decimal = Decimal("0")  # centrifugal blow-off (C-8)


class PeriodResponse(BaseModel):
    period_index: int
    label: str
    demand_nm3_per_hr: Decimal
    duration_hours: Decimal
    supplied_flow_nm3_per_hr: Decimal
    shortfall_nm3_per_hr: Decimal
    average_header_pressure_bar_g: Decimal
    total_power_kw: Decimal
    energy_kwh: Decimal
    machines: list[MachinePeriodResponse]


class SequencingRunResponse(BaseModel):
    periods: list[PeriodResponse]
    total_energy_kwh: Decimal
    total_energy_cost: Decimal
    specific_power_kw_per_nm3_per_min: Decimal
    unload_energy_kwh: Decimal
    standby_energy_kwh: Decimal
    unmet_demand_hours: Decimal


class ProposedMachineResponse(BaseModel):
    unit_code: str
    control_mode: ControlMode
    priority: int
    band: PressureBandSchema


class SequencingAssessmentResponse(BaseModel):
    analysis_code: str
    baseline: SequencingRunResponse
    proposed: SequencingRunResponse
    proposed_machines: list[ProposedMachineResponse]
    profile_hours: Decimal
    annualisation_factor: Decimal
    baseline_average_header_pressure_bar_g: Decimal
    proposed_average_header_pressure_bar_g: Decimal
    standby_saving_kwh: Decimal
    trim_saving_kwh: Decimal
    pressure_saving_kwh: Decimal
    total_annual_saving_kwh: Decimal
    total_annual_cost_saving: Decimal
    saving_claimed: bool
    note: str
