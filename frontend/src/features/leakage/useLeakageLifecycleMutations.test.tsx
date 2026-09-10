import type { PropsWithChildren } from "react";

import {
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import {
  act,
  renderHook,
} from "@testing-library/react";
import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import {
  assignCompressedAirLeak,
  closeCompressedAirLeak,
  createCompressedAirLeak,
  createCompressedAirLeakKpiSnapshot,
} from "./leakageLifecycleService";
import type {
  CompressedAirLeakKpiSnapshotResponse,
  CompressedAirLeakResponse,
} from "./leakageLifecycleTypes";
import {
  leakageLifecycleDetailQueryKeys,
} from "./useLeakageLifecycleDetail";
import {
  useLeakageLifecycleMutations,
} from "./useLeakageLifecycleMutations";
import {
  leakageLifecycleQueryKeys,
} from "./useLeakageLifecycleRegister";

vi.mock("./leakageLifecycleService", () => ({
  assignCompressedAirLeak: vi.fn(),
  closeCompressedAirLeak: vi.fn(),
  createCompressedAirLeak: vi.fn(),
  createCompressedAirLeakKpiSnapshot: vi.fn(),
}));

const taggedLeakFixture: CompressedAirLeakResponse = {
  id: 17,
  project_id: 42,
  leak_code: "LEAK-001",
  location: "Compressor room",
  lifecycle_status: "TAGGED",
  assigned_to: null,
  source_snapshot: {
    baseline_leakage_flow_nm3_per_hr: "12.5",
  },
  closure_evidence: null,
  closure_notes: null,
  created_by: "surveyor@example.com",
  updated_by: "surveyor@example.com",
  tagged_at: "2026-09-10T08:00:00Z",
  assigned_at: null,
  closed_at: null,
  created_at: "2026-09-10T08:00:00Z",
  updated_at: "2026-09-10T08:00:00Z",
};

const assignedLeakFixture: CompressedAirLeakResponse = {
  ...taggedLeakFixture,
  lifecycle_status: "ASSIGNED",
  assigned_to: "maintenance@example.com",
  updated_by: "engineer@example.com",
  assigned_at: "2026-09-10T09:00:00Z",
  updated_at: "2026-09-10T09:00:00Z",
};

const closedLeakFixture: CompressedAirLeakResponse = {
  ...assignedLeakFixture,
  lifecycle_status: "CLOSED",
  closure_evidence: {
    verified_leakage_flow_nm3_per_hr: "0",
  },
  closure_notes: "Leak repaired and verified.",
  updated_by: "reviewer@example.com",
  closed_at: "2026-09-10T10:00:00Z",
  updated_at: "2026-09-10T10:00:00Z",
};

const kpiSnapshotFixture: CompressedAirLeakKpiSnapshotResponse = {
  id: 5,
  leak_id: 17,
  snapshot_code: "POST_REPAIR",
  lifecycle_status: "CLOSED",
  metrics_payload: {
    verified_leakage_flow_nm3_per_hr: "0",
  },
  captured_by: "reviewer@example.com",
  captured_at: "2026-09-10T10:05:00Z",
};

function createHarness() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
        retry: false,
      },
    },
  });

  function Wrapper({
    children,
  }: PropsWithChildren) {
    return (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );
  }

  return {
    queryClient,
    Wrapper,
  };
}

