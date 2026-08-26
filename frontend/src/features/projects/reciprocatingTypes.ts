export type EngineeringNumber = number | string;

export type CylinderAction =
  | "SINGLE_ACTING"
  | "DOUBLE_ACTING";

export type ReciprocatingCalculation = {
  required_flow_m3_per_hr: number;

  bore_mm: number;
  stroke_mm: number;
  rod_diameter_mm: number;
  speed_rpm: number;
  clearance_fraction: number;

  stage_compression_ratio: number;

  suction_z_factor: number;
  discharge_z_factor: number;
  isentropic_exponent: number;

  suction_pressure_bar: number;
  discharge_pressure_bar: number;

  allowable_rod_load_kn: number;
};

export type ReciprocatingExecutionMetadata = {
  persist_result: boolean;
  project_id?: number | null;
  calculation_code?: string | null;
  title?: string | null;
  engineering_notes?: string | null;
};

export type ReciprocatingExecutionRequest = {
  calculation: ReciprocatingCalculation;
  execution: ReciprocatingExecutionMetadata;
};

export type ReciprocatingCylinderGeometryResult = {
  bore_mm: EngineeringNumber;
  stroke_mm: EngineeringNumber;
  rod_diameter_mm: EngineeringNumber;
  speed_rpm: EngineeringNumber;
  clearance_fraction: EngineeringNumber;
  action: CylinderAction;
};

export type ReciprocatingDisplacementResult = {
  piston_area_m2: EngineeringNumber;
  rod_area_m2: EngineeringNumber;
  head_end_displacement_m3_per_min: EngineeringNumber;
  crank_end_displacement_m3_per_min: EngineeringNumber;
  total_displacement_m3_per_min: EngineeringNumber;
  total_displacement_m3_per_hr: EngineeringNumber;
};

export type VolumetricEfficiencyResult = {
  volumetric_efficiency: EngineeringNumber;
  delivered_flow_m3_per_hr: EngineeringNumber;
};

export type ReciprocatingCapacityResult = {
  geometry: ReciprocatingCylinderGeometryResult;
  displacement: ReciprocatingDisplacementResult;
  volumetric_efficiency: VolumetricEfficiencyResult;
};

export type ReciprocatingCapacitySizingResult = {
  required_flow_m3_per_hr: EngineeringNumber;
  delivered_flow_per_cylinder_m3_per_hr: EngineeringNumber;
  required_cylinders: number;
  installed_capacity_m3_per_hr: EngineeringNumber;
  capacity_margin_m3_per_hr: EngineeringNumber;
  capacity_margin_fraction: EngineeringNumber;
  capacity_is_adequate: boolean;
};

export type RodLoadResult = {
  compression_load_kn: EngineeringNumber;
  tension_load_kn: EngineeringNumber;
  maximum_absolute_load_kn: EngineeringNumber;
  allowable_rod_load_kn: EngineeringNumber;
  rod_load_is_adequate: boolean;
};

export type ReciprocatingCalculationResult = {
  capacity: ReciprocatingCapacityResult;
  cylinder_sizing: ReciprocatingCapacitySizingResult;
  rod_load: RodLoadResult;
};

export type ReciprocatingExecutionResponse = {
  result: ReciprocatingCalculationResult;
  calculation_case_id: number | null;
};
