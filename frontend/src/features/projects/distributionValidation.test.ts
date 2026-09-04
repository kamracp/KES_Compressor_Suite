import { describe, expect, it } from "vitest";

import { validateDistributionPressures } from "./distributionValidation";

const marker = "cannot exceed 25 bar g";

function inputs(overrides: Partial<Parameters<typeof validateDistributionPressures>[0]> = {}) {
  return {
    designSourcePressure: "7.0",
    nodes: [
      { nodeCode: "N-1", minimumPressure: "" },
      { nodeCode: "N-2", minimumPressure: "6" },
    ],
    segments: [{ segmentCode: "S-1", operatingPressure: "7" }],
    ...overrides,
  };
}

describe("distribution pressure submit-time bounds", () => {
  it("accepts pressures exactly on the plant-air ceiling and blank node minimums", () => {
    const errors = validateDistributionPressures(
      inputs({
        designSourcePressure: "25",
        nodes: [{ nodeCode: "N-1", minimumPressure: "25" }, { nodeCode: "N-2", minimumPressure: "" }],
        segments: [{ segmentCode: "S-1", operatingPressure: "25" }],
      }),
    );
    expect(errors).toEqual([]);
  });

  it("names the node and segment whose pressure exceeds the ceiling", () => {
    const errors = validateDistributionPressures(
      inputs({
        nodes: [{ nodeCode: "N-1", minimumPressure: "6" }, { nodeCode: "N-7", minimumPressure: "30" }],
        segments: [{ segmentCode: "S-1", operatingPressure: "7" }, { segmentCode: "S-4", operatingPressure: "26" }],
      }),
    );
    expect(errors).toHaveLength(2);
    expect(errors[0]).toMatch(/^N-7: minimum pressure/);
    expect(errors[1]).toMatch(/^S-4: operating pressure/);
    expect(errors.every((error) => error.includes(marker))).toBe(true);
  });

  it("rejects a design source pressure above the ceiling", () => {
    const errors = validateDistributionPressures(inputs({ designSourcePressure: "26" }));
    expect(errors).toHaveLength(1);
    expect(errors[0]).toMatch(/^Design source pressure/);
  });

  it("falls back to an index label when the code is blank", () => {
    const errors = validateDistributionPressures(
      inputs({ segments: [{ segmentCode: "  ", operatingPressure: "30" }] }),
    );
    expect(errors[0]).toMatch(/^Segment 1:/);
  });
});
