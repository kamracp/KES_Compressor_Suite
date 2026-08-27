import math
from pydantic import BaseModel, Field
from typing import List

class ReceiverPipingInput(BaseModel):
    system_flow_m3min: float = Field(..., gt=0, description="System compressed air flow (m³/min)")
    operating_pressure_bar: float = Field(7.0, gt=0, description="Operating pressure (bar g)")
    allowable_pressure_drop_bar: float = Field(0.2, gt=0, description="Allowable pressure drop across piping (bar)")
    pipe_length_meters: float = Field(100.0, gt=0, description="Total pipe route length (meters)")
    compressor_control_mode: str = Field("vsd", description="'vsd' or 'load_unload'")
    max_allowable_pressure_band_bar: float = Field(0.5, gt=0.05, description="Pressure fluctuation band (bar)")

class ReceiverPipingOutput(BaseModel):
    recommended_receiver_volume_m3: float
    recommended_receiver_liters: float
    recommended_pipe_inner_dia_mm: float
    selected_standard_pipe_size_inches: str
    calculated_air_velocity_m_s: float
    calculated_pressure_drop_bar: float
    is_velocity_acceptable: bool

class ReceiverPipingEngine:
    @staticmethod
    def calculate(inputs: ReceiverPipingInput) -> ReceiverPipingOutput:
        flow_m3min = inputs.system_flow_m3min
        p_operating = inputs.operating_pressure_bar
        p_abs = p_operating + 1.013

        # 1. Receiver Sizing (ISO / Engineering Standard rules of thumb)
        # Load/Unload requires larger volume to prevent rapid cycling; VSD needs less buffer.
        factor = 0.35 if inputs.compressor_control_mode.lower() == "load_unload" else 0.15
        rec_vol_m3 = (flow_m3min * factor * 1.013) / max(inputs.max_allowable_pressure_band_bar, 0.1)
        rec_vol_liters = rec_vol_m3 * 1000.0

        # 2. Piping Sizing for Header Velocity Target ~ 6 m/s
        target_velocity = 6.0  # m/s
        actual_vol_flow_m3s = (flow_m3min / 60.0) * (1.013 / p_abs)
        req_area_m2 = actual_vol_flow_m3s / target_velocity
        req_dia_mm = math.sqrt((4.0 * req_area_m2) / math.pi) * 1000.0

        # Standard Pipe NB mapping (approx inner dia in mm)
        pipe_standards = [
            (15, "1/2\""), (20, "3/4\""), (25, "1\""), (32, "1-1/4\""),
            (40, "1-1/2\""), (50, "2\""), (65, "2-1/2\""), (80, "3\""),
            (100, "4\""), (125, "5\""), (150, "6\""), (200, "8\""), (250, "10\"")
        ]

        selected_inch = "12\"+"
        selected_dia = req_dia_mm
        for dia_mm, name in pipe_standards:
            if dia_mm >= req_dia_mm:
                selected_dia = float(dia_mm)
                selected_inch = name
                break

        # 3. Calculate actual velocity & pressure drop with chosen diameter
        actual_area = math.pi * ((selected_dia / 1000.0) ** 2) / 4.0
        actual_velocity = actual_vol_flow_m3s / actual_area

        # Approximate Empirical Pressure Drop equation (Empirical Friction factor based)
        # delta_P (bar) = 1.6e-3 * L * (Q_fad^1.85) / (P_abs * D_mm^5)
        dp_bar = (1.6e-3 * inputs.pipe_length_meters * (flow_m3min ** 1.85)) / (p_abs * (selected_dia ** 5.0))

        return ReceiverPipingOutput(
            recommended_receiver_volume_m3=round(rec_vol_m3, 2),
            recommended_receiver_liters=round(rec_vol_liters, 0),
            recommended_pipe_inner_dia_mm=round(selected_dia, 1),
            selected_standard_pipe_size_inches=selected_inch,
            calculated_air_velocity_m_s=round(actual_velocity, 2),
            calculated_pressure_drop_bar=round(dp_bar, 3),
            is_velocity_acceptable=actual_velocity <= 10.0
        )

receiver_piping_engine = ReceiverPipingEngine()
