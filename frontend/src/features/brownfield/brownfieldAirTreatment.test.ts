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
    auditCode: "BF-2026-002",
    annualOperatingHours: "8000",
    electricityTariffPerKwh: "5",
  };
}

describe("brownfield air-treatment inputs", () => {
  it("starts with both air-treatment fields blank", () => {
    const state = createInitialBrownfieldFormState();

    expect(state.condensateDrainAirLossNm3PerHr).toBe("");
    expect(state.filterExcessPressureDropBar).toBe("");
  });

  it("sends unmeasured air-treatment fields as null, never as zero", () => {
    const payload = buildBrownfieldAuditRequest(baseState(), 1);

    expect(payload.condensate_drain_air_loss_nm3_per_hr).toBeNull();
    expect(payload.filter_excess_pressure_drop_bar).toBeNull();
  });

  it("carries measured air-treatment values into the payload", () => {
    const payload = buildBrownfieldAuditRequest(
      {
        ...baseState(),
        condensateDrainAirLossNm3PerHr: "12",
        filterExcessPressureDropBar: "0.35",
      },
      1,
    );

    expect(payload.condensate_drain_air_loss_nm3_per_hr).toBe("12");
    expect(payload.filter_excess_pressure_drop_bar).toBe("0.35");
  });

  it("rejects a negative condensate drain air loss", () => {
    const errors = validateBrownfieldFormState({
      ...baseState(),
      condensateDrainAirLossNm3PerHr: "-5",
    });

    expect(
      errors.some((error) =>
        error.includes("Condensate drain air loss"),
      ),
    ).toBe(true);
  });

  it("rejects a negative filter excess pressure drop", () => {
    const errors = validateBrownfieldFormState({
      ...baseState(),
      filterExcessPressureDropBar: "-0.2",
    });

    expect(
      errors.some((error) =>
        error.includes("Filter excess pressure drop"),
      ),
    ).toBe(true);
  });

  it("rejects an implausible filter excess pressure drop", () => {
    // Regression: a dropped decimal point ("035" for "0.35") reached the
    // backend as 35 bar and produced a 39 percent energy saving claim
    // from a filter element change. A clean element runs near 0.14 bar
    // and replacement is advised by roughly 0.35 bar, so anything above
    // 1 bar is a data-entry error.
    // Ref: US DOE / Compressed Air Challenge Sourcebook.
    const errors = validateBrownfieldFormState({
      ...baseState(),
      filterExcessPressureDropBar: "035",
    });
    expect(
      errors.some((error) =>
        error.includes("Filter excess pressure drop"),
      ),
    ).toBe(true);
  });

  it("accepts a form with no air-treatment measurement at all", () => {
    const airTreatmentLabels = [
      "Condensate drain air loss",
      "Filter excess pressure drop",
    ];

    const errors = validateBrownfieldFormState(baseState());

    expect(
      errors.some((error) =>
        airTreatmentLabels.some((label) => error.includes(label)),
      ),
    ).toBe(false);
  });
});
