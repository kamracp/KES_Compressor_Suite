from decimal import Decimal

from app.domain.centrifugal.centrifugal_models import (
    CentrifugalDriverType,
    CentrifugalOperatingPoint,
)
from app.domain.centrifugal.engine import (
    CentrifugalEngineInput,
    calculate_centrifugal_case,
)


def build_engine_input(
    selected_driver_power_kw: Decimal = Decimal("22000"),
) -> CentrifugalEngineInput:
    operating_point = CentrifugalOperatingPoint(
        suction_pressure_bar=Decimal("30"),
        discharge_pressure_bar=Decimal("90"),
        suction_temperature_k=Decimal("308.15"),
        mass_flow_kg_per_s=Decimal("93.376"),
        actual_flow_m3_per_s=Decimal("3.9287"),
        molecular_weight_kg_per_kmol=Decimal("19.075"),
        suction_z_factor=Decimal("0.9398"),
        discharge_z_factor=Decimal("0.8700"),
        isentropic_exponent=Decimal("1.27"),
        polytropic_efficiency=Decimal("0.78"),
    )

    return CentrifugalEngineInput(
        operating_point=operating_point,
        number_of_impeller_stages=3,
        head_coefficient=Decimal("0.55"),
        rotational_speed_rpm=Decimal("8000"),
        mechanical_loss_fraction=Decimal("0.025"),
        driver_margin_fraction=Decimal("0.10"),
        selected_driver_power_kw=selected_driver_power_kw,
        driver_type=CentrifugalDriverType.ELECTRIC_MOTOR,
        motor_efficiency=Decimal("0.96"),
    )


def test_complete_centrifugal_case() -> None:
    result = calculate_centrifugal_case(build_engine_input())

    assert result.head.overall_compression_ratio == Decimal("3")
    assert result.head.average_z_factor == Decimal("0.9049")
    assert result.head.polytropic_head_kj_per_kg > Decimal("100")

    assert result.impeller.number_of_impeller_stages == 3
    assert result.impeller.impeller_tip_speed_m_per_s > Decimal("0")
    assert result.impeller.impeller_diameter_m > Decimal("0")

    assert result.power.gas_power_kw > Decimal("0")
    assert result.power.shaft_power_kw > result.power.gas_power_kw
    assert result.power.required_driver_power_kw > result.power.shaft_power_kw
    assert result.power.driver_is_adequate is True

    assert result.surge.surge_margin_fraction == Decimal("0.30")
    assert result.surge.design_point_is_within_envelope is True

    assert len(result.performance_map.points) == 3


def test_undersized_driver_is_detected() -> None:
    result = calculate_centrifugal_case(
        build_engine_input(
            selected_driver_power_kw=Decimal("15000"),
        )
    )

    assert result.power.driver_is_adequate is False
    assert result.power.driver_margin_kw < Decimal("0")


def test_performance_map_contains_expected_speed_lines() -> None:
    result = calculate_centrifugal_case(build_engine_input())

    speed_fractions = {point.speed_fraction for point in result.performance_map.points}

    assert speed_fractions == {
        Decimal("1.00"),
        Decimal("0.90"),
        Decimal("0.80"),
    }


def test_surge_and_stonewall_bound_design_flow() -> None:
    result = calculate_centrifugal_case(build_engine_input())

    design_flow = result.surge.design_flow_m3_per_hr

    assert result.surge.surge_flow_m3_per_hr < design_flow
    assert design_flow < result.surge.stonewall_flow_m3_per_hr


def test_electrical_input_is_calculated_for_electric_motor() -> None:
    result = calculate_centrifugal_case(build_engine_input())

    assert result.power.electrical_input_power_kw is not None
    assert result.power.electrical_input_power_kw > result.power.required_driver_power_kw
