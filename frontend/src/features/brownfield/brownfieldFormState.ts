import type {
  BrownfieldSystemAuditRequest,
  CompressorMeasurementInput,
  ExistingCompressorInput,
  LeakageSurveyInput,
  SystemMeasurementInput,
} from "./brownfieldTypes";

export type BrownfieldFormState = {
  auditCode: string;

  compressors: ExistingCompressorInput[];
  compressorMeasurements: CompressorMeasurementInput[];
  systemMeasurements: SystemMeasurementInput[];

  leakageSummary: LeakageSurveyInput | null;

  electricityTariffPerKwh: string;
  annualOperatingHours: string;

  optimizedDischargePressureBarG: string;
  expectedLeakRepairFraction: string;
  powerPenaltyFractionPerBar: string;

  notes: string;
};

export function createBrownfieldCompressor(
  index = 0,
): ExistingCompressorInput {
  return {
    unit_code: `AC-${String(index + 1).padStart(2, "0")}`,
    equipment_source: null,
    manufacturer: null,
    model: null,
    technology: "ROTARY_SCREW_OIL_INJECTED",
    control_mode: "LOAD_UNLOAD",
    rated_fad_nm3_per_hr: "",
    rated_discharge_pressure_bar_g: "",
    rated_motor_power_kw: "",
    installation_year: null,
    operating_hours: null,
    available: true,
    notes: null,
  };
}

export function createBrownfieldCompressorMeasurement(
  unitCode = "",
): CompressorMeasurementInput {
  return {
    unit_code: unitCode,
    timestamp_label: "",
    operating_state: "LOADED",
    measured_flow_nm3_per_hr: "",
    measured_discharge_pressure_bar_g: "",
    measured_power_kw: "",
    load_fraction: null,
  };
}

export function createBrownfieldSystemMeasurement(): SystemMeasurementInput {
  return {
    timestamp_label: "",
    total_flow_nm3_per_hr: "",
    header_pressure_bar_g: "",
    total_power_kw: "",
    production_state: null,
    notes: null,
  };
}

export function createBrownfieldLeakageSurvey(): LeakageSurveyInput {
  return {
    measured_leakage_flow_nm3_per_hr: "",
    survey_method: "",
    estimated_repair_fraction: "0.80",
    survey_notes: null,
  };
}

