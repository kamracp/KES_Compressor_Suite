import type { ReactNode } from "react";

import {
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import {
  render,
  screen,
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
import {
  getCalculationCase,
  listProjectCalculationCases,
} from "../features/projects/calculationCaseService";
import type { CalculationCase } from "../features/projects/calculationCaseTypes";
import { useProjectContext } from "../features/projects/useProjectContext";
import { ApiError } from "../services/apiClient";
import type { Project } from "../types/project";
import { CalculationDetailPage } from "./CalculationDetailPage";
import { CalculationHistoryPage } from "./CalculationHistoryPage";

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
  "../features/projects/calculationCaseService",
  () => ({
    getCalculationCase: vi.fn(),
    listProjectCalculationCases: vi.fn(),
  }),
);

type ProjectContextValue = ReturnType<typeof useProjectContext>;

type ProjectQuery = ProjectContextValue["projectQuery"];

const projectFixture: Project = {
  id: 42,
  organization_id: 6406,
  project_code: "S15-M11-TEST",
  project_name: "Calculation Records Workspace Test",
  client_name: "KES Test Client",
  plant_name: null,
  location: null,
  service_description: null,
  status: "DRAFT",
  created_at: "2026-08-27T00:00:00Z",
  updated_at: "2026-08-27T00:00:00Z",
};

const calculationFixture: CalculationCase = {
  id: 77,
  project_id: 42,
  calculation_code: "S15-M11-COMP-001",
  calculation_type: "COMPRESSION",
  status: "COMPLETED",
  revision: 1,
  title: "Compression Engineering Calculation",
  description: "Project calculation integrity test.",
  input_data: {
    suction_pressure_bar: 1.013,
  },
  result_data: {
    overall_status: "PASS",
  },
  engineering_notes:
    "Authenticated project calculation test.",
  created_at: "2026-08-27T00:00:00Z",
  updated_at: "2026-08-27T00:02:00Z",
  completed_at: "2026-08-27T00:05:00Z",
};

const centrifugalDraftFixture: CalculationCase = {
  ...calculationFixture,
  id: 78,
  calculation_code: "S15-M11-CENT-002",
  calculation_type: "CENTRIFUGAL",
  status: "DRAFT",
  revision: 2,
  title: "Centrifugal Driver Review",
  description: "Draft driver and anti-surge engineering review.",
  result_data: null,
  engineering_notes: "Confirm the selected driver margin.",
  created_at: "2026-08-27T01:00:00Z",
  updated_at: "2026-08-27T01:05:00Z",
  completed_at: null,
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

function renderPage({
  element,
  initialEntry,
  routePath,
}: {
  element: ReactNode;
  initialEntry: string;
  routePath: string;
}) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  const user = userEvent.setup();

  render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[initialEntry]}>
        <Routes>
          <Route
            path={routePath}
            element={element}
          />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );

  return {
    queryClient,
    user,
  };
}

