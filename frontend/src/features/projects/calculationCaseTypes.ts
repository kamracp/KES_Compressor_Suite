export type CalculationType =
  | "COMPRESSION"
  | "RECIPROCATING"
  | "CENTRIFUGAL"
  | "ROTARY_SCREW"
  | "SELECTION";

export type CalculationStatus =
  | "DRAFT"
  | "COMPLETED"
  | "FAILED"
  | "ARCHIVED";

export type CalculationCase = {
  id: number;
  project_id: number;

  calculation_code: string;
  calculation_type: CalculationType;
  status: CalculationStatus;
  revision: number;

  title: string;
  description: string | null;

  input_data: Record<string, unknown>;
  result_data: Record<string, unknown> | null;

  engineering_notes: string | null;

  created_at: string;
  updated_at: string;
  completed_at: string | null;
};
