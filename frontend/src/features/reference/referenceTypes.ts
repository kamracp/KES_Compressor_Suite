// Mirrors backend app/schemas/reference_options.py (InputOptionsResponse).
// Tariffs arrive as decimal strings so no float rounding is introduced.
export type SupplyPhase = "single" | "three";

export interface InputOptionsResponse {
  electricity_tariff_inr_per_kwh: string[];
  supply_phase: SupplyPhase[];
  nominal_supply_voltage_v: number[];
  supply_frequency_hz: number[];
}
