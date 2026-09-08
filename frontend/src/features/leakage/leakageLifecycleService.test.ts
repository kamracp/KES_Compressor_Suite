import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import { apiRequest } from "../../services/apiClient";
import {
  assignCompressedAirLeak,
  closeCompressedAirLeak,
  createCompressedAirLeak,
  createCompressedAirLeakKpiSnapshot,
  getCompressedAirLeak,
  listCompressedAirLeakHistory,
  listCompressedAirLeakKpiSnapshots,
  listCompressedAirLeaks,
} from "./leakageLifecycleService";

vi.mock("../../services/apiClient", () => ({
  apiRequest: vi.fn(),
}));

const apiRequestMock = vi.mocked(apiRequest);

describe("leakageLifecycleService", () => {
  beforeEach(() => {
    apiRequestMock.mockReset();
    apiRequestMock.mockResolvedValue(
      undefined as never,
    );
  });

  it("creates a project-scoped leakage record", async () => {
    const payload = {
      leak_code: "LEAK-001",
      location: "Compressor room",
      source_snapshot: {
        baseline_leakage_flow_nm3_per_hr: "12.5",
      },
    };

    await createCompressedAirLeak(
      "access-token",
      42,
      payload,
    );

    expect(apiRequestMock).toHaveBeenCalledWith(
      "/compressed-air/leakage/projects/42/records",
      {
        method: "POST",
        accessToken: "access-token",
        body: JSON.stringify(payload),
      },
    );
  });

  it("lists and gets leakage records", async () => {
    await listCompressedAirLeaks(
      "access-token",
      42,
    );

    await getCompressedAirLeak(
      "access-token",
      17,
    );

    expect(apiRequestMock).toHaveBeenNthCalledWith(
      1,
      "/compressed-air/leakage/projects/42/records",
      {
        accessToken: "access-token",
      },
    );

    expect(apiRequestMock).toHaveBeenNthCalledWith(
      2,
      "/compressed-air/leakage/records/17",
      {
        accessToken: "access-token",
      },
    );
  });

  it("assigns and closes leakage records", async () => {
    const assignPayload = {
      assigned_to: "maintenance@example.com",
      change_notes: "Assigned for repair.",
    };

    const closePayload = {
      closure_evidence: {
        verified_post_repair_flow_nm3_per_hr: "0.8",
      },
      closure_notes: "Repair verified.",
      change_notes: "Closed after verification.",
    };

    await assignCompressedAirLeak(
      "access-token",
      17,
      assignPayload,
    );

    await closeCompressedAirLeak(
      "access-token",
      17,
      closePayload,
    );

    expect(apiRequestMock).toHaveBeenNthCalledWith(
      1,
      "/compressed-air/leakage/records/17/assign",
      {
        method: "PATCH",
        accessToken: "access-token",
        body: JSON.stringify(assignPayload),
      },
    );

    expect(apiRequestMock).toHaveBeenNthCalledWith(
      2,
      "/compressed-air/leakage/records/17/close",
      {
        method: "PATCH",
        accessToken: "access-token",
        body: JSON.stringify(closePayload),
      },
    );
  });

  it("lists immutable leakage status history", async () => {
    await listCompressedAirLeakHistory(
      "access-token",
      17,
    );

    expect(apiRequestMock).toHaveBeenCalledWith(
      "/compressed-air/leakage/records/17/history",
      {
        accessToken: "access-token",
      },
    );
  });

  it("creates and lists leakage KPI snapshots", async () => {
    const payload = {
      snapshot_code: "KPI-001",
      metrics_payload: {
        leakage_flow_nm3_per_hr: "12.5",
        annual_cost: "45000",
      },
    };

    await createCompressedAirLeakKpiSnapshot(
      "access-token",
      17,
      payload,
    );

    await listCompressedAirLeakKpiSnapshots(
      "access-token",
      17,
    );

    expect(apiRequestMock).toHaveBeenNthCalledWith(
      1,
      "/compressed-air/leakage/records/17/kpi-snapshots",
      {
        method: "POST",
        accessToken: "access-token",
        body: JSON.stringify(payload),
      },
    );

    expect(apiRequestMock).toHaveBeenNthCalledWith(
      2,
      "/compressed-air/leakage/records/17/kpi-snapshots",
      {
        accessToken: "access-token",
      },
    );
  });
});
