from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from app.domain.compressed_air.station.station_models import (
    CompressorControlMode,
    CompressorTechnology,
)


class EquipmentDataSourceType(StrEnum):
    """Source type for manufacturer performance data."""

    DATASHEET = "DATASHEET"
    CATALOG = "CATALOG"
    PERFORMANCE_CURVE = "PERFORMANCE_CURVE"
    SOFTWARE_EXPORT = "SOFTWARE_EXPORT"
    TEST_CERTIFICATE = "TEST_CERTIFICATE"
    MANUAL = "MANUAL"
    OTHER = "OTHER"


class EquipmentDataVerificationStatus(StrEnum):
    """Verification status for manufacturer-supplied data."""

    UNVERIFIED = "UNVERIFIED"
    SOURCE_VERIFIED = "SOURCE_VERIFIED"
    ENGINEERING_VERIFIED = "ENGINEERING_VERIFIED"
    APPROVED = "APPROVED"


@dataclass(frozen=True, slots=True)
class EquipmentReference:
    """Traceable manufacturer data source."""

    source_name: str

    source_type: EquipmentDataSourceType

    document_title: str
    document_reference: str | None = None
    document_revision: str | None = None

    source_url: str | None = None

    verification_status: EquipmentDataVerificationStatus = (
        EquipmentDataVerificationStatus.UNVERIFIED
    )

    notes: str | None = None


@dataclass(frozen=True, slots=True)
class CompressorCatalogModel:
    """Vendor-neutral compressor catalog model."""

    source_name: str
    model_code: str

    technology: CompressorTechnology
    control_mode: CompressorControlMode

    rated_fad_nm3_per_hr: Decimal
    rated_discharge_pressure_bar_g: Decimal

    rated_motor_power_kw: Decimal

    minimum_fad_nm3_per_hr: Decimal | None = None
    maximum_fad_nm3_per_hr: Decimal | None = None

    specific_power_kw_per_nm3_per_min: Decimal | None = None

    minimum_operating_pressure_bar_g: Decimal | None = None
    maximum_operating_pressure_bar_g: Decimal | None = None

    inlet_temperature_min_c: Decimal | None = None
    inlet_temperature_max_c: Decimal | None = None

    cooling_air_requirement_m3_per_hr: Decimal | None = None
    cooling_water_requirement_m3_per_hr: Decimal | None = None

    dimensions_length_mm: Decimal | None = None
    dimensions_width_mm: Decimal | None = None
    dimensions_height_mm: Decimal | None = None

    mass_kg: Decimal | None = None

    sound_pressure_level_dba: Decimal | None = None

    voltage_v: Decimal | None = None
    frequency_hz: Decimal | None = None

    reference: EquipmentReference | None = None

    notes: str | None = None


@dataclass(frozen=True, slots=True)
class CompressorPerformancePoint:
    """One published or verified compressor performance point."""

    source_name: str
    model_code: str

    discharge_pressure_bar_g: Decimal

    fad_nm3_per_hr: Decimal
    shaft_or_input_power_kw: Decimal

    specific_power_kw_per_nm3_per_min: Decimal

    inlet_temperature_c: Decimal | None = None

    relative_humidity_fraction: Decimal | None = None

    speed_fraction: Decimal | None = None

    load_fraction: Decimal | None = None

    reference: EquipmentReference | None = None


@dataclass(frozen=True, slots=True)
class EquipmentCatalog:
    """Collection of vendor-neutral compressor catalog models."""

    models: tuple[CompressorCatalogModel, ...]

    total_models: int

    sources: tuple[str, ...]
