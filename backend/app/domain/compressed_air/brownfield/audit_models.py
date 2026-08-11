from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from app.domain.compressed_air.station.station_models import (
    CompressorControlMode,
    CompressorTechnology,
)


class AuditOperatingState(StrEnum):
    """Observed operating state of an existing compressor."""

    LOADED = "LOADED"
    UNLOADED = "UNLOADED"
    PART_LOAD = "PART_LOAD"
    STOPPED = "STOPPED"


class AuditObservationSeverity(StrEnum):
    """Severity of a compressed-air audit observation."""

    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True, slots=True)
class ExistingCompressor:
    """One compressor installed in an existing factory."""

    unit_code: str
    equipment_source: str | None
    model: str | None

    technology: CompressorTechnology
    control_mode: CompressorControlMode

    rated_fad_nm3_per_hr: Decimal
    rated_discharge_pressure_bar_g: Decimal
    rated_motor_power_kw: Decimal

    installation_year: int | None = None
    operating_hours: Decimal | None = None

    available: bool = True
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class CompressorMeasurementPoint:
    """Measured operating point for one existing compressor."""

    unit_code: str
    timestamp_label: str

    operating_state: AuditOperatingState

    measured_flow_nm3_per_hr: Decimal
    measured_discharge_pressure_bar_g: Decimal
    measured_power_kw: Decimal

    load_fraction: Decimal | None = None


@dataclass(frozen=True, slots=True)
class SystemMeasurementPoint:
    """Plant-level compressed-air measurement point."""

    timestamp_label: str

    total_flow_nm3_per_hr: Decimal
    header_pressure_bar_g: Decimal
    total_power_kw: Decimal

    production_state: str | None = None
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class LeakageSurveySummary:
    """Measured or estimated plant compressed-air leakage."""

    measured_leakage_flow_nm3_per_hr: Decimal

    survey_method: str

    estimated_repair_fraction: Decimal

    survey_notes: str | None = None


@dataclass(frozen=True, slots=True)
class AuditObservation:
    """One engineering observation recorded during a system audit."""

    observation_code: str
    title: str

    severity: AuditObservationSeverity

    description: str

    recommended_action: str | None = None


@dataclass(frozen=True, slots=True)
class BrownfieldAuditCase:
    """Complete existing compressed-air system audit input."""

    audit_code: str
    project_id: int

    compressors: tuple[ExistingCompressor, ...]

    compressor_measurements: tuple[CompressorMeasurementPoint, ...]
    system_measurements: tuple[SystemMeasurementPoint, ...]

    leakage_summary: LeakageSurveySummary | None = None

    observations: tuple[AuditObservation, ...] = ()

    electricity_tariff_per_kwh: Decimal = Decimal("0")

    annual_operating_hours: Decimal = Decimal("0")

    notes: str | None = None
