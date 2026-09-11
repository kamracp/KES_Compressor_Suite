import {
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import {
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {
  MemoryRouter,
  Route,
  Routes,
} from "react-router";
import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import { useAuth } from "../features/auth/AuthProvider";
import { LEAKAGE_SOURCE_SNAPSHOT_SCHEMA } from "../features/leakage/leakageLifecyclePayload";
import type { CompressedAirLeakAssignRequest } from "../features/leakage/leakageLifecycleTypes";
import { useLeakageLifecycleDetail } from "../features/leakage/useLeakageLifecycleDetail";
import { useLeakageLifecycleMutations } from "../features/leakage/useLeakageLifecycleMutations";
import { useLeakageLifecycleRegister } from "../features/leakage/useLeakageLifecycleRegister";
import type { LeakRegisterItemInput } from "../features/leakage/leakageTypes";
import { useProjectContext } from "../features/projects/useProjectContext";
import { useInputOptions } from "../features/reference/useInputOptions";
import type { Project } from "../types/project";
import { LeakageManagementPage } from "./LeakageManagementPage";

vi.mock("../features/auth/AuthProvider", () => ({
  useAuth: vi.fn(),
}));

vi.mock(
  "../features/projects/useProjectContext",
  () => ({
    useProjectContext: vi.fn(),
  }),
);

vi.mock(
  "../features/reference/useInputOptions",
  () => ({
    useInputOptions: vi.fn(),
  }),
);

vi.mock(
  "../features/leakage/useLeakageLifecycleRegister",
  () => ({
    useLeakageLifecycleRegister: vi.fn(),
  }),
);

vi.mock(
  "../features/leakage/useLeakageLifecycleDetail",
  () => ({
    useLeakageLifecycleDetail: vi.fn(),
  }),
);

vi.mock(
  "../features/leakage/useLeakageLifecycleMutations",
  () => ({
    useLeakageLifecycleMutations: vi.fn(),
  }),
);

vi.mock(
  "../features/leakage/components/LeakageLifecycleTaggingSection",
  () => ({
    LeakageLifecycleTaggingSection: ({
      onTagLeak,
    }: {
      onTagLeak: (leak: LeakRegisterItemInput) => void;
    }) => (
      <button
        type="button"
        onClick={() =>
          onTagLeak({
            leak_code: "LEAK-001",
            location: "Compressor room",
            baseline_leakage_flow_nm3_per_hr: "12.5",
            quantification_basis: "ULTRASONIC_ESTIMATE",
            source_category: "PIPE_JOINT",
            expected_repair_fraction: "0.8",
            repair_status: "OPEN",
          })
        }
      >
        Tag test leak
      </button>
    ),
  }),
);

vi.mock(
  "../features/leakage/components/LeakageLifecycleAssignmentSection",
  () => ({
    LeakageLifecycleAssignmentSection: ({
      onAssign,
    }: {
      onAssign: (
        payload: CompressedAirLeakAssignRequest,
      ) => void;
    }) => (
      <button
        type="button"
        onClick={() =>
          onAssign({
            assigned_to: "maintenance@example.com",
            change_notes: "Assigned during test review.",
          })
        }
      >
        Assign test leak
      </button>
    ),
  }),
);

vi.mock(
  "../features/leakage/components/LeakageLifecycleRegisterSection",
  () => ({
    LeakageLifecycleRegisterSection: ({
      onSelectLeak,
    }: {
      onSelectLeak: (leakId: number) => void;
    }) => (
      <button
        type="button"
        onClick={() => onSelectLeak(18)}
      >
        Review leak 18
      </button>
    ),
  }),
);

vi.mock(
  "../features/leakage/components/LeakageLifecycleDetailSection",
  () => ({
    LeakageLifecycleDetailSection: ({
      leak,
      history,
      kpiSnapshots,
    }: {
      leak?: { id: number };
      history?: { total: number };
      kpiSnapshots?: { total: number };
    }) => (
      <section aria-label="Leakage lifecycle detail">
        <p>Selected leak {leak?.id ?? "none"}</p>
        <p>History records {history?.total ?? 0}</p>
        <p>KPI snapshots {kpiSnapshots?.total ?? 0}</p>
      </section>
    ),
  }),
);

vi.mock(
  "../features/leakage/components/LeakageStudyBasisSection",
  () => ({
    LeakageStudyBasisSection: () => null,
  }),
);

vi.mock(
  "../features/leakage/components/LeakRegisterSection",
  () => ({
    LeakRegisterSection: () => null,
  }),
);

vi.mock(
  "../features/leakage/components/LeakageEnergyBasisSection",
  () => ({
    LeakageEnergyBasisSection: () => null,
  }),
);

vi.mock(
  "../features/leakage/components/RepairVerificationSection",
  () => ({
    RepairVerificationSection: () => null,
  }),
);

vi.mock(
  "../features/leakage/components/LeakageEngineeringReviewSection",
  () => ({
    LeakageEngineeringReviewSection: () => null,
  }),
);

type ProjectContextValue = ReturnType<typeof useProjectContext>;
type ProjectQuery = ProjectContextValue["projectQuery"];

const createLifecycleRecord = vi.fn();
const resetCreateLifecycleRecord = vi.fn();
const assignLifecycleRecord = vi.fn();
const resetAssignLifecycleRecord = vi.fn();

const projectFixture: Project = {
  id: 42,
  organization_id: 6406,
  project_code: "C-9K8-TEST",
  project_name: "Leakage Lifecycle Page Test",
  client_name: "KES Test Client",
  plant_name: null,
  location: null,
  service_description: null,
  status: "DRAFT",
  created_at: "2026-09-10T00:00:00Z",
  updated_at: "2026-09-10T00:00:00Z",
};

function configurePageDependencies(): void {
  createLifecycleRecord.mockReset();
  resetCreateLifecycleRecord.mockReset();
  assignLifecycleRecord.mockReset();
  resetAssignLifecycleRecord.mockReset();

  vi.mocked(useAuth).mockReturnValue({
    accessToken: "test-access-token",
    currentUser: null,
    isAuthenticated: true,
    isLoading: false,
    login: vi.fn(async () => undefined),
    logout: vi.fn(),
  });

  const projectQuery = {
    data: projectFixture,
    error: null,
    isError: false,
    isFetching: false,
    isPending: false,
    refetch: vi.fn(),
  } as unknown as ProjectQuery;

  vi.mocked(useProjectContext).mockReturnValue({
    projectId: 42,
    hasValidProjectId: true,
    project: projectFixture,
    projectQuery,
  });

  vi.mocked(useInputOptions).mockReturnValue({
    data: undefined,
  } as unknown as ReturnType<typeof useInputOptions>);

  vi.mocked(useLeakageLifecycleRegister).mockReturnValue({
    data: undefined,
    error: null,
    isError: false,
    isFetching: false,
    isPending: false,
    refetch: vi.fn(),
  } as unknown as ReturnType<
    typeof useLeakageLifecycleRegister
  >);

  vi.mocked(useLeakageLifecycleDetail).mockImplementation(
    (_accessToken, leakId, enabled) => ({
      detailQuery: {
        data: enabled ? { id: leakId } : undefined,
        error: null,
        isPending: false,
      },
      historyQuery: {
        data: enabled ? { total: 2 } : undefined,
        error: null,
        isPending: false,
      },
      kpiSnapshotsQuery: {
        data: enabled ? { total: 3 } : undefined,
        error: null,
        isPending: false,
      },
    }) as unknown as ReturnType<
      typeof useLeakageLifecycleDetail
    >,
  );

  vi.mocked(useLeakageLifecycleMutations).mockReturnValue({
    createMutation: {
      mutate: createLifecycleRecord,
      reset: resetCreateLifecycleRecord,
      isPending: false,
      isError: false,
      error: null,
      variables: undefined,
    },
    assignMutation: {
      mutate: assignLifecycleRecord,
      reset: resetAssignLifecycleRecord,
      isPending: false,
      isError: false,
      error: null,
    },
    closeMutation: {},
    createKpiSnapshotMutation: {},
  } as unknown as ReturnType<
    typeof useLeakageLifecycleMutations
  >);
}

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  const user = userEvent.setup();

  render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter
        initialEntries={[
          "/projects/42/compressor/leakage",
        ]}
      >
        <Routes>
          <Route
            path="/projects/:projectId/compressor/leakage"
            element={<LeakageManagementPage />}
          />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );

  return user;
}

