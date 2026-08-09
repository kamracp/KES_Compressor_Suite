from decimal import Decimal

from app.domain.compression.engine import (
    CompressionEngineInput,
    calculate_compression_case,
)
from app.domain.compression.validation import ValidationStatus


def build_engine_input(
    selected_driver_power_kw: Decimal = Decimal("25000"),
) -> CompressionEngineInput:
    return CompressionEngineInput(
        suction_pressure_bar=Decimal("30"),
        discharge_pressure_bar=Decimal("90"),
        number_of_stages=3,
        inlet_temperature_k=Decimal("308.15"),
        isentropic_exponent=Decimal("1.27"),
        isentropic_efficiency=Decimal("0.78"),
        mechanical_efficiency=Decimal("0.95"),
        mass_flow_kg_per_s=Decimal("93.376"),
        specific_heat_cp_kj_per_kg_k=Decimal("2.35"),
        intercooler_outlet_temperature_k=Decimal("313.15"),
        cooling_water_inlet_temperature_k=Decimal("303.15"),
        cooling_water_outlet_temperature_k=Decimal("313.15"),
        selected_driver_power_kw=selected_driver_power_kw,
        driver_service_factor=Decimal("0.10"),
        motor_efficiency=Decimal("0.96"),
    )


def test_complete_compression_case() -> None:
    result = calculate_compression_case(build_engine_input())

    assert result.staging.overall_compression_ratio == Decimal("3")
    assert Decimal("1.44") < result.staging.stage_compression_ratio < Decimal("1.45")

    assert result.temperature.actual_discharge_temperature_k > Decimal("330")
    assert result.temperature.actual_discharge_temperature_k < Decimal("350")

    assert result.power.isentropic_power_kw > Decimal("16000")
    assert result.power.shaft_power_kw > result.power.isentropic_power_kw

    assert result.cooling.cooling_duty_kw > Decimal("0")

    assert result.driver.required_driver_power_kw > Decimal("0")
    assert result.driver.driver_is_adequate is True

    assert result.overall_status == ValidationStatus.PASS


def test_undersized_driver_causes_fail_status() -> None:
    result = calculate_compression_case(
        build_engine_input(
            selected_driver_power_kw=Decimal("15000"),
        )
    )

    assert result.driver.driver_is_adequate is False
    assert result.overall_status == ValidationStatus.FAIL


def test_validation_checks_are_returned() -> None:
    result = calculate_compression_case(build_engine_input())

    codes = {check.code for check in result.validation_checks}

    assert "STAGE_RATIO_OK" in codes
    assert "DISCHARGE_TEMP_OK" in codes
    assert "DRIVER_OK" in codes
