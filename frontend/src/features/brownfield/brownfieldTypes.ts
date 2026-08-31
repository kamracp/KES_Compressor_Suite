export type DecimalString = string;

export type AuditOperatingState =
  | "LOADED"
  | "UNLOADED"
  | "PART_LOAD"
  | "STOPPED";

export type CompressorTechnology =
  | "ROTARY_SCREW_OIL_INJECTED"
  | "ROTARY_SCREW_OIL_FREE"
  | "RECIPROCATING"
  | "CENTRIFUGAL"
  | "SCROLL";

export type CompressorControlMode =
  | "FIXED_SPEED"
  | "VSD"
  | "LOAD_UNLOAD"
  | "MODULATION"
  | "INLET_GUIDE_VANE";

export type BrownfieldOpportunityCategory =
  | "LEAKAGE"
  | "UNLOADED_RUNNING"
  | "PRESSURE"
  | "CAPACITY"
  | "UTILIZATION"
  | "CONDENSATE_DRAIN"
  | "FILTER_EFFICIENCY"
  | "POWER_FACTOR";

export type BrownfieldOpportunityPriority =
  | "HIGH"
  | "MEDIUM"
  | "LOW";

export type ExistingCompressorInput = {
  unit_code: string;
  equipment_source?: string | null;
  manufacturer?: string | null;
  model?: string | null;

  technology: CompressorTechnology;
  control_mode: CompressorControlMode;

  rated_fad_nm3_per_hr: DecimalString;
  rated_discharge_pressure_bar_g: DecimalString;
  rated_motor_power_kw: DecimalString;

  installation_year?: number | null;
  operating_hours?: DecimalString | null;

  available: boolean;
  notes?: string | null;
};

export type CompressorMeasurementInput = {
  unit_code: string;
  timestamp_label: string;

  operating_state: AuditOperatingState;

  measured_flow_nm3_per_hr: DecimalString;
  measured_discharge_pressure_bar_g: DecimalString;
  measured_power_kw: DecimalString;

  load_fraction?: DecimalString | null;
};

export type SystemMeasurementInput = {
  timestamp_label: string;

  total_flow_nm3_per_hr: DecimalString;
  header_pressure_bar_g: DecimalString;
  total_power_kw: DecimalString;

  production_state?: string | null;
  notes?: string | null;
};

export type LeakageSurveyInput = {
  measured_leakage_flow_nm3_per_hr: DecimalString;
  survey_method: string;
  estimated_repair_fraction: DecimalString;
  survey_notes?: string | null;
};

export type BrownfieldSystemAuditRequest = {
  audit_code: string;
  project_id: number;

  compressors: ExistingCompressorInput[];
  compressor_measurements: CompressorMeasurementInput[];
  system_measurements: SystemMeasurementInput[];

  leakage_summary: LeakageSurveyInput | null;

  electricity_tariff_per_kwh: DecimalString;
  annual_operating_hours: DecimalString;

  optimized_discharge_pressure_bar_g: DecimalString | null;
  expected_leak_repair_fraction: DecimalString;
  // System-level control conversion factor for demand-side savings (0-1).
  demand_saving_control_factor?: DecimalString;
  power_penalty_fraction_per_bar: DecimalString | null;

  // Motor electrical measurement (C-6). All three of voltage, current
  // and power factor must be present for the PF-CORRECTION opportunity
  // to be raised. Ref: IEEE Std 141, IS 15167 Part 1.
  motor_measured_voltage_v?: DecimalString | null;
  motor_measured_current_a?: DecimalString | null;
  motor_measured_power_factor?: DecimalString | null;
  motor_target_power_factor?: DecimalString;
  motor_rated_power_kw?: DecimalString | null;

  // Annual PF penalty the utility currently bills this site.
  // User-supplied only; no penalty saving is claimed without it.
  pf_penalty_annual_cost?: DecimalString | null;

  notes?: string | null;
};

export type MotorPfcResult = {
  measured_voltage_v: DecimalString;
  measured_current_a: DecimalString;
  measured_power_factor: DecimalString;
  target_power_factor: DecimalString;

  measured_active_power_kw: DecimalString;
  measured_reactive_power_kvar: DecimalString;
  target_reactive_power_kvar: DecimalString;

  required_capacitor_kvar: DecimalString;

  pfc_correction_beneficial: boolean;

  power_deviation_from_nameplate: DecimalString | null;
};

export type BrownfieldOpportunity = {
  opportunity_code: string;
  category: BrownfieldOpportunityCategory;
  priority: BrownfieldOpportunityPriority;

  title: string;
  rationale: string;

  estimated_power_saving_kw: DecimalString;
  estimated_annual_energy_saving_kwh: DecimalString;
  estimated_annual_cost_saving: DecimalString;
};

export type BrownfieldSystemAuditResponse = {
  audit_code: string;
  project_id: number;

  installed_capacity_nm3_per_hr: DecimalString;
  available_capacity_nm3_per_hr: DecimalString;

  average_system_flow_nm3_per_hr: DecimalString;
  peak_system_flow_nm3_per_hr: DecimalString;
  minimum_system_flow_nm3_per_hr: DecimalString;

  average_system_power_kw: DecimalString;
  peak_system_power_kw: DecimalString;

  average_header_pressure_bar_g: DecimalString;
  minimum_header_pressure_bar_g: DecimalString;
  maximum_header_pressure_bar_g: DecimalString;

  average_capacity_utilization_fraction: DecimalString;
  peak_capacity_utilization_fraction: DecimalString;

  measured_specific_power_kw_per_nm3_per_min:
    | DecimalString
    | null;

  unloaded_measurement_fraction: DecimalString;

  leakage_flow_nm3_per_hr: DecimalString;
  leakage_fraction_of_average_demand: DecimalString;

  current_annual_energy_kwh: DecimalString;
  current_annual_energy_cost: DecimalString;

  estimated_total_power_saving_kw: DecimalString;
  estimated_total_annual_energy_saving_kwh: DecimalString;
  estimated_total_annual_cost_saving: DecimalString;

  estimated_optimized_average_power_kw: DecimalString;
  estimated_optimized_annual_energy_kwh: DecimalString;
  estimated_optimized_annual_energy_cost: DecimalString;

  estimated_energy_reduction_fraction: DecimalString;

  installed_capacity_is_sufficient_for_peak: boolean;
  high_unloaded_running_detected: boolean;
  significant_leakage_detected: boolean;

  motor_pfc: MotorPfcResult | null;

  opportunities: BrownfieldOpportunity[];
};
