import {
  describe,
  expect,
  it,
} from "vitest";

import {
  buildLeakageLifecycleCreateRequest,
  LEAKAGE_SOURCE_SNAPSHOT_SCHEMA,
  validateLeakageLifecycleTagging,
} from "./leakageLifecyclePayload";
import type {
  LeakRegisterItemInput,
} from "./leakageTypes";

function validLeak(): LeakRegisterItemInput {
  return {
    leak_code: " LEAK-001 ",
    location: " Compressor room ",
    baseline_leakage_flow_nm3_per_hr: " 12.5 ",
    quantification_basis: "ULTRASONIC_ESTIMATE",
    source_category: "PIPE_JOINT",
    area: " Utilities ",
    equipment_tag: " AIR-HDR-01 ",
    component_description: " Threaded elbow ",
    survey_pressure_bar_g: " 6.5 ",
    expected_repair_fraction: " 0.8 ",
    repair_status: "OPEN",
    estimated_repair_cost: " 2500 ",
    verified_post_repair_flow_nm3_per_hr: " 1.5 ",
    survey_method_reference: " UT-2026-0910 ",
    notes: " Repair during next shutdown. ",
  };
}

describe("leakage lifecycle payload", () => {
  it("accepts a valid leak register item", () => {
    expect(
      validateLeakageLifecycleTagging(validLeak()),
    ).toEqual([]);
  });

  it("rejects missing and overlength identity fields", () => {
    const leak = validLeak();

    const errors = validateLeakageLifecycleTagging({
      ...leak,
      leak_code: " ",
      location: "L".repeat(256),
    });

    expect(errors).toEqual([
      "Leak code is required.",
      "Leak location must be 255 characters or fewer.",
    ]);
  });

  it("rejects invalid engineering quantities", () => {
    const leak = validLeak();

    const errors = validateLeakageLifecycleTagging({
      ...leak,
      baseline_leakage_flow_nm3_per_hr: "-0.1",
      expected_repair_fraction: "1.1",
      survey_pressure_bar_g: "-1",
      estimated_repair_cost: "not-a-number",
      verified_post_repair_flow_nm3_per_hr: "-2",
    });

    expect(errors).toEqual([
      "Baseline leakage flow must be zero or greater.",
      "Expected repair fraction must be between zero and one.",
      "Survey pressure must be zero or greater.",
      "Estimated repair cost must be zero or greater.",
      "Verified post-repair flow must be zero or greater.",
    ]);
  });

  it("accepts inclusive zero and one boundaries", () => {
    const leak = validLeak();

    expect(
      validateLeakageLifecycleTagging({
        ...leak,
        baseline_leakage_flow_nm3_per_hr: "0",
        expected_repair_fraction: "1",
        survey_pressure_bar_g: "0",
        estimated_repair_cost: "0",
        verified_post_repair_flow_nm3_per_hr: "0",
      }),
    ).toEqual([]);

    expect(
      validateLeakageLifecycleTagging({
        ...leak,
        expected_repair_fraction: "0",
      }),
    ).toEqual([]);
  });

  it("builds a normalized API request with a complete source snapshot", () => {
    expect(
      buildLeakageLifecycleCreateRequest(validLeak()),
    ).toEqual({
      leak_code: "LEAK-001",
      location: "Compressor room",
      source_snapshot: {
        schema: LEAKAGE_SOURCE_SNAPSHOT_SCHEMA,
        baseline_leakage_flow_nm3_per_hr: "12.5",
        quantification_basis: "ULTRASONIC_ESTIMATE",
        source_category: "PIPE_JOINT",
        area: "Utilities",
        equipment_tag: "AIR-HDR-01",
        component_description: "Threaded elbow",
        survey_pressure_bar_g: "6.5",
        expected_repair_fraction: "0.8",
        repair_status: "OPEN",
        estimated_repair_cost: "2500",
        verified_post_repair_flow_nm3_per_hr: "1.5",
        survey_method_reference: "UT-2026-0910",
        notes: "Repair during next shutdown.",
      },
    });
  });

  it("normalizes empty optional snapshot values to null", () => {
    const leak = validLeak();

    const request = buildLeakageLifecycleCreateRequest({
      ...leak,
      area: " ",
      equipment_tag: null,
      component_description: undefined,
      survey_pressure_bar_g: "",
      estimated_repair_cost: null,
      verified_post_repair_flow_nm3_per_hr: undefined,
      survey_method_reference: " ",
      notes: null,
    });

    expect(request.source_snapshot).toMatchObject({
      area: null,
      equipment_tag: null,
      component_description: null,
      survey_pressure_bar_g: null,
      estimated_repair_cost: null,
      verified_post_repair_flow_nm3_per_hr: null,
      survey_method_reference: null,
      notes: null,
    });
  });
});
