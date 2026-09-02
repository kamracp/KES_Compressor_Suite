import type {
  AftercoolerConfigurationInput,
  AlliedEquipmentAnalysisRequest,
  CondensateDrainConfigurationInput,
  FilterStageConfigurationInput,
  MoistureSeparatorConfigurationInput,
  ReceiverConfigurationInput,
  TreatmentConfigurationInput,
} from "./alliedTypes";

import {
  MAX_PLANT_AIR_PRESSURE_BAR_G,
  pushIfAbove,
} from "../reference/inputBounds";

export type AlliedFormState = {
  analysisCode: string;

  receiver: ReceiverConfigurationInput | null;
  treatment: TreatmentConfigurationInput | null;
  aftercooler: AftercoolerConfigurationInput | null;
  moistureSeparator: MoistureSeparatorConfigurationInput | null;

  filterStages: FilterStageConfigurationInput[];
  condensateDrains: CondensateDrainConfigurationInput[];

  notes: string;
};


export function createReceiverConfiguration(): ReceiverConfigurationInput {
  return {
    sizing_input: {
      peak_demand_nm3_per_hr: "",
      available_compressor_flow_nm3_per_hr: "",
      event_duration_seconds: "30",
      receiver_high_pressure_bar_g: "7",
      receiver_low_pressure_bar_g: "6.5",
      reserve_fraction: "0.20",
    },
    selected_receiver_volume_m3: null,
    receiver_quantity: 1,
    design_pressure_bar_g: null,
    redundancy_philosophy: "NONE",
    equipment_reference: null,
    notes: null,
  };
}


export function createTreatmentConfiguration(): TreatmentConfigurationInput {
  return {
    sizing_input: {
      required_delivered_flow_nm3_per_hr: "",
      required_air_quality: "GENERAL_PLANT_AIR",
      dryer_type: "REFRIGERATED",
      dryer_correction_factor: "1",
      dryer_purge_fraction: "0",
      prefilter_pressure_drop_bar: "0",
      afterfilter_pressure_drop_bar: "0",
      dryer_pressure_drop_bar: "0",
      treatment_capacity_margin_fraction: "0.10",
    },
    selected_treatment_capacity_nm3_per_hr: null,
    installed_unit_count: 1,
    duty_unit_count: 1,
    redundancy_philosophy: "NONE",
    equipment_reference: null,
    notes: null,
  };
}


export function createAftercoolerConfiguration(): AftercoolerConfigurationInput {
  return {
    aftercooler_type: "AIR_COOLED",
    selected_flow_capacity_nm3_per_hr: null,
    pressure_drop_bar: "0",
    inlet_temperature_c: null,
    outlet_temperature_c: null,
    equipment_reference: null,
    notes: null,
  };
}


export function createMoistureSeparatorConfiguration(): MoistureSeparatorConfigurationInput {
  return {
    separator_type: "CYCLONIC",
    selected_flow_capacity_nm3_per_hr: null,
    pressure_drop_bar: "0",
    equipment_reference: null,
    notes: null,
  };
}


export function createFilterStage(
  index = 0,
): FilterStageConfigurationInput {
  return {
    stage_code: `F-${String(index + 1).padStart(2, "0")}`,
    stage_type: "COALESCING",
    selected_flow_capacity_nm3_per_hr: null,
    pressure_drop_bar: "0",
    equipment_reference: null,
    notes: null,
  };
}


export function createCondensateDrain(
  index = 0,
): CondensateDrainConfigurationInput {
  return {
    drain_code: `D-${String(index + 1).padStart(2, "0")}`,
    location: "",
    drain_type: "ZERO_LOSS",
    selected_condensate_capacity_l_per_hr: null,
    equipment_reference: null,
    notes: null,
  };
}


