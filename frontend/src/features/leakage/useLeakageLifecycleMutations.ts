import {
  useMutation,
  useQueryClient,
  type QueryClient,
} from "@tanstack/react-query";

import {
  assignCompressedAirLeak,
  closeCompressedAirLeak,
  createCompressedAirLeak,
  createCompressedAirLeakKpiSnapshot,
} from "./leakageLifecycleService";
import type {
  CompressedAirLeakAssignRequest,
  CompressedAirLeakCloseRequest,
  CompressedAirLeakCreateRequest,
  CompressedAirLeakKpiSnapshotCreateRequest,
} from "./leakageLifecycleTypes";
import {
  leakageLifecycleDetailQueryKeys,
} from "./useLeakageLifecycleDetail";
import {
  leakageLifecycleQueryKeys,
} from "./useLeakageLifecycleRegister";

export type AssignCompressedAirLeakVariables = {
  leakId: number;
  payload: CompressedAirLeakAssignRequest;
};

export type CloseCompressedAirLeakVariables = {
  leakId: number;
  payload: CompressedAirLeakCloseRequest;
};

export type CreateLeakageKpiSnapshotVariables = {
  leakId: number;
  payload: CompressedAirLeakKpiSnapshotCreateRequest;
};

function requireAccessToken(
  accessToken: string | null,
): string {
  if (!accessToken) {
    throw new Error(
      "Authenticated access token is required.",
    );
  }

  return accessToken;
}

function requirePositiveInteger(
  value: number,
  label: string,
): number {
  if (!Number.isInteger(value) || value <= 0) {
    throw new Error(`Valid ${label} ID is required.`);
  }

  return value;
}

async function invalidateRegister(
  queryClient: QueryClient,
  projectId: number,
): Promise<void> {
  await queryClient.invalidateQueries({
    queryKey:
      leakageLifecycleQueryKeys.register(projectId),
    exact: true,
  });
}

async function invalidateLeakDetail(
  queryClient: QueryClient,
  leakId: number,
): Promise<void> {
  await Promise.all([
    queryClient.invalidateQueries({
      queryKey:
        leakageLifecycleDetailQueryKeys.detail(leakId),
      exact: true,
    }),
    queryClient.invalidateQueries({
      queryKey:
        leakageLifecycleDetailQueryKeys.history(leakId),
      exact: true,
    }),
  ]);
}

export function useLeakageLifecycleMutations(
  accessToken: string | null,
  projectId: number,
) {
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: (
      payload: CompressedAirLeakCreateRequest,
    ) =>
      createCompressedAirLeak(
        requireAccessToken(accessToken),
        requirePositiveInteger(projectId, "project"),
        payload,
      ),
    onSuccess: async () => {
      await invalidateRegister(
        queryClient,
        projectId,
      );
    },
  });

  const assignMutation = useMutation({
    mutationFn: ({
      leakId,
      payload,
    }: AssignCompressedAirLeakVariables) => {
      requirePositiveInteger(projectId, "project");

      return assignCompressedAirLeak(
        requireAccessToken(accessToken),
        requirePositiveInteger(leakId, "leakage record"),
        payload,
      );
    },
    onSuccess: async (leak) => {
      await Promise.all([
        invalidateRegister(queryClient, projectId),
        invalidateLeakDetail(queryClient, leak.id),
      ]);
    },
  });

  const closeMutation = useMutation({
    mutationFn: ({
      leakId,
      payload,
    }: CloseCompressedAirLeakVariables) => {
      requirePositiveInteger(projectId, "project");

      return closeCompressedAirLeak(
        requireAccessToken(accessToken),
        requirePositiveInteger(leakId, "leakage record"),
        payload,
      );
    },
    onSuccess: async (leak) => {
      await Promise.all([
        invalidateRegister(queryClient, projectId),
        invalidateLeakDetail(queryClient, leak.id),
      ]);
    },
  });

  const createKpiSnapshotMutation = useMutation({
    mutationFn: ({
      leakId,
      payload,
    }: CreateLeakageKpiSnapshotVariables) => {
      requirePositiveInteger(projectId, "project");

      return createCompressedAirLeakKpiSnapshot(
        requireAccessToken(accessToken),
        requirePositiveInteger(leakId, "leakage record"),
        payload,
      );
    },
    onSuccess: async (snapshot) => {
      await queryClient.invalidateQueries({
        queryKey:
          leakageLifecycleDetailQueryKeys.kpiSnapshots(
            snapshot.leak_id,
          ),
        exact: true,
      });
    },
  });

  return {
    createMutation,
    assignMutation,
    closeMutation,
    createKpiSnapshotMutation,
  };
}
