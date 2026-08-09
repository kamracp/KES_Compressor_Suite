from decimal import Decimal

from app.domain.reciprocating.engine import (
    ReciprocatingEngineInput,
    calculate_reciprocating_case,
)
from app.domain.reciprocating.recip_models import (
    CylinderAction,
    ReciprocatingCylinderGeometry,
)


def build_engine_input(
    required_flow_m3_per_hr: Decimal = Decimal("14143.4"),
    allowable_rod_load_kn: Decimal = Decimal("450"),
) -> ReciprocatingEngineInput:
    geometry = ReciprocatingCylinderGeometry(
        bore_mm=Decimal("300"),
        stroke_mm=Decimal("400"),
        rod_diameter_mm=Decimal("70"),
        speed_rpm=Decimal("600"),
        clearance_fraction=Decimal("0.10"),
        action=CylinderAction.DOUBLE_ACTING,
    )

    return ReciprocatingEngineInput(
        geometry=geometry,
        required_flow_m3_per_hr=required_flow_m3_per_hr,
        stage_compression_ratio=Decimal("1.442"),
        suction_z_factor=Decimal("0.9398"),
        discharge_z_factor=Decimal("0.8700"),
        isentropic_exponent=Decimal("1.27"),
        suction_pressure_bar=Decimal("30"),
        discharge_pressure_bar=Decimal("43.27"),
        allowable_rod_load_kn=allowable_rod_load_kn,
    )


def test_complete_reciprocating_case() -> None:
    result = calculate_reciprocating_case(build_engine_input())

    assert result.capacity.displacement.total_displacement_m3_per_hr > Decimal("1980")
    assert result.capacity.displacement.total_displacement_m3_per_hr < Decimal("1985")

    assert result.capacity.volumetric_efficiency.volumetric_efficiency > Decimal("0.95")
    assert result.capacity.volumetric_efficiency.volumetric_efficiency < Decimal("0.98")

    assert result.capacity.volumetric_efficiency.delivered_flow_m3_per_hr > Decimal("1900")

    assert result.cylinder_sizing.required_cylinders == 8
    assert result.cylinder_sizing.capacity_is_adequate is True

    assert result.rod_load.maximum_absolute_load_kn > Decimal("90")
    assert result.rod_load.maximum_absolute_load_kn < Decimal("95")
    assert result.rod_load.rod_load_is_adequate is True


def test_lower_required_flow_reduces_required_cylinder_count() -> None:
    result = calculate_reciprocating_case(
        build_engine_input(
            required_flow_m3_per_hr=Decimal("5000"),
        )
    )

    assert result.cylinder_sizing.required_cylinders == 3


def test_low_allowable_rod_load_detects_overload() -> None:
    result = calculate_reciprocating_case(
        build_engine_input(
            allowable_rod_load_kn=Decimal("90"),
        )
    )

    assert result.rod_load.rod_load_is_adequate is False
