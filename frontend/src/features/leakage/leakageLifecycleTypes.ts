export type CompressedAirLeakLifecycleStatus =
  | "TAGGED"
  | "ASSIGNED"
  | "CLOSED";

export type LeakageLifecycleJsonObject = Record<
  string,
  unknown
>;

export type CompressedAirLeakCreateRequest = {
  leak_code: string;
  location: string;
  source_snapshot: LeakageLifecycleJsonObject;
};

export type CompressedAirLeakAssignRequest = {
  assigned_to: string;
  change_notes?: string | null;
};

export type CompressedAirLeakCloseRequest = {
  closure_evidence: LeakageLifecycleJsonObject;
  closure_notes?: string | null;
  change_notes?: string | null;
};

export type CompressedAirLeakKpiSnapshotCreateRequest = {
  snapshot_code: string;
  metrics_payload: LeakageLifecycleJsonObject;
};

export type CompressedAirLeakStatusHistoryResponse = {
  id: number;
  leak_id: number;
  previous_status:
    | CompressedAirLeakLifecycleStatus
    | null;
  new_status: CompressedAirLeakLifecycleStatus;
  changed_by: string | null;
  change_notes: string | null;
  changed_at: string;
};

export type CompressedAirLeakKpiSnapshotResponse = {
  id: number;
  leak_id: number;
  snapshot_code: string;
  lifecycle_status: CompressedAirLeakLifecycleStatus;
  metrics_payload: LeakageLifecycleJsonObject;
  captured_by: string | null;
  captured_at: string;
};

export type CompressedAirLeakResponse = {
  id: number;
  project_id: number;
  leak_code: string;
  location: string;
  lifecycle_status: CompressedAirLeakLifecycleStatus;
  assigned_to: string | null;
  source_snapshot: LeakageLifecycleJsonObject;
  closure_evidence: LeakageLifecycleJsonObject | null;
  closure_notes: string | null;
  created_by: string | null;
  updated_by: string | null;
  tagged_at: string;
  assigned_at: string | null;
  closed_at: string | null;
  created_at: string;
  updated_at: string;
};

export type CompressedAirLeakListResponse = {
  project_id: number;
  total_leaks: number;
  tagged_leaks: number;
  assigned_leaks: number;
  closed_leaks: number;
  items: CompressedAirLeakResponse[];
};