export function createInitialAlliedFormState(): AlliedFormState {
  return {
    analysisCode: "",
    receiver: null,
    treatment: null,
    aftercooler: null,
    moistureSeparator: null,
    filterStages: [],
    condensateDrains: [],
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


function requirePurgeFraction(
  value: string,
  label: string,
  errors: string[],
): void {
  const numericValue = parseNumber(value);

  if (
    value.trim() === "" ||
    !Number.isFinite(numericValue) ||
    numericValue < 0 ||
    numericValue >= 1
  ) {
    errors.push(`${label} must be zero or greater and less than one.`);
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


function validateOptionalNumber(
  value: string | null | undefined,
  label: string,
  errors: string[],
): void {
  if (value === null || value === undefined || value.trim() === "") {
    return;
  }

  if (!Number.isFinite(parseNumber(value))) {
    errors.push(`${label} must be a valid number.`);
  }
}


function validatePositiveInteger(
  value: number | undefined,
  label: string,
  errors: string[],
): void {
  if (
    value === undefined ||
    !Number.isInteger(value) ||
    value <= 0
  ) {
    errors.push(`${label} must be a positive whole number.`);
  }
}


export function validateAlliedFormState(
  state: AlliedFormState,
): string[] {
  const errors: string[] = [];

  requireText(state.analysisCode, "Analysis code", errors);

  const hasEquipment =
    state.receiver !== null ||
    state.treatment !== null ||
    state.aftercooler !== null ||
    state.moistureSeparator !== null ||
    state.filterStages.length > 0 ||
    state.condensateDrains.length > 0;

  if (!hasEquipment) {
    errors.push("At least one allied-equipment item is required.");
  }

  if (state.receiver) {
    const receiver = state.receiver;
    const sizing = receiver.sizing_input;

    requireNonNegative(
      sizing.peak_demand_nm3_per_hr,
      "Receiver peak demand",
      errors,
    );

    requireNonNegative(
      sizing.available_compressor_flow_nm3_per_hr,
      "Available compressor flow",
      errors,
    );

    requirePositive(
      sizing.event_duration_seconds,
      "Receiver event duration",
      errors,
    );

    requirePositive(
      sizing.receiver_high_pressure_bar_g,
      "Receiver high pressure",
      errors,
    );

    requireNonNegative(
      sizing.receiver_low_pressure_bar_g,
      "Receiver low pressure",
      errors,
    );

    requireFraction(
      sizing.reserve_fraction ?? "0",
      "Receiver reserve fraction",
      errors,
    );

    const highPressure = parseNumber(
      sizing.receiver_high_pressure_bar_g,
    );
    const lowPressure = parseNumber(
      sizing.receiver_low_pressure_bar_g,
    );

    if (
      Number.isFinite(highPressure) &&
      Number.isFinite(lowPressure) &&
      highPressure <= lowPressure
    ) {
      errors.push(
        "Receiver high pressure must be greater than receiver low pressure.",
      );
    }

    validateOptionalPositive(
      receiver.selected_receiver_volume_m3,
      "Selected receiver volume",
      errors,
    );

    validateOptionalPositive(
      receiver.design_pressure_bar_g,
      "Receiver design pressure",
      errors,
    );

    validatePositiveInteger(
      receiver.receiver_quantity,
      "Receiver quantity",
      errors,
    );
  }

  if (state.treatment) {
    const treatment = state.treatment;
    const sizing = treatment.sizing_input;

    requirePositive(
      sizing.required_delivered_flow_nm3_per_hr,
      "Required delivered flow",
      errors,
    );

    requirePositive(
      sizing.dryer_correction_factor ?? "1",
      "Dryer correction factor",
      errors,
    );

    requirePurgeFraction(
      sizing.dryer_purge_fraction ?? "0",
      "Dryer purge fraction",
      errors,
    );

    requireNonNegative(
      sizing.prefilter_pressure_drop_bar ?? "0",
      "Prefilter pressure drop",
      errors,
    );

    requireNonNegative(
      sizing.afterfilter_pressure_drop_bar ?? "0",
      "Afterfilter pressure drop",
      errors,
    );

    requireNonNegative(
      sizing.dryer_pressure_drop_bar ?? "0",
      "Dryer pressure drop",
      errors,
    );

    requireFraction(
      sizing.treatment_capacity_margin_fraction ?? "0",
      "Treatment capacity margin",
      errors,
    );

    validateOptionalPositive(
      treatment.selected_treatment_capacity_nm3_per_hr,
      "Selected treatment capacity",
      errors,
    );

    validatePositiveInteger(
      treatment.installed_unit_count,
      "Installed treatment unit count",
      errors,
    );

    validatePositiveInteger(
      treatment.duty_unit_count,
      "Duty treatment unit count",
      errors,
    );

    if (
      treatment.installed_unit_count !== undefined &&
      treatment.duty_unit_count !== undefined &&
      treatment.duty_unit_count > treatment.installed_unit_count
    ) {
      errors.push(
        "Duty treatment unit count cannot exceed installed unit count.",
      );
    }
  }

  const flowRatedEquipmentPresent =
    state.aftercooler !== null ||
    state.moistureSeparator !== null ||
    state.filterStages.length > 0;

  if (
    flowRatedEquipmentPresent &&
    state.receiver === null &&
    state.treatment === null
  ) {
    errors.push(
      "Receiver or treatment sizing basis is required for flow-rated allied equipment.",
    );
  }

  if (state.aftercooler) {
    validateOptionalPositive(
      state.aftercooler.selected_flow_capacity_nm3_per_hr,
      "Selected aftercooler flow capacity",
      errors,
    );

    requireNonNegative(
      state.aftercooler.pressure_drop_bar ?? "0",
      "Aftercooler pressure drop",
      errors,
    );

    validateOptionalNumber(
      state.aftercooler.inlet_temperature_c,
      "Aftercooler inlet temperature",
      errors,
    );

    validateOptionalNumber(
      state.aftercooler.outlet_temperature_c,
      "Aftercooler outlet temperature",
      errors,
    );
  }

  if (state.moistureSeparator) {
    validateOptionalPositive(
      state.moistureSeparator.selected_flow_capacity_nm3_per_hr,
      "Selected moisture separator flow capacity",
      errors,
    );

    requireNonNegative(
      state.moistureSeparator.pressure_drop_bar ?? "0",
      "Moisture separator pressure drop",
      errors,
    );
  }

  const filterCodes = new Set<string>();

  state.filterStages.forEach((stage, index) => {
    const prefix = `Filter stage ${index + 1}`;

    requireText(stage.stage_code, `${prefix} code`, errors);

    const normalizedCode = stage.stage_code.trim().toLowerCase();

    if (normalizedCode) {
      if (filterCodes.has(normalizedCode)) {
        errors.push(
          `Duplicate filter stage code: ${stage.stage_code.trim()}.`,
        );
      }

      filterCodes.add(normalizedCode);
    }

    validateOptionalPositive(
      stage.selected_flow_capacity_nm3_per_hr,
      `${prefix} selected flow capacity`,
      errors,
    );

    requireNonNegative(
      stage.pressure_drop_bar ?? "0",
      `${prefix} pressure drop`,
      errors,
    );
  });

  const drainCodes = new Set<string>();

  state.condensateDrains.forEach((drain, index) => {
    const prefix = `Condensate drain ${index + 1}`;

    requireText(drain.drain_code, `${prefix} code`, errors);
    requireText(drain.location, `${prefix} location`, errors);

    const normalizedCode = drain.drain_code.trim().toLowerCase();

    if (normalizedCode) {
      if (drainCodes.has(normalizedCode)) {
        errors.push(
          `Duplicate condensate drain code: ${drain.drain_code.trim()}.`,
        );
      }

      drainCodes.add(normalizedCode);
    }

    validateOptionalPositive(
      drain.selected_condensate_capacity_l_per_hr,
      `${prefix} selected condensate capacity`,
      errors,
    );
  });

  // C-7b submit-time mirrors of the backend bounds (see reference/inputBounds).
  if (state.receiver) {
    const plantAir = `cannot exceed ${MAX_PLANT_AIR_PRESSURE_BAR_G} bar g (plant-air ceiling).`;
    pushIfAbove(
      state.receiver.sizing_input.receiver_high_pressure_bar_g,
      MAX_PLANT_AIR_PRESSURE_BAR_G,
      `Receiver high pressure ${plantAir}`,
      errors,
    );
    pushIfAbove(
      state.receiver.sizing_input.receiver_low_pressure_bar_g,
      MAX_PLANT_AIR_PRESSURE_BAR_G,
      `Receiver low pressure ${plantAir}`,
      errors,
    );
  }

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


export function buildAlliedEquipmentAnalysisRequest(
  state: AlliedFormState,
): AlliedEquipmentAnalysisRequest {
  return {
    analysis_code: state.analysisCode.trim(),

    receiver: state.receiver
      ? {
          sizing_input: {
            peak_demand_nm3_per_hr:
              state.receiver.sizing_input.peak_demand_nm3_per_hr.trim(),

            available_compressor_flow_nm3_per_hr:
              state.receiver.sizing_input.available_compressor_flow_nm3_per_hr.trim(),

            event_duration_seconds:
              state.receiver.sizing_input.event_duration_seconds.trim(),

            receiver_high_pressure_bar_g:
              state.receiver.sizing_input.receiver_high_pressure_bar_g.trim(),

            receiver_low_pressure_bar_g:
              state.receiver.sizing_input.receiver_low_pressure_bar_g.trim(),

            reserve_fraction:
              state.receiver.sizing_input.reserve_fraction?.trim() ?? "0",
          },

          selected_receiver_volume_m3: optionalDecimal(
            state.receiver.selected_receiver_volume_m3,
          ),

          receiver_quantity:
            state.receiver.receiver_quantity ?? 1,

          design_pressure_bar_g: optionalDecimal(
            state.receiver.design_pressure_bar_g,
          ),

          redundancy_philosophy:
            state.receiver.redundancy_philosophy ?? "NONE",

          equipment_reference: optionalText(
            state.receiver.equipment_reference,
          ),

          notes: optionalText(state.receiver.notes),
        }
      : null,

    treatment: state.treatment
      ? {
          sizing_input: {
            required_delivered_flow_nm3_per_hr:
              state.treatment.sizing_input.required_delivered_flow_nm3_per_hr.trim(),

            required_air_quality:
              state.treatment.sizing_input.required_air_quality,

            dryer_type:
              state.treatment.sizing_input.dryer_type,

            dryer_correction_factor:
              state.treatment.sizing_input.dryer_correction_factor?.trim() ?? "1",

            dryer_purge_fraction:
              state.treatment.sizing_input.dryer_purge_fraction?.trim() ?? "0",

            prefilter_pressure_drop_bar:
              state.treatment.sizing_input.prefilter_pressure_drop_bar?.trim() ?? "0",

            afterfilter_pressure_drop_bar:
              state.treatment.sizing_input.afterfilter_pressure_drop_bar?.trim() ?? "0",

            dryer_pressure_drop_bar:
              state.treatment.sizing_input.dryer_pressure_drop_bar?.trim() ?? "0",

            treatment_capacity_margin_fraction:
              state.treatment.sizing_input.treatment_capacity_margin_fraction?.trim() ??
              "0",
          },

          selected_treatment_capacity_nm3_per_hr: optionalDecimal(
            state.treatment.selected_treatment_capacity_nm3_per_hr,
          ),

          installed_unit_count:
            state.treatment.installed_unit_count ?? 1,

          duty_unit_count:
            state.treatment.duty_unit_count ?? 1,

          redundancy_philosophy:
            state.treatment.redundancy_philosophy ?? "NONE",

          equipment_reference: optionalText(
            state.treatment.equipment_reference,
          ),

          notes: optionalText(state.treatment.notes),
        }
      : null,

    aftercooler: state.aftercooler
      ? {
          aftercooler_type:
            state.aftercooler.aftercooler_type,

          selected_flow_capacity_nm3_per_hr: optionalDecimal(
            state.aftercooler.selected_flow_capacity_nm3_per_hr,
          ),

          pressure_drop_bar:
            state.aftercooler.pressure_drop_bar?.trim() ?? "0",

          inlet_temperature_c: optionalDecimal(
            state.aftercooler.inlet_temperature_c,
          ),

          outlet_temperature_c: optionalDecimal(
            state.aftercooler.outlet_temperature_c,
          ),

          equipment_reference: optionalText(
            state.aftercooler.equipment_reference,
          ),

          notes: optionalText(state.aftercooler.notes),
        }
      : null,

    moisture_separator: state.moistureSeparator
      ? {
          separator_type:
            state.moistureSeparator.separator_type,

          selected_flow_capacity_nm3_per_hr: optionalDecimal(
            state.moistureSeparator.selected_flow_capacity_nm3_per_hr,
          ),

          pressure_drop_bar:
            state.moistureSeparator.pressure_drop_bar?.trim() ?? "0",

          equipment_reference: optionalText(
            state.moistureSeparator.equipment_reference,
          ),

          notes: optionalText(
            state.moistureSeparator.notes,
          ),
        }
      : null,

    filter_stages: state.filterStages.map((stage) => ({
      stage_code: stage.stage_code.trim(),
      stage_type: stage.stage_type,

      selected_flow_capacity_nm3_per_hr: optionalDecimal(
        stage.selected_flow_capacity_nm3_per_hr,
      ),

      pressure_drop_bar:
        stage.pressure_drop_bar?.trim() ?? "0",

      equipment_reference: optionalText(
        stage.equipment_reference,
      ),

      notes: optionalText(stage.notes),
    })),

    condensate_drains: state.condensateDrains.map((drain) => ({
      drain_code: drain.drain_code.trim(),
      location: drain.location.trim(),
      drain_type: drain.drain_type,

      selected_condensate_capacity_l_per_hr: optionalDecimal(
        drain.selected_condensate_capacity_l_per_hr,
      ),

      equipment_reference: optionalText(
        drain.equipment_reference,
      ),

      notes: optionalText(drain.notes),
    })),

    notes: optionalText(state.notes),
  };
}
