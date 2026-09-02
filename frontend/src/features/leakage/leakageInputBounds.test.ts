import { describe, expect, it } from "vitest";

import {
  createInitialLeakageFormState,
  validateLeakageFormState,
} from "./leakageFormState";

// Submit-time mirror of the backend tariff bound (C-7b). The tariff is a
// select in the UI, but form state can still arrive from elsewhere.
const marker = "between 5 and 25 INR/kWh";

describe("leakage submit-time input bounds", () => {
  it("accepts tariffs on both ends of the backend range", () => {
    for (const tariff of ["5", "25"]) {
      const errors = validateLeakageFormState({
        ...createInitialLeakageFormState(),
        electricityTariffPerKwh: tariff,
      });
      expect(errors.some((error) => error.includes(marker))).toBe(false);
    }
  });

  it("rejects tariffs just outside the backend range", () => {
    for (const tariff of ["4", "26"]) {
      const errors = validateLeakageFormState({
        ...createInitialLeakageFormState(),
        electricityTariffPerKwh: tariff,
      });
      expect(errors.some((error) => error.includes(marker))).toBe(true);
    }
  });
});
