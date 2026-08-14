import { apiRequest } from "../../services/apiClient";

import type {
  CompressedAirPerformanceAnalysisRequest,
  CompressedAirPerformanceAnalysisResponse,
} from "./performanceTypes";

export function analyzeCompressedAirPerformance(
  accessToken: string,
  payload: CompressedAirPerformanceAnalysisRequest,
): Promise<CompressedAirPerformanceAnalysisResponse> {
  return apiRequest<CompressedAirPerformanceAnalysisResponse>(
    "/compressed-air/performance/analyze",
    {
      method: "POST",
      accessToken,
      body: JSON.stringify(payload),
    },
  );
}
