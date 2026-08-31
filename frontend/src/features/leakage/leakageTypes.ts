export type DecimalString = string;

export type LeakQuantificationBasis =
  | "FLOW_METER"
  | "ULTRASONIC_ESTIMATE"
  | "DECAY_TEST"
  | "LOAD_UNLOAD_TEST"
  | "ORIFICE_ESTIMATE"
  | "ENGINEERING_ESTIMATE"
  | "OTHER";

export type LeakSourceCategory =
  | "PIPE_JOINT"
  | "HOSE"
  | "FITTING"
  | "QUICK_COUPLING"
  | "VALVE"
  | "FRL"
  | "CYLINDER"
  | "ACTUATOR"
  | "DRAIN"
  | "EQUIPMENT_INTERNAL"
  | "OTHER";

export type LeakRepairStatus =
  | "OPEN"
  | "PLANNED"
  | "REPAIRED"
  | "VERIFIED"
  | "DEFERRED";

export type LeakPriority =
  | "CRITICAL"
  | "HIGH"
  | "MEDIUM"
  | "LOW";

export type LeakRegisterItemInput = {
  leak_code: string;
  location: string;

  baseline_leakage_flow_nm3_per_hr: DecimalString;
  quantification_basis: LeakQuantificationBasis;

  source_category: LeakSourceCategory;

  area?: string | null;
  equipment_tag?: string | null;
  component_description?: string | null;

  survey_pressure_bar_g?: DecimalString | null;

  expected_repair_fraction: DecimalString;

  repair_status: LeakRepairStatus;

  estimated_repair_cost?: DecimalString | null;

  verified_post_repair_flow_nm3_per_hr?:
    | DecimalString
    | null;

  survey_method_reference?: string | null;
  notes?: string | null;
};

export type CompressedAirLeakageManagementRequest = {
  analysis_code: string;

  leaks: LeakRegisterItemInput[];

  specific_power_kw_per_nm3_per_min: DecimalString;

  annual_operating_hours: DecimalString;
  electricity_tariff_per_kwh: DecimalString;

  // System-level control conversion factor for demand-side savings
  // (0-1). Optional on the wire: the backend defaults to 1.
  demand_saving_control_factor?: DecimalString;

  average_system_demand_nm3_per_hr?:
    | DecimalString
    | null;

  notes?: string | null;
};

export type LeakageEnergyResponse = {
  leakage_flow_nm3_per_hr: DecimalString;
  leakage_flow_nm3_per_min: DecimalString;

  wasted_power_kw: DecimalString;

  annual_wasted_energy_kwh: DecimalString;
  annual_wasted_energy_cost: DecimalString;

  expected_repair_fraction: DecimalString;
  demand_saving_control_factor: DecimalString;

  recoverable_leakage_flow_nm3_per_hr: DecimalString;
  recoverable_power_kw: DecimalString;

  annual_energy_saving_kwh: DecimalString;
  annual_cost_saving: DecimalString;

  residual_leakage_flow_nm3_per_hr: DecimalString;
};

export type LeakageRegisterItemResultResponse = {
  leak_code: string;
  location: string;

  source_category: LeakSourceCategory;
  quantification_basis: LeakQuantificationBasis;

  repair_status: LeakRepairStatus;
  priority: LeakPriority;

  baseline_leakage_flow_nm3_per_hr: DecimalString;

  fraction_of_total_registered_leakage: DecimalString;

  energy: LeakageEnergyResponse;

  estimated_repair_cost: DecimalString | null;
  simple_payback_years: DecimalString | null;

  verified_post_repair_flow_nm3_per_hr:
    | DecimalString
    | null;

  verified_flow_reduction_nm3_per_hr:
    | DecimalString
    | null;

  verified_repair_fraction: DecimalString | null;

  notes?: string | null;
};

export type CompressedAirLeakageManagementResponse = {
  analysis_code: string;

  leak_count: number;

  total_registered_leakage_flow_nm3_per_hr:
    DecimalString;

  leakage_fraction_of_average_system_demand:
    | DecimalString
    | null;

  total_wasted_power_kw: DecimalString;

  total_annual_wasted_energy_kwh: DecimalString;
  total_annual_wasted_energy_cost: DecimalString;

  total_recoverable_leakage_flow_nm3_per_hr:
    DecimalString;

  total_recoverable_power_kw: DecimalString;

  total_annual_energy_saving_kwh: DecimalString;
  total_annual_cost_saving: DecimalString;

  total_residual_leakage_flow_nm3_per_hr:
    DecimalString;

  verified_leak_count: number;

  verified_flow_reduction_nm3_per_hr:
    DecimalString;

  items: LeakageRegisterItemResultResponse[];
};
