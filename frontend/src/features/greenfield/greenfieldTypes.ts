export type DecimalString = string;

export type AirConsumerCategory =
  | "PRODUCTION_MACHINE"
  | "PNEUMATIC_CYLINDER"
  | "AIR_TOOL"
  | "BAG_FILTER"
  | "PNEUMATIC_CONVEYING"
  | "PACKAGING_MACHINE"
  | "CONTROL_VALVE"
  | "INSTRUMENT_AIR"
  | "PROCESS_AIR"
  | "AIR_CLEANING"
  | "OTHER";

export type AirConsumptionBasis =
  | "CONTINUOUS_FLOW"
  | "FLOW_WHEN_OPERATING"
  | "PER_CYCLE";

export type AirQualityClass =
  | "GENERAL_PLANT_AIR"
  | "INSTRUMENT_AIR"
  | "OIL_FREE_PROCESS_AIR"
  | "CRITICAL_PROCESS_AIR";

export type ConsumerCriticality =
  | "CRITICAL"
  | "ESSENTIAL"
  | "NORMAL"
  | "NON_CRITICAL";

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

export type CompressorDutyRole =
  | "BASE_LOAD"
  | "TRIM"
  | "DUTY"
  | "STANDBY";

export type RedundancyPhilosophy =
  | "NONE"
  | "N_PLUS_1"
  | "N_PLUS_2"
  | "FULL_STANDBY";

export type DryerType =
  | "REFRIGERATED"
  | "HEATLESS_DESICCANT"
  | "HEATED_DESICCANT"
  | "BLOWER_PURGE_DESICCANT"
  | "MEMBRANE"
  | "NONE";

export type AirConsumerInput = {
  consumer_code: string;
  name: string;
  category: AirConsumerCategory;
  quantity: number;
  required_pressure_bar_g: DecimalString;
  air_quality_class: AirQualityClass;
  consumption_basis: AirConsumptionBasis;
  flow_per_unit_nm3_per_hr?: DecimalString | null;
  air_per_cycle_nl?: DecimalString | null;
  cycles_per_minute?: DecimalString | null;
  duty_factor?: DecimalString;
  simultaneity_factor?: DecimalString;
  operating_hours_per_day?: DecimalString;
  operating_days_per_year?: DecimalString;
  criticality?: ConsumerCriticality;
  area?: string | null;
  production_line?: string | null;
  notes?: string | null;
};

export type DemandProfilePointInput = {
  period_index: number;
  label: string;
  demand_nm3_per_hr: DecimalString;
  required_pressure_bar_g: DecimalString;
  duration_hours: DecimalString;
};

export type PressureLossComponentInput = {
  component_code: string;
  name: string;
  pressure_drop_bar: DecimalString;
  category: string;
  notes?: string | null;
};

export type AirTreatmentInput = {
  required_delivered_flow_nm3_per_hr: DecimalString;
  required_air_quality: AirQualityClass;
  dryer_type: DryerType;
  dryer_correction_factor?: DecimalString;
  dryer_purge_fraction?: DecimalString;
  prefilter_pressure_drop_bar?: DecimalString;
  afterfilter_pressure_drop_bar?: DecimalString;
  dryer_pressure_drop_bar?: DecimalString;
  treatment_capacity_margin_fraction?: DecimalString;
};

export type CompressorUnitInput = {
  unit_code: string;
  technology: CompressorTechnology;
  control_mode: CompressorControlMode;
  duty_role: CompressorDutyRole;
  rated_fad_nm3_per_hr: DecimalString;
  minimum_stable_flow_fraction: DecimalString;
  rated_discharge_pressure_bar_g: DecimalString;
  rated_motor_power_kw?: DecimalString | null;
  specific_power_kw_per_nm3_per_min?: DecimalString | null;
  available?: boolean;
  notes?: string | null;
};

export type CompressorStationInput = {
  station_code: string;
  units: CompressorUnitInput[];
  redundancy_philosophy: RedundancyPhilosophy;
  minimum_required_pressure_bar_g: DecimalString;
  design_flow_nm3_per_hr: DecimalString;
  master_control_enabled?: boolean;
};

export type ReceiverSizingInput = {
  peak_demand_nm3_per_hr: DecimalString;
  available_compressor_flow_nm3_per_hr: DecimalString;
  event_duration_seconds: DecimalString;
  receiver_high_pressure_bar_g: DecimalString;
  receiver_low_pressure_bar_g: DecimalString;
  reserve_fraction?: DecimalString;
};

export type GreenfieldSystemDesignRequest = {
  consumers: AirConsumerInput[];
  demand_profile_points: DemandProfilePointInput[];
  leakage_fraction?: DecimalString;
  future_expansion_fraction?: DecimalString;
  other_allowance_fraction?: DecimalString;
  minimum_point_of_use_pressure_bar_g?: DecimalString;
  pressure_loss_components?: PressureLossComponentInput[];
  control_margin_bar?: DecimalString;
  treatment?: AirTreatmentInput | null;
  station?: CompressorStationInput | null;
  receiver?: ReceiverSizingInput | null;
  specific_power_kw_per_nm3_per_min?: DecimalString | null;
  annual_operating_days?: DecimalString | null;
  electricity_tariff_per_kwh?: DecimalString;
};

export type GreenfieldSystemDesignResponse = {
  required_design_flow_nm3_per_hr: DecimalString;
  required_compressor_discharge_pressure_bar_g: DecimalString;
  simultaneous_demand_nm3_per_hr: DecimalString;
  peak_profile_demand_nm3_per_hr: DecimalString;
  leakage_allowance_nm3_per_hr: DecimalString;
  future_expansion_allowance_nm3_per_hr: DecimalString;
  treatment_capacity_nm3_per_hr: DecimalString | null;
  station_available_capacity_nm3_per_hr: DecimalString | null;
  station_capacity_is_adequate: boolean | null;
  receiver_volume_m3: DecimalString | null;
  receiver_storage_required: boolean | null;
  annual_energy_kwh: DecimalString | null;
  annual_energy_cost: DecimalString | null;
  system_design_is_feasible: boolean;
  engineering_messages: string[];
};
