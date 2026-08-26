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
import { useProjectContext } from "../features/projects/useProjectContext";
import { executeCompressorSelection } from "../features/projects/selectionService";
import type { CompressorSelectionExecutionResponse } from "../features/projects/selectionTypes";
import { ApiError } from "../services/apiClient";
import type { Project } from "../types/project";
import { CompressorSelectionPage } from "./CompressorSelectionPage";

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
  "../features/projects/selectionService",
  () => ({
    executeCompressorSelection: vi.fn(),
  }),
);

type ProjectContextValue = ReturnType<typeof useProjectContext>;

type ProjectQuery = ProjectContextValue["projectQuery"];

const projectFixture: Project = {
  id: 42,
  organization_id: 6406,
  project_code: "S15-M8-TEST",
  project_name: "Compressor Selection Workspace Test",
  client_name: "KES Test Client",
  plant_name: null,
  location: null,
  service_description: null,
  status: "DRAFT",
  created_at: "2026-08-26T00:00:00Z",
  updated_at: "2026-08-26T00:00:00Z",
};

const resultFixture: CompressorSelectionExecutionResponse = {
  result: {
    recommended_type: "CENTRIFUGAL",
    reciprocating: {
      compressor_type: "RECIPROCATING",
      capacity_rating: "GOOD",
      pressure_ratio_rating: "EXCELLENT",
      turndown_rating: "EXCELLENT",
      efficiency_rating: "GOOD",
      maintenance_rating: "ACCEPTABLE",
      overall_score: "82",
      rationale: [
        "Strong turndown capability.",
        "Suitable for the specified pressure ratio.",
      ],
    },
    centrifugal: {
      compressor_type: "CENTRIFUGAL",
      capacity_rating: "EXCELLENT",
      pressure_ratio_rating: "GOOD",
      turndown_rating: "ACCEPTABLE",
      efficiency_rating: "EXCELLENT",
      maintenance_rating: "GOOD",
      overall_score: "86",
      rationale: [
        "Strong capacity fit for the required flow.",
        "High annual utilization supports the efficiency case.",
      ],
    },
    score_difference: "4",
    recommendation_summary:
      "Centrifugal compression is preferred for the submitted duty.",
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
        initialEntries={["/projects/42/compressor/selection"]}
      >
        <Routes>
          <Route
            path="/projects/:projectId/compressor/selection"
            element={<CompressorSelectionPage />}
          />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );

  return user;
}

