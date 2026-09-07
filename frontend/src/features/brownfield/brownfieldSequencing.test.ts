import { describe, expect, it } from "vitest";

import {
  buildBrownfieldAuditRequest,
  createBrownfieldCompressor,
  createCompressorSequencingSettings,
  createInitialBrownfieldFormState,
  validateBrownfieldFormState,
} from "./brownfieldFormState";
import type { ExistingCompressorInput } from "./brownfieldTypes";

function compressor(
  index: number,
  overrides: Partial<ExistingCompressorInput> = {},
): ExistingCompressorInput {
  return {
    ...createBrownfieldCompressor(index),
    rated_fad_nm3_per_hr: "1000",
    rated_discharge_pressure_bar_g: "7.5",
    rated_motor_power_kw: "100",
    sequencing: {
      ...createCompressorSequencingSettings(),
      band: { load_pressure_bar_g: "6.5", unload_pressure_bar_g: "7.3" },
    },
    ...overrides,
  };
}

function enabledState() {
  return {
    ...createInitialBrownfieldFormState(),
    auditCode: "BF-2026-001",
    annualOperatingHours: "8000",
    electricityTariffPerKwh: "5",
    compressors: [compressor(0), compressor(1)],
    sequencingEnabled: true,
    sequencingProposedLoadPressureBarG: "6.5",
    sequencingProposedUnloadPressureBarG: "7.0",
    sequencingReceiverVolumeM3: "10",
  };
}

function sequencingErrors(state: ReturnType<typeof enabledState>): string[] {
  return validateBrownfieldFormState(state).filter((error) =>
    /sequenc/i.test(error),
  );
}

describe("brownfield sequencing proposal (C-7d)", () => {
  it("is off by default and sends nulls, never partial settings", () => {
    const payload = buildBrownfieldAuditRequest(
      createInitialBrownfieldFormState(),
      1,
    );

    expect(payload.sequencing_proposal).toBeNull();
    expect(payload.compressors.every((c) => c.sequencing === null)).toBe(true);
  });

  it("drops stale machine settings when the proposal is switched off", () => {
    const payload = buildBrownfieldAuditRequest(
      { ...enabledState(), sequencingEnabled: false },
      1,
    );

    expect(payload.sequencing_proposal).toBeNull();
    expect(payload.compressors[0].sequencing).toBeNull();
  });

  it("carries the proposal and trimmed machine settings into the payload", () => {
    const payload = buildBrownfieldAuditRequest(enabledState(), 1);

    expect(payload.sequencing_proposal).toEqual({
      proposed_band: { load_pressure_bar_g: "6.5", unload_pressure_bar_g: "7.0" },
      receiver_volume_m3: "10",
    });
    expect(payload.compressors[0].sequencing).toEqual({
      band: { load_pressure_bar_g: "6.5", unload_pressure_bar_g: "7.3" },
      unload_power_fraction: "0.25",
      priority: null,
      minimum_flow_fraction: null,
      minimum_flow_power_fraction: null,
      standby_runs_unloaded: false,
      modulation_floor_capacity_fraction: null,
      turndown_flow_fraction: null,
      power_fraction_at_turndown: null,
      below_turndown: null,
      unload_blowdown_seconds: null,
    });
  });

  it("nulls minimum-flow fields on non-VSD units even if typed", () => {
    const state = enabledState();
    state.compressors[0].sequencing!.minimum_flow_fraction = "0.3";

    const payload = buildBrownfieldAuditRequest(state, 1);

    expect(payload.compressors[0].sequencing?.minimum_flow_fraction).toBeNull();
  });

  it("accepts a complete proposal without sequencing errors", () => {
    expect(sequencingErrors(enabledState())).toEqual([]);
  });

  it("requires settings on every available unit", () => {
    const state = enabledState();
    state.compressors[1] = compressor(1, { sequencing: null });

    expect(sequencingErrors(state).join(" ")).toMatch(
      /Compressor 2 sequencing settings are required/,
    );
  });

  it("does not require settings on an unavailable unit", () => {
    const state = enabledState();
    state.compressors[1] = compressor(1, { sequencing: null, available: false });

    expect(sequencingErrors(state)).toEqual([]);
  });

  it("mirrors the DOE unload-power-fraction band", () => {
    const state = enabledState();
    state.compressors[0].sequencing!.unload_power_fraction = "0.5";

    expect(sequencingErrors(state).join(" ")).toMatch(/0.15-0.35/);
  });

  it("rejects an unload setpoint at or below the load setpoint", () => {
    const state = enabledState();
    state.compressors[0].sequencing!.band.unload_pressure_bar_g = "6.5";

    expect(sequencingErrors(state).join(" ")).toMatch(/above the load setpoint/);
  });

  it("accepts modulation units and sends the floor only for them", () => {
    const state = enabledState();
    state.compressors[0] = compressor(0, { control_mode: "MODULATION" });
    state.compressors[0].sequencing!.modulation_floor_capacity_fraction = "0.3";
    state.compressors[1].sequencing!.modulation_floor_capacity_fraction = "0.3";

    expect(sequencingErrors(state)).toEqual([]);
    const payload = buildBrownfieldAuditRequest(state, 1);
    expect(payload.compressors[0].sequencing?.modulation_floor_capacity_fraction).toBe("0.3");
    expect(payload.compressors[1].sequencing?.modulation_floor_capacity_fraction).toBeNull();
  });

  it("requires turndown fields on an inlet-guide-vane unit and defaults to blow-off", () => {
    const state = enabledState();
    state.compressors[0] = compressor(0, { control_mode: "INLET_GUIDE_VANE" });
    state.compressors[0].sequencing!.unload_power_fraction = null;

    const joined = sequencingErrors(state).join(" ");
    expect(joined).toMatch(/turndown fraction/);
    expect(joined).toMatch(/power at turndown/);

    state.compressors[0].sequencing!.turndown_flow_fraction = "0.3";
    state.compressors[0].sequencing!.power_fraction_at_turndown = "0.8";
    expect(sequencingErrors(state)).toEqual([]);
    const payload = buildBrownfieldAuditRequest(state, 1);
    expect(payload.compressors[0].sequencing?.below_turndown).toBe("BLOW_OFF");
    expect(payload.compressors[0].sequencing?.unload_power_fraction).toBeNull();
  });

  it("requires a centrifugal off-loaded fraction for auto-dual", () => {
    const state = enabledState();
    state.compressors[0] = compressor(0, { control_mode: "INLET_GUIDE_VANE" });
    Object.assign(state.compressors[0].sequencing!, {
      unload_power_fraction: null,
      turndown_flow_fraction: "0.3",
      power_fraction_at_turndown: "0.8",
      below_turndown: "UNLOAD",
    });

    expect(sequencingErrors(state).join(" ")).toMatch(/centrifugal unload power fraction/);
  });

  it("requires priority on all units or none", () => {
    const state = enabledState();
    state.compressors[0].sequencing!.priority = 1;

    expect(sequencingErrors(state).join(" ")).toMatch(/every available unit or on none/);
  });

  it("requires both minimum-flow fields on a VSD unit", () => {
    const state = enabledState();
    state.compressors[0] = compressor(0, { control_mode: "VSD" });

    const joined = sequencingErrors(state).join(" ");

    expect(joined).toMatch(/minimum flow fraction/);
    expect(joined).toMatch(/minimum-flow power fraction/);
  });
});
