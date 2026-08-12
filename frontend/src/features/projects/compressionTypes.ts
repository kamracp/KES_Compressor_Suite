export type CompressionGasInput = {
  suction_pressure_bar: number;
  discharge_pressure_bar: number;
  suction_temperature_k: number;
  mass_flow_kg_per_s: number;
  actual_flow_m3_per_s: number;
  molecular_weight_kg_per_kmol: number;
  suction_z_factor: number;
  discharge_z_factor: number;
  isentropic_exponent: number;
};

export type CompressionCalculation = {
  gas: CompressionGasInput;

  number_of_stages: number;

  specific_heat_cp_kj_per_kg_k: number;
  isentropic_efficiency: number;
  mechanical_efficiency: number;

  intercooler_outlet_temperature_k: number;

  cooling_water_inlet_temperature_k: number;
  cooling_water_outlet_temperature_k: number;

  selected_driver_power_kw: number;
  driver_service_factor: number;
  motor_efficiency?: number | null;
};

export type CompressionExecutionMetadata = {
  persist_result: boolean;
  project_id?: number | null;
  calculation_code?: string | null;
  title?: string | null;
  engineering_notes?: string | null;
};

export type CompressionExecutionRequest = {
  calculation: CompressionCalculation;
  execution: CompressionExecutionMetadata;
};

export type CompressionExecutionResponse = {
  result: Record<string, unknown>;
  calculation_case_id: number | null;
};
