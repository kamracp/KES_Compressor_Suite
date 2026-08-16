import type {
  DecimalString,
  DryerType,
} from "../greenfield/greenfieldTypes";

export type {
  DecimalString,
  DryerType,
} from "../greenfield/greenfieldTypes";

export type SkidComponentType =
  | "COMPRESSOR"
  | "AFTERCOOLER"
  | "MOISTURE_SEPARATOR"
  | "WET_RECEIVER"
  | "PREFILTER"
  | "DRYER"
  | "AFTERFILTER"
  | "DRY_RECEIVER"
  | "CONDENSATE_DRAIN"
  | "OIL_WATER_SEPARATOR"
  | "FLOW_METER"
  | "PRESSURE_SENSOR"
  | "DEW_POINT_SENSOR"
  | "MASTER_CONTROLLER"
  | "ISOLATION_VALVE"
  | "CHECK_VALVE"
  | "OTHER";

export type SkidArrangement =
  | "CENTRALIZED"
  | "DECENTRALIZED"
  | "HYBRID";

export type SkidComponentInput = {
  component_code: string;
  name: string;
  component_type: SkidComponentType;

  rated_flow_nm3_per_hr?: DecimalString | null;
  rated_pressure_bar_g?: DecimalString | null;
  pressure_drop_bar?: DecimalString;

  quantity?: number;

  equipment_source?: string | null;
  model?: string | null;
  notes?: string | null;
};

export type AirSkidAssessmentRequest = {
  skid_code: string;
  arrangement: SkidArrangement;

  design_flow_nm3_per_hr: DecimalString;
  design_pressure_bar_g: DecimalString;

  dryer_type: DryerType;

  components: SkidComponentInput[];

  has_wet_receiver: boolean;
  has_dry_receiver: boolean;

  has_flow_metering: boolean;
  has_pressure_monitoring: boolean;
  has_dew_point_monitoring: boolean;

  master_control_enabled: boolean;

  description?: string | null;
};

export type AirSkidAssessmentResponse = {
  skid_code: string;

  design_flow_nm3_per_hr: DecimalString;
  design_pressure_bar_g: DecimalString;

  total_component_count: number;

  total_pressure_drop_bar: DecimalString;

  minimum_component_flow_capacity_nm3_per_hr:
    | DecimalString
    | null;

  minimum_component_pressure_rating_bar_g:
    | DecimalString
    | null;

  flow_capacity_is_adequate: boolean;
  pressure_rating_is_adequate: boolean;

  has_wet_receiver: boolean;
  has_dry_receiver: boolean;

  has_flow_metering: boolean;
  has_pressure_monitoring: boolean;
  has_dew_point_monitoring: boolean;

  master_control_enabled: boolean;

  instrumentation_is_complete: boolean;
  skid_is_adequate: boolean;
};
