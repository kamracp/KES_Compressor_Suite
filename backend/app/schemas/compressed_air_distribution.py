from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.compressed_air.distribution.network_models import (
    NetworkNodeType,
    NetworkTopology,
    PipeSegmentRole,
)
from app.schemas._bounds import MAX_PLANT_AIR_PRESSURE_BAR_G
from app.schemas.calculation_execution import CalculationExecutionMetadata


class NetworkNodePayload(BaseModel):
    """One node in a compressed-air distribution network."""

    node_code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=200)
    node_type: NetworkNodeType

    elevation_m: Decimal = Decimal("0")

    demand_nm3_per_hr: Decimal = Field(default=Decimal("0"), ge=0)
    minimum_pressure_bar_g: Decimal | None = Field(
        default=None, ge=0, le=MAX_PLANT_AIR_PRESSURE_BAR_G
    )

    area: str | None = Field(default=None, max_length=200)
    notes: str | None = Field(default=None, max_length=1000)


class PipeSegmentPayload(BaseModel):
    """One pipe segment connecting two network nodes."""

    segment_code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=200)
    role: PipeSegmentRole

    start_node_code: str = Field(min_length=1, max_length=50)
    end_node_code: str = Field(min_length=1, max_length=50)

    length_m: Decimal = Field(gt=0)
    equivalent_fitting_length_m: Decimal = Field(ge=0)

    internal_diameter_mm: Decimal = Field(gt=0)

    roughness_mm: Decimal = Field(
        ge=0,
        le=Decimal("10"),
        description=(
            "Moody (1944) absolute roughness table: drawn tubing 0.0015 mm to riveted "
            "steel about 9 mm."
        ),
    )
    design_flow_nm3_per_hr: Decimal = Field(gt=0)

    operating_pressure_bar_g: Decimal = Field(ge=0, le=MAX_PLANT_AIR_PRESSURE_BAR_G)
    operating_temperature_k: Decimal = Field(
        ge=Decimal("233"),
        le=Decimal("423"),
        description=(
            "-40 degC intake floor to 150 degC uncooled discharge ceiling (API 618 practice)."
        ),
    )
    material: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None, max_length=1000)


class NetworkPathPayload(BaseModel):
    """One flow path from source to a downstream node."""

    path_code: str = Field(min_length=1, max_length=50)
    node_codes: list[str] = Field(min_length=2)
    segment_codes: list[str] = Field(min_length=1)


class DistributionNetworkCalculationRequest(BaseModel):
    """Request payload for compressed-air distribution network analysis.

    Runs structural validation and hydraulic path solving; when candidate
    internal diameters are supplied (from the user's actual pipe schedule),
    a pipe-diameter optimization pass is also executed.
    """

    network_code: str = Field(min_length=1, max_length=50)
    topology: NetworkTopology

    nodes: list[NetworkNodePayload] = Field(min_length=1)
    segments: list[PipeSegmentPayload] = Field(min_length=1)
    paths: list[NetworkPathPayload] = Field(min_length=1)

    design_source_pressure_bar_g: Decimal = Field(ge=0, le=MAX_PLANT_AIR_PRESSURE_BAR_G)

    air_density_kg_per_m3: Decimal = Field(
        ge=Decimal("0.5"),
        le=Decimal("25"),
        description=(
            "Ideal gas: 1 bar a at 60 degC gives 1.05 kg/m3; 16 bar a at 0 degC gives 20.4 kg/m3."
        ),
    )
    darcy_friction_factor: Decimal = Field(gt=0, lt=1)

    candidate_internal_diameters_mm: list[Decimal] | None = Field(
        default=None,
        min_length=1,
        description=(
            "Available pipe internal diameters from the user's actual pipe "
            "schedule. When provided, deficient paths are optimized against "
            "these candidates."
        ),
    )

    maximum_preferred_velocity_m_per_s: Decimal = Field(
        # Calibrated default: CAGI recommends <= 20 ft/s (~6 m/s); BCAS design
        # band is 6-7 m/s with a 9 m/s never-exceed ceiling for mains.
        # Standards registry: CAGI-CAGH, BCAS-BPG-101.
        default=Decimal("6"),
        gt=0,
    )
    minimum_pressure_drop_reduction_fraction: Decimal = Field(
        default=Decimal("0.20"),
        gt=0,
        lt=1,
    )

    description: str | None = Field(default=None, max_length=1000)


class DistributionNetworkExecutionRequest(BaseModel):
    """Execution wrapper: calculation payload plus persistence metadata."""

    calculation: DistributionNetworkCalculationRequest
    execution: CalculationExecutionMetadata
