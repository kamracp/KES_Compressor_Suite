import type {
  AirSkidAssessmentRequest,
  DryerType,
  SkidArrangement,
  SkidComponentInput,
  SkidComponentType,
} from "./skidTypes";

import {
  MAX_PLANT_AIR_PRESSURE_BAR_G,
  pushIfAbove,
} from "../reference/inputBounds";

export type SkidFormState = {
  skidCode: string;
  arrangement: SkidArrangement;

  designFlowNm3PerHr: string;
  designPressureBarG: string;

  dryerType: DryerType;

  components: SkidComponentInput[];

  hasWetReceiver: boolean;
  hasDryReceiver: boolean;

  hasFlowMetering: boolean;
  hasPressureMonitoring: boolean;
  hasDewPointMonitoring: boolean;

  masterControlEnabled: boolean;

  description: string;
};

export function createSkidComponent(
  index: number,
  componentType: SkidComponentType = "OTHER",
): SkidComponentInput {
  return {
    component_code: `SK-${String(index + 1).padStart(2, "0")}`,
    name: "",
    component_type: componentType,
    rated_flow_nm3_per_hr: null,
    rated_pressure_bar_g: null,
    pressure_drop_bar: "0",
    quantity: 1,
    equipment_source: null,
    model: null,
    notes: null,
  };
}

export function createInitialSkidFormState(): SkidFormState {
  return {
    skidCode: "",
    arrangement: "CENTRALIZED",

    designFlowNm3PerHr: "",
    designPressureBarG: "",

    dryerType: "REFRIGERATED",

    components: [],

    hasWetReceiver: false,
    hasDryReceiver: false,

    hasFlowMetering: false,
    hasPressureMonitoring: false,
    hasDewPointMonitoring: false,

    masterControlEnabled: false,

    description: "",
  };
}

function parseNumber(value: string | number | null | undefined): number {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return Number.NaN;
  }

  return Number(value);
}

function validatePositive(
  value: string | number | null | undefined,
  label: string,
  errors: string[],
): void {
  const numericValue = parseNumber(value);

  if (
    !Number.isFinite(numericValue) ||
    numericValue <= 0
  ) {
    errors.push(`${label} must be greater than zero.`);
  }
}

function validateOptionalPositive(
  value: string | number | null | undefined,
  label: string,
  errors: string[],
): void {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return;
  }

  validatePositive(value, label, errors);
}

function validateNonNegative(
  value: string | number | null | undefined,
  label: string,
  errors: string[],
): void {
  const numericValue = parseNumber(value);

  if (
    !Number.isFinite(numericValue) ||
    numericValue < 0
  ) {
    errors.push(`${label} cannot be negative.`);
  }
}

export function validateSkidFormState(
  state: SkidFormState,
): string[] {
  const errors: string[] = [];

  if (!state.skidCode.trim()) {
    errors.push("Skid code is required.");
  }

  validatePositive(
    state.designFlowNm3PerHr,
    "Skid design flow",
    errors,
  );

  validatePositive(
    state.designPressureBarG,
    "Skid design pressure",
    errors,
  );

  if (state.components.length === 0) {
    errors.push("At least one skid component is required.");
  }

  const componentCodes = new Set<string>();

  state.components.forEach((component, index) => {
    const position = index + 1;

    if (!component.component_code.trim()) {
      errors.push(
        `Component ${position}: component code is required.`,
      );
    } else if (componentCodes.has(component.component_code)) {
      errors.push(
        `Duplicate skid component code: ${component.component_code}.`,
      );
    } else {
      componentCodes.add(component.component_code);
    }

    if (!component.name.trim()) {
      errors.push(
        `Component ${position}: component name is required.`,
      );
    }

    if (
      !Number.isInteger(component.quantity) ||
      (component.quantity ?? 0) <= 0
    ) {
      errors.push(
        `Component ${position}: quantity must be a positive integer.`,
      );
    }

    validateNonNegative(
      component.pressure_drop_bar ?? "0",
      `Component ${position}: pressure drop`,
      errors,
    );

    validateOptionalPositive(
      component.rated_flow_nm3_per_hr,
      `Component ${position}: rated flow`,
      errors,
    );

    validateOptionalPositive(
      component.rated_pressure_bar_g,
      `Component ${position}: rated pressure`,
      errors,
    );
  });

  // C-7b submit-time mirror of the backend bound (see reference/inputBounds).
  pushIfAbove(
    state.designPressureBarG,
    MAX_PLANT_AIR_PRESSURE_BAR_G,
    `Design pressure cannot exceed ${MAX_PLANT_AIR_PRESSURE_BAR_G} bar g (plant-air ceiling).`,
    errors,
  );

  return errors;
}

function optionalText(
  value: string | null | undefined,
): string | null {
  const normalized = value?.trim() ?? "";

  return normalized.length > 0 ? normalized : null;
}

function optionalDecimal(
  value: string | null | undefined,
): string | null {
  if (value === null || value === undefined || value === "") {
    return null;
  }

  return value;
}

export function buildAirSkidAssessmentRequest(
  state: SkidFormState,
): AirSkidAssessmentRequest {
  return {
    skid_code: state.skidCode.trim(),
    arrangement: state.arrangement,

    design_flow_nm3_per_hr: state.designFlowNm3PerHr,
    design_pressure_bar_g: state.designPressureBarG,

    dryer_type: state.dryerType,

    components: state.components.map((component) => ({
      component_code: component.component_code.trim(),
      name: component.name.trim(),
      component_type: component.component_type,

      rated_flow_nm3_per_hr: optionalDecimal(
        component.rated_flow_nm3_per_hr,
      ),
      rated_pressure_bar_g: optionalDecimal(
        component.rated_pressure_bar_g,
      ),
      pressure_drop_bar: component.pressure_drop_bar ?? "0",

      quantity: component.quantity ?? 1,

      equipment_source: optionalText(
        component.equipment_source,
      ),
      model: optionalText(component.model),
      notes: optionalText(component.notes),
    })),

    has_wet_receiver: state.hasWetReceiver,
    has_dry_receiver: state.hasDryReceiver,

    has_flow_metering: state.hasFlowMetering,
    has_pressure_monitoring: state.hasPressureMonitoring,
    has_dew_point_monitoring: state.hasDewPointMonitoring,

    master_control_enabled: state.masterControlEnabled,

    description: optionalText(state.description),
  };
}
