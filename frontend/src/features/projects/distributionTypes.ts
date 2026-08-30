export type EngineeringNumber = number | string;

export type NetworkTopology =
  | "DEAD_END"
  | "BRANCHED"
  | "RING_MAIN"
  | "MULTIPLE_RING"
  | "HYBRID";

export type NetworkNodeType =
  | "COMPRESSOR_STATION"
  | "RECEIVER"
  | "HEADER_JUNCTION"
  | "BRANCH_JUNCTION"
  | "CONSUMER"
  | "RING_CONNECTION";

export type PipeSegmentRole =
  | "MAIN_HEADER"
  | "RING_MAIN"
  | "SUB_HEADER"
  | "BRANCH"
  | "DROP_LEG"
  | "EQUIPMENT_CONNECTION";

// Calibrated screening bands -- CAGI <= 20 ft/s (~6 m/s); BCAS design
// 6-7 m/s, never above 9 m/s. Standards registry: CAGI-CAGH, BCAS-BPG-101.
export type VelocityScreeningStatus = "RECOMMENDED" | "CAUTION" | "EXCESSIVE";

export type OptimizationRecommendationStatus =
  | "RECOMMENDED"
  | "REVIEW"
  | "NO_CHANGE_REQUIRED";

export type NetworkNodeInput = {
  node_code: string;
  name: string;
  node_type: NetworkNodeType;
  elevation_m: number;
  demand_nm3_per_hr: number;
  minimum_pressure_bar_g?: number | null;
  area?: string | null;
  notes?: string | null;
};

export type PipeSegmentInput = {
  segment_code: string;
  name: string;
  role: PipeSegmentRole;
  start_node_code: string;
  end_node_code: string;
  length_m: number;
  equivalent_fitting_length_m: number;
  internal_diameter_mm: number;
  roughness_mm: number;
  design_flow_nm3_per_hr: number;
  operating_pressure_bar_g: number;
  operating_temperature_k: number;
  material?: string | null;
  notes?: string | null;
};

export type NetworkPathInput = {
  path_code: string;
  node_codes: string[];
  segment_codes: string[];
};

export type DistributionCalculationRequest = {
  network_code: string;
  topology: NetworkTopology;
  nodes: NetworkNodeInput[];
  segments: PipeSegmentInput[];
  paths: NetworkPathInput[];
  design_source_pressure_bar_g: number;
  air_density_kg_per_m3: number;
  darcy_friction_factor: number;
  candidate_internal_diameters_mm?: number[] | null;
  maximum_preferred_velocity_m_per_s?: number;
  minimum_pressure_drop_reduction_fraction?: number;
  description?: string | null;
};

export type DistributionExecutionMetadata = {
  persist_result: boolean;
  project_id?: number | null;
  calculation_code?: string | null;
  title?: string | null;
  engineering_notes?: string | null;
};

export type DistributionExecutionRequest = {
  calculation: DistributionCalculationRequest;
  execution: DistributionExecutionMetadata;
};

export type NetworkValidationResult = {
  network_code: string;
  node_count: number;
  segment_count: number;
  source_node_count: number;
  consumer_node_count: number;
  duplicate_node_codes: string[];
  duplicate_segment_codes: string[];
  orphan_segment_codes: string[];
  is_structurally_valid: boolean;
};

export type PathSegmentResult = {
  segment_code: string;
  start_node_code: string;
  end_node_code: string;
  design_flow_nm3_per_hr: EngineeringNumber;
  length_m: EngineeringNumber;
  equivalent_fitting_length_m: EngineeringNumber;
  total_equivalent_length_m: EngineeringNumber;
  velocity_m_per_s: EngineeringNumber;
  pressure_drop_bar: EngineeringNumber;
};

export type NetworkPathResult = {
  path_code: string;
  source_node_code: string;
  destination_node_code: string;
  segment_results: PathSegmentResult[];
  total_straight_length_m: EngineeringNumber;
  total_equivalent_fitting_length_m: EngineeringNumber;
  total_equivalent_length_m: EngineeringNumber;
  total_pressure_drop_bar: EngineeringNumber;
  source_pressure_bar_g: EngineeringNumber;
  destination_pressure_bar_g: EngineeringNumber;
  destination_minimum_pressure_bar_g: EngineeringNumber | null;
  destination_pressure_margin_bar: EngineeringNumber | null;
  destination_pressure_is_adequate: boolean | null;
};

export type NetworkHydraulicResult = {
  network_code: string;
  path_results: NetworkPathResult[];
  worst_pressure_path_code: string;
  highest_pressure_drop_path_code: string;
  minimum_destination_pressure_bar_g: EngineeringNumber;
  maximum_path_pressure_drop_bar: EngineeringNumber;
  pressure_deficient_path_codes: string[];
  total_paths: number;
  adequate_paths: number;
  deficient_paths: number;
  network_pressure_is_adequate: boolean;
};

export type SegmentOptimizationRecommendation = {
  segment_code: string;
  segment_name: string;
  affected_deficient_paths: string[];
  current_internal_diameter_mm: EngineeringNumber;
  recommended_internal_diameter_mm: EngineeringNumber;
  current_velocity_m_per_s: EngineeringNumber;
  recommended_velocity_m_per_s: EngineeringNumber;
  current_pressure_drop_bar: EngineeringNumber;
  recommended_pressure_drop_bar: EngineeringNumber;
  pressure_drop_reduction_bar: EngineeringNumber;
  pressure_drop_reduction_fraction: EngineeringNumber;
  recommendation_status: OptimizationRecommendationStatus;
  rationale: string[];
};

export type NetworkOptimizationResult = {
  network_code: string;
  deficient_path_codes: string[];
  recommendations: SegmentOptimizationRecommendation[];
  total_current_target_segment_drop_bar: EngineeringNumber;
  total_recommended_target_segment_drop_bar: EngineeringNumber;
  estimated_total_pressure_drop_reduction_bar: EngineeringNumber;
  optimization_required: boolean;
};

export type DistributionAnalysisResult = {
  validation: NetworkValidationResult;
  hydraulics: NetworkHydraulicResult;
  optimization: NetworkOptimizationResult | null;
};

export type DistributionExecutionResponse = {
  result: DistributionAnalysisResult;
  calculation_case_id: number | null;
};
