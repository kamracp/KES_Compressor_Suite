import { apiRequest } from "../../services/apiClient";

import type {
  AirSkidAssessmentRequest,
  AirSkidAssessmentResponse,
} from "./skidTypes";

export function assessCompressedAirSkid(
  accessToken: string,
  payload: AirSkidAssessmentRequest,
): Promise<AirSkidAssessmentResponse> {
  return apiRequest<AirSkidAssessmentResponse>(
    "/compressed-air/skid/assess",
    {
      method: "POST",
      accessToken,
      body: JSON.stringify(payload),
    },
  );
}
