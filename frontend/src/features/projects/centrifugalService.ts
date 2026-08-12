import { apiRequest } from "../../services/apiClient";
import type {
  CentrifugalExecutionRequest,
  CentrifugalExecutionResponse,
} from "./centrifugalTypes";

export function executeCentrifugalCalculation(
  accessToken: string,
  payload: CentrifugalExecutionRequest,
): Promise<CentrifugalExecutionResponse> {
  return apiRequest<CentrifugalExecutionResponse>(
    "/compressor-execution/centrifugal",
    {
      method: "POST",
      accessToken,
      body: JSON.stringify(payload),
    },
  );
}
