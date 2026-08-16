import { apiRequest } from "../../services/apiClient";

import type {
  AlliedEquipmentAnalysisRequest,
  AlliedEquipmentAnalysisResponse,
} from "./alliedTypes";

export function analyzeCompressedAirAlliedEquipment(
  accessToken: string,
  payload: AlliedEquipmentAnalysisRequest,
): Promise<AlliedEquipmentAnalysisResponse> {
  return apiRequest<AlliedEquipmentAnalysisResponse>(
    "/compressed-air/allied/analyze",
    {
      method: "POST",
      accessToken,
      body: JSON.stringify(payload),
    },
  );
}