describe("LeakageManagementPage", () => {
  beforeEach(() => {
    configurePageDependencies();
  });

  it("loads lifecycle detail, history, and KPI data for the reviewed leak", async () => {
    const user = renderPage();

    expect(useLeakageLifecycleDetail).toHaveBeenCalledWith(
      "test-access-token",
      0,
      false,
    );
    expect(screen.getByText("Selected leak none")).toBeInTheDocument();

    await user.click(
      screen.getByRole("button", {
        name: "Review leak 18",
      }),
    );

    await waitFor(() => {
      expect(useLeakageLifecycleDetail).toHaveBeenLastCalledWith(
        "test-access-token",
        18,
        true,
      );
    });

    expect(screen.getByText("Selected leak 18")).toBeInTheDocument();
    expect(screen.getByText("History records 2")).toBeInTheDocument();
    expect(screen.getByText("KPI snapshots 3")).toBeInTheDocument();
  });

  it("submits a normalized lifecycle record when a leak is tagged", async () => {
    const user = renderPage();

    expect(useLeakageLifecycleMutations).toHaveBeenCalledWith(
      "test-access-token",
      42,
    );

    await user.click(
      screen.getByRole("button", {
        name: "Tag test leak",
      }),
    );

    expect(createLifecycleRecord).toHaveBeenCalledTimes(1);
    expect(createLifecycleRecord).toHaveBeenCalledWith({
      leak_code: "LEAK-001",
      location: "Compressor room",
      source_snapshot: {
        schema: LEAKAGE_SOURCE_SNAPSHOT_SCHEMA,
        baseline_leakage_flow_nm3_per_hr: "12.5",
        quantification_basis: "ULTRASONIC_ESTIMATE",
        source_category: "PIPE_JOINT",
        area: null,
        equipment_tag: null,
        component_description: null,
        survey_pressure_bar_g: null,
        expected_repair_fraction: "0.8",
        repair_status: "OPEN",
        estimated_repair_cost: null,
        verified_post_repair_flow_nm3_per_hr: null,
        survey_method_reference: null,
        notes: null,
      },
    });
  });

  it("assigns the selected lifecycle record with its transition payload", async () => {
    const user = renderPage();

    await user.click(
      screen.getByRole("button", {
        name: "Assign test leak",
      }),
    );
    expect(assignLifecycleRecord).not.toHaveBeenCalled();

    await user.click(
      screen.getByRole("button", {
        name: "Review leak 18",
      }),
    );

    await waitFor(() => {
      expect(useLeakageLifecycleDetail).toHaveBeenLastCalledWith(
        "test-access-token",
        18,
        true,
      );
    });

    expect(resetAssignLifecycleRecord).toHaveBeenCalledTimes(1);

    await user.click(
      screen.getByRole("button", {
        name: "Assign test leak",
      }),
    );

    expect(assignLifecycleRecord).toHaveBeenCalledTimes(1);
    expect(assignLifecycleRecord).toHaveBeenCalledWith({
      leakId: 18,
      payload: {
        assigned_to: "maintenance@example.com",
        change_notes: "Assigned during test review.",
      },
    });
  });
});
