import { apiRequest } from "../../services/apiClient";
import type {
  GasPropertiesRequest,
  GasPropertiesResponse,
} from "./gasTypes";

export function calculateGasProperties(
  accessToken: string,
  payload: GasPropertiesRequest,
): Promise<GasPropertiesResponse> {
  return apiRequest<GasPropertiesResponse>(
    "/compressor/gas-properties/calculate",
    {
      method: "POST",
      accessToken,
      body: JSON.stringify(payload),
    },
  );
}
