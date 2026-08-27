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
import { executeCentrifugalCalculation } from "../features/projects/centrifugalService";
import type { CentrifugalExecutionResponse } from "../features/projects/centrifugalTypes";
import { useProjectContext } from "../features/projects/useProjectContext";
import { ApiError } from "../services/apiClient";
import type { Project } from "../types/project";
import { CentrifugalEngineeringPage } from "./CentrifugalEngineeringPage";

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
  "../features/projects/centrifugalService",
  () => ({
    executeCentrifugalCalculation: vi.fn(),
  }),
);

type ProjectContextValue = ReturnType<typeof useProjectContext>;

type ProjectQuery = ProjectContextValue["projectQuery"];

const projectFixture: Project = {
  id: 42,
  organization_id: 6406,
  project_code: "S15-M10-TEST",
  project_name: "Centrifugal Engineering Workspace Test",
  client_name: "KES Test Client",
  plant_name: null,
  location: null,
  service_description: null,
  status: "DRAFT",
  created_at: "2026-08-27T00:00:00Z",
  updated_at: "2026-08-27T00:00:00Z",
};

const resultFixture: CentrifugalExecutionResponse = {
  result: {
    head: {
      average_z_factor: "1.0",
      polytropic_exponent: "1.478",
      overall_compression_ratio: "7.89733465",
      polytropic_head_kj_per_kg: "250",
    },
    impeller: {
      number_of_impeller_stages: 4,
      head_per_stage_kj_per_kg: "62.5",
      head_coefficient: "0.65",
      impeller_tip_speed_m_per_s: "310.086",
      rotational_speed_rpm: "12000",
      impeller_diameter_m: "0.49352",
    },
    power: {
      gas_power_kw: "304.878",
      shaft_power_kw: "314.024",
      required_driver_power_kw: "345.426",
      selected_driver_power_kw: "500",
      driver_margin_kw: "154.574",
      driver_is_adequate: true,
      electrical_input_power_kw: "363.606",
      driver_type: "ELECTRIC_MOTOR",
    },
    surge: {
      design_flow_m3_per_hr: "3600",
      surge_flow_m3_per_hr: "2520",
      anti_surge_setpoint_m3_per_hr: "2772",
      surge_margin_fraction: "0.30",
      stonewall_flow_m3_per_hr: "4500",
      operating_range_m3_per_hr: "1980",
      design_point_is_within_envelope: true,
    },
    performance_map: {
      design_speed_rpm: "12000",
      design_flow_m3_per_hr: "3600",
      design_head_kj_per_kg: "250",
      points: [
        {
          speed_fraction: "1.00",
          speed_rpm: "12000",
          flow_m3_per_hr: "3600",
          head_kj_per_kg: "250",
        },
        {
          speed_fraction: "0.90",
          speed_rpm: "10800",
          flow_m3_per_hr: "3240",
          head_kj_per_kg: "202.5",
        },
        {
          speed_fraction: "0.80",
          speed_rpm: "9600",
          flow_m3_per_hr: "2880",
          head_kj_per_kg: "160",
        },
      ],
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
        initialEntries={["/projects/42/compressor/centrifugal"]}
      >
        <Routes>
          <Route
            path="/projects/:projectId/compressor/centrifugal"
            element={<CentrifugalEngineeringPage />}
          />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );

  return user;
}

describe("CentrifugalEngineeringPage", () => {
  beforeEach(() => {
    configureAuth();
    configureProjectContext();
    vi.mocked(executeCentrifugalCalculation).mockReset();
  });

  it("submits the default engineering basis and renders the assessment", async () => {
    vi.mocked(executeCentrifugalCalculation).mockResolvedValue(
      resultFixture,
    );

    const user = renderPage();

    expect(screen.getByLabelText("Suction Pressure")).toHaveValue(1.013);
    expect(screen.getByLabelText("Discharge Pressure")).toHaveValue(8);
    expect(screen.getByLabelText("Mass Flow")).toHaveValue(1);
    expect(screen.getByLabelText("Actual Inlet Flow")).toHaveValue(1);
    expect(screen.getByLabelText("Impeller Stages")).toHaveValue(4);
    expect(screen.getByLabelText("Rotational Speed")).toHaveValue(12000);
    expect(screen.getByText("7.897")).toBeInTheDocument();
    expect(
      screen.getByText("Centrifugal Engineering Workspace Test", {
        exact: false,
      }),
    ).toBeInTheDocument();

    await user.click(
      screen.getByRole("button", {
        name: "Run Calculation",
      }),
    );

    await waitFor(() => {
      expect(executeCentrifugalCalculation).toHaveBeenCalledTimes(1);
    });

    expect(executeCentrifugalCalculation).toHaveBeenCalledWith(
      "test-access-token",
      {
        calculation: {
          gas: {
            suction_pressure_bar: 1.013,
            discharge_pressure_bar: 8,
            suction_temperature_k: 300,
            mass_flow_kg_per_s: 1,
            actual_flow_m3_per_s: 1,
            molecular_weight_kg_per_kmol: 28.97,
            suction_z_factor: 1,
            discharge_z_factor: 1,
            isentropic_exponent: 1.4,
          },
          polytropic_efficiency: 0.82,
          number_of_impeller_stages: 4,
          head_coefficient: 0.65,
          rotational_speed_rpm: 12000,
          mechanical_loss_fraction: 0.03,
          driver_margin_fraction: 0.1,
          selected_driver_power_kw: 500,
          motor_efficiency: 0.95,
          surge_flow_fraction: 0.7,
          anti_surge_margin_fraction: 0.1,
          stonewall_flow_fraction: 1.25,
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
      await screen.findByText("Centrifugal Engineering Complete"),
    ).toBeInTheDocument();
    expect(screen.getByText("DESIGN ADEQUATE")).toBeInTheDocument();
    expect(screen.getByText("Electric Motor")).toBeInTheDocument();
    expect(
      screen.getByText("Scaled Performance-map Points"),
    ).toBeInTheDocument();
    expect(screen.getByText("154.57 kW")).toBeInTheDocument();
    expect(screen.getByText("30%")).toBeInTheDocument();
  });

  it("blocks an invalid pressure basis, clears results, and resets defaults", async () => {
    vi.mocked(executeCentrifugalCalculation).mockResolvedValue(
      resultFixture,
    );

    const user = renderPage();

    await user.click(
      screen.getByRole("button", {
        name: "Run Calculation",
      }),
    );

    expect(
      await screen.findByText("Centrifugal Engineering Complete"),
    ).toBeInTheDocument();

    const dischargePressureInput = screen.getByLabelText(
      "Discharge Pressure",
    );

    await user.clear(dischargePressureInput);
    await user.type(dischargePressureInput, "1");

    expect(
      screen.getByText(
        "Use positive absolute conditions, keep discharge pressure above suction pressure, and enter an isentropic exponent greater than one.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.queryByText("Centrifugal Engineering Complete"),
    ).not.toBeInTheDocument();
    expect(
      screen.getByRole("button", {
        name: "Run Calculation",
      }),
    ).toBeDisabled();
    expect(
      screen.getByRole("button", {
        name: "Calculate Centrifugal Case",
      }),
    ).toBeDisabled();

    await user.click(
      screen.getByRole("button", {
        name: "Reset",
      }),
    );

    expect(dischargePressureInput).toHaveValue(8);
    expect(
      screen.getByRole("button", {
        name: "Run Calculation",
      }),
    ).toBeEnabled();
    expect(executeCentrifugalCalculation).toHaveBeenCalledTimes(1);
  });

  it("persists the calculation and links to the saved calculation case", async () => {
    vi.mocked(executeCentrifugalCalculation).mockResolvedValue({
      ...resultFixture,
      calculation_case_id: 1098,
    });

    const user = renderPage();

    await user.click(
      screen.getByRole("checkbox", {
        name: /Save Result to Project/,
      }),
    );

    await user.type(
      screen.getByLabelText("Calculation Code"),
      "S15-M10-CALC-001",
    );

    const calculationTitleInput = screen.getByLabelText(
      "Calculation Title",
    );
    await user.clear(calculationTitleInput);
    await user.type(
      calculationTitleInput,
      "Centrifugal Compressor Review",
    );

    await user.type(
      screen.getByLabelText("Engineering Notes"),
      "Confirm driver selection and anti-surge control basis.",
    );

    await user.click(
      screen.getByRole("button", {
        name: "Run Calculation",
      }),
    );

    await waitFor(() => {
      expect(executeCentrifugalCalculation).toHaveBeenCalledTimes(1);
    });

    expect(executeCentrifugalCalculation).toHaveBeenCalledWith(
      "test-access-token",
      expect.objectContaining({
        execution: {
          persist_result: true,
          project_id: 42,
          calculation_code: "S15-M10-CALC-001",
          title: "Centrifugal Compressor Review",
          engineering_notes:
            "Confirm driver selection and anti-surge control basis.",
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
      "/projects/42/calculations/1098",
    );
  });

  it("renders backend validation detail for a rejected calculation", async () => {
    vi.mocked(executeCentrifugalCalculation).mockRejectedValue(
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
        name: "Run Calculation",
      }),
    );

    expect(
      await screen.findByText("Centrifugal Calculation Error"),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "Discharge pressure must be greater than suction pressure.",
      ),
    ).toBeInTheDocument();
  });
});
