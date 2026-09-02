import { describe, expect, it } from "vitest";

import {
  createBrownfieldCompressor,
  createBrownfieldCompressorMeasurement,
  createInitialBrownfieldFormState,
  validateBrownfieldFormState,
} from "./brownfieldFormState";

// Submit-time mirrors of the backend bounds landed in C-7b
// (evidence set MFR-ATLASCOPCO-AIR-RANGE-2026-09; schemas/_bounds.py).
const BOUND_MARKERS = ["cannot exceed", "must be between"];

function boundErrors(errors: string[]): string[] {
  return errors.filter((error) =>
    BOUND_MARKERS.some((marker) => error.includes(marker)),
  );
}

function baseState() {
  return {
    ...createInitialBrownfieldFormState(),
    auditCode: "BF-2026-003",
    annualOperatingHours: "8000",
    electricityTariffPerKwh: "8",
    optimizedDischargePressureBarG: "6.5",
  };
}

describe("brownfield submit-time input bounds", () => {
  it("accepts values sitting exactly on the backend ceilings", () => {
    const compressor = {
      ...createBrownfieldCompressor(0),
      rated_fad_nm3_per_hr: "36000",
      rated_motor_power_kw: "3150",
      rated_discharge_pressure_bar_g: "25",
    };
    const measurement = {
      ...createBrownfieldCompressorMeasurement(compressor.unit_code),
      measured_flow_nm3_per_hr: "36000",
      measured_power_kw: "3400",
      measured_discharge_pressure_bar_g: "25",
    };
    const errors = validateBrownfieldFormState({
      ...baseState(),
      electricityTariffPerKwh: "25",
      optimizedDischargePressureBarG: "25",
      compressors: [compressor],
      compressorMeasurements: [measurement],
    });

    expect(boundErrors(errors)).toEqual([]);
  });

  it("names the compressor when a rated value exceeds its ceiling", () => {
    const errors = validateBrownfieldFormState({
      ...baseState(),
      compressors: [
        createBrownfieldCompressor(0),
        {
          ...createBrownfieldCompressor(1),
          rated_fad_nm3_per_hr: "40000",
          rated_motor_power_kw: "3200",
          rated_discharge_pressure_bar_g: "30",
        },
      ],
    });
    const found = boundErrors(errors);

    expect(found).toHaveLength(3);
    expect(found.every((error) => error.startsWith("Compressor 2:"))).toBe(true);
    expect(found.some((error) => error.includes("36000 Nm3/h"))).toBe(true);
    expect(found.some((error) => error.includes("3150 kW"))).toBe(true);
    expect(found.some((error) => error.includes("25 bar g"))).toBe(true);
  });

  it("rejects measured power above the 3400 kW measured ceiling", () => {
    const errors = validateBrownfieldFormState({
      ...baseState(),
      compressorMeasurements: [
        {
          ...createBrownfieldCompressorMeasurement("C-1"),
          measured_power_kw: "3500",
          measured_flow_nm3_per_hr: "1200",
          measured_discharge_pressure_bar_g: "7",
        },
      ],
    });
    const found = boundErrors(errors);

    expect(found).toHaveLength(1);
    expect(found[0]).toContain("Measurement 1: measured power");
    expect(found[0]).toContain("3400 kW");
  });

  it("rejects an electricity tariff outside 5-25 INR/kWh on both sides", () => {
    for (const tariff of ["4", "26"]) {
      const errors = validateBrownfieldFormState({
        ...baseState(),
        electricityTariffPerKwh: tariff,
      });
      expect(
        errors.some((error) => error.includes("between 5 and 25 INR/kWh")),
      ).toBe(true);
    }
  });

  it("rejects an optimized discharge pressure above the plant-air ceiling", () => {
    const errors = validateBrownfieldFormState({
      ...baseState(),
      optimizedDischargePressureBarG: "26",
    });

    expect(
      errors.some((error) => error.includes("Optimized discharge pressure")),
    ).toBe(true);
  });
});