describe("CompressorSelectionPage", () => {
  beforeEach(() => {
    configureAuth();
    configureProjectContext();
    vi.mocked(executeCompressorSelection).mockReset();
  });

  it("submits the default engineering basis and renders the assessment", async () => {
    vi.mocked(executeCompressorSelection).mockResolvedValue(resultFixture);

    const user = renderPage();

    expect(screen.getByLabelText("Required Flow")).toHaveValue(3000);
    expect(screen.getByLabelText("Suction Pressure")).toHaveValue(1);
    expect(screen.getByLabelText("Discharge Pressure")).toHaveValue(8);
    expect(screen.getByText("8.000")).toBeInTheDocument();
    expect(
      screen.getByText("Compressor Selection Workspace Test", {
        exact: false,
      }),
    ).toBeInTheDocument();

    await user.click(
      screen.getByRole("button", {
        name: "Run Selection",
      }),
    );

    await waitFor(() => {
      expect(executeCompressorSelection).toHaveBeenCalledTimes(1);
    });

    expect(executeCompressorSelection).toHaveBeenCalledWith(
      "test-access-token",
      {
        calculation: {
          required_flow_m3_per_hr: 3000,
          suction_pressure_bar: 1,
          discharge_pressure_bar: 8,
          required_turndown_fraction: 0.3,
          continuous_operation: true,
          gas_molecular_weight: 28.97,
          estimated_operating_hours_per_year: 8000,
        },
        execution: {
          persist_result: false,
          project_id: null,
          calculation_code: null,
          title: null,
          engineering_notes: null,
        },
      },
    );

    expect(
      await screen.findByText("Technology Selection Complete"),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "Centrifugal compression is preferred for the submitted duty.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Strong turndown capability."),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "High annual utilization supports the efficiency case.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Technology Assessment Matrix"),
    ).toBeInTheDocument();
  });

  it("blocks an invalid pressure basis, clears results, and resets defaults", async () => {
    vi.mocked(executeCompressorSelection).mockResolvedValue(resultFixture);

    const user = renderPage();

    await user.click(
      screen.getByRole("button", {
        name: "Run Selection",
      }),
    );

    expect(
      await screen.findByText("Technology Selection Complete"),
    ).toBeInTheDocument();

    const dischargePressureInput = screen.getByLabelText(
      "Discharge Pressure",
    );

    await user.clear(dischargePressureInput);
    await user.type(dischargePressureInput, "0.8");

    expect(
      screen.getByText(
        "Enter positive pressures with discharge pressure greater than suction pressure.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.queryByText("Technology Selection Complete"),
    ).not.toBeInTheDocument();
    expect(
      screen.getByRole("button", {
        name: "Run Selection",
      }),
    ).toBeDisabled();
    expect(
      screen.getByRole("button", {
        name: "Evaluate Compressor Technologies",
      }),
    ).toBeDisabled();

    await user.click(
      screen.getByRole("button", {
        name: "Reset",
      }),
    );

    expect(dischargePressureInput).toHaveValue(8);
    expect(screen.getByText("8.000")).toBeInTheDocument();
    expect(
      screen.getByRole("button", {
        name: "Run Selection",
      }),
    ).toBeEnabled();
    expect(executeCompressorSelection).toHaveBeenCalledTimes(1);
  });

  it("persists the selection and links to the saved calculation case", async () => {
    vi.mocked(executeCompressorSelection).mockResolvedValue({
      ...resultFixture,
      calculation_case_id: 987,
    });

    const user = renderPage();

    await user.click(
      screen.getByRole("checkbox", {
        name: /Save Result to Project/,
      }),
    );

    await user.type(
      screen.getByLabelText("Calculation Code"),
      "S15-M8-CALC-001",
    );

    const calculationTitleInput = screen.getByLabelText(
      "Calculation Title",
    );
    await user.clear(calculationTitleInput);
    await user.type(
      calculationTitleInput,
      "Technology Selection Review",
    );

    await user.type(
      screen.getByLabelText("Engineering Notes"),
      "Compare both technologies on the recorded design basis.",
    );

    await user.click(
      screen.getByRole("button", {
        name: "Run Selection",
      }),
    );

    await waitFor(() => {
      expect(executeCompressorSelection).toHaveBeenCalledTimes(1);
    });

    expect(executeCompressorSelection).toHaveBeenCalledWith(
      "test-access-token",
      expect.objectContaining({
        execution: {
          persist_result: true,
          project_id: 42,
          calculation_code: "S15-M8-CALC-001",
          title: "Technology Selection Review",
          engineering_notes:
            "Compare both technologies on the recorded design basis.",
        },
      }),
    );

    expect(
      await screen.findByText("Calculation Case Saved"),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", {
        name: "Open Saved Case",
      }),
    ).toHaveAttribute(
      "href",
      "/projects/42/calculations/987",
    );
  });

  it("renders backend validation detail for a rejected selection", async () => {
    vi.mocked(executeCompressorSelection).mockRejectedValue(
      new ApiError(
        "API request failed with status 422.",
        422,
        {
          detail:
            "Discharge pressure must be greater than suction pressure.",
        },
      ),
    );

    const user = renderPage();

    await user.click(
      screen.getByRole("button", {
        name: "Run Selection",
      }),
    );

    expect(
      await screen.findByText("Compressor Selection Error"),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "Discharge pressure must be greater than suction pressure.",
      ),
    ).toBeInTheDocument();
  });
});
