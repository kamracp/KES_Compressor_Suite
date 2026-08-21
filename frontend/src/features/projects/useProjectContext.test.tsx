import type { PropsWithChildren } from "react";

import {
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import {
  renderHook,
  waitFor,
} from "@testing-library/react";
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

import type { Project } from "../../types/project";
import { useAuth } from "../auth/AuthProvider";
import { getProject } from "./projectService";
import { useProjectContext } from "./useProjectContext";

vi.mock("../auth/AuthProvider", () => ({
  useAuth: vi.fn(),
}));

vi.mock("./projectService", () => ({
  getProject: vi.fn(),
}));

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

function configureAuth(
  accessToken: string | null,
): void {
  vi.mocked(useAuth).mockReturnValue({
    accessToken,
    currentUser: null,
    isAuthenticated: Boolean(accessToken),
    isLoading: false,
    login: vi.fn(async () => undefined),
    logout: vi.fn(),
  });
}

function createHarness(route: string) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  function Wrapper({
    children,
  }: PropsWithChildren) {
    return (
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={[route]}>
          <Routes>
            <Route
              path="/projects/:projectId"
              element={children}
            />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );
  }

  return {
    queryClient,
    Wrapper,
  };
}

describe("useProjectContext", () => {
  beforeEach(() => {
    configureAuth("test-access-token");
    vi.mocked(getProject).mockReset();
  });

  it("fetches and caches the authenticated route project", async () => {
    vi.mocked(getProject).mockResolvedValue(projectFixture);

    const {
      queryClient,
      Wrapper,
    } = createHarness("/projects/42");

    const { result } = renderHook(
      () => useProjectContext(),
      {
        wrapper: Wrapper,
      },
    );

    expect(result.current.projectId).toBe(42);
    expect(result.current.hasValidProjectId).toBe(true);

    await waitFor(() => {
      expect(result.current.projectQuery.isSuccess).toBe(true);
    });

    expect(getProject).toHaveBeenCalledTimes(1);
    expect(getProject).toHaveBeenCalledWith(
      "test-access-token",
      42,
    );
    expect(result.current.project).toEqual(projectFixture);
    expect(
      queryClient.getQueryData([
        "projects",
        42,
      ]),
    ).toEqual(projectFixture);
  });

  it.each([
    "/projects/0",
    "/projects/not-a-number",
  ])(
    "rejects invalid route project ID %s",
    (route) => {
      const { Wrapper } = createHarness(route);

      const { result } = renderHook(
        () => useProjectContext(),
        {
          wrapper: Wrapper,
        },
      );

      expect(result.current.hasValidProjectId).toBe(false);
      expect(result.current.projectQuery.fetchStatus).toBe("idle");
      expect(getProject).not.toHaveBeenCalled();
    },
  );

  it("does not fetch without an authenticated access token", () => {
    configureAuth(null);

    const { Wrapper } = createHarness("/projects/42");

    const { result } = renderHook(
      () => useProjectContext(),
      {
        wrapper: Wrapper,
      },
    );

    expect(result.current.projectId).toBe(42);
    expect(result.current.hasValidProjectId).toBe(true);
    expect(result.current.projectQuery.fetchStatus).toBe("idle");
    expect(getProject).not.toHaveBeenCalled();
  });

  it("exposes project API failures through the query result", async () => {
    vi.mocked(getProject).mockRejectedValue(
      new Error("Project request failed."),
    );

    const { Wrapper } = createHarness("/projects/42");

    const { result } = renderHook(
      () => useProjectContext(),
      {
        wrapper: Wrapper,
      },
    );

    await waitFor(() => {
      expect(result.current.projectQuery.isError).toBe(true);
    });

    expect(result.current.project).toBeUndefined();
    expect(result.current.projectQuery.error).toEqual(
      new Error("Project request failed."),
    );
  });
});