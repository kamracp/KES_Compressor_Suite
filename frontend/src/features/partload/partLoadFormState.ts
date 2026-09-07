import {
  MAX_ASSET_FAD_NM3_PER_HR,
  MAX_ASSET_MOTOR_KW,
  MAX_CENTRIFUGAL_TURNDOWN_FRACTION,
  MAX_CENTRIFUGAL_UNLOAD_POWER_FRACTION,
  MAX_FIXED_SPEED_UNLOAD_POWER_FRACTION,
  MAX_MODULATION_FLOOR_CAPACITY_FRACTION,
  MIN_CENTRIFUGAL_POWER_FRACTION_AT_TURNDOWN,
  MIN_CENTRIFUGAL_TURNDOWN_FRACTION,
  MIN_CENTRIFUGAL_UNLOAD_POWER_FRACTION,
  MIN_FIXED_SPEED_UNLOAD_POWER_FRACTION,
  MIN_MODULATION_FLOOR_CAPACITY_FRACTION,
  MIN_VSD_MINIMUM_FLOW_FRACTION,
  pushIfAbove,
  pushIfTariffOutOfRange,
} from "../reference/inputBounds";
import type {
  BelowTurndownMode,
  PartLoadComparisonRequest,
  PartLoadMode,
} from "./partLoadTypes";

export type CandidateFormState = {
  id: string;
  label: string;
  mode: PartLoadMode;
  unloadPowerFraction: string;
  modulationFloorCapacityFraction: string;
  minimumFlowFraction: string;
  minimumFlowPowerFraction: string;
  turndownFlowFraction: string;
  powerFractionAtTurndown: string;
  belowTurndown: BelowTurndownMode;
};

export type LoadDurationRowState = {
  id: string;
  capacityFraction: string;
  hours: string;
};

export type PartLoadFormState = {
  analysisCode: string;
  ratedFadNm3PerHr: string;
  ratedPowerKw: string;
  electricityTariffPerKwh: string;
  capacityFractionsText: string; // comma separated, e.g. "0.25, 0.5, 0.75, 1"
  candidates: CandidateFormState[];
  loadDuration: LoadDurationRowState[];
};

export const PART_LOAD_MODE_OPTIONS: { value: PartLoadMode; label: string }[] = [
  { value: "LOAD_UNLOAD", label: "Load / unload" },
  { value: "MODULATION", label: "Inlet modulation" },
  { value: "VARIABLE_DISPLACEMENT", label: "Variable displacement" },
  { value: "VARIABLE_SPEED", label: "Variable speed (VSD)" },
  { value: "INLET_GUIDE_VANE", label: "Inlet guide vane (centrifugal)" },
];

let nextId = 1;

function newId(prefix: string): string {
  nextId += 1;
  return `${prefix}-${nextId}`;
}

export function createCandidate(mode: PartLoadMode = "LOAD_UNLOAD"): CandidateFormState {
  const option = PART_LOAD_MODE_OPTIONS.find((item) => item.value === mode);

  return {
    id: newId("cand"),
    label: option ? option.label : mode,
    mode,
    unloadPowerFraction: mode === "INLET_GUIDE_VANE" ? "" : "0.25",
    modulationFloorCapacityFraction: "",
    minimumFlowFraction: "",
    minimumFlowPowerFraction: "",
    turndownFlowFraction: "",
    powerFractionAtTurndown: "",
    belowTurndown: "BLOW_OFF",
  };
}

export function createLoadDurationRow(): LoadDurationRowState {
  return { id: newId("ld"), capacityFraction: "", hours: "" };
}

export function createInitialPartLoadFormState(): PartLoadFormState {
  return {
    analysisCode: "",
    ratedFadNm3PerHr: "",
    ratedPowerKw: "",
    electricityTariffPerKwh: "",
    capacityFractionsText: "0.25, 0.5, 0.75, 1",
    candidates: [createCandidate("LOAD_UNLOAD"), createCandidate("MODULATION")],
    loadDuration: [],
  };
}

function parseNumber(value: string): number {
  return Number(value.trim());
}

