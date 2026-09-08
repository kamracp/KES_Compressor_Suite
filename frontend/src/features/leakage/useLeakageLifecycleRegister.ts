import { useQuery } from "@tanstack/react-query";

import { listCompressedAirLeaks } from "./leakageLifecycleService";

export const leakageLifecycleQueryKeys = {
  register: (projectId: number) =>
    [
      "compressed-air",
      "leakage",
      "lifecycle",
      "projects",
      projectId,
      "records",
    ] as const,
};

export function useLeakageLifecycleRegister(
  accessToken: string | null,
  projectId: number,
  enabled = true,
) {
  const hasValidProjectId =
    Number.isInteger(projectId) &&
    projectId > 0;

  return useQuery({
    queryKey:
      leakageLifecycleQueryKeys.register(projectId),
    queryFn: () => {
      if (!accessToken) {
        throw new Error(
          "Authenticated access token is required.",
        );
      }

      if (!hasValidProjectId) {
        throw new Error(
          "Valid project ID is required.",
        );
      }

      return listCompressedAirLeaks(
        accessToken,
        projectId,
      );
    },
    enabled:
      enabled &&
      Boolean(accessToken) &&
      hasValidProjectId,
  });
}
