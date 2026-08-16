import type {
  AirQualityClass,
  AirTreatmentInput,
  DecimalString,
  DryerType,
  ReceiverSizingInput,
} from "../greenfield/greenfieldTypes";

export type {
  AirQualityClass,
  AirTreatmentInput,
  DecimalString,
  DryerType,
  ReceiverSizingInput,
} from "../greenfield/greenfieldTypes";


export type AlliedRedundancyPhilosophy =
  | "NONE"
  | "DUTY_STANDBY"
  | "N_PLUS_1"
  | "MULTIPLE_DUTY";

export type EquipmentAdequacyStatus =
  | "NOT_EVALUATED"
  | "NOT_REQUIRED"
  | "NOT_SELECTED"
  | "ADEQUATE"
  | "UNDERSIZED";

export type AftercoolerType =
  | "AIR_COOLED"
  | "WATER_COOLED"
  | "INTEGRATED"
  | "NONE";

export type MoistureSeparatorType =
  | "CENTRIFUGAL"
  | "CYCLONIC"
  | "DEMISTER"
  | "INTEGRATED"
  | "NONE";

export type FilterStageType =
  | "PARTICULATE"
  | "COALESCING"
  | "FINE_COALESCING"
  | "ACTIVATED_CARBON"
  | "STERILE"
  | "OTHER";

export type CondensateDrainType =
  | "MANUAL"
  | "TIMER"
  | "FLOAT"
  | "ZERO_LOSS"
  | "OTHER";

export type RecommendationSeverity =
  | "INFORMATION"
  | "ADVISORY"
  | "WARNING"
  | "CRITICAL";


export type ReceiverConfigurationInput = {
  sizing_input: ReceiverSizingInput;
  selected_receiver_volume_m3?: DecimalString | null;
  receiver_quantity?: number;
  design_pressure_bar_g?: DecimalString | null;
  redundancy_philosophy?: AlliedRedundancyPhilosophy;
  equipment_reference?: string | null;
  notes?: string | null;
};

export type TreatmentConfigurationInput = {
  sizing_input: AirTreatmentInput;
  selected_treatment_capacity_nm3_per_hr?: DecimalString | null;
  installed_unit_count?: number;
  duty_unit_count?: number;
  redundancy_philosophy?: AlliedRedundancyPhilosophy;
  equipment_reference?: string | null;
  notes?: string | null;
};

export type AftercoolerConfigurationInput = {
  aftercooler_type: AftercoolerType;
  selected_flow_capacity_nm3_per_hr?: DecimalString | null;
  pressure_drop_bar?: DecimalString;
  inlet_temperature_c?: DecimalString | null;
  outlet_temperature_c?: DecimalString | null;
  equipment_reference?: string | null;
  notes?: string | null;
};

export type MoistureSeparatorConfigurationInput = {
  separator_type: MoistureSeparatorType;
  selected_flow_capacity_nm3_per_hr?: DecimalString | null;
  pressure_drop_bar?: DecimalString;
  equipment_reference?: string | null;
  notes?: string | null;
};

export type FilterStageConfigurationInput = {
  stage_code: string;
  stage_type: FilterStageType;
  selected_flow_capacity_nm3_per_hr?: DecimalString | null;
  pressure_drop_bar?: DecimalString;
  equipment_reference?: string | null;
  notes?: string | null;
};

export type CondensateDrainConfigurationInput = {
  drain_code: string;
  location: string;
  drain_type: CondensateDrainType;
  selected_condensate_capacity_l_per_hr?: DecimalString | null;
  equipment_reference?: string | null;
  notes?: string | null;
};


export type AlliedEquipmentAnalysisRequest = {
  analysis_code: string;
  receiver?: ReceiverConfigurationInput | null;
  treatment?: TreatmentConfigurationInput | null;
  aftercooler?: AftercoolerConfigurationInput | null;
  moisture_separator?: MoistureSeparatorConfigurationInput | null;
  filter_stages?: FilterStageConfigurationInput[];
  condensate_drains?: CondensateDrainConfigurationInput[];
  notes?: string | null;
};


export type ReceiverSizingResult = {
  peak_demand_nm3_per_hr: DecimalString;
  available_compressor_flow_nm3_per_hr: DecimalString;
  flow_deficit_nm3_per_hr: DecimalString;
  event_duration_seconds: DecimalString;
  receiver_high_pressure_bar_g: DecimalString;
  receiver_low_pressure_bar_g: DecimalString;
  pressure_band_bar: DecimalString;
  base_receiver_volume_m3: DecimalString;
  reserve_fraction: DecimalString;
  recommended_receiver_volume_m3: DecimalString;
  storage_required: boolean;
};

export type AirTreatmentResult = {
  required_delivered_flow_nm3_per_hr: DecimalString;
  dryer_purge_loss_nm3_per_hr: DecimalString;
  gross_flow_before_purge_nm3_per_hr: DecimalString;
  corrected_required_treatment_capacity_nm3_per_hr: DecimalString;
  recommended_treatment_capacity_nm3_per_hr: DecimalString;
  total_treatment_pressure_drop_bar: DecimalString;
  dryer_type: DryerType;
  required_air_quality: AirQualityClass;
  purge_loss_fraction: DecimalString;
  correction_factor: DecimalString;
  treatment_capacity_margin_fraction: DecimalString;
};

export type EquipmentCapacityEvaluation = {
  equipment_code: string;
  required_capacity: DecimalString;
  selected_capacity: DecimalString | null;
  capacity_margin: DecimalString | null;
  capacity_margin_fraction: DecimalString | null;
  status: EquipmentAdequacyStatus;
};

export type EngineeringRecommendation = {
  recommendation_code: string;
  severity: RecommendationSeverity;
  equipment_code: string;
  message: string;
  rationale: string;
};

export type AlliedEquipmentAnalysisResponse = {
  analysis_code: string;
  receiver_result: ReceiverSizingResult | null;
  treatment_result: AirTreatmentResult | null;
  receiver_evaluation: EquipmentCapacityEvaluation | null;
  treatment_evaluation: EquipmentCapacityEvaluation | null;
  aftercooler_evaluation: EquipmentCapacityEvaluation | null;
  moisture_separator_evaluation: EquipmentCapacityEvaluation | null;
  filter_evaluations: EquipmentCapacityEvaluation[];
  total_additional_pressure_drop_bar: DecimalString;
  recommendations: EngineeringRecommendation[];
  notes: string | null;
};
