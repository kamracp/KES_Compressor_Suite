import { apiRequest } from "../../services/apiClient";

import type {
  BrownfieldSystemAuditRequest,
  BrownfieldSystemAuditResponse,
} from "./brownfieldTypes";

export function analyzeBrownfieldSystem(
  accessToken: string,
  payload: BrownfieldSystemAuditRequest,
): Promise<BrownfieldSystemAuditResponse> {
  return apiRequest<BrownfieldSystemAuditResponse>(
    "/compressed-air/brownfield/audit",
    {
      method: "POST",
      accessToken,
      body: JSON.stringify(payload),
    },
  );
}
