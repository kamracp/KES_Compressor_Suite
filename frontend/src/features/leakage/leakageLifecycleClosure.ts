import {
  MAX_ASSET_FAD_NM3_PER_HR,
} from "../reference/inputBounds";
import type {
  CompressedAirLeakCloseRequest,
} from "./leakageLifecycleTypes";
import type {
  LeakQuantificationBasis,
} from "./leakageTypes";

export const LEAKAGE_CLOSURE_EVIDENCE_SCHEMA =
  "KES_LEAK_CLOSURE_EVIDENCE_V1";

export type LeakageLifecycleClosureFormState = {
  repairAction: string;
  verificationMethod: LeakQuantificationBasis | "";
  verifiedPostRepairFlowNm3PerHr: string;
  verificationReference: string;
  closureNotes: string;
  changeNotes: string;
};

export function createInitialLeakageLifecycleClosureFormState(): LeakageLifecycleClosureFormState {
  return {
    repairAction: "",
    verificationMethod: "",
    verifiedPostRepairFlowNm3PerHr: "",
    verificationReference: "",
    closureNotes: "",
    changeNotes: "",
  };
}

function optionalText(value: string): string | null {
  const trimmed = value.trim();

  return trimmed === "" ? null : trimmed;
}

export function validateLeakageLifecycleClosureFormState(
  state: LeakageLifecycleClosureFormState,
): string[] {
  const errors: string[] = [];
  const verifiedFlow = Number(
    state.verifiedPostRepairFlowNm3PerHr,
  );

  if (!state.repairAction.trim()) {
    errors.push("Repair action is required.");
  }

  if (!state.verificationMethod) {
    errors.push("Verification method is required.");
  }

  if (
    state.verifiedPostRepairFlowNm3PerHr.trim() === "" ||
    !Number.isFinite(verifiedFlow) ||
    verifiedFlow < 0
  ) {
    errors.push(
      "Verified post-repair flow must be zero or greater.",
    );
  } else if (verifiedFlow > MAX_ASSET_FAD_NM3_PER_HR) {
    errors.push(
      `Verified post-repair flow must not exceed ${MAX_ASSET_FAD_NM3_PER_HR} Nm³/h; check for a missing decimal point.`,
    );
  }

  return errors;
}

export function buildLeakageLifecycleCloseRequest(
  state: LeakageLifecycleClosureFormState,
): CompressedAirLeakCloseRequest {
  return {
    closure_evidence: {
      schema: LEAKAGE_CLOSURE_EVIDENCE_SCHEMA,
      repair_action: state.repairAction.trim(),
      verification_method: state.verificationMethod,
      verified_post_repair_flow_nm3_per_hr:
        state.verifiedPostRepairFlowNm3PerHr.trim(),
      verification_reference: optionalText(
        state.verificationReference,
      ),
    },
    closure_notes: optionalText(state.closureNotes),
    change_notes: optionalText(state.changeNotes),
  };
}
