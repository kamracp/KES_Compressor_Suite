export type DecimalString = string;

export type PerformanceOperatingState =
  | "LOADED"
  | "UNLOADED"
  | "PART_LOAD"
  | "STOPPED";

export type PerformanceMeasurementInput = {
  timestamp_label: string;

  flow_nm3_per_hr: DecimalString;
  pressure_bar_g: DecimalString;
  power_kw: DecimalString;

  operating_state?: PerformanceOperatingState | null;
  load_fraction?: DecimalString | null;

  production_state?: string | null;
  notes?: string | null;
};

export type CompressedAirPerformanceAnalysisRequest = {
  analysis_code: string;

  measurements: PerformanceMeasurementInput[];

  annual_operating_hours: DecimalString;
  electricity_tariff_per_kwh: DecimalString;

  rated_capacity_nm3_per_hr?: DecimalString | null;
  rated_power_kw?: DecimalString | null;

  reference_specific_power_kw_per_nm3_per_min?:
    | DecimalString
    | null;

  optimized_discharge_pressure_bar_g?:
    | DecimalString
    | null;

  power_penalty_fraction_per_bar: DecimalString;

  notes?: string | null;
};

export type PressureEnergyPerformanceResponse = {
  current_discharge_pressure_bar_g: DecimalString;
  optimized_discharge_pressure_bar_g: DecimalString;

  pressure_reduction_bar: DecimalString;

  current_average_power_kw: DecimalString;
  estimated_optimized_power_kw: DecimalString;
  estimated_power_saving_kw: DecimalString;

  power_saving_fraction: DecimalString;

  annual_operating_hours: DecimalString;
  annual_energy_saving_kwh: DecimalString;

  electricity_tariff_per_kwh: DecimalString;
  annual_cost_saving: DecimalString;

  power_penalty_fraction_per_bar: DecimalString;

  pressure_reduction_is_beneficial: boolean;
};

export type CompressedAirPerformanceAnalysisResponse = {
  analysis_code: string;
  measurement_count: number;

  average_flow_nm3_per_hr: DecimalString;
  peak_flow_nm3_per_hr: DecimalString;
  minimum_flow_nm3_per_hr: DecimalString;

  average_pressure_bar_g: DecimalString;
  maximum_pressure_bar_g: DecimalString;
  minimum_pressure_bar_g: DecimalString;

  average_power_kw: DecimalString;
  peak_power_kw: DecimalString;

  measured_specific_power_kw_per_nm3_per_min:
    | DecimalString
    | null;

  measured_specific_energy_kwh_per_1000_nm3:
    | DecimalString
    | null;

  average_load_fraction: DecimalString | null;
  unloaded_measurement_fraction: DecimalString;

  rated_capacity_nm3_per_hr: DecimalString | null;

  average_capacity_utilization_fraction:
    | DecimalString
    | null;

  peak_capacity_utilization_fraction:
    | DecimalString
    | null;

  rated_power_kw: DecimalString | null;

  average_power_utilization_fraction:
    | DecimalString
    | null;

  reference_specific_power_kw_per_nm3_per_min:
    | DecimalString
    | null;

  specific_power_deviation_fraction:
    | DecimalString
    | null;

  annual_operating_hours: DecimalString;
  annual_energy_kwh: DecimalString;

  electricity_tariff_per_kwh: DecimalString;
  annual_energy_cost: DecimalString;

  pressure_energy: PressureEnergyPerformanceResponse | null;
};
