import math
from pydantic import BaseModel, Field

class RotaryScrewInput(BaseModel):
    is_oil_injected: bool = Field(True, description="True for Oil-Injected, False for Oil-Free")
    stages: int = Field(1, ge=1, le=2, description="1 or 2 stage compression")
    is_vsd: bool = Field(False, description="Fixed Speed vs Variable Speed Drive")
    rated_fad_m3min: float = Field(..., gt=0, description="Rated Free Air Delivery (m³/min)")
    discharge_pressure_bar: float = Field(..., gt=0, description="Discharge Pressure (bar g)")
    ambient_pressure_bar: float = Field(1.013, gt=0, description="Ambient Pressure (bar a)")
    load_percentage: float = Field(100.0, ge=10, le=100, description="Current operating load %")

class RotaryScrewOutput(BaseModel):
    actual_fad_m3min: float
    shaft_power_kw: float
    specific_power_kw_m3min: float
    volumetric_efficiency_pct: float
    isothermal_efficiency_pct: float
    discharge_temp_celsius: float

class RotaryScrewEngine:
    @staticmethod
    def calculate(inputs: RotaryScrewInput) -> RotaryScrewOutput:
        p1 = inputs.ambient_pressure_bar
        p2 = inputs.discharge_pressure_bar + p1
        pressure_ratio = p2 / p1
        
        leakage_factor = 0.03 if inputs.is_oil_injected else 0.06
        vol_eff = max(70.0, 95.0 - (pressure_ratio / inputs.stages) * leakage_factor * 10)
        
        load_frac = inputs.load_percentage / 100.0
        if inputs.is_vsd:
            actual_fad = inputs.rated_fad_m3min * load_frac * (vol_eff / 100.0)
            power_factor = 0.15 + 0.85 * load_frac
        else:
            actual_fad = inputs.rated_fad_m3min * load_frac * (vol_eff / 100.0)
            power_factor = 0.70 + 0.30 * load_frac if load_frac < 1.0 else 1.0
            
        base_sec = (5.5 if inputs.stages == 2 else 6.2) * (1.0 if inputs.is_oil_injected else 1.12)
        sec = base_sec * (p2 / 7.0) ** 0.35
        shaft_power = actual_fad * sec * power_factor
        
        k = 1.39 if not inputs.is_oil_injected else 1.25
        t1_k = 293.15
        t2_k = t1_k * ((p2 / p1) ** ((k - 1) / (k * inputs.stages)))
        discharge_temp = (t2_k - 273.15) if inputs.is_oil_injected else min(t2_k - 273.15, 200.0)
        
        p_iso = p1 * 100 * (actual_fad / 60) * math.log(p2 / p1)
        iso_eff = (p_iso / shaft_power) * 100 if shaft_power > 0 else 0.0

        return RotaryScrewOutput(
            actual_fad_m3min=round(actual_fad, 2),
            shaft_power_kw=round(shaft_power, 2),
            specific_power_kw_m3min=round(shaft_power / actual_fad, 3) if actual_fad > 0 else 0.0,
            volumetric_efficiency_pct=round(vol_eff, 1),
            isothermal_efficiency_pct=round(iso_eff, 1),
            discharge_temp_celsius=round(discharge_temp, 1)
        )

rotary_screw_engine = RotaryScrewEngine()
