import { apiRequest } from "../../services/apiClient";

import type {
  PartLoadComparisonRequest,
  PartLoadComparisonResponse,
} from "./partLoadTypes";

export function comparePartLoadModes(
  accessToken: string,
  payload: PartLoadComparisonRequest,
): Promise<PartLoadComparisonResponse> {
  return apiRequest<PartLoadComparisonResponse>(
    "/compressed-air/performance/part-load",
    {
      method: "POST",
      accessToken,
      body: JSON.stringify(payload),
    },
  );
}
