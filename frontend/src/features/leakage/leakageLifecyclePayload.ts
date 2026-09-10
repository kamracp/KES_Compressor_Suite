import type {
  CompressedAirLeakCreateRequest,
  LeakageLifecycleJsonObject,
} from "./leakageLifecycleTypes";
import type {
  LeakRegisterItemInput,
} from "./leakageTypes";

export const LEAKAGE_SOURCE_SNAPSHOT_SCHEMA =
  "KES_LEAK_REGISTER_ITEM_V1";

function optionalText(
  value: string | null | undefined,
): string | null {
  if (value === null || value === undefined) {
    return null;
  }

  const trimmed = value.trim();

  return trimmed === "" ? null : trimmed;
}

function requireText(
  value: string,
  label: string,
  maximumLength: number,
  errors: string[],
): void {
  const trimmed = value.trim();

  if (!trimmed) {
    errors.push(`${label} is required.`);
    return;
  }

  if (trimmed.length > maximumLength) {
    errors.push(
      `${label} must be ${maximumLength} characters or fewer.`,
    );
  }
}

function requireNonNegativeDecimal(
  value: string,
  label: string,
  errors: string[],
): void {
  const numericValue = Number(value);

  if (
    value.trim() === "" ||
    !Number.isFinite(numericValue) ||
    numericValue < 0
  ) {
    errors.push(`${label} must be zero or greater.`);
  }
}

function requireFraction(
  value: string,
  label: string,
  errors: string[],
): void {
  const numericValue = Number(value);

  if (
    value.trim() === "" ||
    !Number.isFinite(numericValue) ||
    numericValue < 0 ||
    numericValue > 1
  ) {
    errors.push(`${label} must be between zero and one.`);
  }
}

function validateOptionalNonNegativeDecimal(
  value: string | null | undefined,
  label: string,
  errors: string[],
): void {
  if (
    value === null ||
    value === undefined ||
    value.trim() === ""
  ) {
    return;
  }

  requireNonNegativeDecimal(value, label, errors);
}

export function validateLeakageLifecycleTagging(
  leak: LeakRegisterItemInput,
): string[] {
  const errors: string[] = [];

  requireText(
    leak.leak_code,
    "Leak code",
    100,
    errors,
  );
  requireText(
    leak.location,
    "Leak location",
    255,
    errors,
  );
  requireNonNegativeDecimal(
    leak.baseline_leakage_flow_nm3_per_hr,
    "Baseline leakage flow",
    errors,
  );
  requireFraction(
    leak.expected_repair_fraction,
    "Expected repair fraction",
    errors,
  );
  validateOptionalNonNegativeDecimal(
    leak.survey_pressure_bar_g,
    "Survey pressure",
    errors,
  );
  validateOptionalNonNegativeDecimal(
    leak.estimated_repair_cost,
    "Estimated repair cost",
    errors,
  );
  validateOptionalNonNegativeDecimal(
    leak.verified_post_repair_flow_nm3_per_hr,
    "Verified post-repair flow",
    errors,
  );

  return errors;
}

function buildSourceSnapshot(
  leak: LeakRegisterItemInput,
): LeakageLifecycleJsonObject {
  return {
    schema: LEAKAGE_SOURCE_SNAPSHOT_SCHEMA,
    baseline_leakage_flow_nm3_per_hr:
      leak.baseline_leakage_flow_nm3_per_hr.trim(),
    quantification_basis: leak.quantification_basis,
    source_category: leak.source_category,
    area: optionalText(leak.area),
    equipment_tag: optionalText(leak.equipment_tag),
    component_description: optionalText(
      leak.component_description,
    ),
    survey_pressure_bar_g: optionalText(
      leak.survey_pressure_bar_g,
    ),
    expected_repair_fraction:
      leak.expected_repair_fraction.trim(),
    repair_status: leak.repair_status,
    estimated_repair_cost: optionalText(
      leak.estimated_repair_cost,
    ),
    verified_post_repair_flow_nm3_per_hr:
      optionalText(
        leak.verified_post_repair_flow_nm3_per_hr,
      ),
    survey_method_reference: optionalText(
      leak.survey_method_reference,
    ),
    notes: optionalText(leak.notes),
  };
}

export function buildLeakageLifecycleCreateRequest(
  leak: LeakRegisterItemInput,
): CompressedAirLeakCreateRequest {
  return {
    leak_code: leak.leak_code.trim(),
    location: leak.location.trim(),
    source_snapshot: buildSourceSnapshot(leak),
  };
}
