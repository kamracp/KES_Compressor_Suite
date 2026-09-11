import {
  fireEvent,
  render,
  screen,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {
  describe,
  expect,
  it,
  vi,
} from "vitest";

import type {
  CompressedAirLeakResponse,
} from "../leakageLifecycleTypes";
import {
  LeakageLifecycleAssignmentSection,
} from "./LeakageLifecycleAssignmentSection";

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
  tagged_at: "2026-09-11T08:00:00Z",
  assigned_at: null,
  closed_at: null,
  created_at: "2026-09-11T08:00:00Z",
  updated_at: "2026-09-11T08:00:00Z",
};

describe("LeakageLifecycleAssignmentSection", () => {
  it("prompts for a tagged lifecycle selection", () => {
    render(
      <LeakageLifecycleAssignmentSection
        leak={undefined}
        isPending={false}
        onAssign={vi.fn()}
      />,
    );

    expect(
      screen.getByText(
        "Select a tagged leakage record to assign its repair.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", {
        name: "Assign Leak",
      }),
    ).not.toBeInTheDocument();
  });

  it("validates the required assignee and backend length limit", async () => {
    const onAssign = vi.fn();
    const user = userEvent.setup();

    render(
      <LeakageLifecycleAssignmentSection
        leak={taggedLeakFixture}
        isPending={false}
        onAssign={onAssign}
      />,
    );

    await user.click(
      screen.getByRole("button", {
        name: "Assign Leak",
      }),
    );

    expect(screen.getByRole("alert")).toHaveTextContent(
      "Assigned-to person or team is required.",
    );
    expect(onAssign).not.toHaveBeenCalled();

    fireEvent.change(
      screen.getByLabelText("Assigned to"),
      {
        target: { value: "A".repeat(256) },
      },
    );

    await user.click(
      screen.getByRole("button", {
        name: "Assign Leak",
      }),
    );

    expect(screen.getByRole("alert")).toHaveTextContent(
      "Assigned-to person or team must be 255 characters or fewer.",
    );
    expect(onAssign).not.toHaveBeenCalled();
  });

  it("submits a trimmed assignment with its audit note", async () => {
    const onAssign = vi.fn();
    const user = userEvent.setup();

    render(
      <LeakageLifecycleAssignmentSection
        leak={taggedLeakFixture}
        isPending={false}
        onAssign={onAssign}
      />,
    );

    await user.type(
      screen.getByLabelText("Assigned to"),
      "  Mechanical Maintenance Team  ",
    );
    await user.type(
      screen.getByLabelText("Assignment note"),
      "  Assigned during the weekly leakage review.  ",
    );
    await user.click(
      screen.getByRole("button", {
        name: "Assign Leak",
      }),
    );

    expect(onAssign).toHaveBeenCalledTimes(1);
    expect(onAssign).toHaveBeenCalledWith({
      assigned_to: "Mechanical Maintenance Team",
      change_notes:
        "Assigned during the weekly leakage review.",
    });
  });

  it("disables assignment inputs while the transition is pending", () => {
    render(
      <LeakageLifecycleAssignmentSection
        leak={taggedLeakFixture}
        isPending
        onAssign={vi.fn()}
      />,
    );

    expect(
      screen.getByLabelText("Assigned to"),
    ).toBeDisabled();
    expect(
      screen.getByLabelText("Assignment note"),
    ).toBeDisabled();
    expect(
      screen.getByRole("button", {
        name: "Assigning...",
      }),
    ).toBeDisabled();
  });

  it("prevents reassignment after the tagged transition", () => {
    const { rerender } = render(
      <LeakageLifecycleAssignmentSection
        leak={{
          ...taggedLeakFixture,
          lifecycle_status: "ASSIGNED",
          assigned_to: "maintenance@example.com",
          assigned_at: "2026-09-11T09:00:00Z",
        }}
        isPending={false}
        onAssign={vi.fn()}
      />,
    );

    expect(
      screen.getByText(
        "Repair ownership is already assigned to maintenance@example.com.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", {
        name: "Assign Leak",
      }),
    ).not.toBeInTheDocument();

    rerender(
      <LeakageLifecycleAssignmentSection
        leak={{
          ...taggedLeakFixture,
          lifecycle_status: "CLOSED",
          assigned_to: "maintenance@example.com",
          assigned_at: "2026-09-11T09:00:00Z",
          closed_at: "2026-09-11T10:00:00Z",
        }}
        isPending={false}
        onAssign={vi.fn()}
      />,
    );

    expect(
      screen.getByText(
        "This lifecycle is closed and cannot be assigned again.",
      ),
    ).toBeInTheDocument();
  });

  it("shows assignment API failures", () => {
    render(
      <LeakageLifecycleAssignmentSection
        leak={taggedLeakFixture}
        isPending={false}
        errorMessage="Leakage record could not be assigned."
        onAssign={vi.fn()}
      />,
    );

    expect(screen.getByRole("alert")).toHaveTextContent(
      "Leakage record could not be assigned.",
    );
  });
});
