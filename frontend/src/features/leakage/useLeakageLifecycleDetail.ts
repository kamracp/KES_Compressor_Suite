import { useQuery } from "@tanstack/react-query";

import {
  getCompressedAirLeak,
  listCompressedAirLeakHistory,
  listCompressedAirLeakKpiSnapshots,
} from "./leakageLifecycleService";

export const leakageLifecycleDetailQueryKeys = {
  detail: (leakId: number) =>
    [
      "compressed-air",
      "leakage",
      "lifecycle",
      "records",
      leakId,
    ] as const,
  history: (leakId: number) =>
    [
      "compressed-air",
      "leakage",
      "lifecycle",
      "records",
      leakId,
      "history",
    ] as const,
  kpiSnapshots: (leakId: number) =>
    [
      "compressed-air",
      "leakage",
      "lifecycle",
      "records",
      leakId,
      "kpi-snapshots",
    ] as const,
};

function hasValidLeakId(leakId: number): boolean {
  return Number.isInteger(leakId) && leakId > 0;
}

export function useLeakageLifecycleDetail(
  accessToken: string | null,
  leakId: number,
  enabled = true,
) {
  const canQuery =
    enabled &&
    Boolean(accessToken) &&
    hasValidLeakId(leakId);

  const detailQuery = useQuery({
    queryKey:
      leakageLifecycleDetailQueryKeys.detail(leakId),
    queryFn: () => {
      if (!accessToken) {
        throw new Error(
          "Authenticated access token is required.",
        );
      }

      if (!hasValidLeakId(leakId)) {
        throw new Error(
          "Valid leakage record ID is required.",
        );
      }

      return getCompressedAirLeak(
        accessToken,
        leakId,
      );
    },
    enabled: canQuery,
  });

  const historyQuery = useQuery({
    queryKey:
      leakageLifecycleDetailQueryKeys.history(leakId),
    queryFn: () => {
      if (!accessToken) {
        throw new Error(
          "Authenticated access token is required.",
        );
      }

      if (!hasValidLeakId(leakId)) {
        throw new Error(
          "Valid leakage record ID is required.",
        );
      }

      return listCompressedAirLeakHistory(
        accessToken,
        leakId,
      );
    },
    enabled: canQuery,
  });

  const kpiSnapshotsQuery = useQuery({
    queryKey:
      leakageLifecycleDetailQueryKeys.kpiSnapshots(
        leakId,
      ),
    queryFn: () => {
      if (!accessToken) {
        throw new Error(
          "Authenticated access token is required.",
        );
      }

      if (!hasValidLeakId(leakId)) {
        throw new Error(
          "Valid leakage record ID is required.",
        );
      }

      return listCompressedAirLeakKpiSnapshots(
        accessToken,
        leakId,
      );
    },
    enabled: canQuery,
  });

  return {
    detailQuery,
    historyQuery,
    kpiSnapshotsQuery,
  };
}
