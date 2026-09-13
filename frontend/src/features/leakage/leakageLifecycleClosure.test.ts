import {
  describe,
  expect,
  it,
} from "vitest";

import {
  MAX_ASSET_FAD_NM3_PER_HR,
} from "../reference/inputBounds";
import {
  buildLeakageLifecycleCloseRequest,
  createInitialLeakageLifecycleClosureFormState,
  LEAKAGE_CLOSURE_EVIDENCE_SCHEMA,
  validateLeakageLifecycleClosureFormState,
  type LeakageLifecycleClosureFormState,
} from "./leakageLifecycleClosure";

function validState(): LeakageLifecycleClosureFormState {
  return {
    repairAction: " Replaced damaged hose coupling ",
    verificationMethod: "ULTRASONIC_ESTIMATE",
    verifiedPostRepairFlowNm3PerHr: " 0.8 ",
    verificationReference: " UT-2026-0913-01 ",
    closureNotes: " Repair verified at operating pressure. ",
    changeNotes: " Closed after maintenance review. ",
  };
}

describe("leakage lifecycle closure payload", () => {
  it("creates a blank closure form state", () => {
    expect(
      createInitialLeakageLifecycleClosureFormState(),
    ).toEqual({
      repairAction: "",
      verificationMethod: "",
      verifiedPostRepairFlowNm3PerHr: "",
      verificationReference: "",
      closureNotes: "",
      changeNotes: "",
    });
  });

  it("requires repair and verification evidence", () => {
    expect(
      validateLeakageLifecycleClosureFormState(
        createInitialLeakageLifecycleClosureFormState(),
      ),
    ).toEqual([
      "Repair action is required.",
      "Verification method is required.",
      "Verified post-repair flow must be zero or greater.",
    ]);
  });

  it("rejects invalid and physically excessive verified flow", () => {
    expect(
      validateLeakageLifecycleClosureFormState({
        ...validState(),
        verifiedPostRepairFlowNm3PerHr: "not-a-number",
      }),
    ).toContain(
      "Verified post-repair flow must be zero or greater.",
    );

    expect(
      validateLeakageLifecycleClosureFormState({
        ...validState(),
        verifiedPostRepairFlowNm3PerHr: "-0.1",
      }),
    ).toContain(
      "Verified post-repair flow must be zero or greater.",
    );

    expect(
      validateLeakageLifecycleClosureFormState({
        ...validState(),
        verifiedPostRepairFlowNm3PerHr: String(
          MAX_ASSET_FAD_NM3_PER_HR + 1,
        ),
      }),
    ).toContain(
      `Verified post-repair flow must not exceed ${MAX_ASSET_FAD_NM3_PER_HR} Nm³/h; check for a missing decimal point.`,
    );
  });

  it("accepts inclusive verified-flow boundaries", () => {
    for (const verifiedFlow of [
      "0",
      String(MAX_ASSET_FAD_NM3_PER_HR),
    ]) {
      expect(
        validateLeakageLifecycleClosureFormState({
          ...validState(),
          verifiedPostRepairFlowNm3PerHr: verifiedFlow,
        }),
      ).toEqual([]);
    }
  });

  it("builds normalized structured closure evidence", () => {
    expect(
      buildLeakageLifecycleCloseRequest(validState()),
    ).toEqual({
      closure_evidence: {
        schema: LEAKAGE_CLOSURE_EVIDENCE_SCHEMA,
        repair_action: "Replaced damaged hose coupling",
        verification_method: "ULTRASONIC_ESTIMATE",
        verified_post_repair_flow_nm3_per_hr: "0.8",
        verification_reference: "UT-2026-0913-01",
      },
      closure_notes: "Repair verified at operating pressure.",
      change_notes: "Closed after maintenance review.",
    });
  });

  it("normalizes optional closure text to null", () => {
    expect(
      buildLeakageLifecycleCloseRequest({
        ...validState(),
        verificationReference: " ",
        closureNotes: "",
        changeNotes: "  ",
      }),
    ).toMatchObject({
      closure_evidence: {
        verification_reference: null,
      },
      closure_notes: null,
      change_notes: null,
    });
  });
});
