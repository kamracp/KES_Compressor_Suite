import { apiRequest } from "../../services/apiClient";
import type {
  RotaryScrewExecutionRequest,
  RotaryScrewExecutionResponse,
} from "./rotaryScrewTypes";

export function executeRotaryScrewCalculation(
  accessToken: string,
  payload: RotaryScrewExecutionRequest,
): Promise<RotaryScrewExecutionResponse> {
  return apiRequest<RotaryScrewExecutionResponse>(
    "/compressor-execution/rotary-screw",
    {
      method: "POST",
      accessToken,
      body: JSON.stringify(payload),
    },
  );
}
