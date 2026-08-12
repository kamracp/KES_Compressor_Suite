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

export type ReciprocatingExecutionResponse = {
  result: Record<string, unknown>;
  calculation_case_id: number | null;
};
