import type {
  AuditOperatingState,
  BrownfieldOpportunityCategory,
  BrownfieldOpportunityPriority,
  CompressorControlMode,
  CompressorTechnology,
} from "./brownfieldTypes";

type Option<T extends string> = {
  value: T;
  label: string;
};

export const compressorTechnologyOptions: Option<CompressorTechnology>[] = [
  {
    value: "ROTARY_SCREW_OIL_INJECTED",
    label: "Rotary Screw - Oil Injected",
  },
  {
    value: "ROTARY_SCREW_OIL_FREE",
    label: "Rotary Screw - Oil Free",
  },
  {
    value: "RECIPROCATING",
    label: "Reciprocating",
  },
  {
    value: "CENTRIFUGAL",
    label: "Centrifugal",
  },
  {
    value: "SCROLL",
    label: "Scroll",
  },
];

export const compressorControlModeOptions: Option<CompressorControlMode>[] = [
  {
    value: "FIXED_SPEED",
    label: "Fixed Speed",
  },
  {
    value: "VSD",
    label: "Variable Speed Drive",
  },
  {
    value: "LOAD_UNLOAD",
    label: "Load / Unload",
  },
  {
    value: "MODULATION",
    label: "Modulation",
  },
  {
    value: "INLET_GUIDE_VANE",
    label: "Inlet Guide Vane",
  },
];

export const auditOperatingStateOptions: Option<AuditOperatingState>[] = [
  {
    value: "LOADED",
    label: "Loaded",
  },
  {
    value: "UNLOADED",
    label: "Unloaded",
  },
  {
    value: "PART_LOAD",
    label: "Part Load",
  },
  {
    value: "STOPPED",
    label: "Stopped",
  },
];

export const opportunityCategoryLabels: Record<
  BrownfieldOpportunityCategory,
  string
> = {
  LEAKAGE: "Leakage",
  UNLOADED_RUNNING: "Unloaded Running",
  PRESSURE: "Pressure",
  CAPACITY: "Capacity",
  UTILIZATION: "Utilization",
  CONDENSATE_DRAIN: "Condensate Drain",
  FILTER_EFFICIENCY: "Filter Efficiency",
  POWER_FACTOR: "Power Factor",
};

export const opportunityPriorityLabels: Record<
  BrownfieldOpportunityPriority,
  string
> = {
  HIGH: "High",
  MEDIUM: "Medium",
  LOW: "Low",
};
