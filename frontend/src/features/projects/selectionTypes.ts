export type CompressorType =
  | "RECIPROCATING"
  | "CENTRIFUGAL"
  | "ROTARY_SCREW";

export type SelectionRating =
  | "EXCELLENT"
  | "GOOD"
  | "ACCEPTABLE"
  | "POOR";

export type CompressorSelectionCalculation = {
  required_flow_m3_per_hr: number;
  suction_pressure_bar: number;
  discharge_pressure_bar: number;
  required_turndown_fraction: number;
  continuous_operation: boolean;
  gas_molecular_weight: number;
  estimated_operating_hours_per_year: number;
};

export type CalculationExecutionMetadata = {
  persist_result: boolean;
  project_id?: number | null;
  calculation_code?: string | null;
  title?: string | null;
  engineering_notes?: string | null;
};

export type CompressorSelectionExecutionRequest = {
  calculation: CompressorSelectionCalculation;
  execution: CalculationExecutionMetadata;
};

export type CompressorOptionAssessment = {
  compressor_type: CompressorType;
  capacity_rating: SelectionRating;
  pressure_ratio_rating: SelectionRating;
  turndown_rating: SelectionRating;
  efficiency_rating: SelectionRating;
  maintenance_rating: SelectionRating;
  overall_score: string;
  rationale: string[];
};

export type CompressorSelectionResult = {
  recommended_type: CompressorType;
  reciprocating: CompressorOptionAssessment;
  centrifugal: CompressorOptionAssessment;
  rotary_screw: CompressorOptionAssessment;
  score_difference: string;
  recommendation_summary: string;
};

export type CompressorSelectionExecutionResponse = {
  result: CompressorSelectionResult;
  calculation_case_id: number | null;
};
