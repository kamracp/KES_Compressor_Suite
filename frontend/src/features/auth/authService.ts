import { apiRequest } from "../../services/apiClient";
import type {
  AccessTokenResponse,
  CurrentUserResponse,
  LoginRequest,
} from "../../types/auth";

export function login(
  payload: LoginRequest,
): Promise<AccessTokenResponse> {
  return apiRequest<AccessTokenResponse>(
    "/auth/login",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function getCurrentUser(
  accessToken: string,
): Promise<CurrentUserResponse> {
  return apiRequest<CurrentUserResponse>(
    "/auth/me",
    {
      accessToken,
    },
  );
}
