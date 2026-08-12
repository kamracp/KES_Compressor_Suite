import { apiRequest } from "../../services/apiClient";
import type {
  ReciprocatingExecutionRequest,
  ReciprocatingExecutionResponse,
} from "./reciprocatingTypes";

export function executeReciprocatingCalculation(
  accessToken: string,
  payload: ReciprocatingExecutionRequest,
): Promise<ReciprocatingExecutionResponse> {
  return apiRequest<ReciprocatingExecutionResponse>(
    "/compressor-execution/reciprocating",
    {
      method: "POST",
      accessToken,
      body: JSON.stringify(payload),
    },
  );
}
