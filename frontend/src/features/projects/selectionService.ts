import { apiRequest } from "../../services/apiClient";
import type {
  CompressorSelectionExecutionRequest,
  CompressorSelectionExecutionResponse,
} from "./selectionTypes";

export function executeCompressorSelection(
  accessToken: string,
  payload: CompressorSelectionExecutionRequest,
): Promise<CompressorSelectionExecutionResponse> {
  return apiRequest<CompressorSelectionExecutionResponse>(
    "/compressor-execution/selection",
    {
      method: "POST",
      accessToken,
      body: JSON.stringify(payload),
    },
  );
}
