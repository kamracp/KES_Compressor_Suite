import { apiRequest } from "../../services/apiClient";
import type {
  GreenfieldSystemDesignRequest,
  GreenfieldSystemDesignResponse,
} from "./greenfieldTypes";

export function designGreenfieldSystem(
  accessToken: string,
  payload: GreenfieldSystemDesignRequest,
): Promise<GreenfieldSystemDesignResponse> {
  return apiRequest<GreenfieldSystemDesignResponse>(
    "/compressed-air/greenfield/design",
    {
      method: "POST",
      accessToken,
      body: JSON.stringify(payload),
    },
  );
}
