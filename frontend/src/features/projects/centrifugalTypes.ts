export type EngineeringNumber = number | string;

export type CentrifugalDriverType =
  | "ELECTRIC_MOTOR"
  | "GAS_TURBINE"
  | "STEAM_TURBINE";

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

export type CentrifugalHeadResult = {
  average_z_factor: EngineeringNumber;
  polytropic_exponent: EngineeringNumber;
  overall_compression_ratio: EngineeringNumber;
  polytropic_head_kj_per_kg: EngineeringNumber;
};

export type CentrifugalImpellerResult = {
  number_of_impeller_stages: number;
  head_per_stage_kj_per_kg: EngineeringNumber;
  head_coefficient: EngineeringNumber;
  impeller_tip_speed_m_per_s: EngineeringNumber;
  rotational_speed_rpm: EngineeringNumber;
  impeller_diameter_m: EngineeringNumber;
};

export type CentrifugalPowerResult = {
  gas_power_kw: EngineeringNumber;
  shaft_power_kw: EngineeringNumber;
  required_driver_power_kw: EngineeringNumber;
  selected_driver_power_kw: EngineeringNumber;
  driver_margin_kw: EngineeringNumber;
  driver_is_adequate: boolean;
  electrical_input_power_kw: EngineeringNumber | null;
  driver_type: CentrifugalDriverType;
};

export type CentrifugalSurgeResult = {
  design_flow_m3_per_hr: EngineeringNumber;
  surge_flow_m3_per_hr: EngineeringNumber;
  anti_surge_setpoint_m3_per_hr: EngineeringNumber;
  surge_margin_fraction: EngineeringNumber;
  stonewall_flow_m3_per_hr: EngineeringNumber;
  operating_range_m3_per_hr: EngineeringNumber;
  design_point_is_within_envelope: boolean;
};

export type CentrifugalPerformanceMapPoint = {
  speed_fraction: EngineeringNumber;
  speed_rpm: EngineeringNumber;
  flow_m3_per_hr: EngineeringNumber;
  head_kj_per_kg: EngineeringNumber;
};

export type CentrifugalPerformanceMapResult = {
  design_speed_rpm: EngineeringNumber;
  design_flow_m3_per_hr: EngineeringNumber;
  design_head_kj_per_kg: EngineeringNumber;
  points: CentrifugalPerformanceMapPoint[];
};

export type CentrifugalCalculationResult = {
  head: CentrifugalHeadResult;
  impeller: CentrifugalImpellerResult;
  power: CentrifugalPowerResult;
  surge: CentrifugalSurgeResult;
  performance_map: CentrifugalPerformanceMapResult;
};

export type CentrifugalExecutionResponse = {
  result: CentrifugalCalculationResult;
  calculation_case_id: number | null;
};
