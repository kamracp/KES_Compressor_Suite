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
import { executeDistributionCalculation } from "../features/projects/distributionService";
import type { DistributionExecutionResponse } from "../features/projects/distributionTypes";
import { useProjectContext } from "../features/projects/useProjectContext";
import { ApiError } from "../services/apiClient";
import type { Project } from "../types/project";
import { DistributionNetworkPage } from "./DistributionNetworkPage";

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
  "../features/projects/distributionService",
  () => ({
    executeDistributionCalculation: vi.fn(),
  }),
);

type ProjectContextValue = ReturnType<typeof useProjectContext>;

type ProjectQuery = ProjectContextValue["projectQuery"];

const projectFixture: Project = {
  id: 42,
  organization_id: 6406,
  project_code: "S15-M9-TEST",
  project_name: "Distribution Network Workspace Test",
  client_name: "KES Test Client",
  plant_name: null,
  location: null,
  service_description: null,
  status: "DRAFT",
  created_at: "2026-08-26T00:00:00Z",
  updated_at: "2026-08-26T00:00:00Z",
};

const resultFixture: DistributionExecutionResponse = {
  result: {
    validation: {
      network_code: "NET-1",
      node_count: 2,
      segment_count: 1,
      source_node_count: 1,
      consumer_node_count: 1,
      duplicate_node_codes: [],
      duplicate_segment_codes: [],
      orphan_segment_codes: [],
      is_structurally_valid: true,
    },
    hydraulics: {
      network_code: "NET-1",
      path_results: [
        {
          path_code: "P1",
          source_node_code: "N1",
          destination_node_code: "N2",
          segment_results: [
            {
              segment_code: "S1",
              start_node_code: "N1",
              end_node_code: "N2",
              design_flow_nm3_per_hr: "600",
              length_m: "80",
              equivalent_fitting_length_m: "20",
              total_equivalent_length_m: "100",
              velocity_m_per_s: "5.2",
              pressure_drop_bar: "0.031",
            },
            {
              segment_code: "S2",
              start_node_code: "N2",
              end_node_code: "N3",
              design_flow_nm3_per_hr: "600",
              length_m: "40",
              equivalent_fitting_length_m: "10",
              total_equivalent_length_m: "50",
              velocity_m_per_s: "7.5",
              pressure_drop_bar: "0.058",
            },
            {
              segment_code: "S3",
              start_node_code: "N3",
              end_node_code: "N4",
              design_flow_nm3_per_hr: "600",
              length_m: "25",
              equivalent_fitting_length_m: "5",
              total_equivalent_length_m: "30",
              velocity_m_per_s: "10.4",
              pressure_drop_bar: "0.094",
            },
          ],
          total_straight_length_m: "145",
          total_equivalent_fitting_length_m: "35",
          total_equivalent_length_m: "180",
          total_pressure_drop_bar: "0.183",
          source_pressure_bar_g: "7.0",
          destination_pressure_bar_g: "6.817",
          destination_minimum_pressure_bar_g: "6.0",
          destination_pressure_margin_bar: "0.817",
          destination_pressure_is_adequate: true,
        },
      ],
      worst_pressure_path_code: "P1",
      highest_pressure_drop_path_code: "P1",
      minimum_destination_pressure_bar_g: "6.817",
      maximum_path_pressure_drop_bar: "0.183",
      pressure_deficient_path_codes: [],
      total_paths: 1,
      adequate_paths: 1,
      deficient_paths: 0,
      network_pressure_is_adequate: true,
    },
    optimization: null,
  },
  calculation_case_id: null,
};

function configureAuth(): void {
  vi.mocked(useAuth).mockReturnValue({
    accessToken: "test-access-token",
    currentUser: null,
    isAuthenticated: true,
    isLoading: false,
    login: vi.fn(async () => undefined),
    logout: vi.fn(),
  });
}

function configureProjectContext(): void {
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
}

