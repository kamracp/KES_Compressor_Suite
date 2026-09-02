import { describe, expect, it } from "vitest";

import {
  createInitialGreenfieldFormState,
  validateGreenfieldFormState,
} from "./greenfieldFormState";
import type {
  CompressorStationInput,
  CompressorUnitInput,
  ReceiverSizingInput,
} from "./greenfieldTypes";

// Submit-time mirrors of the backend bounds landed in C-7b
// (reference/inputBounds.ts; evidence MFR-ATLASCOPCO-AIR-RANGE-2026-09).
const BOUND_MARKERS = ["cannot exceed", "must be between"];

function boundErrors(errors: string[]): string[] {
  return errors.filter((error) =>
    BOUND_MARKERS.some((marker) => error.includes(marker)),
  );
}

function unit(code: string, fad: string, pressure: string): CompressorUnitInput {
  return {
    unit_code: code,
    technology: "ROTARY_SCREW_OIL_INJECTED",
    control_mode: "FIXED_SPEED",
    duty_role: "BASE_LOAD",
    rated_fad_nm3_per_hr: fad,
    minimum_stable_flow_fraction: "0.4",
    rated_discharge_pressure_bar_g: pressure,
  };
}

function station(units: CompressorUnitInput[], minPressure = "7"): CompressorStationInput {
  return {
    station_code: "CS-1",
    units,
    redundancy_philosophy: "N_PLUS_1",
    minimum_required_pressure_bar_g: minPressure,
    design_flow_nm3_per_hr: "1500",
  };
}

function receiver(high: string, low: string): ReceiverSizingInput {
  return {
    peak_demand_nm3_per_hr: "2000",
    available_compressor_flow_nm3_per_hr: "1500",
    event_duration_seconds: "30",
    receiver_high_pressure_bar_g: high,
    receiver_low_pressure_bar_g: low,
  };
}

function baseState() {
  const state = createInitialGreenfieldFormState();
  return {
    ...state,
    designBasis: {
      ...state.designBasis,
      annualOperatingDays: "330",
      electricityTariffPerKwh: "8",
    },
  };
}

describe("greenfield submit-time input bounds", () => {
  it("accepts values sitting exactly on the backend ceilings", () => {
    const base = baseState();
    const errors = validateGreenfieldFormState({
      ...base,
      designBasis: {
        ...base.designBasis,
        minimumPointOfUsePressureBarG: "25",
        electricityTariffPerKwh: "25",
      },
      consumers: [{ ...base.consumers[0], required_pressure_bar_g: "25" }],
      station: station([unit("C-1", "36000", "25")], "25"),
      receiver: receiver("25", "25"),
    });

    expect(boundErrors(errors)).toEqual([]);
  });

  it("labels the compressor unit whose rated values exceed the ceilings", () => {
    const errors = validateGreenfieldFormState({
      ...baseState(),
      station: station([unit("C-1", "1500", "7"), unit("C-2", "40000", "30")]),
    });
    const found = boundErrors(errors);

    expect(found).toHaveLength(2);
    expect(found.every((error) => error.startsWith("Compressor unit 2:"))).toBe(
      true,
    );
  });

  it("rejects receiver pressures above the plant-air ceiling", () => {
    const errors = validateGreenfieldFormState({
      ...baseState(),
      receiver: receiver("26", "26"),
    });
    const found = boundErrors(errors);

    expect(found).toHaveLength(2);
    expect(found.some((error) => error.startsWith("Receiver high"))).toBe(true);
    expect(found.some((error) => error.startsWith("Receiver low"))).toBe(true);
  });

  it("stays silent on bounds when station and receiver are not entered", () => {
    const errors = validateGreenfieldFormState({
      ...baseState(),
      station: null,
      receiver: null,
    });

    expect(boundErrors(errors)).toEqual([]);
  });

  it("rejects an electricity tariff outside 5-25 INR/kWh on both sides", () => {
    for (const tariff of ["4", "26"]) {
      const base = baseState();
      const errors = validateGreenfieldFormState({
        ...base,
        designBasis: { ...base.designBasis, electricityTariffPerKwh: tariff },
      });
      expect(
        errors.some((error) => error.includes("between 5 and 25 INR/kWh")),
      ).toBe(true);
    }
  });
});
