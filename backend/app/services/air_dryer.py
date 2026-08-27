from pydantic import BaseModel, Field
from typing import List

class AirDryerInput(BaseModel):
    inlet_flow_m3min: float = Field(..., gt=0, description="Inlet compressed air flow (m³/min)")
    inlet_pressure_bar: float = Field(7.0, gt=0, description="Inlet operating pressure (bar g)")
    inlet_temp_celsius: float = Field(35.0, gt=0, description="Inlet air temperature (°C)")
    ambient_temp_celsius: float = Field(35.0, gt=0, description="Ambient air/cooling temp (°C)")
    required_pdp_celsius: float = Field(3.0, description="Required Pressure Dew Point (°C)")
    dryer_type: str = Field("refrigerated", description="'refrigerated' or 'desiccant'")

class AirDryerOutput(BaseModel):
    selected_dryer_type: str
    rated_dryer_capacity_m3min: float
    correction_factor: float
    pressure_drop_bar: float
    purge_loss_m3min: float
    net_outlet_flow_m3min: float
    iso_class_achieved: str
    recommended_filters: List[str]

class AirDryerEngine:
    @staticmethod
    def calculate(inputs: AirDryerInput) -> AirDryerOutput:
        # 1. Correction Factor Logic based on operating conditions
        f_press = (inputs.inlet_pressure_bar / 7.0) ** 0.3
        f_inlet_temp = max(0.5, 1.0 - (inputs.inlet_temp_celsius - 35.0) * 0.015)
        f_amb_temp = max(0.6, 1.0 - (inputs.ambient_temp_celsius - 35.0) * 0.01)
        
        total_cf = round(f_press * f_inlet_temp * f_amb_temp, 3)

        # 2. Minimum rated dryer capacity required
        rated_capacity_req = inputs.inlet_flow_m3min / max(total_cf, 0.3)

        # 3. Type Selection & Purge Loss Calculation
        if inputs.required_pdp_celsius < 0.0 or inputs.dryer_type.lower() == "desiccant":
            selected_type = "Desiccant (Adsorption) Dryer"
            purge_loss_pct = 0.15  # 15% standard heatless desiccant purge
            p_drop = 0.25
            iso_class = "ISO 8573-1 Class 1 to 2 (-40°C to -70°C PDP)"
            filters = [
                "Water Separator / Coarse Pre-Filter (5 micron)",
                "High-Efficiency Coalescing Oil Removal Pre-Filter (0.01 micron)",
                "Dust / Particulate After-Filter (1 micron)"
            ]
        else:
            selected_type = "Refrigerated Dryer"
            purge_loss_pct = 0.0  # Zero purge loss for refrigerated
            p_drop = 0.15
            iso_class = "ISO 8573-1 Class 4 (+3°C PDP)"
            filters = [
                "General Purpose Coalescing Pre-Filter (1 micron)",
                "High-Efficiency Oil Removal Filter (0.01 micron)"
            ]

        purge_loss = inputs.inlet_flow_m3min * purge_loss_pct
        net_outlet = inputs.inlet_flow_m3min - purge_loss

        return AirDryerOutput(
            selected_dryer_type=selected_type,
            rated_dryer_capacity_m3min=round(rated_capacity_req, 2),
            correction_factor=total_cf,
            pressure_drop_bar=p_drop,
            purge_loss_m3min=round(purge_loss, 2),
            net_outlet_flow_m3min=round(net_outlet, 2),
            iso_class_achieved=iso_class,
            recommended_filters=filters
        )

air_dryer_engine = AirDryerEngine()
