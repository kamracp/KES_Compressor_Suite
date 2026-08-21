import type { PropsWithChildren } from "react";

import {
  render,
  screen,
} from "@testing-library/react";
import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import type { Project } from "../types/project";
import { useAuth } from "../features/auth/AuthProvider";
import { useProjectContext } from "../features/projects/useProjectContext";
import { AppRouter } from "./AppRouter";

vi.mock("../features/auth/AuthProvider", () => ({
  useAuth: vi.fn(),
}));

vi.mock(
  "../features/projects/useProjectContext",
  () => ({
    useProjectContext: vi.fn(),
  }),
);

vi.mock("../layouts/AppLayout", () => ({
  AppLayout: ({
    children,
  }: PropsWithChildren) => (
    <>
      {children}
    </>
  ),
}));

vi.mock("../pages/DashboardPage", () => ({
  DashboardPage: () => (
    <p>Dashboard route content</p>
  ),
}));

vi.mock("../pages/LoginPage", () => ({
  LoginPage: () => (
    <p>Login route content</p>
  ),
}));

vi.mock("../pages/ProjectWorkspacePage", () => ({
  ProjectWorkspacePage: () => (
    <p>Project workspace route content</p>
  ),
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

type AuthOptions = {
  isAuthenticated?: boolean;
  isLoading?: boolean;
};

function configureAuth({
  isAuthenticated = true,
  isLoading = false,
}: AuthOptions = {}): void {
  vi.mocked(useAuth).mockReturnValue({
    accessToken:
      isAuthenticated
        ? "test-access-token"
        : null,
    currentUser: null,
    isAuthenticated,
    isLoading,
    login: vi.fn(async () => undefined),
    logout: vi.fn(),
  });
}

type ProjectOptions = {
  hasProject?: boolean;
  hasValidProjectId?: boolean;
  query?: Partial<ProjectQuery>;
};

function configureProjectContext({
  hasProject = true,
  hasValidProjectId = true,
  query = {},
}: ProjectOptions = {}): void {
  const project = hasProject
    ? projectFixture
    : undefined;

  const projectQuery = {
    data: project,
    error: null,
    isError: false,
    isFetching: false,
    isPending: false,
    refetch: vi.fn(),
    ...query,
  } as ProjectQuery;

  vi.mocked(useProjectContext).mockReturnValue({
    projectId: 42,
    hasValidProjectId,
    project,
    projectQuery,
  });
}

function renderRoute(path: string) {
  window.history.pushState(
    {},
    "",
    path,
  );

  return render(<AppRouter />);
}

describe("AppRouter project context integration", () => {
  beforeEach(() => {
    window.history.pushState(
      {},
      "",
      "/",
    );

    configureAuth();
    configureProjectContext();
  });

  it("renders a resolved authenticated project route", () => {
    renderRoute("/projects/42");

    expect(
      screen.getByText(
        "Project workspace route content",
      ),
    ).toBeInTheDocument();

    expect(useProjectContext).toHaveBeenCalledTimes(1);
  });

  it("blocks an invalid project route before page rendering", () => {
    configureProjectContext({
      hasProject: false,
      hasValidProjectId: false,
    });

    renderRoute("/projects/not-a-number");

    expect(
      screen.getByRole("alert"),
    ).toHaveTextContent(
      "Invalid Project Address",
    );

    expect(
      screen.queryByText(
        "Project workspace route content",
      ),
    ).not.toBeInTheDocument();
  });

  it("does not resolve project context for non-project routes", () => {
    renderRoute("/");

    expect(
      screen.getByText("Dashboard route content"),
    ).toBeInTheDocument();

    expect(useProjectContext).not.toHaveBeenCalled();
  });

  it("redirects unauthenticated project access before context loading", async () => {
    configureAuth({
      isAuthenticated: false,
    });

    renderRoute("/projects/42");

    expect(
      await screen.findByText(
        "Login route content",
      ),
    ).toBeInTheDocument();

    expect(useProjectContext).not.toHaveBeenCalled();
  });

  it("waits for session restoration before context loading", () => {
    configureAuth({
      isAuthenticated: false,
      isLoading: true,
    });

    renderRoute("/projects/42");

    expect(
      screen.getByText("Loading session..."),
    ).toBeInTheDocument();

    expect(useProjectContext).not.toHaveBeenCalled();
  });
});