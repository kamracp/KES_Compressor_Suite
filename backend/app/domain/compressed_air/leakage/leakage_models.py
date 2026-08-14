from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from app.domain.compressed_air.energy.leakage_energy import (
    LeakageEnergyResult,
)


class LeakQuantificationBasis(StrEnum):
    FLOW_METER = "FLOW_METER"
    ULTRASONIC_ESTIMATE = "ULTRASONIC_ESTIMATE"
    DECAY_TEST = "DECAY_TEST"
    LOAD_UNLOAD_TEST = "LOAD_UNLOAD_TEST"
    ORIFICE_ESTIMATE = "ORIFICE_ESTIMATE"
    ENGINEERING_ESTIMATE = "ENGINEERING_ESTIMATE"
    OTHER = "OTHER"


class LeakSourceCategory(StrEnum):
    PIPE_JOINT = "PIPE_JOINT"
    HOSE = "HOSE"
    FITTING = "FITTING"
    QUICK_COUPLING = "QUICK_COUPLING"
    VALVE = "VALVE"
    FRL = "FRL"
    CYLINDER = "CYLINDER"
    ACTUATOR = "ACTUATOR"
    DRAIN = "DRAIN"
    EQUIPMENT_INTERNAL = "EQUIPMENT_INTERNAL"
    OTHER = "OTHER"


class LeakRepairStatus(StrEnum):
    OPEN = "OPEN"
    PLANNED = "PLANNED"
    REPAIRED = "REPAIRED"
    VERIFIED = "VERIFIED"
    DEFERRED = "DEFERRED"


class LeakPriority(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass(frozen=True, slots=True)
class LeakRegisterItem:
    """One identified compressed-air leakage point."""

    leak_code: str
    location: str

    baseline_leakage_flow_nm3_per_hr: Decimal
    quantification_basis: LeakQuantificationBasis

    source_category: LeakSourceCategory = LeakSourceCategory.OTHER

    area: str | None = None
    equipment_tag: str | None = None
    component_description: str | None = None

    survey_pressure_bar_g: Decimal | None = None

    expected_repair_fraction: Decimal = Decimal("1")

    repair_status: LeakRepairStatus = LeakRepairStatus.OPEN
    estimated_repair_cost: Decimal | None = None

    verified_post_repair_flow_nm3_per_hr: Decimal | None = None

    survey_method_reference: str | None = None
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class LeakageManagementInput:
    """Input basis for a complete compressed-air leakage-management study."""

    analysis_code: str

    leaks: tuple[LeakRegisterItem, ...]

    specific_power_kw_per_nm3_per_min: Decimal
    annual_operating_hours: Decimal
    electricity_tariff_per_kwh: Decimal

    average_system_demand_nm3_per_hr: Decimal | None = None

    notes: str | None = None


@dataclass(frozen=True, slots=True)
class LeakItemAnalysisResult:
    """Engineering and economic result for one registered leakage point."""

    leak_code: str
    location: str

    source_category: LeakSourceCategory
    quantification_basis: LeakQuantificationBasis

    repair_status: LeakRepairStatus
    priority: LeakPriority

    baseline_leakage_flow_nm3_per_hr: Decimal

    fraction_of_total_registered_leakage: Decimal

    energy: LeakageEnergyResult

    estimated_repair_cost: Decimal | None
    simple_payback_years: Decimal | None

    verified_post_repair_flow_nm3_per_hr: Decimal | None
    verified_flow_reduction_nm3_per_hr: Decimal | None
    verified_repair_fraction: Decimal | None

    notes: str | None = None


@dataclass(frozen=True, slots=True)
class LeakageManagementResult:
    """Aggregate leakage-management engineering result."""

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

    items: tuple[LeakItemAnalysisResult, ...]
