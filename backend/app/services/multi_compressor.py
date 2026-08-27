from pydantic import BaseModel, Field
from typing import List

class CompressorUnitInput(BaseModel):
    unit_id: str = Field(..., description="Compressor identifier (e.g. Comp-1)")
    rated_fad_m3min: float = Field(..., gt=0, description="Rated FAD capacity")
    rated_power_kw: float = Field(..., gt=0, description="Rated motor power")
    is_vsd: bool = Field(False, description="Variable Speed Drive unit")
    is_master_vsd: bool = Field(False, description="Designated as trim/master unit")

class StationInput(BaseModel):
    required_peak_fad_m3min: float = Field(..., gt=0, description="Required peak system demand")
    required_avg_fad_m3min: float = Field(..., gt=0, description="Required average demand")
    operating_pressure_bar: float = Field(7.0, gt=0, description="System header pressure")
    compressors: List[CompressorUnitInput]

class StationOutput(BaseModel):
    total_installed_capacity_m3min: float
    n_plus_1_redundant: bool
    firm_capacity_m3min: float
    total_running_power_kw: float
    station_specific_power_kw_m3min: float
    sequencer_trim_unit_id: str
    warnings: List[str]

class MultiCompressorEngine:
    @staticmethod
    def calculate(inputs: StationInput) -> StationOutput:
        if not inputs.compressors:
            return StationOutput(
                total_installed_capacity_m3min=0.0,
                n_plus_1_redundant=False,
                firm_capacity_m3min=0.0,
                total_running_power_kw=0.0,
                station_specific_power_kw_m3min=0.0,
                sequencer_trim_unit_id="None",
                warnings=["No compressor units provided in station configuration."]
            )

        total_cap = sum(c.rated_fad_m3min for c in inputs.compressors)
        max_unit_cap = max(c.rated_fad_m3min for c in inputs.compressors)
        firm_cap = total_cap - max_unit_cap
        is_redundant = firm_cap >= inputs.required_peak_fad_m3min

        trim_unit = next((c.unit_id for c in inputs.compressors if c.is_vsd or c.is_master_vsd), inputs.compressors[0].unit_id)

        total_power = sum(c.rated_power_kw for c in inputs.compressors)
        avg_demand = inputs.required_avg_fad_m3min
        station_sec = (total_power / total_cap) if total_cap > 0 else 0.0

        warnings = []
        if not is_redundant:
            warnings.append("Station lacks N+1 redundancy for peak demand. Loss of largest unit will cause pressure drop.")
        if total_cap < inputs.required_peak_fad_m3min:
            warnings.append("Total installed capacity is less than required peak demand!")

        return StationOutput(
            total_installed_capacity_m3min=round(total_cap, 2),
            n_plus_1_redundant=is_redundant,
            firm_capacity_m3min=round(firm_cap, 2),
            total_running_power_kw=round(total_power, 2),
            station_specific_power_kw_m3min=round(station_sec, 3),
            sequencer_trim_unit_id=trim_unit,
            warnings=warnings
        )

multi_compressor_engine = MultiCompressorEngine()
