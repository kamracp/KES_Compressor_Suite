import { apiRequest } from "../../services/apiClient";

import type {
  CompressedAirLeakageManagementRequest,
  CompressedAirLeakageManagementResponse,
} from "./leakageTypes";

export function analyzeCompressedAirLeakage(
  accessToken: string,
  payload: CompressedAirLeakageManagementRequest,
): Promise<CompressedAirLeakageManagementResponse> {
  return apiRequest<CompressedAirLeakageManagementResponse>(
    "/compressed-air/leakage/analyze",
    {
      method: "POST",
      accessToken,
      body: JSON.stringify(payload),
    },
  );
}
