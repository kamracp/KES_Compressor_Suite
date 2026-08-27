from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.services.rotary_screw import RotaryScrewInput, rotary_screw_engine

class TechSelectionInput(BaseModel):
    required_flow_m3min: float = Field(..., gt=0, description="Required Free Air Delivery (m³/min)")
    discharge_pressure_bar: float = Field(..., gt=0, description="Discharge Pressure (bar g)")
    oil_free_required: bool = Field(False, description="Is ISO 8573-1 Class 0 oil-free air required?")
    operating_hours_per_year: float = Field(8000.0, gt=0, le=8760, description="Annual operating hours")
    electricity_cost_per_kwh: float = Field(0.12, gt=0, description="Electricity cost per kWh ($/kWh)")
    is_variable_demand: bool = Field(False, description="Is air demand fluctuating?")

class TechComparisonResult(BaseModel):
    technology_name: str
    suitable: bool
    suitability_score: float  # 0 to 100
    estimated_power_kw: float
    annual_energy_cost: float
    capex_estimate_usd: float
    maintenance_score_pct: float
    iso_class_achieved: str
    notes: List[str]

class TechnologySelectionEngine:
    @staticmethod
    def evaluate(inputs: TechSelectionInput) -> List[TechComparisonResult]:
        results = []
        flow = inputs.required_flow_m3min
        press = inputs.discharge_pressure_bar
        hours = inputs.operating_hours_per_year
        rate = inputs.electricity_cost_per_kwh

        # 1. Rotary Screw Evaluation
        stages = 2 if press > 8.5 or flow > 20 else 1
        screw_input = RotaryScrewInput(
            is_oil_injected=not inputs.oil_free_required,
            stages=stages,
            is_vsd=inputs.is_variable_demand,
            rated_fad_m3min=flow,
            discharge_pressure_bar=press,
            load_percentage=100.0
        )
        screw_out = rotary_screw_engine.calculate(screw_input)
        screw_energy_cost = screw_out.shaft_power_kw * hours * rate
        screw_capex = flow * (1200.0 if inputs.oil_free_required else 700.0)

        screw_score = 90.0
        screw_notes = ["High reliability for continuous demand"]
        if inputs.is_variable_demand:
            screw_notes.append("VSD configuration recommended for energy savings during turn-down")
            screw_score += 5.0

        results.append(TechComparisonResult(
            technology_name="Rotary Screw",
            suitable=True,
            suitability_score=min(screw_score, 100.0),
            estimated_power_kw=screw_out.shaft_power_kw,
            annual_energy_cost=round(screw_energy_cost, 2),
            capex_estimate_usd=round(screw_capex, 2),
            maintenance_score_pct=85.0 if not inputs.oil_free_required else 75.0,
            iso_class_achieved="Class 0" if inputs.oil_free_required else "Class 2 (Oil Injected)",
            notes=screw_notes
        ))

        # 2. Reciprocating Evaluation
        recip_suitable = flow <= 15.0
        recip_power = flow * (6.8 if press <= 7 else 7.8)
        recip_score = 80.0 if flow <= 5 else (60.0 if flow <= 15 else 30.0)
        results.append(TechComparisonResult(
            technology_name="Reciprocating Piston",
            suitable=recip_suitable,
            suitability_score=recip_score,
            estimated_power_kw=round(recip_power, 2),
            annual_energy_cost=round(recip_power * hours * rate, 2),
            capex_estimate_usd=round(flow * 450.0, 2),
            maintenance_score_pct=65.0,
            iso_class_achieved="Class 2 to Class 4",
            notes=["Ideal for low flow or intermittent duty cycles", "Higher vibration and maintenance requirements"]
        ))

        # 3. Centrifugal Evaluation
        centrim_suitable = flow >= 30.0
        centrim_power = flow * 5.5
        centrim_score = 95.0 if flow >= 50 else (75.0 if flow >= 30 else 20.0)
        results.append(TechComparisonResult(
            technology_name="Centrifugal Dynamic",
            suitable=centrim_suitable,
            suitability_score=centrim_score,
            estimated_power_kw=round(centrim_power, 2),
            annual_energy_cost=round(centrim_power * hours * rate, 2),
            capex_estimate_usd=round(flow * 1400.0, 2),
            maintenance_score_pct=90.0,
            iso_class_achieved="Class 0 (100% Oil Free)",
            notes=["Best performance for base-load high volume applications", "Requires stable base load to avoid surge conditions"]
        ))

        return results

technology_selection_engine = TechnologySelectionEngine()
