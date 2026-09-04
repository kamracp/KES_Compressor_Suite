import type { SupplyPhase } from "./referenceTypes";

// Shared presentation helpers for the IS 12360 supply-basis selects
// (Leakage, Brownfield, Greenfield). The pairing rule mirrors the backend
// validate_supply_basis: 240 V is single-phase, every higher voltage three-phase.
export const SELECT_CLASS =
  "h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 disabled:opacity-50";

export function voltagesForPhase(
  voltages: readonly number[],
  phase: SupplyPhase,
): number[] {
  return voltages.filter((v) => (phase === "single" ? v === 240 : v !== 240));
}

export function defaultVoltageForPhase(phase: SupplyPhase): number {
  return phase === "single" ? 240 : 415;
}

export function phaseLabel(phase: SupplyPhase): string {
  return phase === "single" ? "Single-phase" : "Three-phase";
}

export function voltageLabel(voltage: number): string {
  return voltage >= 1000 ? `${voltage / 1000} kV` : `${voltage} V`;
}
