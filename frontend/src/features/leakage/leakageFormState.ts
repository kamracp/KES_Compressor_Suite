import type {
  CompressedAirLeakageManagementRequest,
  LeakRegisterItemInput,
} from "./leakageTypes";
import type { SupplyPhase } from "../reference/referenceTypes";

export type LeakageFormState = {
  analysisCode: string;

  leaks: LeakRegisterItemInput[];

  specificPowerKwPerNm3PerMin: string;
  annualOperatingHours: string;
  electricityTariffPerKwh: string;
  supplyPhase: SupplyPhase;
  nominalSupplyVoltageV: number;
  supplyFrequencyHz: number;
  demandSavingControlFactor: string;

  averageSystemDemandNm3PerHr: string;

  notes: string;
};

export function createLeakRegisterItem(
  index = 0,
): LeakRegisterItemInput {
  return {
    leak_code: `L-${String(index + 1).padStart(3, "0")}`,
    location: "",

    baseline_leakage_flow_nm3_per_hr: "",
    quantification_basis: "ULTRASONIC_ESTIMATE",

    source_category: "OTHER",

    area: null,
    equipment_tag: null,
    component_description: null,

    survey_pressure_bar_g: null,

    expected_repair_fraction: "1",

    repair_status: "OPEN",

    estimated_repair_cost: null,

    verified_post_repair_flow_nm3_per_hr: null,

    survey_method_reference: null,
    notes: null,
  };
}

export function createInitialLeakageFormState(): LeakageFormState {
  return {
    analysisCode: "",
    leaks: [createLeakRegisterItem()],
    specificPowerKwPerNm3PerMin: "",
    annualOperatingHours: "",
    electricityTariffPerKwh: "",
    supplyPhase: "three",
    nominalSupplyVoltageV: 415,
    supplyFrequencyHz: 50,
    demandSavingControlFactor: "1",
    averageSystemDemandNm3PerHr: "",
    notes: "",
  };
}

function parseNumber(value: string): number {
  return Number(value);
}

function requireText(
  value: string,
  label: string,
  errors: string[],
): void {
  if (!value.trim()) {
    errors.push(`${label} is required.`);
  }
}

function requirePositive(
  value: string,
  label: string,
  errors: string[],
): void {
  const numericValue = parseNumber(value);

  if (
    value.trim() === "" ||
    !Number.isFinite(numericValue) ||
    numericValue <= 0
  ) {
    errors.push(`${label} must be greater than zero.`);
  }
}

function requireNonNegative(
  value: string,
  label: string,
  errors: string[],
): void {
  const numericValue = parseNumber(value);

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
  const numericValue = parseNumber(value);

  if (
    value.trim() === "" ||
    !Number.isFinite(numericValue) ||
    numericValue < 0 ||
    numericValue > 1
  ) {
    errors.push(`${label} must be between zero and one.`);
  }
}

function validateOptionalPositive(
  value: string | null | undefined,
  label: string,
  errors: string[],
): void {
  if (value === null || value === undefined || value.trim() === "") {
    return;
  }

  requirePositive(value, label, errors);
}

function validateOptionalNonNegative(
  value: string | null | undefined,
  label: string,
  errors: string[],
): void {
  if (value === null || value === undefined || value.trim() === "") {
    return;
  }

  requireNonNegative(value, label, errors);
}

export function validateLeakageFormState(
  state: LeakageFormState,
): string[] {
  const errors: string[] = [];

  requireText(
    state.analysisCode,
    "Analysis code",
    errors,
  );

  if (state.leaks.length === 0) {
    errors.push("At least one leakage register item is required.");
  }

  const leakCodes = new Set<string>();

  state.leaks.forEach((leak, index) => {
    const prefix = `Leak item ${index + 1}`;

    requireText(
      leak.leak_code,
      `${prefix} leak code`,
      errors,
    );

    const normalizedCode = leak.leak_code.trim();

    if (normalizedCode) {
      if (leakCodes.has(normalizedCode)) {
        errors.push(`Duplicate leak code: ${normalizedCode}.`);
      }

      leakCodes.add(normalizedCode);
    }

    requireText(
      leak.location,
      `${prefix} location`,
      errors,
    );

    requireNonNegative(
      leak.baseline_leakage_flow_nm3_per_hr,
      `${prefix} baseline leakage flow`,
      errors,
    );

    requireFraction(
      leak.expected_repair_fraction,
      `${prefix} expected repair fraction`,
      errors,
    );

    validateOptionalNonNegative(
      leak.survey_pressure_bar_g,
      `${prefix} survey pressure`,
      errors,
    );

    validateOptionalNonNegative(
      leak.estimated_repair_cost,
      `${prefix} estimated repair cost`,
      errors,
    );

    validateOptionalNonNegative(
      leak.verified_post_repair_flow_nm3_per_hr,
      `${prefix} verified post-repair flow`,
      errors,
    );
  });

  requirePositive(
    state.specificPowerKwPerNm3PerMin,
    "Specific power",
    errors,
  );

  requirePositive(
    state.annualOperatingHours,
    "Annual operating hours",
    errors,
  );

  requireNonNegative(
    state.electricityTariffPerKwh,
    "Electricity tariff",
    errors,
  );
  requireFraction(
    state.demandSavingControlFactor,
    "Demand-saving control factor",
    errors,
  );

  validateOptionalPositive(
    state.averageSystemDemandNm3PerHr,
    "Average system demand",
    errors,
  );

  return errors;
}

function optionalDecimal(
  value: string | null | undefined,
): string | null {
  if (value === null || value === undefined) {
    return null;
  }

  const trimmed = value.trim();

  return trimmed === "" ? null : trimmed;
}

function optionalText(
  value: string | null | undefined,
): string | null {
  if (value === null || value === undefined) {
    return null;
  }

  const trimmed = value.trim();

  return trimmed === "" ? null : trimmed;
}

export function buildLeakageManagementRequest(
  state: LeakageFormState,
): CompressedAirLeakageManagementRequest {
  return {
    analysis_code: state.analysisCode.trim(),

    leaks: state.leaks.map((leak) => ({
      ...leak,

      leak_code: leak.leak_code.trim(),
      location: leak.location.trim(),

      area: optionalText(leak.area),
      equipment_tag: optionalText(leak.equipment_tag),
      component_description: optionalText(
        leak.component_description,
      ),

      survey_pressure_bar_g: optionalDecimal(
        leak.survey_pressure_bar_g,
      ),

      estimated_repair_cost: optionalDecimal(
        leak.estimated_repair_cost,
      ),

      verified_post_repair_flow_nm3_per_hr: optionalDecimal(
        leak.verified_post_repair_flow_nm3_per_hr,
      ),

      survey_method_reference: optionalText(
        leak.survey_method_reference,
      ),

      notes: optionalText(leak.notes),
    })),

    specific_power_kw_per_nm3_per_min:
      state.specificPowerKwPerNm3PerMin.trim(),

    annual_operating_hours:
      state.annualOperatingHours.trim(),

    electricity_tariff_per_kwh:
      state.electricityTariffPerKwh.trim(),
    demand_saving_control_factor:
      state.demandSavingControlFactor.trim(),

    average_system_demand_nm3_per_hr: optionalDecimal(
      state.averageSystemDemandNm3PerHr,
    ),

    notes: optionalText(state.notes),
  };
}
