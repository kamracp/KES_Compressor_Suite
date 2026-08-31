import { describe, expect, it } from "vitest";

import {
  buildBrownfieldAuditRequest,
  createInitialBrownfieldFormState,
  validateBrownfieldFormState,
} from "./brownfieldFormState";

function baseState() {
  const state = createInitialBrownfieldFormState();

  return {
    ...state,
    auditCode: "BF-2026-001",
    annualOperatingHours: "8000",
    electricityTariffPerKwh: "5",
  };
}

describe("brownfield motor and PFC inputs", () => {
  it("defaults the target power factor to 0.95", () => {
    expect(
      createInitialBrownfieldFormState().motorTargetPowerFactor,
    ).toBe("0.95");
  });

  it("sends unmeasured motor fields as null, never as zero", () => {
    const payload = buildBrownfieldAuditRequest(baseState(), 1);

    expect(payload.motor_measured_voltage_v).toBeNull();
    expect(payload.motor_measured_current_a).toBeNull();
    expect(payload.motor_measured_power_factor).toBeNull();
    expect(payload.motor_rated_power_kw).toBeNull();
    expect(payload.pf_penalty_annual_cost).toBeNull();
  });

  it("carries a full motor measurement into the payload", () => {
    const payload = buildBrownfieldAuditRequest(
      {
        ...baseState(),
        motorMeasuredVoltageV: "415",
        motorMeasuredCurrentA: "78",
        motorMeasuredPowerFactor: "0.82",
        motorRatedPowerKw: "55",
        pfPenaltyAnnualCost: "48000",
      },
      1,
    );

    expect(payload.motor_measured_voltage_v).toBe("415");
    expect(payload.motor_measured_current_a).toBe("78");
    expect(payload.motor_measured_power_factor).toBe("0.82");
    expect(payload.motor_target_power_factor).toBe("0.95");
    expect(payload.motor_rated_power_kw).toBe("55");
    expect(payload.pf_penalty_annual_cost).toBe("48000");
  });

  it("falls back to 0.95 when the target power factor is cleared", () => {
    const payload = buildBrownfieldAuditRequest(
      { ...baseState(), motorTargetPowerFactor: "" },
      1,
    );

    expect(payload.motor_target_power_factor).toBe("0.95");
  });

  it("rejects a measured power factor above one", () => {
    const errors = validateBrownfieldFormState({
      ...baseState(),
      motorMeasuredPowerFactor: "1.4",
    });

    expect(
      errors.some((error) =>
        error.includes("Measured motor power factor"),
      ),
    ).toBe(true);
  });

  it("accepts a form with no motor measurement at all", () => {
    // The initial form carries one blank compressor row, whose own
    // "Rated motor power" validation is unrelated to C-6. Assert on the
    // exact labels this feature added, not on the word "motor".
    const motorMeasurementLabels = [
      "Measured motor power factor",
      "Target power factor",
      "Measured motor voltage",
      "Measured motor current",
      "Motor nameplate power",
      "Annual power-factor penalty",
    ];

    const errors = validateBrownfieldFormState(baseState());

    expect(
      errors.some((error) =>
        motorMeasurementLabels.some((label) => error.includes(label)),
      ),
    ).toBe(false);
  });
});
