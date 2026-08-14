import type {
  AirConsumptionBasis,
  AirConsumerCategory,
  AirQualityClass,
  CompressorControlMode,
  CompressorDutyRole,
  CompressorTechnology,
  ConsumerCriticality,
  DryerType,
  RedundancyPhilosophy,
} from "./greenfieldTypes";

export type SelectOption<T extends string> = {
  value: T;
  label: string;
};

export const airConsumerCategoryOptions: SelectOption<AirConsumerCategory>[] = [
  { value: "PRODUCTION_MACHINE", label: "Production Machine" },
  { value: "PNEUMATIC_CYLINDER", label: "Pneumatic Cylinder" },
  { value: "AIR_TOOL", label: "Air Tool" },
  { value: "BAG_FILTER", label: "Bag Filter" },
  { value: "PNEUMATIC_CONVEYING", label: "Pneumatic Conveying" },
  { value: "PACKAGING_MACHINE", label: "Packaging Machine" },
  { value: "CONTROL_VALVE", label: "Control Valve" },
  { value: "INSTRUMENT_AIR", label: "Instrument Air" },
  { value: "PROCESS_AIR", label: "Process Air" },
  { value: "AIR_CLEANING", label: "Air Cleaning" },
  { value: "OTHER", label: "Other" },
];

export const airConsumptionBasisOptions: SelectOption<AirConsumptionBasis>[] = [
  { value: "CONTINUOUS_FLOW", label: "Continuous Flow" },
  { value: "FLOW_WHEN_OPERATING", label: "Flow When Operating" },
  { value: "PER_CYCLE", label: "Per Cycle" },
];

export const airQualityClassOptions: SelectOption<AirQualityClass>[] = [
  { value: "GENERAL_PLANT_AIR", label: "General Plant Air" },
  { value: "INSTRUMENT_AIR", label: "Instrument Air" },
  { value: "OIL_FREE_PROCESS_AIR", label: "Oil-Free Process Air" },
  { value: "CRITICAL_PROCESS_AIR", label: "Critical Process Air" },
];

export const consumerCriticalityOptions: SelectOption<ConsumerCriticality>[] = [
  { value: "CRITICAL", label: "Critical" },
  { value: "ESSENTIAL", label: "Essential" },
  { value: "NORMAL", label: "Normal" },
  { value: "NON_CRITICAL", label: "Non-Critical" },
];

export const compressorTechnologyOptions: SelectOption<CompressorTechnology>[] = [
  {
    value: "ROTARY_SCREW_OIL_INJECTED",
    label: "Rotary Screw — Oil Injected",
  },
  {
    value: "ROTARY_SCREW_OIL_FREE",
    label: "Rotary Screw — Oil Free",
  },
  { value: "RECIPROCATING", label: "Reciprocating" },
  { value: "CENTRIFUGAL", label: "Centrifugal" },
  { value: "SCROLL", label: "Scroll" },
];

export const compressorControlModeOptions: SelectOption<CompressorControlMode>[] =
  [
    { value: "FIXED_SPEED", label: "Fixed Speed" },
    { value: "VSD", label: "Variable Speed Drive" },
    { value: "LOAD_UNLOAD", label: "Load / Unload" },
    { value: "MODULATION", label: "Modulation" },
    { value: "INLET_GUIDE_VANE", label: "Inlet Guide Vane" },
  ];

export const compressorDutyRoleOptions: SelectOption<CompressorDutyRole>[] = [
  { value: "BASE_LOAD", label: "Base Load" },
  { value: "TRIM", label: "Trim" },
  { value: "DUTY", label: "Duty" },
  { value: "STANDBY", label: "Standby" },
];

export const redundancyPhilosophyOptions: SelectOption<RedundancyPhilosophy>[] =
  [
    { value: "NONE", label: "No Redundancy" },
    { value: "N_PLUS_1", label: "N + 1" },
    { value: "N_PLUS_2", label: "N + 2" },
    { value: "FULL_STANDBY", label: "Full Standby" },
  ];

export const dryerTypeOptions: SelectOption<DryerType>[] = [
  { value: "REFRIGERATED", label: "Refrigerated Dryer" },
  { value: "HEATLESS_DESICCANT", label: "Heatless Desiccant Dryer" },
  { value: "HEATED_DESICCANT", label: "Heated Desiccant Dryer" },
  {
    value: "BLOWER_PURGE_DESICCANT",
    label: "Blower-Purge Desiccant Dryer",
  },
  { value: "MEMBRANE", label: "Membrane Dryer" },
  { value: "NONE", label: "No Dryer" },
];
