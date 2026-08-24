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
import { calculateGasProperties } from "../features/projects/gasService";
import type { GasPropertiesResponse } from "../features/projects/gasTypes";
import { useProjectContext } from "../features/projects/useProjectContext";
import { ApiError } from "../services/apiClient";
import type { Project } from "../types/project";
import { GasPropertiesPage } from "./GasPropertiesPage";

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
  "../features/projects/gasService",
  () => ({
    calculateGasProperties: vi.fn(),
  }),
);

type ProjectContextValue =
  ReturnType<typeof useProjectContext>;

type ProjectQuery =
  ProjectContextValue["projectQuery"];

const projectFixture: Project = {
  id: 42,
  organization_id: 6406,
  project_code: "S15-M7-TEST",
  project_name: "Gas Properties Workspace Test",
  client_name: "KES Test Client",
  plant_name: null,
  location: null,
  service_description: null,
  status: "DRAFT",
  created_at: "2026-08-24T00:00:00Z",
  updated_at: "2026-08-24T00:00:00Z",
};

const resultFixture: GasPropertiesResponse = {
  molecular_weight_kg_per_kmol: "17.6628",
  specific_gravity_air_1: "0.6098",
  pseudocritical_temperature_k: "196.675",
  pseudocritical_pressure_bar: "46.418",
  reduced_temperature: "1.5254",
  reduced_pressure: "0.2154",
  z_factor: "0.9766",
  z_factor_correlation: "Papay",
  density_kg_per_m3: "7.2511",
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
      <MemoryRouter initialEntries={["/projects/42/compressor/gas"]}>
        <Routes>
          <Route
            path="/projects/:projectId/compressor/gas"
            element={<GasPropertiesPage />}
          />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );

  return user;
}

describe("GasPropertiesPage", () => {
  beforeEach(() => {
    configureAuth();
    configureProjectContext();
    vi.mocked(calculateGasProperties).mockReset();
  });

  it("submits the balanced default gas-property request and renders results", async () => {
    vi.mocked(calculateGasProperties).mockResolvedValue(resultFixture);

    const user = renderPage();

    expect(screen.getByLabelText("Methane (CH₄)")).toHaveValue(0.9);
    expect(screen.getByLabelText("Ethane (C₂H₆)")).toHaveValue(0.05);
    expect(screen.getByLabelText("Nitrogen (N₂)")).toHaveValue(0.03);
    expect(screen.getByLabelText("Carbon Dioxide (CO₂)")).toHaveValue(0.02);
    expect(screen.getByText("1.000000")).toBeInTheDocument();

    await user.click(
      screen.getByRole("button", {
        name: "Run Calculation",
      }),
    );

    await waitFor(() => {
      expect(calculateGasProperties).toHaveBeenCalledTimes(1);
    });

    expect(calculateGasProperties).toHaveBeenCalledWith(
      "test-access-token",
      {
        components: [
          {
            component: "methane",
            mole_fraction: 0.9,
          },
          {
            component: "ethane",
            mole_fraction: 0.05,
          },
          {
            component: "nitrogen",
            mole_fraction: 0.03,
          },
          {
            component: "carbon_dioxide",
            mole_fraction: 0.02,
          },
        ],
        pressure_bar: 10,
        temperature_k: 300,
      },
    );

    expect(
      await screen.findByText("Gas Property Calculation Complete"),
    ).toBeInTheDocument();
    expect(screen.getByText("17.6628")).toBeInTheDocument();
    expect(screen.getByText("0.9766")).toBeInTheDocument();
    expect(screen.getByText("7.2511")).toBeInTheDocument();
    expect(screen.getByText("Papay")).toBeInTheDocument();
  });

  it("blocks an unbalanced mixture, clears stale results, and resets defaults", async () => {
    vi.mocked(calculateGasProperties).mockResolvedValue(resultFixture);

    const user = renderPage();

    await user.click(
      screen.getByRole("button", {
        name: "Run Calculation",
      }),
    );

    expect(
      await screen.findByText("Gas Property Calculation Complete"),
    ).toBeInTheDocument();

    const methaneInput = screen.getByLabelText("Methane (CH₄)");

    await user.clear(methaneInput);
    await user.type(methaneInput, "0.89");

    expect(screen.getByText("0.990000")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Adjust the component fractions until the total equals 1.000000.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.queryByText("Gas Property Calculation Complete"),
    ).not.toBeInTheDocument();
    expect(
      screen.getByRole("button", {
        name: "Run Calculation",
      }),
    ).toBeDisabled();
    expect(
      screen.getByRole("button", {
        name: "Calculate Gas Properties",
      }),
    ).toBeDisabled();

    await user.click(
      screen.getByRole("button", {
        name: "Reset",
      }),
    );

    expect(methaneInput).toHaveValue(0.9);
    expect(screen.getByText("1.000000")).toBeInTheDocument();
    expect(
      screen.getByRole("button", {
        name: "Run Calculation",
      }),
    ).toBeEnabled();
    expect(calculateGasProperties).toHaveBeenCalledTimes(1);
  });

  it("renders the backend validation detail for a rejected calculation", async () => {
    vi.mocked(calculateGasProperties).mockRejectedValue(
      new ApiError(
        "API request failed with status 422.",
        422,
        {
          detail: "Critical properties are unavailable for this component.",
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
      await screen.findByText("Gas Property Calculation Error"),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "Critical properties are unavailable for this component.",
      ),
    ).toBeInTheDocument();
  });
});
