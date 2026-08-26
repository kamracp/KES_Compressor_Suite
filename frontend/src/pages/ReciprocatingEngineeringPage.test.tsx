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
import { executeReciprocatingCalculation } from "../features/projects/reciprocatingService";
import type { ReciprocatingExecutionResponse } from "../features/projects/reciprocatingTypes";
import { useProjectContext } from "../features/projects/useProjectContext";
import { ApiError } from "../services/apiClient";
import type { Project } from "../types/project";
import { ReciprocatingEngineeringPage } from "./ReciprocatingEngineeringPage";

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
  "../features/projects/reciprocatingService",
  () => ({
    executeReciprocatingCalculation: vi.fn(),
  }),
);

type ProjectContextValue = ReturnType<typeof useProjectContext>;

type ProjectQuery = ProjectContextValue["projectQuery"];

const projectFixture: Project = {
  id: 42,
  organization_id: 6406,
  project_code: "S15-M9-TEST",
  project_name: "Reciprocating Engineering Workspace Test",
  client_name: "KES Test Client",
  plant_name: null,
  location: null,
  service_description: null,
  status: "DRAFT",
  created_at: "2026-08-26T00:00:00Z",
  updated_at: "2026-08-26T00:00:00Z",
};

const resultFixture: ReciprocatingExecutionResponse = {
  result: {
    capacity: {
      geometry: {
        bore_mm: "250",
        stroke_mm: "200",
        rod_diameter_mm: "60",
        speed_rpm: "600",
        clearance_fraction: "0.05",
        action: "DOUBLE_ACTING",
      },
      displacement: {
        piston_area_m2: "0.049087",
        rod_area_m2: "0.002827",
        head_end_displacement_m3_per_min: "5.8905",
        crank_end_displacement_m3_per_min: "5.5512",
        total_displacement_m3_per_min: "11.4417",
        total_displacement_m3_per_hr: "686.502",
      },
      volumetric_efficiency: {
        volumetric_efficiency: "0.865",
        delivered_flow_m3_per_hr: "593.824",
      },
    },
    cylinder_sizing: {
      required_flow_m3_per_hr: "1000",
      delivered_flow_per_cylinder_m3_per_hr: "593.824",
      required_cylinders: 2,
      installed_capacity_m3_per_hr: "1187.648",
      capacity_margin_m3_per_hr: "187.648",
      capacity_margin_fraction: "0.187648",
      capacity_is_adequate: true,
    },
    rod_load: {
      compression_load_kn: "34.305",
      tension_load_kn: "31.954",
      maximum_absolute_load_kn: "34.305",
      allowable_rod_load_kn: "150",
      rod_load_is_adequate: true,
    },
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
        initialEntries={["/projects/42/compressor/reciprocating"]}
      >
        <Routes>
          <Route
            path="/projects/:projectId/compressor/reciprocating"
            element={<ReciprocatingEngineeringPage />}
          />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );

  return user;
}

