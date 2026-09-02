import { describe, expect, it } from "vitest";

import { createInitialSkidFormState, validateSkidFormState } from "./skidFormState";

// Submit-time mirror of the backend skid design_pressure bound (C-7b).
const marker = "Design pressure cannot exceed 25 bar g";

describe("skid submit-time input bounds", () => {
  it("accepts a design pressure exactly on the plant-air ceiling", () => {
    const errors = validateSkidFormState({
      ...createInitialSkidFormState(),
      designPressureBarG: "25",
    });
    expect(errors.some((error) => error.includes(marker))).toBe(false);
  });

  it("rejects a design pressure above the plant-air ceiling", () => {
    const errors = validateSkidFormState({
      ...createInitialSkidFormState(),
      designPressureBarG: "26",
    });
    expect(errors.some((error) => error.includes(marker))).toBe(true);
  });
});
