from dataclasses import asdict
from typing import Any

from sqlalchemy.orm import Session

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
from app.domain.rotary_screw.engine import (
    RotaryScrewEngineInput,
    calculate_rotary_screw_case,
)
from app.domain.rotary_screw.models import (
    RotaryScrewOperatingPoint,
    RotaryScrewRotorGeometry,
)
from app.domain.selection.selection_engine import select_compressor_type
from app.domain.selection.selection_models import CompressorSelectionCriteria
from app.models.calculation_case import CalculationType
from app.schemas.calculation_execution import CalculationExecutionMetadata
from app.schemas.compressed_air_distribution import (
    DistributionNetworkCalculationRequest,
)
from app.schemas.compressor_calculation import (
    CentrifugalCalculationRequest,
    CompressionCalculationRequest,
    CompressorSelectionRequest,
    ReciprocatingCalculationRequest,
    RotaryScrewCalculationRequest,
)
from app.services.calculation_execution import calculation_execution_service


class InvalidCalculationPersistenceMetadataError(ValueError):
    """Raised when persistence metadata is incomplete or invalid."""


class CompressorExecutionService:
    """Orchestrate compressor calculations and optional persistence."""

    def _validate_persistence_metadata(
        self,
        execution: CalculationExecutionMetadata,
    ) -> None:
        if not execution.persist_result:
            return

        if execution.project_id is None:
            raise InvalidCalculationPersistenceMetadataError(
                "Project id is required when result persistence is enabled."
            )

        if execution.calculation_code is None:
            raise InvalidCalculationPersistenceMetadataError(
                "Calculation code is required when result persistence is enabled."
            )

        if execution.title is None:
            raise InvalidCalculationPersistenceMetadataError(
                "Calculation title is required when result persistence is enabled."
            )

    def _persist_if_requested(
        self,
        db: Session,
        *,
        organization_id: int,
        execution: CalculationExecutionMetadata,
        calculation_type: CalculationType,
        input_data: dict[str, Any],
        result: Any,
    ) -> int | None:
        self._validate_persistence_metadata(execution)

        if not execution.persist_result:
            return None

        calculation_case = calculation_execution_service.persist_execution(
            db,
            organization_id=organization_id,
            project_id=execution.project_id,
            calculation_code=execution.calculation_code,
            calculation_type=calculation_type,
            title=execution.title,
            input_data=input_data,
            result=result,
            engineering_notes=execution.engineering_notes,
        )

        return calculation_case.id

    def execute_compression(
        self,
        db: Session,
        *,
        organization_id: int,
        calculation: CompressionCalculationRequest,
        execution: CalculationExecutionMetadata,
    ) -> dict[str, Any]:
        inputs = CompressionEngineInput(
            suction_pressure_bar=calculation.gas.suction_pressure_bar,
            discharge_pressure_bar=calculation.gas.discharge_pressure_bar,
            number_of_stages=calculation.number_of_stages,
            inlet_temperature_k=calculation.gas.suction_temperature_k,
            isentropic_exponent=calculation.gas.isentropic_exponent,
            isentropic_efficiency=calculation.isentropic_efficiency,
            mechanical_efficiency=calculation.mechanical_efficiency,
            mass_flow_kg_per_s=calculation.gas.mass_flow_kg_per_s,
            specific_heat_cp_kj_per_kg_k=calculation.specific_heat_cp_kj_per_kg_k,
            intercooler_outlet_temperature_k=(calculation.intercooler_outlet_temperature_k),
            cooling_water_inlet_temperature_k=(calculation.cooling_water_inlet_temperature_k),
            cooling_water_outlet_temperature_k=(calculation.cooling_water_outlet_temperature_k),
            selected_driver_power_kw=calculation.selected_driver_power_kw,
            driver_service_factor=calculation.driver_service_factor,
            motor_efficiency=calculation.motor_efficiency,
        )

        result = calculate_compression_case(inputs)

        calculation_case_id = self._persist_if_requested(
            db,
            organization_id=organization_id,
            execution=execution,
            calculation_type=CalculationType.COMPRESSION,
            input_data=calculation.model_dump(mode="json"),
            result=result,
        )

        return {
            "result": asdict(result),
            "calculation_case_id": calculation_case_id,
        }

    def execute_reciprocating(
        self,
        db: Session,
        *,
        organization_id: int,
        calculation: ReciprocatingCalculationRequest,
        execution: CalculationExecutionMetadata,
    ) -> dict[str, Any]:
        geometry = ReciprocatingCylinderGeometry(
            bore_mm=calculation.bore_mm,
            stroke_mm=calculation.stroke_mm,
            rod_diameter_mm=calculation.rod_diameter_mm,
            speed_rpm=calculation.speed_rpm,
            clearance_fraction=calculation.clearance_fraction,
            action=CylinderAction.DOUBLE_ACTING,
        )

        inputs = ReciprocatingEngineInput(
            geometry=geometry,
            required_flow_m3_per_hr=calculation.required_flow_m3_per_hr,
            stage_compression_ratio=calculation.stage_compression_ratio,
            suction_z_factor=calculation.suction_z_factor,
            discharge_z_factor=calculation.discharge_z_factor,
            isentropic_exponent=calculation.isentropic_exponent,
            suction_pressure_bar=calculation.suction_pressure_bar,
            discharge_pressure_bar=calculation.discharge_pressure_bar,
            allowable_rod_load_kn=calculation.allowable_rod_load_kn,
        )

        result = calculate_reciprocating_case(inputs)

        calculation_case_id = self._persist_if_requested(
            db,
            organization_id=organization_id,
            execution=execution,
            calculation_type=CalculationType.RECIPROCATING,
            input_data=calculation.model_dump(mode="json"),
            result=result,
        )

        return {
            "result": asdict(result),
            "calculation_case_id": calculation_case_id,
        }

    def execute_centrifugal(
        self,
        db: Session,
        *,
        organization_id: int,
        calculation: CentrifugalCalculationRequest,
        execution: CalculationExecutionMetadata,
    ) -> dict[str, Any]:
        operating_point = CentrifugalOperatingPoint(
            suction_pressure_bar=calculation.gas.suction_pressure_bar,
            discharge_pressure_bar=calculation.gas.discharge_pressure_bar,
            suction_temperature_k=calculation.gas.suction_temperature_k,
            mass_flow_kg_per_s=calculation.gas.mass_flow_kg_per_s,
            actual_flow_m3_per_s=calculation.gas.actual_flow_m3_per_s,
            molecular_weight_kg_per_kmol=(calculation.gas.molecular_weight_kg_per_kmol),
            suction_z_factor=calculation.gas.suction_z_factor,
            discharge_z_factor=calculation.gas.discharge_z_factor,
            isentropic_exponent=calculation.gas.isentropic_exponent,
            polytropic_efficiency=calculation.polytropic_efficiency,
        )

        inputs = CentrifugalEngineInput(
            operating_point=operating_point,
            number_of_impeller_stages=calculation.number_of_impeller_stages,
            head_coefficient=calculation.head_coefficient,
            rotational_speed_rpm=calculation.rotational_speed_rpm,
            mechanical_loss_fraction=calculation.mechanical_loss_fraction,
            driver_margin_fraction=calculation.driver_margin_fraction,
            selected_driver_power_kw=calculation.selected_driver_power_kw,
            driver_type=CentrifugalDriverType.ELECTRIC_MOTOR,
            motor_efficiency=calculation.motor_efficiency,
            surge_flow_fraction=calculation.surge_flow_fraction,
            anti_surge_margin_fraction=calculation.anti_surge_margin_fraction,
            stonewall_flow_fraction=calculation.stonewall_flow_fraction,
        )

        result = calculate_centrifugal_case(inputs)

        calculation_case_id = self._persist_if_requested(
            db,
            organization_id=organization_id,
            execution=execution,
            calculation_type=CalculationType.CENTRIFUGAL,
            input_data=calculation.model_dump(mode="json"),
            result=result,
        )

        return {
            "result": asdict(result),
            "calculation_case_id": calculation_case_id,
        }

    def execute_selection(
        self,
        db: Session,
        *,
        organization_id: int,
        calculation: CompressorSelectionRequest,
        execution: CalculationExecutionMetadata,
    ) -> dict[str, Any]:
        criteria = CompressorSelectionCriteria(
            required_flow_m3_per_hr=calculation.required_flow_m3_per_hr,
            suction_pressure_bar=calculation.suction_pressure_bar,
            discharge_pressure_bar=calculation.discharge_pressure_bar,
            required_turndown_fraction=calculation.required_turndown_fraction,
            continuous_operation=calculation.continuous_operation,
            gas_molecular_weight=calculation.gas_molecular_weight,
            estimated_operating_hours_per_year=(calculation.estimated_operating_hours_per_year),
            oil_free_air_required=calculation.oil_free_air_required,
        )

        result = select_compressor_type(criteria)

        calculation_case_id = self._persist_if_requested(
            db,
            organization_id=organization_id,
            execution=execution,
            calculation_type=CalculationType.SELECTION,
            input_data=calculation.model_dump(mode="json"),
            result=result,
        )

        return {
            "result": asdict(result),
            "calculation_case_id": calculation_case_id,
        }

    def execute_rotary_screw(
        self,
        db: Session,
        *,
        organization_id: int,
        calculation: RotaryScrewCalculationRequest,
        execution: CalculationExecutionMetadata,
    ) -> dict[str, Any]:
        operating_point = RotaryScrewOperatingPoint(
            inlet_pressure_bar_a=calculation.inlet_pressure_bar_a,
            inlet_temperature_k=calculation.inlet_temperature_k,
            discharge_pressure_bar_g=calculation.discharge_pressure_bar_g,
            rotational_speed_rpm=calculation.rotational_speed_rpm,
            oil_type=calculation.oil_type,
            control_type=calculation.control_type,
            stage_count=calculation.stage_count,
        )

        rotor_geometry = None
        if calculation.rotor_geometry is not None:
            rotor_geometry = RotaryScrewRotorGeometry(
                male_rotor_diameter_mm=calculation.rotor_geometry.male_rotor_diameter_mm,
                rotor_length_mm=calculation.rotor_geometry.rotor_length_mm,
                area_utilisation_coefficient=(
                    calculation.rotor_geometry.area_utilisation_coefficient
                ),
            )

        inputs = RotaryScrewEngineInput(
            operating_point=operating_point,
            rated_fad_m3_per_min=calculation.rated_fad_m3_per_min,
            package_input_power_kw=calculation.package_input_power_kw,
            rotor_geometry=rotor_geometry,
            standard_reference_pressure_bar_a=(calculation.standard_reference_pressure_bar_a),
            standard_reference_temperature_k=(calculation.standard_reference_temperature_k),
            annual_operating_hours=calculation.annual_operating_hours,
            electricity_tariff_per_kwh=calculation.electricity_tariff_per_kwh,
        )

        result = calculate_rotary_screw_case(inputs)

        calculation_case_id = self._persist_if_requested(
            db,
            organization_id=organization_id,
            execution=execution,
            calculation_type=CalculationType.ROTARY_SCREW,
            input_data=calculation.model_dump(mode="json"),
            result=result,
        )

        return {
            "result": asdict(result),
            "calculation_case_id": calculation_case_id,
        }

    def execute_distribution(
        self,
        db: Session,
        *,
        organization_id: int,
        calculation: DistributionNetworkCalculationRequest,
        execution: CalculationExecutionMetadata,
    ) -> dict[str, Any]:
        from app.services.compressed_air_distribution import (
            compressed_air_distribution_service,
        )

        result = compressed_air_distribution_service.calculate(calculation)

        calculation_case_id = self._persist_if_requested(
            db,
            organization_id=organization_id,
            execution=execution,
            calculation_type=CalculationType.DISTRIBUTION,
            input_data=calculation.model_dump(mode="json"),
            result=result,
        )

        return {
            "result": asdict(result),
            "calculation_case_id": calculation_case_id,
        }


compressor_execution_service = CompressorExecutionService()
