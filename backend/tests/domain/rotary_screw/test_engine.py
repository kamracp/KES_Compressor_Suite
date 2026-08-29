from decimal import Decimal

from app.domain.rotary_screw.engine import (
    RotaryScrewEngineInput,
    calculate_rotary_screw_case,
)
from app.domain.rotary_screw.models import (
    RotaryScrewControlType,
    RotaryScrewOilType,
    RotaryScrewOperatingPoint,
    RotaryScrewRotorGeometry,
)


def _operating_point() -> RotaryScrewOperatingPoint:
    return RotaryScrewOperatingPoint(
        inlet_pressure_bar_a=Decimal("1"),
        inlet_temperature_k=Decimal("300"),
        discharge_pressure_bar_g=Decimal("7"),
        rotational_speed_rpm=Decimal("3000"),
        oil_type=RotaryScrewOilType.OIL_INJECTED,
        control_type=RotaryScrewControlType.FIXED_SPEED_LOAD_UNLOAD,
    )


def test_minimal_case_only_computes_performance() -> None:
    inputs = RotaryScrewEngineInput(
        operating_point=_operating_point(),
        rated_fad_m3_per_min=Decimal("10"),
        package_input_power_kw=Decimal("60"),
    )

    result = calculate_rotary_screw_case(inputs)

    assert result.displacement is None
    assert result.standard_air_correction is None
    assert result.annual_energy_cost is None
    assert result.performance.specific_power_kw_per_m3_min == Decimal("6.000")


def test_full_case_computes_all_results() -> None:
    inputs = RotaryScrewEngineInput(
        operating_point=_operating_point(),
        rated_fad_m3_per_min=Decimal("10"),
        package_input_power_kw=Decimal("60"),
        rotor_geometry=RotaryScrewRotorGeometry(
            male_rotor_diameter_mm=Decimal("200"),
            rotor_length_mm=Decimal("300"),
            area_utilisation_coefficient=Decimal("0.5"),
        ),
        standard_reference_pressure_bar_a=Decimal("1"),
        standard_reference_temperature_k=Decimal("300"),
        annual_operating_hours=Decimal("8000"),
        electricity_tariff_per_kwh=Decimal("5"),
    )

    result = calculate_rotary_screw_case(inputs)

    assert result.displacement is not None
    assert result.displacement.theoretical_displacement_m3_per_min == Decimal("18.000")

    assert result.standard_air_correction is not None
    # site inlet == reference conditions here, so correction is a no-op
    assert result.standard_air_correction.corrected_fad_m3_per_min == Decimal("10.0")

    assert result.annual_energy_cost is not None
    assert result.annual_energy_cost.annual_energy_kwh == Decimal("480000")
    assert result.annual_energy_cost.annual_energy_cost == Decimal("2400000")

    assert result.performance.specific_power_kw_per_m3_min == Decimal("6.000")
    assert result.operating_point == inputs.operating_point
