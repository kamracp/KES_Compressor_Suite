import { apiRequest } from "../../services/apiClient";

import type {
  CompressedAirLeakAssignRequest,
  CompressedAirLeakCloseRequest,
  CompressedAirLeakCreateRequest,
  CompressedAirLeakKpiSnapshotCreateRequest,
  CompressedAirLeakKpiSnapshotResponse,
  CompressedAirLeakListResponse,
  CompressedAirLeakResponse,
  CompressedAirLeakStatusHistoryResponse,
} from "./leakageLifecycleTypes";

const LEAKAGE_PATH = "/compressed-air/leakage";

export function createCompressedAirLeak(
  accessToken: string,
  projectId: number,
  payload: CompressedAirLeakCreateRequest,
): Promise<CompressedAirLeakResponse> {
  return apiRequest<CompressedAirLeakResponse>(
    `${LEAKAGE_PATH}/projects/${projectId}/records`,
    {
      method: "POST",
      accessToken,
      body: JSON.stringify(payload),
    },
  );
}

export function listCompressedAirLeaks(
  accessToken: string,
  projectId: number,
): Promise<CompressedAirLeakListResponse> {
  return apiRequest<CompressedAirLeakListResponse>(
    `${LEAKAGE_PATH}/projects/${projectId}/records`,
    {
      accessToken,
    },
  );
}

export function getCompressedAirLeak(
  accessToken: string,
  leakId: number,
): Promise<CompressedAirLeakResponse> {
  return apiRequest<CompressedAirLeakResponse>(
    `${LEAKAGE_PATH}/records/${leakId}`,
    {
      accessToken,
    },
  );
}

export function assignCompressedAirLeak(
  accessToken: string,
  leakId: number,
  payload: CompressedAirLeakAssignRequest,
): Promise<CompressedAirLeakResponse> {
  return apiRequest<CompressedAirLeakResponse>(
    `${LEAKAGE_PATH}/records/${leakId}/assign`,
    {
      method: "PATCH",
      accessToken,
      body: JSON.stringify(payload),
    },
  );
}

export function closeCompressedAirLeak(
  accessToken: string,
  leakId: number,
  payload: CompressedAirLeakCloseRequest,
): Promise<CompressedAirLeakResponse> {
  return apiRequest<CompressedAirLeakResponse>(
    `${LEAKAGE_PATH}/records/${leakId}/close`,
    {
      method: "PATCH",
      accessToken,
      body: JSON.stringify(payload),
    },
  );
}

export function listCompressedAirLeakHistory(
  accessToken: string,
  leakId: number,
): Promise<CompressedAirLeakStatusHistoryResponse[]> {
  return apiRequest<
    CompressedAirLeakStatusHistoryResponse[]
  >(`${LEAKAGE_PATH}/records/${leakId}/history`, {
    accessToken,
  });
}

export function createCompressedAirLeakKpiSnapshot(
  accessToken: string,
  leakId: number,
  payload: CompressedAirLeakKpiSnapshotCreateRequest,
): Promise<CompressedAirLeakKpiSnapshotResponse> {
  return apiRequest<CompressedAirLeakKpiSnapshotResponse>(
    `${LEAKAGE_PATH}/records/${leakId}/kpi-snapshots`,
    {
      method: "POST",
      accessToken,
      body: JSON.stringify(payload),
    },
  );
}

export function listCompressedAirLeakKpiSnapshots(
  accessToken: string,
  leakId: number,
): Promise<CompressedAirLeakKpiSnapshotResponse[]> {
  return apiRequest<CompressedAirLeakKpiSnapshotResponse[]>(
    `${LEAKAGE_PATH}/records/${leakId}/kpi-snapshots`,
    {
      accessToken,
    },
  );
}
