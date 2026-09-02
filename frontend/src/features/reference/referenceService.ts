import { apiRequest } from "../../services/apiClient";
import type { InputOptionsResponse } from "./referenceTypes";

export function fetchInputOptions(
  accessToken: string,
): Promise<InputOptionsResponse> {
  return apiRequest<InputOptionsResponse>("/reference/input-options", {
    method: "GET",
    accessToken,
  });
}
