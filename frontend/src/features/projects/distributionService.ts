import { apiRequest } from "../../services/apiClient";
import type {
  DistributionAnalysisResult,
  DistributionCalculationRequest,
  DistributionExecutionRequest,
  DistributionExecutionResponse,
} from "./distributionTypes";

export function calculateDistributionNetwork(
  accessToken: string,
  payload: DistributionCalculationRequest,
): Promise<DistributionAnalysisResult> {
  return apiRequest<DistributionAnalysisResult>(
    "/compressed-air/distribution/calculate",
    {
      method: "POST",
      accessToken,
      body: JSON.stringify(payload),
    },
  );
}

export function executeDistributionCalculation(
  accessToken: string,
  payload: DistributionExecutionRequest,
): Promise<DistributionExecutionResponse> {
  return apiRequest<DistributionExecutionResponse>(
    "/compressed-air/distribution/execute",
    {
      method: "POST",
      accessToken,
      body: JSON.stringify(payload),
    },
  );
}
