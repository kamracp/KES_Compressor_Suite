from dataclasses import dataclass
from decimal import Decimal

from app.domain.compression.cooling import CoolingResult, calculate_cooling_duty
from app.domain.compression.driver import DriverSizingResult, size_driver
from app.domain.compression.power import (
    CompressionPowerResult,
    calculate_compression_power,
)
from app.domain.compression.staging import StagingResult, calculate_equal_staging
from app.domain.compression.temperature import (
    CompressionTemperatureResult,
    calculate_discharge_temperature,
)
from app.domain.compression.validation import (
    ValidationCheck,
    ValidationStatus,
    check_discharge_temperature,
    check_driver_adequacy,
    check_stage_compression_ratio,
    summarize_validation_checks,
)


@dataclass(frozen=True, slots=True)
class CompressionEngineInput:
    """Input data for a complete compressor thermodynamic calculation."""

    suction_pressure_bar: Decimal
    discharge_pressure_bar: Decimal
    number_of_stages: int

    inlet_temperature_k: Decimal
    isentropic_exponent: Decimal
    isentropic_efficiency: Decimal
    mechanical_efficiency: Decimal

    mass_flow_kg_per_s: Decimal
    specific_heat_cp_kj_per_kg_k: Decimal

    intercooler_outlet_temperature_k: Decimal

    cooling_water_inlet_temperature_k: Decimal
    cooling_water_outlet_temperature_k: Decimal

    selected_driver_power_kw: Decimal
    driver_service_factor: Decimal
    motor_efficiency: Decimal | None = None


@dataclass(frozen=True, slots=True)
class CompressionEngineResult:
    """Complete compressor thermodynamic calculation result."""

    staging: StagingResult
    temperature: CompressionTemperatureResult
    power: CompressionPowerResult
    cooling: CoolingResult
    driver: DriverSizingResult
    validation_checks: tuple[ValidationCheck, ...]
    overall_status: ValidationStatus


def calculate_compression_case(
    inputs: CompressionEngineInput,
) -> CompressionEngineResult:
    """Run a complete compressor thermodynamic calculation case."""

    staging = calculate_equal_staging(
        suction_pressure_bar=inputs.suction_pressure_bar,
        discharge_pressure_bar=inputs.discharge_pressure_bar,
        number_of_stages=inputs.number_of_stages,
    )

    temperature = calculate_discharge_temperature(
        inlet_temperature_k=inputs.inlet_temperature_k,
        stage_compression_ratio=staging.stage_compression_ratio,
        isentropic_exponent=inputs.isentropic_exponent,
        isentropic_efficiency=inputs.isentropic_efficiency,
    )

    power = calculate_compression_power(
        mass_flow_kg_per_s=inputs.mass_flow_kg_per_s,
        inlet_temperature_k=inputs.inlet_temperature_k,
        stage_compression_ratio=staging.stage_compression_ratio,
        isentropic_exponent=inputs.isentropic_exponent,
        specific_heat_cp_kj_per_kg_k=inputs.specific_heat_cp_kj_per_kg_k,
        number_of_stages=inputs.number_of_stages,
        isentropic_efficiency=inputs.isentropic_efficiency,
        mechanical_efficiency=inputs.mechanical_efficiency,
        driver_margin_fraction=Decimal("0"),
    )

    cooling = calculate_cooling_duty(
        gas_mass_flow_kg_per_s=inputs.mass_flow_kg_per_s,
        gas_specific_heat_kj_per_kg_k=inputs.specific_heat_cp_kj_per_kg_k,
        gas_inlet_temperature_k=temperature.actual_discharge_temperature_k,
        gas_outlet_temperature_k=inputs.intercooler_outlet_temperature_k,
        cooling_water_inlet_temperature_k=inputs.cooling_water_inlet_temperature_k,
        cooling_water_outlet_temperature_k=inputs.cooling_water_outlet_temperature_k,
    )

    driver = size_driver(
        shaft_power_kw=power.shaft_power_kw,
        selected_driver_power_kw=inputs.selected_driver_power_kw,
        service_factor=inputs.driver_service_factor,
        motor_efficiency=inputs.motor_efficiency,
    )

    validation_checks = (
        check_stage_compression_ratio(staging.stage_compression_ratio),
        check_discharge_temperature(temperature.actual_discharge_temperature_k),
        check_driver_adequacy(driver.driver_is_adequate),
    )

    overall_status = summarize_validation_checks(validation_checks)

    return CompressionEngineResult(
        staging=staging,
        temperature=temperature,
        power=power,
        cooling=cooling,
        driver=driver,
        validation_checks=validation_checks,
        overall_status=overall_status,
    )
