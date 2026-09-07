import { describe, expect, it } from "vitest";

import {
  buildPartLoadComparisonRequest,
  createCandidate,
  createInitialPartLoadFormState,
  createLoadDurationRow,
  validatePartLoadFormState,
} from "./partLoadFormState";

function validState() {
  return {
    ...createInitialPartLoadFormState(),
    analysisCode: "PL-2026-001",
    ratedFadNm3PerHr: "1000",
    ratedPowerKw: "100",
  };
}

describe("part-load comparison form state (C-8)", () => {
  it("starts with load/unload and modulation candidates at the DOE unload fraction", () => {
    const state = createInitialPartLoadFormState();

    expect(state.candidates.map((c) => c.mode)).toEqual(["LOAD_UNLOAD", "MODULATION"]);
    expect(state.candidates[0].unloadPowerFraction).toBe("0.25");
    expect(validatePartLoadFormState(validState())).toEqual([]);
  });

  it("parses capacity fractions from free text and rejects duplicates", () => {
    const state = { ...validState(), capacityFractionsText: "0.2 0.4, 0.4" };

    expect(validatePartLoadFormState(state).join(" ")).toMatch(/unique/);
    expect(buildPartLoadComparisonRequest({ ...state, capacityFractionsText: "0.2, 0.6" }).capacity_fractions).toEqual(["0.2", "0.6"]);
  });

  it("mirrors the mode rules: screw unload band, IGV turndown fields, VSD minimum flow", () => {
    const state = validState();
    state.candidates[0].unloadPowerFraction = "0.5";
    state.candidates.push({ ...createCandidate("INLET_GUIDE_VANE"), label: "igv" });
    state.candidates.push({ ...createCandidate("VARIABLE_SPEED"), label: "vsd" });

    const joined = validatePartLoadFormState(state).join(" ");
    expect(joined).toMatch(/0.15-0.35/);
    expect(joined).toMatch(/turndown fraction/);
    expect(joined).toMatch(/minimum flow fraction/);
  });

  it("sends mode-specific fields only and nulls the rest", () => {
    const state = validState();
    const igv = { ...createCandidate("INLET_GUIDE_VANE"), label: "igv" };
    igv.turndownFlowFraction = "0.3";
    igv.powerFractionAtTurndown = "0.8";
    igv.minimumFlowFraction = "0.3"; // typed on the wrong mode, must be dropped
    state.candidates = [igv];

    const payload = buildPartLoadComparisonRequest(state);

    expect(payload.candidates[0]).toEqual({
      label: "igv",
      mode: "INLET_GUIDE_VANE",
      unload_power_fraction: null,
      modulation_floor_capacity_fraction: null,
      minimum_flow_fraction: null,
      minimum_flow_power_fraction: null,
      turndown_flow_fraction: "0.3",
      power_fraction_at_turndown: "0.8",
      below_turndown: "BLOW_OFF",
    });
    expect(payload.electricity_tariff_per_kwh).toBeNull();
  });

  it("validates the load-duration profile against a calendar year", () => {
    const state = validState();
    const row = createLoadDurationRow();
    row.capacityFraction = "0.5";
    row.hours = "9000";
    state.loadDuration = [row];

    expect(validatePartLoadFormState(state).join(" ")).toMatch(/calendar year/);
  });
});
