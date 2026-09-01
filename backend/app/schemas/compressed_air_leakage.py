from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.compressed_air.leakage.leakage_models import (
    LeakPriority,
    LeakQuantificationBasis,
    LeakRepairStatus,
    LeakSourceCategory,
)
from app.schemas._bounds import (
    MAX_ELECTRICITY_TARIFF_INR_PER_KWH,
    MIN_ELECTRICITY_TARIFF_INR_PER_KWH,
)


class LeakRegisterItemInputSchema(BaseModel):
    """One identified compressed-air leakage point."""

    leak_code: str
    location: str

    baseline_leakage_flow_nm3_per_hr: Decimal = Field(ge=0)
    quantification_basis: LeakQuantificationBasis

    source_category: LeakSourceCategory = LeakSourceCategory.OTHER

    area: str | None = None
    equipment_tag: str | None = None
    component_description: str | None = None

    survey_pressure_bar_g: Decimal | None = Field(
        default=None,
        ge=0,
    )

    expected_repair_fraction: Decimal = Field(
        default=Decimal("1"),
        ge=0,
        le=1,
    )

    repair_status: LeakRepairStatus = LeakRepairStatus.OPEN

    estimated_repair_cost: Decimal | None = Field(
        default=None,
        ge=0,
    )

    verified_post_repair_flow_nm3_per_hr: Decimal | None = Field(
        default=None,
        ge=0,
    )

    survey_method_reference: str | None = None
    notes: str | None = None


class CompressedAirLeakageManagementRequest(BaseModel):
    """Request for standalone compressed-air leakage management."""

    analysis_code: str

    leaks: list[LeakRegisterItemInputSchema] = Field(
        min_length=1,
    )

    specific_power_kw_per_nm3_per_min: Decimal = Field(gt=0)

    # Fraction of avoided demand converted to electrical saving by the
    # compressor controls (1 = fully effective turndown such as VSD or a
    # well-sequenced station; ~0.5 for inlet modulation without unloading).
    demand_saving_control_factor: Decimal = Field(
        default=Decimal("1"),
        ge=0,
        le=1,
        description=(
            "Fraction of avoided air demand that the compressor "
            "controls convert into electrical savings. 1 = fully "
            "effective turndown (VSD, on/off, or a well-sequenced "
            "station); load/unload typically 0.3-0.6; inlet modulation "
            "without unloading roughly 0.3. Ref: US DOE / Compressed "
            "Air Challenge, 'Improving Compressed Air System "
            "Performance: A Sourcebook for Industry'."
        ),
    )

    annual_operating_hours: Decimal = Field(gt=0)

    electricity_tariff_per_kwh: Decimal = Field(
        ge=MIN_ELECTRICITY_TARIFF_INR_PER_KWH,
        le=MAX_ELECTRICITY_TARIFF_INR_PER_KWH,
    )

    average_system_demand_nm3_per_hr: Decimal | None = Field(
        default=None,
        gt=0,
    )

    notes: str | None = None


class LeakageEnergyResponse(BaseModel):
    """Energy and economic result for a leakage quantity."""

    leakage_flow_nm3_per_hr: Decimal
    leakage_flow_nm3_per_min: Decimal

    wasted_power_kw: Decimal

    annual_wasted_energy_kwh: Decimal
    annual_wasted_energy_cost: Decimal

    expected_repair_fraction: Decimal
    demand_saving_control_factor: Decimal

    recoverable_leakage_flow_nm3_per_hr: Decimal
    recoverable_power_kw: Decimal

    annual_energy_saving_kwh: Decimal
    annual_cost_saving: Decimal

    residual_leakage_flow_nm3_per_hr: Decimal


class LeakageRegisterItemResultResponse(BaseModel):
    """Engineering result for one registered leakage point."""

    leak_code: str
    location: str

    source_category: LeakSourceCategory
    quantification_basis: LeakQuantificationBasis

    repair_status: LeakRepairStatus
    priority: LeakPriority

    baseline_leakage_flow_nm3_per_hr: Decimal

    fraction_of_total_registered_leakage: Decimal

    energy: LeakageEnergyResponse

    estimated_repair_cost: Decimal | None
    simple_payback_years: Decimal | None

    verified_post_repair_flow_nm3_per_hr: Decimal | None
    verified_flow_reduction_nm3_per_hr: Decimal | None
    verified_repair_fraction: Decimal | None

    notes: str | None = None


class CompressedAirLeakageManagementResponse(BaseModel):
    """Aggregate compressed-air leakage-management result."""

    analysis_code: str

    leak_count: int

    total_registered_leakage_flow_nm3_per_hr: Decimal

    leakage_fraction_of_average_system_demand: Decimal | None

    total_wasted_power_kw: Decimal
    total_annual_wasted_energy_kwh: Decimal
    total_annual_wasted_energy_cost: Decimal

    total_recoverable_leakage_flow_nm3_per_hr: Decimal
    total_recoverable_power_kw: Decimal

    total_annual_energy_saving_kwh: Decimal
    total_annual_cost_saving: Decimal

    total_residual_leakage_flow_nm3_per_hr: Decimal

    verified_leak_count: int
    verified_flow_reduction_nm3_per_hr: Decimal

    items: list[LeakageRegisterItemResultResponse]
