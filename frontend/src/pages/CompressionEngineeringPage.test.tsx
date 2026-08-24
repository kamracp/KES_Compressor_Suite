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

import type { Project } from "../types/project";
import { useAuth } from "../features/auth/AuthProvider";
import {
  executeCompressionCalculation,
} from "../features/projects/compressionService";
import type {
  CompressionExecutionResponse,
} from "../features/projects/compressionTypes";
import { useProjectContext } from "../features/projects/useProjectContext";
import { CompressionEngineeringPage } from "./CompressionEngineeringPage";

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
  "../features/projects/compressionService",
  () => ({
    executeCompressionCalculation: vi.fn(),
  }),
);

type ProjectContextValue =
  ReturnType<typeof useProjectContext>;

type ProjectQuery =
  ProjectContextValue["projectQuery"];

const projectFixture: Project = {
  id: 42,
  organization_id: 6406,
  project_code: "S15-M6-TEST",
  project_name: "Compression Workspace Test",
  client_name: "KES Test Client",
  plant_name: null,
  location: null,
  service_description: null,
  status: "DRAFT",
  created_at: "2026-08-24T00:00:00Z",
  updated_at: "2026-08-24T00:00:00Z",
};

const commonResult = {
  staging: {
    stage_compression_ratio: "2.810219679945996",
  },
  temperature: {
    actual_discharge_temperature_k: "428.782147859338125",
  },
};

const passingValidationChecks = [
  {
    code: "STAGE_RATIO_OK",
    description:
      "Stage compression ratio is within the recommended range.",
    status: "PASS",
    actual_value: "2.810219679945996",
    limit_description: "1.2 to 4.0",
  },
  {
    code: "DISCHARGE_TEMP_OK",
    description:
      "Discharge temperature is within the allowable limit.",
    status: "PASS",
    actual_value: "428.782147859338125",
    limit_description: "<= 473.15 K",
  },
  {
    code: "DRIVER_OK",
    description: "Selected driver rating is adequate.",
    status: "PASS",
    actual_value: true,
    limit_description: "Selected driver >= required driver",
  },
];

const passResponse: CompressionExecutionResponse = {
  calculation_case_id: null,
  result: {
    ...commonResult,
    driver: {
      shaft_power_kw: "272.4759128392312304605263158",
      required_driver_power_kw: "299.7235041231543535065789474",
      selected_driver_power_kw: "500",
      driver_margin_kw: "200.2764958768456464934210526",
    },
    validation_checks: passingValidationChecks,
    overall_status: "PASS",
  },
};

const failResponse: CompressionExecutionResponse = {
  calculation_case_id: null,
  result: {
    ...commonResult,
    driver: {
      shaft_power_kw: "272.4759128392312304605263158",
      required_driver_power_kw: "299.7235041231543535065789474",
      selected_driver_power_kw: "250",
      driver_margin_kw: "-49.7235041231543535065789474",
    },
    validation_checks: [
      ...passingValidationChecks.slice(0, 2),
      {
        code: "DRIVER_UNDERSIZED",
        description:
          "Selected driver rating is below the required power.",
        status: "FAIL",
        actual_value: false,
        limit_description: "Selected driver >= required driver",
      },
    ],
    overall_status: "FAIL",
  },
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
      <MemoryRouter initialEntries={["/projects/42/compressor/compression"]}>
        <Routes>
          <Route
            path="/projects/:projectId/compressor/compression"
            element={<CompressionEngineeringPage />}
          />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );

  return user;
}

describe("CompressionEngineeringPage", () => {
  beforeEach(() => {
    configureAuth();
    configureProjectContext();
    vi.mocked(executeCompressionCalculation).mockReset();
  });

  it("submits the backend-compatible default driver service margin", async () => {
    vi.mocked(
      executeCompressionCalculation,
    ).mockResolvedValue(passResponse);

    const user = renderPage();

    expect(
      screen.getByLabelText("Driver Service Margin"),
    ).toHaveValue(0.1);

    await user.click(
      screen.getByRole("button", {
        name: "Run Calculation",
      }),
    );

    await waitFor(() => {
      expect(
        executeCompressionCalculation,
      ).toHaveBeenCalledTimes(1);
    });

    expect(
      executeCompressionCalculation,
    ).toHaveBeenCalledWith(
      "test-access-token",
      expect.objectContaining({
        calculation: expect.objectContaining({
          selected_driver_power_kw: 500,
          driver_service_factor: 0.1,
        }),
        execution: {
          persist_result: false,
          project_id: null,
          calculation_code: null,
          title: null,
          engineering_notes: null,
        },
      }),
    );

    expect(
      await screen.findByText("3 of 3 passed"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Compression Engineering Result"),
    ).toBeInTheDocument();
    expect(screen.getByText("299.724")).toBeInTheDocument();
    expect(screen.getByText("200.276")).toBeInTheDocument();
  });

  it("renders failed driver validation as an engineering review state", async () => {
    vi.mocked(
      executeCompressionCalculation,
    ).mockResolvedValue(failResponse);

    const user = renderPage();
    const selectedDriverInput = screen.getByLabelText(
      "Selected Driver Power",
    );

    await user.clear(selectedDriverInput);
    await user.type(selectedDriverInput, "250");
    await user.click(
      screen.getByRole("button", {
        name: "Run Calculation",
      }),
    );

    expect(
      await screen.findByText("Engineering Review Required"),
    ).toBeInTheDocument();
    expect(screen.getByText("2 of 3 passed")).toBeInTheDocument();
    expect(screen.getByText("DRIVER UNDERSIZED")).toBeInTheDocument();
    expect(screen.getByText("-49.724")).toBeInTheDocument();

    expect(
      executeCompressionCalculation,
    ).toHaveBeenCalledWith(
      "test-access-token",
      expect.objectContaining({
        calculation: expect.objectContaining({
          selected_driver_power_kw: 250,
          driver_service_factor: 0.1,
        }),
      }),
    );
  });
});
