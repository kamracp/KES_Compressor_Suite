export type CentrifugalGasInput = {
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

export type CentrifugalCalculation = {
  gas: CentrifugalGasInput;

  polytropic_efficiency: number;

  number_of_impeller_stages: number;
  head_coefficient: number;
  rotational_speed_rpm: number;

  mechanical_loss_fraction: number;
  driver_margin_fraction: number;

  selected_driver_power_kw: number;
  motor_efficiency?: number | null;

  surge_flow_fraction: number;
  anti_surge_margin_fraction: number;
  stonewall_flow_fraction: number;
};

export type CentrifugalExecutionMetadata = {
  persist_result: boolean;
  project_id?: number | null;
  calculation_code?: string | null;
  title?: string | null;
  engineering_notes?: string | null;
};

export type CentrifugalExecutionRequest = {
  calculation: CentrifugalCalculation;
  execution: CentrifugalExecutionMetadata;
};

export type CentrifugalExecutionResponse = {
  result: Record<string, unknown>;
  calculation_case_id: number | null;
};
