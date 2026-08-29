export type EngineeringNumber = number | string;

export type RotaryScrewOilType = "OIL_INJECTED" | "OIL_FREE";

export type RotaryScrewControlType =
  | "FIXED_SPEED_LOAD_UNLOAD"
  | "VARIABLE_SPEED_DRIVE";

export type RotaryScrewStageCount = "SINGLE_STAGE" | "TWO_STAGE";

export type RotaryScrewGeometryInput = {
  male_rotor_diameter_mm: number;
  rotor_length_mm: number;
  area_utilisation_coefficient: number;
};

export type RotaryScrewCalculation = {
  inlet_pressure_bar_a: number;
  inlet_temperature_k: number;
  discharge_pressure_bar_g: number;
  rotational_speed_rpm: number;
  oil_type: RotaryScrewOilType;
  control_type: RotaryScrewControlType;
  stage_count: RotaryScrewStageCount;

  rated_fad_m3_per_min: number;
  package_input_power_kw: number;

  rotor_geometry?: RotaryScrewGeometryInput | null;
  standard_reference_pressure_bar_a?: number | null;
  standard_reference_temperature_k?: number | null;
};

export type RotaryScrewExecutionMetadata = {
  persist_result: boolean;
  project_id?: number | null;
  calculation_code?: string | null;
  title?: string | null;
  engineering_notes?: string | null;
};

export type RotaryScrewExecutionRequest = {
  calculation: RotaryScrewCalculation;
  execution: RotaryScrewExecutionMetadata;
};

export type RotaryScrewOperatingPointResult = {
  inlet_pressure_bar_a: EngineeringNumber;
  inlet_temperature_k: EngineeringNumber;
  discharge_pressure_bar_g: EngineeringNumber;
  rotational_speed_rpm: EngineeringNumber;
  oil_type: RotaryScrewOilType;
  control_type: RotaryScrewControlType;
  stage_count: RotaryScrewStageCount;
};

export type RotaryScrewDisplacementResult = {
  theoretical_displacement_m3_per_min: EngineeringNumber;
};

export type RotaryScrewStandardAirCorrectionResult = {
  reference_pressure_bar_a: EngineeringNumber;
  reference_temperature_k: EngineeringNumber;
  corrected_fad_m3_per_min: EngineeringNumber;
};

export type RotaryScrewPerformanceResult = {
  rated_fad_m3_per_min: EngineeringNumber;
  package_input_power_kw: EngineeringNumber;
  specific_power_kw_per_m3_min: EngineeringNumber;
};

export type RotaryScrewCalculationResult = {
  operating_point: RotaryScrewOperatingPointResult;
  displacement: RotaryScrewDisplacementResult | null;
  standard_air_correction: RotaryScrewStandardAirCorrectionResult | null;
  performance: RotaryScrewPerformanceResult;
};

export type RotaryScrewExecutionResponse = {
  result: RotaryScrewCalculationResult;
  calculation_case_id: number | null;
};