describe("calculation records workspace", () => {
  beforeEach(() => {
    configureAuth();
    configureProjectContext();
    vi.mocked(getCalculationCase).mockReset();
    vi.mocked(listProjectCalculationCases).mockReset();
  });

  it("loads project-scoped calculation history and record navigation", async () => {
    vi.mocked(listProjectCalculationCases).mockResolvedValue([
      calculationFixture,
    ]);

    const { queryClient } = renderPage({
      element: <CalculationHistoryPage />,
      initialEntry: "/projects/42/calculations",
      routePath: "/projects/:projectId/calculations",
    });

    expect(
      await screen.findByText(calculationFixture.calculation_code),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Calculation Records Workspace Test", {
        exact: false,
      }),
    ).toBeInTheDocument();

    expect(listProjectCalculationCases).toHaveBeenCalledWith(
      "test-access-token",
      42,
    );

    expect(
      queryClient.getQueryData([
        "projects",
        42,
        "calculation-cases",
      ]),
    ).toEqual([calculationFixture]);

    expect(
      screen.getByRole("link", {
        name: "Open",
      }),
    ).toHaveAttribute(
      "href",
      "/projects/42/calculations/77",
    );
  });

  it("filters calculation history by type, status, and search text", async () => {
    vi.mocked(listProjectCalculationCases).mockResolvedValue([
      calculationFixture,
      centrifugalDraftFixture,
    ]);

    const { user } = renderPage({
      element: <CalculationHistoryPage />,
      initialEntry: "/projects/42/calculations",
      routePath: "/projects/:projectId/calculations",
    });

    expect(
      await screen.findByText(calculationFixture.calculation_code),
    ).toBeInTheDocument();
    expect(
      screen.getByText(centrifugalDraftFixture.calculation_code),
    ).toBeInTheDocument();

    await user.selectOptions(
      screen.getByLabelText("Calculation Type"),
      "CENTRIFUGAL",
    );

    expect(
      screen.queryByText(calculationFixture.calculation_code),
    ).not.toBeInTheDocument();
    expect(
      screen.getByText(centrifugalDraftFixture.calculation_code),
    ).toBeInTheDocument();

    await user.selectOptions(
      screen.getByLabelText("Calculation Type"),
      "ALL",
    );
    await user.selectOptions(
      screen.getByLabelText("Record Status"),
      "COMPLETED",
    );

    expect(
      screen.getByText(calculationFixture.calculation_code),
    ).toBeInTheDocument();
    expect(
      screen.queryByText(centrifugalDraftFixture.calculation_code),
    ).not.toBeInTheDocument();

    await user.selectOptions(
      screen.getByLabelText("Record Status"),
      "ALL",
    );
    await user.type(
      screen.getByLabelText("Search Records"),
      "driver review",
    );

    expect(
      screen.queryByText(calculationFixture.calculation_code),
    ).not.toBeInTheDocument();
    expect(
      screen.getByText(centrifugalDraftFixture.calculation_code),
    ).toBeInTheDocument();
  });

  it("renders calculation-history API detail for a failed load", async () => {
    vi.mocked(listProjectCalculationCases).mockRejectedValue(
      new ApiError(
        "API request failed with status 503.",
        503,
        {
          detail: "Calculation register is temporarily unavailable.",
        },
      ),
    );

    renderPage({
      element: <CalculationHistoryPage />,
      initialEntry: "/projects/42/calculations",
      routePath: "/projects/:projectId/calculations",
    });

    expect(
      await screen.findByText("Calculation History Unavailable"),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "Calculation register is temporarily unavailable.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", {
        name: "Retry History Load",
      }),
    ).toBeInTheDocument();
  });

  it("loads calculation detail with a project-scoped cache key", async () => {
    vi.mocked(getCalculationCase).mockResolvedValue(
      calculationFixture,
    );

    const { queryClient } = renderPage({
      element: <CalculationDetailPage />,
      initialEntry: "/projects/42/calculations/77",
      routePath:
        "/projects/:projectId/calculations/:calculationCaseId",
    });

    expect(
      await screen.findByRole("heading", {
        name: calculationFixture.title,
      }),
    ).toBeInTheDocument();

    expect(getCalculationCase).toHaveBeenCalledWith(
      "test-access-token",
      77,
    );

    expect(
      queryClient.getQueryData([
        "projects",
        42,
        "calculation-case",
        77,
      ]),
    ).toEqual(calculationFixture);

    expect(
      screen.getByRole("link", {
        name: "Back to Calculation History",
      }),
    ).toHaveAttribute(
      "href",
      "/projects/42/calculations",
    );
    expect(
      screen.getByText("Authenticated project calculation test."),
    ).toBeInTheDocument();
    expect(screen.getByText(/"overall_status": "PASS"/)).toBeInTheDocument();
    expect(screen.getByText("Project Scope Verified")).toBeInTheDocument();
  });

  it("renders an explicit missing-result review state", async () => {
    vi.mocked(getCalculationCase).mockResolvedValue({
      ...centrifugalDraftFixture,
      project_id: 42,
    });

    renderPage({
      element: <CalculationDetailPage />,
      initialEntry: "/projects/42/calculations/78",
      routePath:
        "/projects/:projectId/calculations/:calculationCaseId",
    });

    expect(
      await screen.findByRole("heading", {
        name: centrifugalDraftFixture.title,
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByText("No result data available."),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", {
        name: "Open Source Module",
      }),
    ).toHaveAttribute(
      "href",
      "/projects/42/compressor/centrifugal",
    );
  });

  it("blocks a calculation belonging to another project", async () => {
    vi.mocked(getCalculationCase).mockResolvedValue({
      ...calculationFixture,
      project_id: 99,
    });

    renderPage({
      element: <CalculationDetailPage />,
      initialEntry: "/projects/42/calculations/77",
      routePath:
        "/projects/:projectId/calculations/:calculationCaseId",
    });

    expect(
      await screen.findByRole("heading", {
        name: "Calculation Project Mismatch",
      }),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        "This calculation does not belong to the requested project.",
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("link", {
        name: "Return to Calculation History",
      }),
    ).toHaveAttribute(
      "href",
      "/projects/42/calculations",
    );
  });
});
