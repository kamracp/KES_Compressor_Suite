import {
  render,
  screen,
} from "@testing-library/react";
import {
  describe,
  expect,
  it,
} from "vitest";

import type {
  CompressedAirLeakKpiSnapshotResponse,
  CompressedAirLeakResponse,
  CompressedAirLeakStatusHistoryResponse,
} from "../leakageLifecycleTypes";
import { LeakageLifecycleDetailSection } from "./LeakageLifecycleDetailSection";

const leakFixture: CompressedAirLeakResponse = {
  id: 17,
  project_id: 42,
  leak_code: "LEAK-001",
  location: "Compressor room",
  lifecycle_status: "CLOSED",
  assigned_to: "maintenance@example.com",
  source_snapshot: {
    baseline_leakage_flow_nm3_per_hr: "12.5",
  },
  closure_evidence: {
    verification_method: "Ultrasonic survey",
    residual_leakage_flow_nm3_per_hr: "1.2",
  },
  closure_notes: "Leak repaired and verified.",
  created_by: "surveyor@example.com",
  updated_by: "engineer@example.com",
  tagged_at: "2026-09-09T08:00:00Z",
  assigned_at: "2026-09-09T09:00:00Z",
  closed_at: "2026-09-09T10:00:00Z",
  created_at: "2026-09-09T08:00:00Z",
  updated_at: "2026-09-09T10:00:00Z",
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
  {
    id: 3,
    leak_id: 17,
    previous_status: "ASSIGNED",
    new_status: "CLOSED",
    changed_by: "engineer@example.com",
    change_notes: "Repair verified.",
    changed_at: "2026-09-09T10:00:00Z",
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
  {
    id: 6,
    leak_id: 17,
    snapshot_code: "POST_REPAIR",
    lifecycle_status: "CLOSED",
    metrics_payload: {
      leakage_flow_nm3_per_hr: "1.2",
      verified_saving_nm3_per_hr: "11.3",
    },
    captured_by: "engineer@example.com",
    captured_at: "2026-09-09T10:05:00Z",
  },
];

describe("LeakageLifecycleDetailSection", () => {
  it("renders loading state", () => {
    render(
      <LeakageLifecycleDetailSection
        leak={undefined}
        history={undefined}
        kpiSnapshots={undefined}
        isPending
      />,
    );

    expect(
      screen.getByText(
        "Loading leakage lifecycle detail...",
      ),
    ).toBeInTheDocument();
  });

  it("renders error state", () => {
    render(
      <LeakageLifecycleDetailSection
        leak={undefined}
        history={undefined}
        kpiSnapshots={undefined}
        isPending={false}
        errorMessage="Lifecycle detail request failed."
      />,
    );

    expect(screen.getByRole("alert")).toHaveTextContent(
      "Lifecycle detail request failed.",
    );
  });

  it("renders no-selection state", () => {
    render(
      <LeakageLifecycleDetailSection
        leak={undefined}
        history={undefined}
        kpiSnapshots={undefined}
        isPending={false}
      />,
    );

    expect(
      screen.getByText(
        "Select a leakage record to review its lifecycle.",
      ),
    ).toBeInTheDocument();
  });

  it("renders selected lifecycle detail, history, and KPI snapshots", () => {
    render(
      <LeakageLifecycleDetailSection
        leak={leakFixture}
        history={historyFixture}
        kpiSnapshots={kpiFixture}
        isPending={false}
      />,
    );

    expect(
      screen.getByText("LEAK-001"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("Compressor room"),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        "maintenance@example.com",
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText("Status History"),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        "Leak tagged during survey.",
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        "Assigned to maintenance.",
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText("Repair verified."),
    ).toBeInTheDocument();

    expect(
      screen.getByText("KPI Snapshots"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("BASELINE"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("POST_REPAIR"),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        "Leak repaired and verified.",
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        /verification_method/,
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        /verified_saving_nm3_per_hr/,
      ),
    ).toBeInTheDocument();
  });

  it("renders empty history and KPI states", () => {
    render(
      <LeakageLifecycleDetailSection
        leak={{
          ...leakFixture,
          lifecycle_status: "TAGGED",
          assigned_to: null,
          assigned_at: null,
          closed_at: null,
          closure_notes: null,
          closure_evidence: null,
        }}
        history={[]}
        kpiSnapshots={[]}
        isPending={false}
      />,
    );

    expect(
      screen.getByText("Unassigned"),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        "No lifecycle history recorded.",
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        "No KPI snapshots recorded.",
      ),
    ).toBeInTheDocument();

    expect(
      screen.getAllByText("Not recorded").length,
    ).toBeGreaterThanOrEqual(2);
  });
});