export function createInitialBrownfieldFormState(): BrownfieldFormState {
  return {
    auditCode: "",

    compressors: [createBrownfieldCompressor()],
    compressorMeasurements: [],
    systemMeasurements: [createBrownfieldSystemMeasurement()],

    leakageSummary: null,

    electricityTariffPerKwh: "0",
    annualOperatingHours: "",

    optimizedDischargePressureBarG: "",
    expectedLeakRepairFraction: "0.80",
    powerPenaltyFractionPerBar: "",

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

function validateOptionalFraction(
  value: string | null | undefined,
  label: string,
  errors: string[],
): void {
  if (value === null || value === undefined || value.trim() === "") {
    return;
  }

  requireFraction(value, label, errors);
}

export function validateBrownfieldFormState(
  state: BrownfieldFormState,
): string[] {
  const errors: string[] = [];

  requireText(
    state.auditCode,
    "Audit code",
    errors,
  );

  if (state.compressors.length === 0) {
    errors.push("At least one existing compressor is required.");
  }

  state.compressors.forEach((compressor, index) => {
    const prefix = `Compressor ${index + 1}`;

    requireText(
      compressor.unit_code,
      `${prefix} unit code`,
      errors,
    );

    requirePositive(
      compressor.rated_fad_nm3_per_hr,
      `${prefix} rated FAD`,
      errors,
    );

    requireNonNegative(
      compressor.rated_discharge_pressure_bar_g,
      `${prefix} rated discharge pressure`,
      errors,
    );

    requirePositive(
      compressor.rated_motor_power_kw,
      `${prefix} rated motor power`,
      errors,
    );

    if (
      compressor.installation_year !== null &&
      compressor.installation_year !== undefined &&
      !Number.isInteger(compressor.installation_year)
    ) {
      errors.push(`${prefix} installation year must be an integer.`);
    }

    validateOptionalNonNegative(
      compressor.operating_hours,
      `${prefix} operating hours`,
      errors,
    );
  });

  const compressorCodes = new Set(
    state.compressors.map((compressor) => compressor.unit_code.trim()),
  );

  state.compressorMeasurements.forEach((measurement, index) => {
    const prefix = `Compressor measurement ${index + 1}`;

    requireText(
      measurement.unit_code,
      `${prefix} unit code`,
      errors,
    );

    requireText(
      measurement.timestamp_label,
      `${prefix} timestamp or operating-period label`,
      errors,
    );

    requireNonNegative(
      measurement.measured_flow_nm3_per_hr,
      `${prefix} measured flow`,
      errors,
    );

    requireNonNegative(
      measurement.measured_discharge_pressure_bar_g,
      `${prefix} measured discharge pressure`,
      errors,
    );

    requireNonNegative(
      measurement.measured_power_kw,
      `${prefix} measured power`,
      errors,
    );

    validateOptionalFraction(
      measurement.load_fraction,
      `${prefix} load fraction`,
      errors,
    );

    if (
      measurement.unit_code.trim() &&
      !compressorCodes.has(measurement.unit_code.trim())
    ) {
      errors.push(
        `${prefix} references a compressor that is not in the equipment inventory.`,
      );
    }
  });

  if (state.systemMeasurements.length === 0) {
    errors.push("At least one system measurement is required.");
  }

  state.systemMeasurements.forEach((measurement, index) => {
    const prefix = `System measurement ${index + 1}`;

    requireText(
      measurement.timestamp_label,
      `${prefix} timestamp or operating-period label`,
      errors,
    );

    requireNonNegative(
      measurement.total_flow_nm3_per_hr,
      `${prefix} total flow`,
      errors,
    );

    requireNonNegative(
      measurement.header_pressure_bar_g,
      `${prefix} header pressure`,
      errors,
    );

    requireNonNegative(
      measurement.total_power_kw,
      `${prefix} total power`,
      errors,
    );
  });

  if (state.leakageSummary) {
    requireNonNegative(
      state.leakageSummary.measured_leakage_flow_nm3_per_hr,
      "Measured leakage flow",
      errors,
    );

    requireText(
      state.leakageSummary.survey_method,
      "Leakage survey method",
      errors,
    );

    requireFraction(
      state.leakageSummary.estimated_repair_fraction,
      "Estimated leakage repair fraction",
      errors,
    );
  }

  requireNonNegative(
    state.electricityTariffPerKwh,
    "Electricity tariff",
    errors,
  );

  requirePositive(
    state.annualOperatingHours,
    "Annual operating hours",
    errors,
  );

  if (state.optimizedDischargePressureBarG.trim()) {
    requireNonNegative(
      state.optimizedDischargePressureBarG,
      "Optimized discharge pressure",
      errors,
    );
  }

  requireFraction(
    state.expectedLeakRepairFraction,
    "Expected leak repair fraction",
    errors,
  );

  validateOptionalFraction(
    state.powerPenaltyFractionPerBar,
    "Power penalty fraction per bar",
    errors,
  );

  return errors;
}

function nullableText(value: string | null | undefined): string | null {
  if (value === null || value === undefined) {
    return null;
  }

  const trimmed = value.trim();

  return trimmed ? trimmed : null;
}

export function buildBrownfieldAuditRequest(
  state: BrownfieldFormState,
  projectId: number,
): BrownfieldSystemAuditRequest {
  return {
    audit_code: state.auditCode.trim(),
    project_id: projectId,

    compressors: state.compressors.map((compressor) => ({
      ...compressor,
      unit_code: compressor.unit_code.trim(),
      equipment_source: nullableText(compressor.equipment_source),
      manufacturer: null,
      model: nullableText(compressor.model),
      notes: nullableText(compressor.notes),
    })),

    compressor_measurements: state.compressorMeasurements.map(
      (measurement) => ({
        ...measurement,
        unit_code: measurement.unit_code.trim(),
        timestamp_label: measurement.timestamp_label.trim(),
      }),
    ),

    system_measurements: state.systemMeasurements.map(
      (measurement) => ({
        ...measurement,
        timestamp_label: measurement.timestamp_label.trim(),
        production_state: nullableText(measurement.production_state),
        notes: nullableText(measurement.notes),
      }),
    ),

    leakage_summary: state.leakageSummary
      ? {
          ...state.leakageSummary,
          survey_method: state.leakageSummary.survey_method.trim(),
          survey_notes: nullableText(
            state.leakageSummary.survey_notes,
          ),
        }
      : null,

    electricity_tariff_per_kwh:
      state.electricityTariffPerKwh,

    annual_operating_hours:
      state.annualOperatingHours,

    optimized_discharge_pressure_bar_g:
      state.optimizedDischargePressureBarG.trim()
        ? state.optimizedDischargePressureBarG
        : null,

    expected_leak_repair_fraction:
      state.expectedLeakRepairFraction,

    power_penalty_fraction_per_bar:
      state.powerPenaltyFractionPerBar.trim() === ""
        ? null
        : state.powerPenaltyFractionPerBar,

    notes: nullableText(state.notes),
  };
}