describe("useLeakageLifecycleMutations", () => {
  beforeEach(() => {
    vi.mocked(assignCompressedAirLeak).mockReset();
    vi.mocked(closeCompressedAirLeak).mockReset();
    vi.mocked(createCompressedAirLeak).mockReset();
    vi.mocked(
      createCompressedAirLeakKpiSnapshot,
    ).mockReset();
  });

  it("creates a tagged leak and invalidates its project register", async () => {
    vi.mocked(createCompressedAirLeak).mockResolvedValue(
      taggedLeakFixture,
    );

    const {
      queryClient,
      Wrapper,
    } = createHarness();
    const invalidateQueries = vi.spyOn(
      queryClient,
      "invalidateQueries",
    );

    const { result } = renderHook(
      () =>
        useLeakageLifecycleMutations(
          "test-access-token",
          42,
        ),
      {
        wrapper: Wrapper,
      },
    );

    const payload = {
      leak_code: "LEAK-001",
      location: "Compressor room",
      source_snapshot: {
        baseline_leakage_flow_nm3_per_hr: "12.5",
      },
    };

    await act(async () => {
      await result.current.createMutation.mutateAsync(
        payload,
      );
    });

    expect(createCompressedAirLeak).toHaveBeenCalledWith(
      "test-access-token",
      42,
      payload,
    );
    expect(invalidateQueries).toHaveBeenCalledWith({
      queryKey:
        leakageLifecycleQueryKeys.register(42),
      exact: true,
    });
  });

  it("assigns a tagged leak and invalidates register, detail, and history", async () => {
    vi.mocked(assignCompressedAirLeak).mockResolvedValue(
      assignedLeakFixture,
    );

    const {
      queryClient,
      Wrapper,
    } = createHarness();
    const invalidateQueries = vi.spyOn(
      queryClient,
      "invalidateQueries",
    );

    const { result } = renderHook(
      () =>
        useLeakageLifecycleMutations(
          "test-access-token",
          42,
        ),
      {
        wrapper: Wrapper,
      },
    );

    const payload = {
      assigned_to: "maintenance@example.com",
      change_notes: "Assigned after survey review.",
    };

    await act(async () => {
      await result.current.assignMutation.mutateAsync({
        leakId: 17,
        payload,
      });
    });

    expect(assignCompressedAirLeak).toHaveBeenCalledWith(
      "test-access-token",
      17,
      payload,
    );
    expect(invalidateQueries).toHaveBeenCalledTimes(3);
    expect(invalidateQueries).toHaveBeenCalledWith({
      queryKey:
        leakageLifecycleQueryKeys.register(42),
      exact: true,
    });
    expect(invalidateQueries).toHaveBeenCalledWith({
      queryKey:
        leakageLifecycleDetailQueryKeys.detail(17),
      exact: true,
    });
    expect(invalidateQueries).toHaveBeenCalledWith({
      queryKey:
        leakageLifecycleDetailQueryKeys.history(17),
      exact: true,
    });
  });

  it("closes an assigned leak and refreshes its lifecycle state", async () => {
    vi.mocked(closeCompressedAirLeak).mockResolvedValue(
      closedLeakFixture,
    );

    const {
      queryClient,
      Wrapper,
    } = createHarness();
    const invalidateQueries = vi.spyOn(
      queryClient,
      "invalidateQueries",
    );

    const { result } = renderHook(
      () =>
        useLeakageLifecycleMutations(
          "test-access-token",
          42,
        ),
      {
        wrapper: Wrapper,
      },
    );

    const payload = {
      closure_evidence: {
        verified_leakage_flow_nm3_per_hr: "0",
      },
      closure_notes: "Leak repaired and verified.",
      change_notes: "Closed after ultrasonic verification.",
    };

    await act(async () => {
      await result.current.closeMutation.mutateAsync({
        leakId: 17,
        payload,
      });
    });

    expect(closeCompressedAirLeak).toHaveBeenCalledWith(
      "test-access-token",
      17,
      payload,
    );
    expect(invalidateQueries).toHaveBeenCalledTimes(3);
    expect(invalidateQueries).toHaveBeenCalledWith({
      queryKey:
        leakageLifecycleQueryKeys.register(42),
      exact: true,
    });
    expect(invalidateQueries).toHaveBeenCalledWith({
      queryKey:
        leakageLifecycleDetailQueryKeys.detail(17),
      exact: true,
    });
    expect(invalidateQueries).toHaveBeenCalledWith({
      queryKey:
        leakageLifecycleDetailQueryKeys.history(17),
      exact: true,
    });
  });

  it("creates a KPI snapshot and invalidates only that leak snapshot list", async () => {
    vi.mocked(
      createCompressedAirLeakKpiSnapshot,
    ).mockResolvedValue(kpiSnapshotFixture);

    const {
      queryClient,
      Wrapper,
    } = createHarness();
    const invalidateQueries = vi.spyOn(
      queryClient,
      "invalidateQueries",
    );

    const { result } = renderHook(
      () =>
        useLeakageLifecycleMutations(
          "test-access-token",
          42,
        ),
      {
        wrapper: Wrapper,
      },
    );

    const payload = {
      snapshot_code: "POST_REPAIR",
      metrics_payload: {
        verified_leakage_flow_nm3_per_hr: "0",
      },
    };

    await act(async () => {
      await result.current.createKpiSnapshotMutation.mutateAsync({
        leakId: 17,
        payload,
      });
    });

    expect(
      createCompressedAirLeakKpiSnapshot,
    ).toHaveBeenCalledWith(
      "test-access-token",
      17,
      payload,
    );
    expect(invalidateQueries).toHaveBeenCalledTimes(1);
    expect(invalidateQueries).toHaveBeenCalledWith({
      queryKey:
        leakageLifecycleDetailQueryKeys.kpiSnapshots(17),
      exact: true,
    });
  });

  it("rejects missing authentication and invalid lifecycle identifiers", async () => {
    const { Wrapper } = createHarness();

    const { result } = renderHook(
      () => useLeakageLifecycleMutations(null, 0),
      {
        wrapper: Wrapper,
      },
    );

    let createError: unknown;
    let assignError: unknown;

    await act(async () => {
      try {
        await result.current.createMutation.mutateAsync({
          leak_code: "LEAK-001",
          location: "Compressor room",
          source_snapshot: {},
        });
      } catch (error) {
        createError = error;
      }

      try {
        await result.current.assignMutation.mutateAsync({
          leakId: 0,
          payload: {
            assigned_to: "maintenance@example.com",
          },
        });
      } catch (error) {
        assignError = error;
      }
    });

    expect(createError).toEqual(
      new Error("Authenticated access token is required."),
    );
    expect(assignError).toEqual(
      new Error("Valid project ID is required."),
    );
    expect(createCompressedAirLeak).not.toHaveBeenCalled();
    expect(assignCompressedAirLeak).not.toHaveBeenCalled();
  });
});
