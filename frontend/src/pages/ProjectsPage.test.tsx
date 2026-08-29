import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useAuth } from "../features/auth/AuthProvider";
import {
  createProject,
  listProjects,
} from "../features/projects/projectService";
import { ApiError } from "../services/apiClient";
import type { Project } from "../types/project";
import { ProjectsPage } from "./ProjectsPage";

vi.mock("../features/auth/AuthProvider", () => ({
  useAuth: vi.fn(),
}));

vi.mock("../features/projects/projectService", () => ({
  createProject: vi.fn(),
  listProjects: vi.fn(),
}));

const draftProject: Project = {
  id: 42,
  organization_id: 6971,
  project_code: "KES-DEMO-001",
  project_name: "KES Compressor Engineering Demonstration",
  client_name: "Kamra Engineering Solutions",
  plant_name: null,
  location: null,
  service_description: null,
  status: "DRAFT",
  created_at: "2026-08-28T00:00:00Z",
  updated_at: "2026-08-29T00:00:00Z",
};

const activeProject: Project = {
  id: 84,
  organization_id: 6971,
  project_code: "KES-ACTIVE-001",
  project_name: "Active Compressor Optimization",
  client_name: null,
  plant_name: null,
  location: null,
  service_description: null,
  status: "ACTIVE",
  created_at: "2026-08-27T00:00:00Z",
  updated_at: "2026-08-28T00:00:00Z",
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
      <MemoryRouter initialEntries={["/projects"]}>
        <ProjectsPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );

  return user;
}

describe("ProjectsPage", () => {
  beforeEach(() => {
    configureAuth();
    vi.mocked(listProjects).mockReset();
    vi.mocked(createProject).mockReset();
  });

  it("renders the tenant project register with status and navigation", async () => {
    vi.mocked(listProjects).mockResolvedValue([draftProject, activeProject]);

    renderPage();

    expect(
      screen.getByRole("heading", {
        name: "Compressor Engineering Projects",
      }),
    ).toBeInTheDocument();

    expect(
      await screen.findByText("KES Compressor Engineering Demonstration"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("Active Compressor Optimization"),
    ).toBeInTheDocument();
    expect(screen.getByText("Kamra Engineering Solutions")).toBeInTheDocument();
    expect(screen.getByText("Not specified")).toBeInTheDocument();
    expect(screen.getByText("DRAFT")).toBeInTheDocument();
    expect(screen.getByText("ACTIVE")).toBeInTheDocument();

    expect(
      screen.getByRole("link", {
        name: "Open project KES-DEMO-001",
      }),
    ).toHaveAttribute("href", "/projects/42");

    expect(
      screen.getByRole("link", {
        name: "Open project KES-ACTIVE-001",
      }),
    ).toHaveAttribute("href", "/projects/84");

    expect(listProjects).toHaveBeenCalledWith("test-access-token");
  });

  it("renders a professional empty state while keeping creation available", async () => {
    vi.mocked(listProjects).mockResolvedValue([]);

    renderPage();

    expect(await screen.findByText("No projects found")).toBeInTheDocument();

    expect(
      screen.getByText(
        "Create the first compressor engineering project using the controlled form.",
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("button", {
        name: "Create Project",
      }),
    ).toBeDisabled();

    expect(
      screen.getByLabelText("Project Code", {
        exact: false,
      }),
    ).toBeInTheDocument();
  });

  it("creates a normalized project and refreshes the register", async () => {
    const createdProject: Project = {
      ...draftProject,
      id: 105,
      project_code: "KES-NEW-001",
      project_name: "New Compressor Study",
      client_name: "KES Client",
    };

    vi.mocked(listProjects)
      .mockResolvedValueOnce([])
      .mockResolvedValue([createdProject]);

    vi.mocked(createProject).mockResolvedValue(createdProject);

    const user = renderPage();

    await screen.findByText("No projects found");

    await user.type(
      screen.getByLabelText("Project Code", {
        exact: false,
      }),
      "  KES-NEW-001  ",
    );

    await user.type(
      screen.getByLabelText("Project Name", {
        exact: false,
      }),
      "  New Compressor Study  ",
    );

    await user.type(
      screen.getByLabelText("Client Name", {
        exact: false,
      }),
      "  KES Client  ",
    );

    await user.click(
      screen.getByRole("button", {
        name: "Create Project",
      }),
    );

    await waitFor(() => {
      expect(createProject).toHaveBeenCalledTimes(1);
    });

    expect(createProject).toHaveBeenCalledWith("test-access-token", {
      project_code: "KES-NEW-001",
      project_name: "New Compressor Study",
      client_name: "KES Client",
      status: "DRAFT",
    });

    expect(await screen.findByText("Project created")).toBeInTheDocument();

    expect(
      screen.getByText("KES-NEW-001 · New Compressor Study"),
    ).toBeInTheDocument();

    expect(
      screen.getByLabelText("Project Code", {
        exact: false,
      }),
    ).toHaveValue("");

    expect(
      screen.getByLabelText("Project Name", {
        exact: false,
      }),
    ).toHaveValue("");

    await waitFor(() => {
      expect(listProjects).toHaveBeenCalledTimes(2);
    });

    expect(await screen.findByText("New Compressor Study")).toBeInTheDocument();
  });

  it("blocks whitespace-only required fields", async () => {
    vi.mocked(listProjects).mockResolvedValue([]);

    const user = renderPage();

    await screen.findByText("No projects found");

    await user.type(
      screen.getByLabelText("Project Code", {
        exact: false,
      }),
      "   ",
    );

    await user.type(
      screen.getByLabelText("Project Name", {
        exact: false,
      }),
      "   ",
    );

    expect(
      screen.getByRole("button", {
        name: "Create Project",
      }),
    ).toBeDisabled();

    expect(createProject).not.toHaveBeenCalled();
  });

  it("renders backend project-creation validation detail", async () => {
    vi.mocked(listProjects).mockResolvedValue([]);

    vi.mocked(createProject).mockRejectedValue(
      new ApiError("API request failed with status 409.", 409, {
        detail: "Project code already exists in this organization.",
      }),
    );

    const user = renderPage();

    await screen.findByText("No projects found");

    await user.type(
      screen.getByLabelText("Project Code", {
        exact: false,
      }),
      "KES-DUPLICATE",
    );

    await user.type(
      screen.getByLabelText("Project Name", {
        exact: false,
      }),
      "Duplicate Project",
    );

    await user.click(
      screen.getByRole("button", {
        name: "Create Project",
      }),
    );

    expect(
      await screen.findByText("Project creation failed"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("Project code already exists in this organization."),
    ).toBeInTheDocument();
  });
});
