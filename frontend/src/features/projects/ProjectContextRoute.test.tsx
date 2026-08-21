import {
  fireEvent,
  render,
  screen,
} from "@testing-library/react";
import { MemoryRouter } from "react-router";
import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import type { Project } from "../../types/project";
import { ApiError } from "../../services/apiClient";
import { ProjectContextRoute } from "./ProjectContextRoute";
import { useProjectContext } from "./useProjectContext";

vi.mock("./useProjectContext", () => ({
  useProjectContext: vi.fn(),
}));

type ProjectContextValue =
  ReturnType<typeof useProjectContext>;

type ProjectQuery =
  ProjectContextValue["projectQuery"];

const projectFixture: Project = {
  id: 42,
  organization_id: 6406,
  project_code: "S15-M4-TEST",
  project_name: "Project Context Test",
  client_name: "KES Test Client",
  plant_name: null,
  location: null,
  service_description: null,
  status: "DRAFT",
  created_at: "2026-08-21T00:00:00Z",
  updated_at: "2026-08-21T00:00:00Z",
};

const refetchMock = vi.fn();

type ContextOptions = {
  hasProject?: boolean;
  hasValidProjectId?: boolean;
  query?: Partial<ProjectQuery>;
};

function configureProjectContext({
  hasProject = true,
  hasValidProjectId = true,
  query = {},
}: ContextOptions = {}): void {
  const project = hasProject
    ? projectFixture
    : undefined;

  const projectQuery = {
    data: project,
    error: null,
    isError: false,
    isFetching: false,
    isPending: false,
    refetch: refetchMock,
    ...query,
  } as ProjectQuery;

  vi.mocked(useProjectContext).mockReturnValue({
    projectId: 42,
    hasValidProjectId,
    project,
    projectQuery,
  });
}

function renderBoundary() {
  return render(
    <MemoryRouter>
      <ProjectContextRoute>
        <p>Protected project content</p>
      </ProjectContextRoute>
    </MemoryRouter>,
  );
}

describe("ProjectContextRoute", () => {
  beforeEach(() => {
    refetchMock.mockReset();
    configureProjectContext();
  });

  it("renders project content after context resolution", () => {
    renderBoundary();

    expect(
      screen.getByText("Protected project content"),
    ).toBeInTheDocument();
  });

  it("renders a recoverable invalid project state", () => {
    configureProjectContext({
      hasProject: false,
      hasValidProjectId: false,
    });

    renderBoundary();

    expect(
      screen.getByRole("alert"),
    ).toHaveTextContent("Invalid Project Address");

    expect(
      screen.getByRole("link", {
        name: "Return to Projects",
      }),
    ).toHaveAttribute("href", "/projects");
  });

  it("renders an accessible project loading state", () => {
    configureProjectContext({
      hasProject: false,
      query: {
        isPending: true,
      },
    });

    renderBoundary();

    expect(
      screen.getByRole("status"),
    ).toHaveTextContent("Loading Project Workspace");
  });

  it("renders a project access-denied state", () => {
    configureProjectContext({
      hasProject: false,
      query: {
        error: new ApiError(
          "Forbidden",
          403,
        ),
        isError: true,
      },
    });

    renderBoundary();

    expect(
      screen.getByRole("alert"),
    ).toHaveTextContent("Project Access Denied");
  });

  it("renders a project-not-found state", () => {
    configureProjectContext({
      hasProject: false,
      query: {
        error: new ApiError(
          "Not found",
          404,
        ),
        isError: true,
      },
    });

    renderBoundary();

    expect(
      screen.getByRole("alert"),
    ).toHaveTextContent("Project Not Found");
  });

  it("offers retry for unexpected project failures", () => {
    configureProjectContext({
      hasProject: false,
      query: {
        error: new Error("Network unavailable."),
        isError: true,
      },
    });

    renderBoundary();

    fireEvent.click(
      screen.getByRole("button", {
        name: "Retry Project",
      }),
    );

    expect(refetchMock).toHaveBeenCalledTimes(1);
  });

  it("renders an unavailable state for an empty response", () => {
    configureProjectContext({
      hasProject: false,
    });

    renderBoundary();

    expect(
      screen.getByRole("alert"),
    ).toHaveTextContent("Project Unavailable");
  });
});