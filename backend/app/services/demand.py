from pydantic import BaseModel, Field
from typing import List, Optional

class ConsumerItem(BaseModel):
    name: str = Field(..., description="Consumer or Machine name")
    quantity: int = Field(1, ge=1, description="Number of identical machines")
    rated_flow_m3min: float = Field(..., gt=0, description="Rated air demand per unit (m³/min)")
    operating_pressure_bar: float = Field(..., gt=0, description="Required operating pressure (bar g)")
    duty_cycle_pct: float = Field(100.0, ge=1.0, le=100.0, description="Percentage of time operating")
    load_factor_pct: float = Field(100.0, ge=1.0, le=100.0, description="Average load factor when running")

class DemandCalculationInput(BaseModel):
    consumers: List[ConsumerItem]
    diversity_factor: float = Field(0.85, ge=0.1, le=1.0, description="Coincidence/Diversity factor")
    leakage_allowance_pct: float = Field(10.0, ge=0.0, le=50.0, description="Estimated system leakage allowance %")
    future_expansion_margin_pct: float = Field(15.0, ge=0.0, le=100.0, description="Safety/Expansion margin %")

class DemandCalculationOutput(BaseModel):
    connected_demand_m3min: float
    average_operating_demand_m3min: float
    coincident_peak_demand_m3min: float
    leakage_demand_m3min: float
    design_demand_m3min: float
    max_required_pressure_bar: float
    recommended_header_size_mm: float

class DemandEngine:
    @staticmethod
    def calculate(inputs: DemandCalculationInput) -> DemandCalculationOutput:
        if not inputs.consumers:
            return DemandCalculationOutput(
                connected_demand_m3min=0.0,
                average_operating_demand_m3min=0.0,
                coincident_peak_demand_m3min=0.0,
                leakage_demand_m3min=0.0,
                design_demand_m3min=0.0,
                max_required_pressure_bar=0.0,
                recommended_header_size_mm=0.0
            )

        connected = sum(c.quantity * c.rated_flow_m3min for c in inputs.consumers)
        
        avg_demand = sum(
            c.quantity * c.rated_flow_m3min * (c.duty_cycle_pct / 100.0) * (c.load_factor_pct / 100.0)
            for c in inputs.consumers
        )

        coincident_peak = connected * inputs.diversity_factor
        leakage = avg_demand * (inputs.leakage_allowance_pct / 100.0)
        
        total_base = coincident_peak + leakage
        design_demand = total_base * (1.0 + inputs.future_expansion_margin_pct / 100.0)
        
        max_pressure = max(c.operating_pressure_bar for c in inputs.consumers)

        # Basic Pipe Diameter Estimate for Design Demand at 6 m/s velocity & max_pressure
        p_abs = max_pressure + 1.013
        flow_m3sec = (design_demand / 60.0) / p_abs
        area_m2 = flow_m3sec / 6.0
        header_dia_mm = ((4.0 * area_m2 / 3.14159) ** 0.5) * 1000.0

        return DemandCalculationOutput(
            connected_demand_m3min=round(connected, 2),
            average_operating_demand_m3min=round(avg_demand, 2),
            coincident_peak_demand_m3min=round(coincident_peak, 2),
            leakage_demand_m3min=round(leakage, 2),
            design_demand_m3min=round(design_demand, 2),
            max_required_pressure_bar=round(max_pressure, 2),
            recommended_header_size_mm=round(max(header_dia_mm, 25.0), 1)
        )

demand_engine = DemandEngine()
