import { describe, expect, it } from "vitest";

import {
  createInitialPerformanceFormState,
  validatePerformanceFormState,
} from "./performanceFormState";

// Submit-time mirrors of the backend bounds landed in C-7b
// (reference/inputBounds.ts). Only fields the backend bounds are mirrored.
const BOUND_MARKERS = ["cannot exceed", "must be between"];

function boundErrors(errors: string[]): string[] {
  return errors.filter((error) =>
    BOUND_MARKERS.some((marker) => error.includes(marker)),
  );
}

function baseState() {
  return { ...createInitialPerformanceFormState(), electricityTariffPerKwh: "8" };
}

describe("performance submit-time input bounds", () => {
  it("accepts a measurement pressure and tariff exactly on the ceilings", () => {
    const base = baseState();
    const errors = validatePerformanceFormState({
      ...base,
      electricityTariffPerKwh: "25",
      measurements: [{ ...base.measurements[0], pressure_bar_g: "25" }],
    });

    expect(boundErrors(errors)).toEqual([]);
  });

  it("labels the measurement whose pressure exceeds the plant-air ceiling", () => {
    const base = baseState();
    const errors = validatePerformanceFormState({
      ...base,
      measurements: [
        { ...base.measurements[0], pressure_bar_g: "7" },
        { ...base.measurements[0], pressure_bar_g: "26" },
      ],
    });
    const found = boundErrors(errors);

    expect(found).toHaveLength(1);
    expect(found[0]).toContain("Measurement 2: pressure");
  });

  it("rejects an electricity tariff outside 5-25 INR/kWh on both sides", () => {
    for (const tariff of ["4", "26"]) {
      const errors = validatePerformanceFormState({
        ...baseState(),
        electricityTariffPerKwh: tariff,
      });
      expect(
        errors.some((error) => error.includes("between 5 and 25 INR/kWh")),
      ).toBe(true);
    }
  });
});
