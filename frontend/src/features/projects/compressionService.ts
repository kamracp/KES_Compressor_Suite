import { apiRequest } from "../../services/apiClient";
import type {
  CompressionExecutionRequest,
  CompressionExecutionResponse,
} from "./compressionTypes";

export function executeCompressionCalculation(
  accessToken: string,
  payload: CompressionExecutionRequest,
): Promise<CompressionExecutionResponse> {
  return apiRequest<CompressionExecutionResponse>(
    "/compressor-execution/compression",
    {
      method: "POST",
      accessToken,
      body: JSON.stringify(payload),
    },
  );
}
