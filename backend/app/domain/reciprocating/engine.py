from dataclasses import dataclass
from decimal import Decimal

from app.domain.reciprocating.capacity import (
    ReciprocatingCapacitySizingResult,
    calculate_required_cylinders,
)
from app.domain.reciprocating.displacement import calculate_displacement
from app.domain.reciprocating.recip_models import (
    ReciprocatingCapacityResult,
    ReciprocatingCylinderGeometry,
)
from app.domain.reciprocating.rod_load import (
    RodLoadResult,
    calculate_rod_load,
)
from app.domain.reciprocating.volumetric_efficiency import (
    calculate_volumetric_efficiency,
)


@dataclass(frozen=True, slots=True)
class ReciprocatingEngineInput:
    """Input data for reciprocating compressor capacity sizing."""

    geometry: ReciprocatingCylinderGeometry

    required_flow_m3_per_hr: Decimal

    stage_compression_ratio: Decimal
    suction_z_factor: Decimal
    discharge_z_factor: Decimal
    isentropic_exponent: Decimal

    suction_pressure_bar: Decimal
    discharge_pressure_bar: Decimal
    allowable_rod_load_kn: Decimal


@dataclass(frozen=True, slots=True)
class ReciprocatingEngineResult:
    """Integrated reciprocating compressor sizing result."""

    capacity: ReciprocatingCapacityResult
    cylinder_sizing: ReciprocatingCapacitySizingResult
    rod_load: RodLoadResult


def calculate_reciprocating_case(
    inputs: ReciprocatingEngineInput,
) -> ReciprocatingEngineResult:
    """Run an integrated reciprocating compressor sizing calculation."""

    displacement = calculate_displacement(inputs.geometry)

    volumetric_efficiency = calculate_volumetric_efficiency(
        clearance_fraction=inputs.geometry.clearance_fraction,
        stage_compression_ratio=inputs.stage_compression_ratio,
        suction_z_factor=inputs.suction_z_factor,
        discharge_z_factor=inputs.discharge_z_factor,
        isentropic_exponent=inputs.isentropic_exponent,
        displacement_m3_per_hr=displacement.total_displacement_m3_per_hr,
    )

    capacity = ReciprocatingCapacityResult(
        geometry=inputs.geometry,
        displacement=displacement,
        volumetric_efficiency=volumetric_efficiency,
    )

    cylinder_sizing = calculate_required_cylinders(
        required_flow_m3_per_hr=inputs.required_flow_m3_per_hr,
        delivered_flow_per_cylinder_m3_per_hr=(volumetric_efficiency.delivered_flow_m3_per_hr),
    )

    rod_load = calculate_rod_load(
        piston_area_m2=displacement.piston_area_m2,
        rod_area_m2=displacement.rod_area_m2,
        suction_pressure_bar=inputs.suction_pressure_bar,
        discharge_pressure_bar=inputs.discharge_pressure_bar,
        allowable_rod_load_kn=inputs.allowable_rod_load_kn,
    )

    return ReciprocatingEngineResult(
        capacity=capacity,
        cylinder_sizing=cylinder_sizing,
        rod_load=rod_load,
    )