export function parseCapacityFractions(text: string): string[] {
  return text
    .split(/[,\s]+/)
    .map((item) => item.trim())
    .filter((item) => item !== "");
}

function inRange(value: string, low: number, high: number): boolean {
  const parsed = parseNumber(value);
  return value.trim() !== "" && Number.isFinite(parsed) && parsed >= low && parsed <= high;
}

export function validatePartLoadFormState(state: PartLoadFormState): string[] {
  const errors: string[] = [];

  if (!state.analysisCode.trim()) {
    errors.push("Analysis code is required.");
  }
  if (!(parseNumber(state.ratedFadNm3PerHr) > 0)) {
    errors.push("Rated FAD must be greater than zero.");
  }
  pushIfAbove(state.ratedFadNm3PerHr, MAX_ASSET_FAD_NM3_PER_HR, "Rated FAD", errors);
  if (!(parseNumber(state.ratedPowerKw) > 0)) {
    errors.push("Rated power must be greater than zero.");
  }
  pushIfAbove(state.ratedPowerKw, MAX_ASSET_MOTOR_KW, "Rated power", errors);
  if (state.electricityTariffPerKwh.trim()) {
    pushIfTariffOutOfRange(state.electricityTariffPerKwh, errors);
  }

  const fractions = parseCapacityFractions(state.capacityFractionsText);
  if (fractions.length === 0) {
    errors.push("At least one capacity fraction is required.");
  }
  if (fractions.some((item) => !inRange(item, 0, 1))) {
    errors.push("Capacity fractions must be numbers within 0 and 1.");
  }
  if (new Set(fractions.map((item) => parseNumber(item))).size !== fractions.length) {
    errors.push("Capacity fractions must be unique.");
  }

  if (state.candidates.length === 0) {
    errors.push("At least one control-mode candidate is required.");
  }
  const labels = state.candidates.map((item) => item.label.trim());
  if (new Set(labels).size !== labels.length) {
    errors.push("Candidate labels must be unique.");
  }

  state.candidates.forEach((candidate, index) => {
    const prefix = `Candidate ${index + 1}`;
    if (!candidate.label.trim()) {
      errors.push(`${prefix} label is required.`);
    }

    const isIgv = candidate.mode === "INLET_GUIDE_VANE";
    if (isIgv) {
      if (
        !inRange(
          candidate.turndownFlowFraction,
          MIN_CENTRIFUGAL_TURNDOWN_FRACTION,
          MAX_CENTRIFUGAL_TURNDOWN_FRACTION,
        )
      ) {
        errors.push(
          `${prefix} turndown fraction must be ${MIN_CENTRIFUGAL_TURNDOWN_FRACTION}-${MAX_CENTRIFUGAL_TURNDOWN_FRACTION} of rated FAD (CAGI).`,
        );
      }
      if (
        !inRange(candidate.powerFractionAtTurndown, MIN_CENTRIFUGAL_POWER_FRACTION_AT_TURNDOWN, 1)
      ) {
        errors.push(
          `${prefix} power at turndown must be ${MIN_CENTRIFUGAL_POWER_FRACTION_AT_TURNDOWN}-1 of rated power.`,
        );
      }
      const needsUnload = candidate.belowTurndown === "UNLOAD";
      if (needsUnload || candidate.unloadPowerFraction.trim()) {
        if (
          !inRange(
            candidate.unloadPowerFraction,
            MIN_CENTRIFUGAL_UNLOAD_POWER_FRACTION,
            MAX_CENTRIFUGAL_UNLOAD_POWER_FRACTION,
          )
        ) {
          errors.push(
            `${prefix} centrifugal off-loaded power must be ${MIN_CENTRIFUGAL_UNLOAD_POWER_FRACTION}-${MAX_CENTRIFUGAL_UNLOAD_POWER_FRACTION} (Atlas Copco CAM ~0.20).`,
          );
        }
      }
    } else if (
      !inRange(
        candidate.unloadPowerFraction,
        MIN_FIXED_SPEED_UNLOAD_POWER_FRACTION,
        MAX_FIXED_SPEED_UNLOAD_POWER_FRACTION,
      )
    ) {
      errors.push(
        `${prefix} unload power fraction must be ${MIN_FIXED_SPEED_UNLOAD_POWER_FRACTION}-${MAX_FIXED_SPEED_UNLOAD_POWER_FRACTION} (DOE CAC Sourcebook).`,
      );
    }

    if (candidate.mode === "MODULATION" && candidate.modulationFloorCapacityFraction.trim()) {
      if (
        !inRange(
          candidate.modulationFloorCapacityFraction,
          MIN_MODULATION_FLOOR_CAPACITY_FRACTION,
          MAX_MODULATION_FLOOR_CAPACITY_FRACTION,
        )
      ) {
        errors.push(
          `${prefix} modulation floor must be ${MIN_MODULATION_FLOOR_CAPACITY_FRACTION}-${MAX_MODULATION_FLOOR_CAPACITY_FRACTION} of capacity (DOE default 0.40).`,
        );
      }
    }

    if (candidate.mode === "VARIABLE_SPEED") {
      if (!inRange(candidate.minimumFlowFraction, MIN_VSD_MINIMUM_FLOW_FRACTION, 1)) {
        errors.push(
          `${prefix} minimum flow fraction must be ${MIN_VSD_MINIMUM_FLOW_FRACTION}-1 for a VSD (turndown <= 86 %).`,
        );
      }
      const minimumFlowPower = parseNumber(candidate.minimumFlowPowerFraction);
      if (!(minimumFlowPower > 0 && minimumFlowPower <= 1)) {
        errors.push(`${prefix} power at minimum flow must be above 0 and at most 1.`);
      }
    }
  });

  state.loadDuration.forEach((row, index) => {
    const prefix = `Load-duration row ${index + 1}`;
    if (!inRange(row.capacityFraction, 0, 1)) {
      errors.push(`${prefix} capacity fraction must be within 0 and 1.`);
    }
    if (!(parseNumber(row.hours) > 0)) {
      errors.push(`${prefix} hours must be greater than zero.`);
    }
  });
  const totalHours = state.loadDuration.reduce((sum, row) => sum + parseNumber(row.hours), 0);
  if (totalHours > 8784) {
    errors.push("Load-duration hours exceed a calendar year (8784 h).");
  }

  return errors;
}

