import { apiRequest } from "./apiClient";
import type { HealthResponse } from "../types/health";

export function getHealth(): Promise<HealthResponse> {
  return apiRequest<HealthResponse>("/health");
}
