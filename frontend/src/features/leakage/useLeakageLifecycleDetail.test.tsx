import type { PropsWithChildren } from "react";

import {
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import {
  renderHook,
  waitFor,
} from "@testing-library/react";
import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import {
  getCompressedAirLeak,
  listCompressedAirLeakHistory,
  listCompressedAirLeakKpiSnapshots,
} from "./leakageLifecycleService";
import type {
  CompressedAirLeakKpiSnapshotResponse,
  CompressedAirLeakResponse,
  CompressedAirLeakStatusHistoryResponse,
} from "./leakageLifecycleTypes";
import {
  leakageLifecycleDetailQueryKeys,
  useLeakageLifecycleDetail,
} from "./useLeakageLifecycleDetail";

vi.mock("./leakageLifecycleService", () => ({
  getCompressedAirLeak: vi.fn(),
  listCompressedAirLeakHistory: vi.fn(),
  listCompressedAirLeakKpiSnapshots: vi.fn(),
}));

const leakFixture: CompressedAirLeakResponse = {
  id: 17,
  project_id: 42,
  leak_code: "LEAK-001",
  location: "Compressor room",
  lifecycle_status: "ASSIGNED",
  assigned_to: "maintenance@example.com",
  source_snapshot: {
    baseline_leakage_flow_nm3_per_hr: "12.5",
  },
  closure_evidence: null,
  closure_notes: null,
  created_by: "surveyor@example.com",
  updated_by: "engineer@example.com",
  tagged_at: "2026-09-09T08:00:00Z",
  assigned_at: "2026-09-09T09:00:00Z",
  closed_at: null,
  created_at: "2026-09-09T08:00:00Z",
  updated_at: "2026-09-09T09:00:00Z",
};

const historyFixture: CompressedAirLeakStatusHistoryResponse[] = [
  {
    id: 1,
    leak_id: 17,
    previous_status: null,
    new_status: "TAGGED",
    changed_by: "surveyor@example.com",
    change_notes: "Leak tagged during survey.",
    changed_at: "2026-09-09T08:00:00Z",
  },
  {
    id: 2,
    leak_id: 17,
    previous_status: "TAGGED",
    new_status: "ASSIGNED",
    changed_by: "engineer@example.com",
    change_notes: "Assigned to maintenance.",
    changed_at: "2026-09-09T09:00:00Z",
  },
];

const kpiFixture: CompressedAirLeakKpiSnapshotResponse[] = [
  {
    id: 5,
    leak_id: 17,
    snapshot_code: "BASELINE",
    lifecycle_status: "ASSIGNED",
    metrics_payload: {
      leakage_flow_nm3_per_hr: "12.5",
    },
    captured_by: "engineer@example.com",
    captured_at: "2026-09-09T09:05:00Z",
  },
];

function createHarness() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
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

describe("useLeakageLifecycleDetail", () => {
  beforeEach(() => {
    vi.mocked(getCompressedAirLeak).mockReset();
    vi.mocked(listCompressedAirLeakHistory).mockReset();
    vi.mocked(listCompressedAirLeakKpiSnapshots).mockReset();
  });

  it("fetches and caches detail, history, and KPI snapshots", async () => {
    vi.mocked(getCompressedAirLeak).mockResolvedValue(
      leakFixture,
    );
    vi.mocked(
      listCompressedAirLeakHistory,
    ).mockResolvedValue(historyFixture);
    vi.mocked(
      listCompressedAirLeakKpiSnapshots,
    ).mockResolvedValue(kpiFixture);

    const {
      queryClient,
      Wrapper,
    } = createHarness();

    const { result } = renderHook(
      () =>
        useLeakageLifecycleDetail(
          "test-access-token",
          17,
        ),
      {
        wrapper: Wrapper,
      },
    );

    await waitFor(() => {
      expect(result.current.detailQuery.isSuccess).toBe(true);
      expect(result.current.historyQuery.isSuccess).toBe(true);
      expect(
        result.current.kpiSnapshotsQuery.isSuccess,
      ).toBe(true);
    });

    expect(getCompressedAirLeak).toHaveBeenCalledWith(
      "test-access-token",
      17,
    );
    expect(
      listCompressedAirLeakHistory,
    ).toHaveBeenCalledWith(
      "test-access-token",
      17,
    );
    expect(
      listCompressedAirLeakKpiSnapshots,
    ).toHaveBeenCalledWith(
      "test-access-token",
      17,
    );

    expect(
      queryClient.getQueryData(
        leakageLifecycleDetailQueryKeys.detail(17),
      ),
    ).toEqual(leakFixture);
    expect(
      queryClient.getQueryData(
        leakageLifecycleDetailQueryKeys.history(17),
      ),
    ).toEqual(historyFixture);
    expect(
      queryClient.getQueryData(
        leakageLifecycleDetailQueryKeys.kpiSnapshots(17),
      ),
    ).toEqual(kpiFixture);
  });

  it.each([
    [null, 17, true],
    ["test-access-token", 0, true],
    ["test-access-token", 17, false],
  ] as const)(
    "stays idle for token=%s leak=%s enabled=%s",
    (
      accessToken,
      leakId,
      enabled,
    ) => {
      const { Wrapper } = createHarness();

      const { result } = renderHook(
        () =>
          useLeakageLifecycleDetail(
            accessToken,
            leakId,
            enabled,
          ),
        {
          wrapper: Wrapper,
        },
      );

      expect(result.current.detailQuery.fetchStatus).toBe(
        "idle",
      );
      expect(result.current.historyQuery.fetchStatus).toBe(
        "idle",
      );
      expect(
        result.current.kpiSnapshotsQuery.fetchStatus,
      ).toBe("idle");

      expect(getCompressedAirLeak).not.toHaveBeenCalled();
      expect(
        listCompressedAirLeakHistory,
      ).not.toHaveBeenCalled();
      expect(
        listCompressedAirLeakKpiSnapshots,
      ).not.toHaveBeenCalled();
    },
  );

  it("exposes independent lifecycle query failures", async () => {
    vi.mocked(getCompressedAirLeak).mockResolvedValue(
      leakFixture,
    );
    vi.mocked(
      listCompressedAirLeakHistory,
    ).mockRejectedValue(
      new Error("Leak history request failed."),
    );
    vi.mocked(
      listCompressedAirLeakKpiSnapshots,
    ).mockResolvedValue(kpiFixture);

    const { Wrapper } = createHarness();

    const { result } = renderHook(
      () =>
        useLeakageLifecycleDetail(
          "test-access-token",
          17,
        ),
      {
        wrapper: Wrapper,
      },
    );

    await waitFor(() => {
      expect(result.current.detailQuery.isSuccess).toBe(true);
      expect(result.current.historyQuery.isError).toBe(true);
      expect(
        result.current.kpiSnapshotsQuery.isSuccess,
      ).toBe(true);
    });

    expect(result.current.historyQuery.error).toEqual(
      new Error("Leak history request failed."),
    );
  });
});
