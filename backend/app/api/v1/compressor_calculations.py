from dataclasses import asdict
from decimal import Decimal
from typing import Any

from fastapi import APIRouter

from app.domain.centrifugal.centrifugal_models import (
    CentrifugalDriverType,
    CentrifugalOperatingPoint,
)
from app.domain.centrifugal.engine import (
    CentrifugalEngineInput,
    calculate_centrifugal_case,
)
from app.domain.compression.engine import (
    CompressionEngineInput,
    calculate_compression_case,
)
from app.domain.reciprocating.engine import (
    ReciprocatingEngineInput,
    calculate_reciprocating_case,
)
from app.domain.reciprocating.recip_models import (
    CylinderAction,
    ReciprocatingCylinderGeometry,
)
from app.domain.selection.selection_engine import select_compressor_type
from app.domain.selection.selection_models import CompressorSelectionCriteria
from app.schemas.compressor_calculation import (
    CentrifugalCalculationRequest,
    CompressionCalculationRequest,
    CompressorSelectionRequest,
    ReciprocatingCalculationRequest,
)

router = APIRouter(
    prefix="/compressor",
    tags=["Compressor Engineering"],
)


@router.post("/compression/calculate")
def calculate_compression(
    payload: CompressionCalculationRequest,
) -> dict[str, Any]:
    inputs = CompressionEngineInput(
        suction_pressure_bar=payload.gas.suction_pressure_bar,
        discharge_pressure_bar=payload.gas.discharge_pressure_bar,
        number_of_stages=payload.number_of_stages,
        inlet_temperature_k=payload.gas.suction_temperature_k,
        isentropic_exponent=payload.gas.isentropic_exponent,
        isentropic_efficiency=payload.isentropic_efficiency,
        mechanical_efficiency=payload.mechanical_efficiency,
        mass_flow_kg_per_s=payload.gas.mass_flow_kg_per_s,
        specific_heat_cp_kj_per_kg_k=payload.specific_heat_cp_kj_per_kg_k,
        intercooler_outlet_temperature_k=payload.intercooler_outlet_temperature_k,
        cooling_water_inlet_temperature_k=payload.cooling_water_inlet_temperature_k,
        cooling_water_outlet_temperature_k=payload.cooling_water_outlet_temperature_k,
        selected_driver_power_kw=payload.selected_driver_power_kw,
        driver_service_factor=payload.driver_service_factor,
        motor_efficiency=payload.motor_efficiency,
    )

    result = calculate_compression_case(inputs)

    return asdict(result)


@router.post("/reciprocating/calculate")
def calculate_reciprocating(
    payload: ReciprocatingCalculationRequest,
) -> dict[str, Any]:
    geometry = ReciprocatingCylinderGeometry(
        bore_mm=payload.bore_mm,
        stroke_mm=payload.stroke_mm,
        rod_diameter_mm=payload.rod_diameter_mm,
        speed_rpm=payload.speed_rpm,
        clearance_fraction=payload.clearance_fraction,
        action=CylinderAction.DOUBLE_ACTING,
    )

    inputs = ReciprocatingEngineInput(
        geometry=geometry,
        required_flow_m3_per_hr=payload.required_flow_m3_per_hr,
        stage_compression_ratio=payload.stage_compression_ratio,
        suction_z_factor=payload.suction_z_factor,
        discharge_z_factor=payload.discharge_z_factor,
        isentropic_exponent=payload.isentropic_exponent,
        suction_pressure_bar=payload.suction_pressure_bar,
        discharge_pressure_bar=payload.discharge_pressure_bar,
        allowable_rod_load_kn=payload.allowable_rod_load_kn,
    )

    result = calculate_reciprocating_case(inputs)

    return asdict(result)


@router.post("/centrifugal/calculate")
def calculate_centrifugal(
    payload: CentrifugalCalculationRequest,
) -> dict[str, Any]:
    operating_point = CentrifugalOperatingPoint(
        suction_pressure_bar=payload.gas.suction_pressure_bar,
        discharge_pressure_bar=payload.gas.discharge_pressure_bar,
        suction_temperature_k=payload.gas.suction_temperature_k,
        mass_flow_kg_per_s=payload.gas.mass_flow_kg_per_s,
        actual_flow_m3_per_s=payload.gas.actual_flow_m3_per_s,
        molecular_weight_kg_per_kmol=payload.gas.molecular_weight_kg_per_kmol,
        suction_z_factor=payload.gas.suction_z_factor,
        discharge_z_factor=payload.gas.discharge_z_factor,
        isentropic_exponent=payload.gas.isentropic_exponent,
        polytropic_efficiency=payload.polytropic_efficiency,
    )

    inputs = CentrifugalEngineInput(
        operating_point=operating_point,
        number_of_impeller_stages=payload.number_of_impeller_stages,
        head_coefficient=payload.head_coefficient,
        rotational_speed_rpm=payload.rotational_speed_rpm,
        mechanical_loss_fraction=payload.mechanical_loss_fraction,
        driver_margin_fraction=payload.driver_margin_fraction,
        selected_driver_power_kw=payload.selected_driver_power_kw,
        driver_type=CentrifugalDriverType.ELECTRIC_MOTOR,
        motor_efficiency=payload.motor_efficiency,
        surge_flow_fraction=payload.surge_flow_fraction,
        anti_surge_margin_fraction=payload.anti_surge_margin_fraction,
        stonewall_flow_fraction=payload.stonewall_flow_fraction,
    )

    result = calculate_centrifugal_case(inputs)

    return asdict(result)


@router.post("/selection")
def select_compressor(
    payload: CompressorSelectionRequest,
) -> dict[str, Any]:
    criteria = CompressorSelectionCriteria(
        required_flow_m3_per_hr=payload.required_flow_m3_per_hr,
        suction_pressure_bar=payload.suction_pressure_bar,
        discharge_pressure_bar=payload.discharge_pressure_bar,
        required_turndown_fraction=payload.required_turndown_fraction,
        continuous_operation=payload.continuous_operation,
        gas_molecular_weight=payload.gas_molecular_weight,
        estimated_operating_hours_per_year=payload.estimated_operating_hours_per_year,
    )

    result = select_compressor_type(criteria)

    return asdict(result)
