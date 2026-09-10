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
  LeakRegisterItemInput,
} from "../leakageTypes";
import {
  LeakageLifecycleTaggingSection,
} from "./LeakageLifecycleTaggingSection";

function validLeak(
  leakCode = "LEAK-001",
): LeakRegisterItemInput {
  return {
    leak_code: leakCode,
    location: "Compressor room",
    baseline_leakage_flow_nm3_per_hr: "12.5",
    quantification_basis: "ULTRASONIC_ESTIMATE",
    source_category: "PIPE_JOINT",
    area: "Utilities",
    equipment_tag: "AIR-HDR-01",
    component_description: "Threaded elbow",
    survey_pressure_bar_g: "6.5",
    expected_repair_fraction: "0.8",
    repair_status: "OPEN",
    estimated_repair_cost: "2500",
    verified_post_repair_flow_nm3_per_hr: null,
    survey_method_reference: "UT-2026-0910",
    notes: "Repair during next shutdown.",
  };
}

describe("LeakageLifecycleTaggingSection", () => {
  it("shows the empty state when no engineering leaks exist", () => {
    render(
      <LeakageLifecycleTaggingSection
        leaks={[]}
        persistedLeakCodes={[]}
        isPending={false}
        onTagLeak={vi.fn()}
      />,
    );

    expect(
      screen.getByText(
        "No engineering leak rows are available.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", {
        name: /in lifecycle/i,
      }),
    ).not.toBeInTheDocument();
  });

  it("renders a valid leak and submits it for lifecycle tagging", async () => {
    const leak = validLeak();
    const onTagLeak = vi.fn();
    const user = userEvent.setup();

    render(
      <LeakageLifecycleTaggingSection
        leaks={[leak]}
        persistedLeakCodes={[]}
        isPending={false}
        onTagLeak={onTagLeak}
      />,
    );

    expect(screen.getByText("Ready to Tag")).toBeInTheDocument();
    expect(screen.getByText("LEAK-001")).toBeInTheDocument();
    expect(
      screen.getByText("Compressor room"),
    ).toBeInTheDocument();
    expect(screen.getByText(/12\.5/)).toHaveTextContent(
      "12.5 Nm³/h",
    );
    expect(
      screen.getByText("Ultrasonic Estimate"),
    ).toBeInTheDocument();
    expect(screen.getByText("Pipe Joint")).toBeInTheDocument();

    await user.click(
      screen.getByRole("button", {
        name: "Tag LEAK-001 in lifecycle",
      }),
    );

    expect(onTagLeak).toHaveBeenCalledTimes(1);
    expect(onTagLeak).toHaveBeenCalledWith(leak);
  });

  it("blocks invalid rows and shows correction guidance", () => {
    const onTagLeak = vi.fn();

    render(
      <LeakageLifecycleTaggingSection
        leaks={[
          {
            ...validLeak(""),
            location: " ",
            baseline_leakage_flow_nm3_per_hr: "-1",
            expected_repair_fraction: "1.2",
          },
        ]}
        persistedLeakCodes={[]}
        isPending={false}
        onTagLeak={onTagLeak}
      />,
    );

    expect(screen.getByText("Needs Input")).toBeInTheDocument();
    expect(
      screen.getByText("Leak code is required."),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Leak location is required."),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "Baseline leakage flow must be zero or greater.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "Expected repair fraction must be between zero and one.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", {
        name: "Tag leak 1 in lifecycle",
      }),
    ).toBeDisabled();
    expect(onTagLeak).not.toHaveBeenCalled();
  });

  it("marks an existing persistent leak as already tagged", () => {
    render(
      <LeakageLifecycleTaggingSection
        leaks={[validLeak(" LEAK-001 ")]}
        persistedLeakCodes={["LEAK-001"]}
        isPending={false}
        onTagLeak={vi.fn()}
      />,
    );

    expect(
      screen.getByText("Already Tagged"),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", {
        name: "Tag LEAK-001 in lifecycle",
      }),
    ).toBeDisabled();
    expect(
      screen.getByRole("button", {
        name: "Tag LEAK-001 in lifecycle",
      }),
    ).toHaveTextContent("Tagged");
  });

  it("prevents duplicate actions while one leak is being tagged", () => {
    render(
      <LeakageLifecycleTaggingSection
        leaks={[
          validLeak("LEAK-001"),
          validLeak("LEAK-002"),
        ]}
        persistedLeakCodes={[]}
        isPending
        pendingLeakCode="LEAK-001"
        onTagLeak={vi.fn()}
      />,
    );

    const pendingButton = screen.getByRole("button", {
      name: "Tag LEAK-001 in lifecycle",
    });
    const otherButton = screen.getByRole("button", {
      name: "Tag LEAK-002 in lifecycle",
    });

    expect(pendingButton).toBeDisabled();
    expect(pendingButton).toHaveTextContent("Tagging...");
    expect(otherButton).toBeDisabled();
  });

  it("shows lifecycle API failures", () => {
    render(
      <LeakageLifecycleTaggingSection
        leaks={[validLeak()]}
        persistedLeakCodes={[]}
        isPending={false}
        errorMessage="Leakage record could not be tagged."
        onTagLeak={vi.fn()}
      />,
    );

    expect(screen.getByRole("alert")).toHaveTextContent(
      "Leakage record could not be tagged.",
    );
  });
});
