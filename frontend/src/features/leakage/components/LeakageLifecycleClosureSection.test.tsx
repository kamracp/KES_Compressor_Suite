import {
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
  LeakageLifecycleClosureSection,
} from "./LeakageLifecycleClosureSection";

const assignedLeakFixture: CompressedAirLeakResponse = {
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
  updated_by: "maintenance@example.com",
  tagged_at: "2026-09-11T08:00:00Z",
  assigned_at: "2026-09-11T09:00:00Z",
  closed_at: null,
  created_at: "2026-09-11T08:00:00Z",
  updated_at: "2026-09-11T09:00:00Z",
};

describe("LeakageLifecycleClosureSection", () => {
  it("prompts for an assigned lifecycle selection", () => {
    render(
      <LeakageLifecycleClosureSection
        leak={undefined}
        isPending={false}
        onClose={vi.fn()}
      />,
    );

    expect(
      screen.getByText(
        "Select an assigned leakage record to review its closure evidence.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", {
        name: "Close Leakage Lifecycle",
      }),
    ).not.toBeInTheDocument();
  });

  it("blocks unsupported tagged and duplicate closed transitions", () => {
    const { rerender } = render(
      <LeakageLifecycleClosureSection
        leak={{
          ...assignedLeakFixture,
          lifecycle_status: "TAGGED",
          assigned_to: null,
          assigned_at: null,
        }}
        isPending={false}
        onClose={vi.fn()}
      />,
    );

    expect(
      screen.getByText(
        "Assign this leakage record before recording closure evidence. Direct TAGGED to CLOSED transitions are not permitted.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", {
        name: "Close Leakage Lifecycle",
      }),
    ).not.toBeInTheDocument();

    rerender(
      <LeakageLifecycleClosureSection
        leak={{
          ...assignedLeakFixture,
          lifecycle_status: "CLOSED",
          closed_at: "2026-09-11T10:00:00Z",
        }}
        isPending={false}
        onClose={vi.fn()}
      />,
    );

    expect(
      screen.getByText(/cannot be closed again\.$/),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", {
        name: "Close Leakage Lifecycle",
      }),
    ).not.toBeInTheDocument();
  });

  it("requires repair, verification, flow, and evidence confirmation", async () => {
    const onClose = vi.fn();
    const user = userEvent.setup();

    render(
      <LeakageLifecycleClosureSection
        leak={assignedLeakFixture}
        isPending={false}
        onClose={onClose}
      />,
    );

    await user.click(
      screen.getByRole("button", {
        name: "Close Leakage Lifecycle",
      }),
    );

    const alert = screen.getByRole("alert");

    expect(alert).toHaveTextContent(
      "Repair action is required.",
    );
    expect(alert).toHaveTextContent(
      "Verification method is required.",
    );
    expect(alert).toHaveTextContent(
      "Verified post-repair flow must be zero or greater.",
    );
    expect(alert).toHaveTextContent(
      "Confirm that the repair and verification evidence has been reviewed.",
    );
    expect(onClose).not.toHaveBeenCalled();
  });

  it("submits normalized closure evidence and audit notes", async () => {
    const onClose = vi.fn();
    const user = userEvent.setup();

    render(
      <LeakageLifecycleClosureSection
        leak={assignedLeakFixture}
        isPending={false}
        onClose={onClose}
      />,
    );

    await user.type(
      screen.getByLabelText("Repair action"),
      "  Replaced damaged coupling and seal  ",
    );
    await user.selectOptions(
      screen.getByLabelText("Verification method"),
      "FLOW_METER",
    );
    await user.type(
      screen.getByLabelText("Verified post-repair flow"),
      "0.8",
    );
    await user.type(
      screen.getByLabelText("Verification reference"),
      "  WO-2026-104  ",
    );
    await user.type(
      screen.getByLabelText("Closure notes"),
      "  No audible leakage remains.  ",
    );
    await user.type(
      screen.getByLabelText("Status-history note"),
      "  Verified during weekly survey.  ",
    );
    await user.click(
      screen.getByRole("checkbox", {
        name: /I confirm that the completed repair/i,
      }),
    );
    await user.click(
      screen.getByRole("button", {
        name: "Close Leakage Lifecycle",
      }),
    );

    expect(onClose).toHaveBeenCalledTimes(1);
    expect(onClose).toHaveBeenCalledWith({
      closure_evidence: {
        schema: "KES_LEAK_CLOSURE_EVIDENCE_V1",
        repair_action: "Replaced damaged coupling and seal",
        verification_method: "FLOW_METER",
        verified_post_repair_flow_nm3_per_hr: "0.8",
        verification_reference: "WO-2026-104",
      },
      closure_notes: "No audible leakage remains.",
      change_notes: "Verified during weekly survey.",
    });
  });

  it("disables closure controls while the transition is pending", () => {
    render(
      <LeakageLifecycleClosureSection
        leak={assignedLeakFixture}
        isPending
        onClose={vi.fn()}
      />,
    );

    expect(
      screen.getByLabelText("Repair action"),
    ).toBeDisabled();
    expect(
      screen.getByLabelText("Verification method"),
    ).toBeDisabled();
    expect(
      screen.getByLabelText("Verified post-repair flow"),
    ).toBeDisabled();
    expect(
      screen.getByRole("checkbox", {
        name: /I confirm that the completed repair/i,
      }),
    ).toBeDisabled();
    expect(
      screen.getByRole("button", {
        name: "Closing Lifecycle...",
      }),
    ).toBeDisabled();
  });

  it("shows closure API failures", () => {
    render(
      <LeakageLifecycleClosureSection
        leak={assignedLeakFixture}
        isPending={false}
        errorMessage="Leakage lifecycle could not be closed."
        onClose={vi.fn()}
      />,
    );

    expect(screen.getByRole("alert")).toHaveTextContent(
      "Leakage lifecycle could not be closed.",
    );
  });
});
