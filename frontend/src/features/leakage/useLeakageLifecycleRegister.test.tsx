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

import { listCompressedAirLeaks } from "./leakageLifecycleService";
import type {
  CompressedAirLeakListResponse,
} from "./leakageLifecycleTypes";
import {
  leakageLifecycleQueryKeys,
  useLeakageLifecycleRegister,
} from "./useLeakageLifecycleRegister";

vi.mock("./leakageLifecycleService", () => ({
  listCompressedAirLeaks: vi.fn(),
}));

const registerFixture: CompressedAirLeakListResponse = {
  project_id: 42,
  total_leaks: 1,
  tagged_leaks: 1,
  assigned_leaks: 0,
  closed_leaks: 0,
  items: [
    {
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
      tagged_at: "2026-09-09T08:00:00Z",
      assigned_at: null,
      closed_at: null,
      created_at: "2026-09-09T08:00:00Z",
      updated_at: "2026-09-09T08:00:00Z",
    },
  ],
};

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

describe("useLeakageLifecycleRegister", () => {
  beforeEach(() => {
    vi.mocked(listCompressedAirLeaks).mockReset();
  });

  it("fetches and caches the project leakage register", async () => {
    vi.mocked(
      listCompressedAirLeaks,
    ).mockResolvedValue(registerFixture);

    const {
      queryClient,
      Wrapper,
    } = createHarness();

    const { result } = renderHook(
      () =>
        useLeakageLifecycleRegister(
          "test-access-token",
          42,
        ),
      {
        wrapper: Wrapper,
      },
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(listCompressedAirLeaks).toHaveBeenCalledTimes(1);
    expect(listCompressedAirLeaks).toHaveBeenCalledWith(
      "test-access-token",
      42,
    );
    expect(result.current.data).toEqual(registerFixture);
    expect(
      queryClient.getQueryData(
        leakageLifecycleQueryKeys.register(42),
      ),
    ).toEqual(registerFixture);
  });

  it.each([
    [
      null,
      42,
      true,
    ],
    [
      "test-access-token",
      0,
      true,
    ],
    [
      "test-access-token",
      42,
      false,
    ],
  ] as const)(
    "stays idle for token=%s project=%s enabled=%s",
    (
      accessToken,
      projectId,
      enabled,
    ) => {
      const { Wrapper } = createHarness();

      const { result } = renderHook(
        () =>
          useLeakageLifecycleRegister(
            accessToken,
            projectId,
            enabled,
          ),
        {
          wrapper: Wrapper,
        },
      );

      expect(result.current.fetchStatus).toBe("idle");
      expect(listCompressedAirLeaks).not.toHaveBeenCalled();
    },
  );

  it("exposes lifecycle API failures", async () => {
    vi.mocked(
      listCompressedAirLeaks,
    ).mockRejectedValue(
      new Error("Leakage register request failed."),
    );

    const { Wrapper } = createHarness();

    const { result } = renderHook(
      () =>
        useLeakageLifecycleRegister(
          "test-access-token",
          42,
        ),
      {
        wrapper: Wrapper,
      },
    );

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toEqual(
      new Error("Leakage register request failed."),
    );
  });
});
