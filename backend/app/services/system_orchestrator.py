from pydantic import BaseModel, Field
from typing import List, Optional

from app.services.demand import DemandCalculationInput, DemandCalculationOutput, demand_engine
from app.services.rotary_screw import RotaryScrewInput, RotaryScrewOutput, rotary_screw_engine
from app.services.air_dryer import AirDryerInput, AirDryerOutput, air_dryer_engine
from app.services.receiver_piping import ReceiverPipingInput, ReceiverPipingOutput, receiver_piping_engine

class SystemDesignInput(BaseModel):
    project_name: str = Field("New Plant Expansion", description="Project Name")
    demand_params: DemandCalculationInput
    oil_free_required: bool = Field(False, description="ISO 8573-1 Class 0 requirement")
    operating_hours_per_year: float = Field(8000.0, gt=0, le=8760)
    electricity_cost_per_kwh: float = Field(0.12, gt=0)
    pipe_route_length_m: float = Field(150.0, gt=0)

class SystemDesignOutput(BaseModel):
    project_name: str
    demand_summary: DemandCalculationOutput
    primary_compressor_specs: RotaryScrewOutput
    air_dryer_specs: AirDryerOutput
    receiver_and_piping_specs: ReceiverPipingOutput
    total_system_power_kw: float
    annual_operating_cost_usd: float
    overall_specific_power_kw_m3min: float
    system_recommendations: List[str]

class SystemOrchestratorEngine:
    @staticmethod
    def calculate_full_system(inputs: SystemDesignInput) -> SystemDesignOutput:
        # 1. Calculate Plant Demand
        demand_out = demand_engine.calculate(inputs.demand_params)
        design_flow = demand_out.design_demand_m3min
        design_press = demand_out.max_required_pressure_bar

        # 2. Size Rotary Screw Compressors
        screw_input = RotaryScrewInput(
            is_oil_injected=not inputs.oil_free_required,
            stages=2 if design_press > 8.5 or design_flow > 20 else 1,
            is_vsd=True,
            rated_fad_m3min=design_flow,
            discharge_pressure_bar=design_press,
            load_percentage=100.0
        )
        screw_out = rotary_screw_engine.calculate(screw_input)

        # 3. Size Air Dryer & Treatment
        dryer_input = AirDryerInput(
            inlet_flow_m3min=design_flow,
            inlet_pressure_bar=design_press,
            inlet_temp_celsius=38.0,
            ambient_temp_celsius=35.0,
            required_pdp_celsius=-40.0 if inputs.oil_free_required else 3.0,
            dryer_type="desiccant" if inputs.oil_free_required else "refrigerated"
        )
        dryer_out = air_dryer_engine.calculate(dryer_input)

        # 4. Size Receiver Tank & Piping Header
        piping_input = ReceiverPipingInput(
            system_flow_m3min=design_flow,
            operating_pressure_bar=design_press,
            allowable_pressure_drop_bar=0.2,
            pipe_length_meters=inputs.pipe_route_length_m,
            compressor_control_mode="vsd",
            max_allowable_pressure_band_bar=0.3
        )
        piping_out = receiver_piping_engine.calculate(piping_input)

        # 5. Overall Performance & System Cost Metrics
        total_power = screw_out.shaft_power_kw + (5.0 if inputs.oil_free_required else 2.5)
        annual_cost = total_power * inputs.operating_hours_per_year * inputs.electricity_cost_per_kwh
        overall_sec = total_power / max(demand_out.average_operating_demand_m3min, 0.1)

        recommendations = [
            f"Recommended primary compressor shaft power: {screw_out.shaft_power_kw} kW",
            f"Install air receiver tank volume of at least {piping_out.recommended_receiver_liters} Liters",
            f"Use main distribution header size: {piping_out.selected_standard_pipe_size_inches} NB"
        ]
        if inputs.oil_free_required:
            recommendations.append("High purity Class 0 air active: Ensure zero-bypass desiccant filtration manifold.")

        return SystemDesignOutput(
            project_name=inputs.project_name,
            demand_summary=demand_out,
            primary_compressor_specs=screw_out,
            air_dryer_specs=dryer_out,
            receiver_and_piping_specs=piping_out,
            total_system_power_kw=round(total_power, 2),
            annual_operating_cost_usd=round(annual_cost, 2),
            overall_specific_power_kw_m3min=round(overall_sec, 3),
            system_recommendations=recommendations
        )

system_orchestrator_engine = SystemOrchestratorEngine()
