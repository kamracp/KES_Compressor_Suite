import type {
  CompressedAirPerformanceAnalysisRequest,
  PerformanceMeasurementInput,
} from "./performanceTypes";

import {
  MAX_PLANT_AIR_PRESSURE_BAR_G,
  pushIfAbove,
  pushIfTariffOutOfRange,
} from "../reference/inputBounds";

export type PerformanceFormState = {
  analysisCode: string;

  measurements: PerformanceMeasurementInput[];

  annualOperatingHours: string;
  electricityTariffPerKwh: string;

  ratedCapacityNm3PerHr: string;
  ratedPowerKw: string;
  referenceSpecificPowerKwPerNm3PerMin: string;

  optimizedDischargePressureBarG: string;
  powerPenaltyFractionPerBar: string;

  notes: string;
};

export function createPerformanceMeasurement(
  index = 0,
): PerformanceMeasurementInput {
  return {
    timestamp_label: `Operating Point ${index + 1}`,
    flow_nm3_per_hr: "",
    pressure_bar_g: "",
    power_kw: "",
    operating_state: "LOADED",
    load_fraction: null,
    production_state: null,
    notes: null,
  };
}

export function createInitialPerformanceFormState(): PerformanceFormState {
  return {
    analysisCode: "",
    measurements: [createPerformanceMeasurement()],
    annualOperatingHours: "",
    electricityTariffPerKwh: "0",
    ratedCapacityNm3PerHr: "",
    ratedPowerKw: "",
    referenceSpecificPowerKwPerNm3PerMin: "",
    optimizedDischargePressureBarG: "",
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

function validateOptionalPositive(
  value: string,
  label: string,
  errors: string[],
): void {
  if (!value.trim()) {
    return;
  }

  requirePositive(value, label, errors);
}

function validateOptionalNonNegative(
  value: string,
  label: string,
  errors: string[],
): void {
  if (!value.trim()) {
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

export function validatePerformanceFormState(
  state: PerformanceFormState,
): string[] {
  const errors: string[] = [];

  requireText(
    state.analysisCode,
    "Analysis code",
    errors,
  );

  if (state.measurements.length === 0) {
    errors.push("At least one operating measurement is required.");
  }

  state.measurements.forEach((measurement, index) => {
    const prefix = `Measurement ${index + 1}`;

    requireText(
      measurement.timestamp_label,
      `${prefix} timestamp or operating-period label`,
      errors,
    );

    requireNonNegative(
      measurement.flow_nm3_per_hr,
      `${prefix} flow`,
      errors,
    );

    requireNonNegative(
      measurement.pressure_bar_g,
      `${prefix} pressure`,
      errors,
    );

    requireNonNegative(
      measurement.power_kw,
      `${prefix} power`,
      errors,
    );

    validateOptionalFraction(
      measurement.load_fraction,
      `${prefix} load fraction`,
      errors,
    );
  });

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

  validateOptionalPositive(
    state.ratedCapacityNm3PerHr,
    "Rated capacity",
    errors,
  );

  validateOptionalPositive(
    state.ratedPowerKw,
    "Rated power",
    errors,
  );

  validateOptionalPositive(
    state.referenceSpecificPowerKwPerNm3PerMin,
    "Reference specific power",
    errors,
  );

  validateOptionalNonNegative(
    state.optimizedDischargePressureBarG,
    "Optimized discharge pressure",
    errors,
  );

  validateOptionalFraction(
    state.powerPenaltyFractionPerBar,
    "Power penalty fraction per bar",
    errors,
  );

  // C-7b submit-time mirrors of the backend bounds (see reference/inputBounds).
  pushIfTariffOutOfRange(state.electricityTariffPerKwh, errors);
  state.measurements.forEach((measurement, index) => {
    pushIfAbove(
      measurement.pressure_bar_g,
      MAX_PLANT_AIR_PRESSURE_BAR_G,
      `Measurement ${index + 1}: pressure cannot exceed ${MAX_PLANT_AIR_PRESSURE_BAR_G} bar g (plant-air ceiling).`,
      errors,
    );
  });

  return errors;
}

function optionalDecimal(
  value: string,
): string | null {
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

export function buildPerformanceAnalysisRequest(
  state: PerformanceFormState,
): CompressedAirPerformanceAnalysisRequest {
  return {
    analysis_code: state.analysisCode.trim(),

    measurements: state.measurements.map((measurement) => ({
      ...measurement,
      timestamp_label: measurement.timestamp_label.trim(),
      production_state: optionalText(measurement.production_state),
      notes: optionalText(measurement.notes),
    })),

    annual_operating_hours: state.annualOperatingHours.trim(),
    electricity_tariff_per_kwh:
      state.electricityTariffPerKwh.trim(),

    rated_capacity_nm3_per_hr:
      optionalDecimal(state.ratedCapacityNm3PerHr),

    rated_power_kw:
      optionalDecimal(state.ratedPowerKw),

    reference_specific_power_kw_per_nm3_per_min:
      optionalDecimal(
        state.referenceSpecificPowerKwPerNm3PerMin,
      ),

    optimized_discharge_pressure_bar_g:
      optionalDecimal(state.optimizedDischargePressureBarG),

    power_penalty_fraction_per_bar:
      optionalDecimal(state.powerPenaltyFractionPerBar),

    notes: optionalText(state.notes),
  };
}
