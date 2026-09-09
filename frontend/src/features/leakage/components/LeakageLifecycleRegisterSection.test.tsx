import {
  fireEvent,
  render,
  screen,
} from "@testing-library/react";
import {
  describe,
  expect,
  it,
  vi,
} from "vitest";

import type {
  CompressedAirLeakListResponse,
} from "../leakageLifecycleTypes";
import {
  LeakageLifecycleRegisterSection,
} from "./LeakageLifecycleRegisterSection";

const registerFixture: CompressedAirLeakListResponse = {
  project_id: 42,
  total_leaks: 3,
  tagged_leaks: 1,
  assigned_leaks: 1,
  closed_leaks: 1,
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
    {
      id: 18,
      project_id: 42,
      leak_code: "LEAK-002",
      location: "Dryer outlet",
      lifecycle_status: "ASSIGNED",
      assigned_to: "maintenance@example.com",
      source_snapshot: {},
      closure_evidence: null,
      closure_notes: null,
      created_by: "surveyor@example.com",
      updated_by: "engineer@example.com",
      tagged_at: "2026-09-09T09:00:00Z",
      assigned_at: "2026-09-09T09:30:00Z",
      closed_at: null,
      created_at: "2026-09-09T09:00:00Z",
      updated_at: "2026-09-09T09:30:00Z",
    },
    {
      id: 19,
      project_id: 42,
      leak_code: "LEAK-003",
      location: "Packaging header",
      lifecycle_status: "CLOSED",
      assigned_to: "maintenance@example.com",
      source_snapshot: {},
      closure_evidence: {
        verified_leakage_flow_nm3_per_hr: "0",
      },
      closure_notes: "Leak repaired and verified.",
      created_by: "surveyor@example.com",
      updated_by: "reviewer@example.com",
      tagged_at: "2026-09-09T10:00:00Z",
      assigned_at: "2026-09-09T10:15:00Z",
      closed_at: "2026-09-09T11:00:00Z",
      created_at: "2026-09-09T10:00:00Z",
      updated_at: "2026-09-09T11:00:00Z",
    },
  ],
};

describe("LeakageLifecycleRegisterSection", () => {
  it("shows the loading state and disables refresh", () => {
    const onRefresh = vi.fn();

    render(
      <LeakageLifecycleRegisterSection
        register={undefined}
        isPending
        isFetching={false}
        onRefresh={onRefresh}
      />,
    );

    expect(
      screen.getByText(
        "Loading persistent leakage register...",
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("button", {
        name: "Refresh",
      }),
    ).toBeDisabled();
  });

  it("shows API failures", () => {
    render(
      <LeakageLifecycleRegisterSection
        register={undefined}
        isPending={false}
        isFetching={false}
        errorMessage="Leakage register request failed."
        onRefresh={vi.fn()}
      />,
    );

    expect(screen.getByRole("alert")).toHaveTextContent(
      "Leakage register request failed.",
    );
  });

  it("shows the empty register state", () => {
    render(
      <LeakageLifecycleRegisterSection
        register={{
          project_id: 42,
          total_leaks: 0,
          tagged_leaks: 0,
          assigned_leaks: 0,
          closed_leaks: 0,
          items: [],
        }}
        isPending={false}
        isFetching={false}
        onRefresh={vi.fn()}
      />,
    );

    expect(
      screen.getByText(
        "No persistent leakage records yet.",
      ),
    ).toBeInTheDocument();
  });

  it("renders lifecycle summary and register rows", () => {
    render(
      <LeakageLifecycleRegisterSection
        register={registerFixture}
        isPending={false}
        isFetching={false}
        onRefresh={vi.fn()}
      />,
    );

    expect(
      screen.getByText("Persistent Leakage Lifecycle"),
    ).toBeInTheDocument();

    expect(screen.getByText("LEAK-001")).toBeInTheDocument();
    expect(screen.getByText("LEAK-002")).toBeInTheDocument();
    expect(screen.getByText("LEAK-003")).toBeInTheDocument();

    expect(
      screen.getByText("Compressor room"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Dryer outlet"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Packaging header"),
    ).toBeInTheDocument();

    expect(screen.getByText("Unassigned")).toBeInTheDocument();
    expect(
      screen.getAllByText("maintenance@example.com"),
    ).toHaveLength(2);

    expect(screen.getAllByText("Tagged").length).toBeGreaterThan(
      0,
    );
    expect(
      screen.getAllByText("Assigned").length,
    ).toBeGreaterThan(0);
    expect(screen.getAllByText("Closed").length).toBeGreaterThan(
      0,
    );
  });

  it("calls refresh and shows fetching state", () => {
    const onRefresh = vi.fn();

    const { rerender } = render(
      <LeakageLifecycleRegisterSection
        register={registerFixture}
        isPending={false}
        isFetching={false}
        onRefresh={onRefresh}
      />,
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Refresh",
      }),
    );

    expect(onRefresh).toHaveBeenCalledTimes(1);

    rerender(
      <LeakageLifecycleRegisterSection
        register={registerFixture}
        isPending={false}
        isFetching
        onRefresh={onRefresh}
      />,
    );

    expect(
      screen.getByRole("button", {
        name: "Refreshing...",
      }),
    ).toBeDisabled();
  });
});