function renderPage() {
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

  const user = userEvent.setup();

  render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter
        initialEntries={["/projects/42/compressor/distribution"]}
      >
        <Routes>
          <Route
            path="/projects/:projectId/compressor/distribution"
            element={<DistributionNetworkPage />}
          />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );

  return user;
}

describe("DistributionNetworkPage", () => {
  beforeEach(() => {
    configureAuth();
    configureProjectContext();
    vi.mocked(executeDistributionCalculation).mockReset();
  });

  it("submits the default network and renders calibrated velocity bands", async () => {
    vi.mocked(executeDistributionCalculation).mockResolvedValue(
      resultFixture,
    );

    const user = renderPage();

    expect(screen.getByLabelText("Network Code")).toHaveValue("NET-1");
    expect(screen.getByLabelText("Design Source Pressure")).toHaveValue(
      "7.0",
    );
    expect(
      screen.getByText("Distribution Network Workspace Test", {
        exact: false,
      }),
    ).toBeInTheDocument();

    await user.click(
      screen.getByRole("button", { name: "Run Analysis" }),
    );

    await waitFor(() => {
      expect(screen.getByText("Structurally Valid")).toBeInTheDocument();
    });

    expect(screen.getByText("Pressure Adequate")).toBeInTheDocument();

    expect(screen.getByText("RECOMMENDED")).toBeInTheDocument();
    expect(screen.getByText("CAUTION")).toBeInTheDocument();
    expect(screen.getByText("EXCESSIVE")).toBeInTheDocument();

    expect(executeDistributionCalculation).toHaveBeenCalledWith(
      "test-access-token",
      expect.objectContaining({
        calculation: expect.objectContaining({
          network_code: "NET-1",
          topology: "DEAD_END",
          design_source_pressure_bar_g: 7,
          candidate_internal_diameters_mm: null,
        }),
        execution: expect.objectContaining({
          persist_result: false,
          project_id: null,
        }),
      }),
    );
  });

  it("renders the service failure detail when the analysis is rejected", async () => {
    vi.mocked(executeDistributionCalculation).mockRejectedValue(
      new ApiError("Unprocessable Content", 422, {
        detail: "Path P1 references unknown segment code S9.",
      }),
    );

    const user = renderPage();

    await user.click(
      screen.getByRole("button", { name: "Run Analysis" }),
    );

    await waitFor(() => {
      expect(screen.getByText("Analysis Failed")).toBeInTheDocument();
    });

    expect(
      screen.getByText("Path P1 references unknown segment code S9."),
    ).toBeInTheDocument();
  });

  it("persists the analysis with project metadata when requested", async () => {
    vi.mocked(executeDistributionCalculation).mockResolvedValue({
      ...resultFixture,
      calculation_case_id: 314,
    });

    const user = renderPage();

    await user.click(screen.getByLabelText("Persist This Analysis", {
      exact: false,
    }));

    await user.type(
      screen.getByLabelText("Calculation Code"),
      "DIST-001",
    );

    await user.click(
      screen.getByRole("button", { name: "Run Analysis" }),
    );

    await waitFor(() => {
      expect(
        screen.getByText("Calculation Case Saved"),
      ).toBeInTheDocument();
    });

    expect(executeDistributionCalculation).toHaveBeenCalledWith(
      "test-access-token",
      expect.objectContaining({
        execution: expect.objectContaining({
          persist_result: true,
          project_id: 42,
          calculation_code: "DIST-001",
          title: "Distribution Network Analysis",
        }),
      }),
    );
  });

  it("adds and removes node rows", async () => {
    vi.mocked(executeDistributionCalculation).mockResolvedValue(
      resultFixture,
    );

    const user = renderPage();

    const initialRemoveButtons = screen.getAllByRole("button", {
      name: "Remove",
    });

    await user.click(
      screen.getByRole("button", { name: "Add Node" }),
    );

    const afterAddRemoveButtons = screen.getAllByRole("button", {
      name: "Remove",
    });

    expect(afterAddRemoveButtons.length).toBe(
      initialRemoveButtons.length + 1,
    );
  });
});