function nullable(value: string): string | null {
  return value.trim() === "" ? null : value.trim();
}

export function buildPartLoadComparisonRequest(
  state: PartLoadFormState,
): PartLoadComparisonRequest {
  return {
    analysis_code: state.analysisCode.trim(),
    rated_fad_nm3_per_hr: state.ratedFadNm3PerHr.trim(),
    rated_power_kw: state.ratedPowerKw.trim(),
    candidates: state.candidates.map((candidate) => {
      const isIgv = candidate.mode === "INLET_GUIDE_VANE";
      const isVsd = candidate.mode === "VARIABLE_SPEED";
      const isModulation = candidate.mode === "MODULATION";

      return {
        label: candidate.label.trim(),
        mode: candidate.mode,
        unload_power_fraction: nullable(candidate.unloadPowerFraction),
        modulation_floor_capacity_fraction: isModulation
          ? nullable(candidate.modulationFloorCapacityFraction)
          : null,
        minimum_flow_fraction: isVsd ? nullable(candidate.minimumFlowFraction) : null,
        minimum_flow_power_fraction: isVsd ? nullable(candidate.minimumFlowPowerFraction) : null,
        turndown_flow_fraction: isIgv ? nullable(candidate.turndownFlowFraction) : null,
        power_fraction_at_turndown: isIgv ? nullable(candidate.powerFractionAtTurndown) : null,
        below_turndown: isIgv ? candidate.belowTurndown : null,
      };
    }),
    capacity_fractions: parseCapacityFractions(state.capacityFractionsText),
    load_duration: state.loadDuration.map((row) => ({
      capacity_fraction: row.capacityFraction.trim(),
      hours: row.hours.trim(),
    })),
    electricity_tariff_per_kwh: nullable(state.electricityTariffPerKwh),
  };
}
