import { describe, expect, it } from "vitest";

import {
  createInitialAlliedFormState,
  createReceiverConfiguration,
  validateAlliedFormState,
} from "./alliedFormState";

// Submit-time mirrors of the backend receiver pressure bounds (C-7b).
const marker = "cannot exceed 25 bar g";

function withReceiver(high: string, low: string) {
  const receiver = createReceiverConfiguration();
  return {
    ...createInitialAlliedFormState(),
    receiver: {
      ...receiver,
      sizing_input: {
        ...receiver.sizing_input,
        receiver_high_pressure_bar_g: high,
        receiver_low_pressure_bar_g: low,
      },
    },
  };
}

describe("allied submit-time input bounds", () => {
  it("accepts receiver pressures exactly on the plant-air ceiling", () => {
    const errors = validateAlliedFormState(withReceiver("25", "25"));
    expect(errors.some((error) => error.includes(marker))).toBe(false);
  });

  it("rejects each receiver pressure above the plant-air ceiling", () => {
    const found = validateAlliedFormState(withReceiver("26", "26")).filter(
      (error) => error.includes(marker),
    );
    expect(found).toHaveLength(2);
  });

  it("stays silent on receiver bounds when no receiver is entered", () => {
    const errors = validateAlliedFormState({
      ...createInitialAlliedFormState(),
      receiver: null,
    });
    expect(errors.some((error) => error.includes(marker))).toBe(false);
  });
});
