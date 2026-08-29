from dataclasses import dataclass
from decimal import Decimal

from app.domain.rotary_screw.annual_energy_cost import calculate_annual_energy_cost
from app.domain.rotary_screw.displacement import calculate_theoretical_displacement
from app.domain.rotary_screw.models import (
    RotaryScrewOperatingPoint,
    RotaryScrewRotorGeometry,
    RotaryScrewSizingResult,
)
from app.domain.rotary_screw.performance_verification import (
    verify_manufacturer_performance,
)
from app.domain.rotary_screw.standard_air_correction import (
    correct_fad_to_standard_air,
)


@dataclass(frozen=True, slots=True)
class RotaryScrewEngineInput:
    """Input for an integrated rotary screw compressor evaluation."""

    operating_point: RotaryScrewOperatingPoint
    rated_fad_m3_per_min: Decimal
    package_input_power_kw: Decimal
    rotor_geometry: RotaryScrewRotorGeometry | None = None
    standard_reference_pressure_bar_a: Decimal | None = None
    standard_reference_temperature_k: Decimal | None = None
    annual_operating_hours: Decimal | None = None
    electricity_tariff_per_kwh: Decimal | None = None


def calculate_rotary_screw_case(
    inputs: RotaryScrewEngineInput,
) -> RotaryScrewSizingResult:
    """Run an integrated rotary screw compressor evaluation.

    Performance verification (from manufacturer-supplied, CAGI-tested data)
    is always calculated. Theoretical displacement is calculated only when
    rotor geometry is supplied. The ISO 1217 standard-air correction is
    calculated only when reference conditions are supplied.
    """

    performance = verify_manufacturer_performance(
        rated_fad_m3_per_min=inputs.rated_fad_m3_per_min,
        package_input_power_kw=inputs.package_input_power_kw,
    )

    displacement = None
    if inputs.rotor_geometry is not None:
        displacement = calculate_theoretical_displacement(
            geometry=inputs.rotor_geometry,
            rotational_speed_rpm=inputs.operating_point.rotational_speed_rpm,
        )

    standard_air_correction = None
    if (
        inputs.standard_reference_pressure_bar_a is not None
        and inputs.standard_reference_temperature_k is not None
    ):
        standard_air_correction = correct_fad_to_standard_air(
            rated_fad_m3_per_min=inputs.rated_fad_m3_per_min,
            reference_pressure_bar_a=inputs.standard_reference_pressure_bar_a,
            reference_temperature_k=inputs.standard_reference_temperature_k,
            site_inlet_pressure_bar_a=inputs.operating_point.inlet_pressure_bar_a,
            site_inlet_temperature_k=inputs.operating_point.inlet_temperature_k,
        )

    annual_energy_cost = None
    if (
        inputs.annual_operating_hours is not None
        and inputs.electricity_tariff_per_kwh is not None
    ):
        annual_energy_cost = calculate_annual_energy_cost(
            package_input_power_kw=inputs.package_input_power_kw,
            annual_operating_hours=inputs.annual_operating_hours,
            electricity_tariff_per_kwh=inputs.electricity_tariff_per_kwh,
        )

    return RotaryScrewSizingResult(
        operating_point=inputs.operating_point,
        displacement=displacement,
        standard_air_correction=standard_air_correction,
        performance=performance,
        annual_energy_cost=annual_energy_cost,
    )