describe("ReciprocatingEngineeringPage", () => {
  beforeEach(() => {
    configureAuth();
    configureProjectContext();
    vi.mocked(executeReciprocatingCalculation).mockReset();
  });

  it("submits the default engineering basis and renders the assessment", async () => {
    vi.mocked(executeReciprocatingCalculation).mockResolvedValue(
      resultFixture,
    );

    const user = renderPage();

    expect(screen.getByLabelText("Required Flow")).toHaveValue(1000);
    expect(screen.getByLabelText("Cylinder Bore")).toHaveValue(250);
    expect(screen.getByLabelText("Piston Stroke")).toHaveValue(200);
    expect(screen.getByLabelText("Piston Rod Diameter")).toHaveValue(60);
    expect(screen.getByLabelText("Suction Pressure")).toHaveValue(1.013);
    expect(screen.getByLabelText("Discharge Pressure")).toHaveValue(8);
    expect(screen.getByText("7.897")).toBeInTheDocument();
    expect(
      screen.getByText("Reciprocating Engineering Workspace Test", {
        exact: false,
      }),
    ).toBeInTheDocument();

    await user.click(
      screen.getByRole("button", {
        name: "Run Calculation",
      }),
    );

    await waitFor(() => {
      expect(executeReciprocatingCalculation).toHaveBeenCalledTimes(1);
    });

    expect(executeReciprocatingCalculation).toHaveBeenCalledWith(
      "test-access-token",
      {
        calculation: {
          required_flow_m3_per_hr: 1000,
          bore_mm: 250,
          stroke_mm: 200,
          rod_diameter_mm: 60,
          speed_rpm: 600,
          clearance_fraction: 0.05,
          stage_compression_ratio: 3,
          suction_z_factor: 1,
          discharge_z_factor: 1,
          isentropic_exponent: 1.4,
          suction_pressure_bar: 1.013,
          discharge_pressure_bar: 8,
          allowable_rod_load_kn: 150,
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
      await screen.findByText("Reciprocating Engineering Complete"),
    ).toBeInTheDocument();
    expect(screen.getByText("DESIGN ADEQUATE")).toBeInTheDocument();
    expect(screen.getByText("Double Acting")).toBeInTheDocument();
    expect(screen.getByText("1,187.65 m³/hr")).toBeInTheDocument();
    expect(screen.getByText("86.5%")).toBeInTheDocument();
    expect(screen.getByText("Engineering Adequacy Review")).toBeInTheDocument();
  });

  it("blocks invalid cylinder geometry, clears results, and resets defaults", async () => {
    vi.mocked(executeReciprocatingCalculation).mockResolvedValue(
      resultFixture,
    );

    const user = renderPage();

    await user.click(
      screen.getByRole("button", {
        name: "Run Calculation",
      }),
    );

    expect(
      await screen.findByText("Reciprocating Engineering Complete"),
    ).toBeInTheDocument();

    const rodDiameterInput = screen.getByLabelText(
      "Piston Rod Diameter",
    );

    await user.clear(rodDiameterInput);
    await user.type(rodDiameterInput, "260");

    expect(
      screen.getByText(
        "Enter positive bore, stroke, and speed values; keep rod diameter below bore and clearance from zero to less than one.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.queryByText("Reciprocating Engineering Complete"),
    ).not.toBeInTheDocument();
    expect(
      screen.getByRole("button", {
        name: "Run Calculation",
      }),
    ).toBeDisabled();
    expect(
      screen.getByRole("button", {
        name: "Calculate Reciprocating Case",
      }),
    ).toBeDisabled();

    await user.click(
      screen.getByRole("button", {
        name: "Reset",
      }),
    );

    expect(rodDiameterInput).toHaveValue(60);
    expect(
      screen.getByRole("button", {
        name: "Run Calculation",
      }),
    ).toBeEnabled();
    expect(executeReciprocatingCalculation).toHaveBeenCalledTimes(1);
  });

  it("persists the calculation and links to the saved calculation case", async () => {
    vi.mocked(executeReciprocatingCalculation).mockResolvedValue({
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
      "S15-M9-CALC-001",
    );

    const calculationTitleInput = screen.getByLabelText(
      "Calculation Title",
    );
    await user.clear(calculationTitleInput);
    await user.type(
      calculationTitleInput,
      "Reciprocating Compressor Review",
    );

    await user.type(
      screen.getByLabelText("Engineering Notes"),
      "Confirm the selected cylinder count and piston-rod load basis.",
    );

    await user.click(
      screen.getByRole("button", {
        name: "Run Calculation",
      }),
    );

    await waitFor(() => {
      expect(executeReciprocatingCalculation).toHaveBeenCalledTimes(1);
    });

    expect(executeReciprocatingCalculation).toHaveBeenCalledWith(
      "test-access-token",
      expect.objectContaining({
        execution: {
          persist_result: true,
          project_id: 42,
          calculation_code: "S15-M9-CALC-001",
          title: "Reciprocating Compressor Review",
          engineering_notes:
            "Confirm the selected cylinder count and piston-rod load basis.",
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

  it("renders backend validation detail for a rejected calculation", async () => {
    vi.mocked(executeReciprocatingCalculation).mockRejectedValue(
      new ApiError(
        "API request failed with status 422.",
        422,
        {
          detail:
            "Rod diameter must be smaller than the cylinder bore.",
        },
      ),
    );

    const user = renderPage();

    await user.click(
      screen.getByRole("button", {
        name: "Run Calculation",
      }),
    );

    expect(
      await screen.findByText("Reciprocating Calculation Error"),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "Rod diameter must be smaller than the cylinder bore.",
      ),
    ).toBeInTheDocument();
  });
});
