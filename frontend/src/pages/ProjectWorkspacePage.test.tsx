import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useProjectContext } from "../features/projects/useProjectContext";
import type { Project } from "../types/project";
import { ProjectWorkspacePage } from "./ProjectWorkspacePage";

vi.mock("../features/projects/useProjectContext", () => ({
  useProjectContext: vi.fn(),
}));

type ProjectContextValue = ReturnType<typeof useProjectContext>;

type ProjectQuery = ProjectContextValue["projectQuery"];

const projectFixture: Project = {
  id: 42,
  organization_id: 6971,
  project_code: "KES-DEMO-001",
  project_name: "KES Compressor Engineering Demonstration",
  client_name: "Kamra Engineering Solutions",
  plant_name: "KES Demonstration Plant",
  location: "Mohali, Punjab",
  service_description:
    "Controlled compressor engineering demonstration project.",
  status: "DRAFT",
  created_at: "2026-08-28T00:00:00Z",
  updated_at: "2026-08-29T00:00:00Z",
};

function configureProjectContext(project: Project = projectFixture): void {
  const projectQuery = {
    data: project,
    error: null,
    isError: false,
    isFetching: false,
    isPending: false,
    refetch: vi.fn(),
  } as unknown as ProjectQuery;

  vi.mocked(useProjectContext).mockReturnValue({
    projectId: project.id,
    hasValidProjectId: true,
    project,
    projectQuery,
  });
}

function renderPage(): void {
  render(
    <MemoryRouter initialEntries={["/projects/42"]}>
      <ProjectWorkspacePage />
    </MemoryRouter>,
  );
}

describe("ProjectWorkspacePage", () => {
  beforeEach(() => {
    configureProjectContext();
  });

  it("renders authenticated project identity and neutral workflow terminology", () => {
    renderPage();

    expect(
      screen.getByRole("heading", {
        name: "KES Compressor Engineering Demonstration",
      }),
    ).toBeInTheDocument();

    expect(screen.getByText("KES-DEMO-001")).toBeInTheDocument();

    expect(screen.getByText("Kamra Engineering Solutions")).toBeInTheDocument();

    expect(screen.getByText("KES Demonstration Plant")).toBeInTheDocument();

    expect(screen.getByText("Mohali, Punjab")).toBeInTheDocument();

    expect(screen.getByText("New System Design")).toBeInTheDocument();

    expect(screen.getByText("Existing Plant Assessment")).toBeInTheDocument();

    expect(
      screen.queryByText("Greenfield System Design"),
    ).not.toBeInTheDocument();

    expect(
      screen.queryByText("Brownfield Plant Assessment"),
    ).not.toBeInTheDocument();

    expect(screen.queryByText("Available")).not.toBeInTheDocument();

    expect(screen.getAllByText("Ready")).toHaveLength(6);
  });

  it("provides project-scoped engineering workflow links", () => {
    renderPage();

    expect(
      screen.getByRole("link", {
        name: "Open New System Design",
      }),
    ).toHaveAttribute("href", "/projects/42/greenfield");

    expect(
      screen.getByRole("link", {
        name: "Open Plant Assessment",
      }),
    ).toHaveAttribute("href", "/projects/42/brownfield");

    expect(
      screen.getByRole("link", {
        name: "Open Performance Analysis",
      }),
    ).toHaveAttribute("href", "/projects/42/performance");

    expect(
      screen.getByRole("link", {
        name: "Open Leakage Management",
      }),
    ).toHaveAttribute("href", "/projects/42/leakage");

    expect(
      screen.getByRole("link", {
        name: "Open Allied Equipment",
      }),
    ).toHaveAttribute("href", "/projects/42/allied-equipment");

    expect(
      screen.getByRole("link", {
        name: "Open Skid Engineering",
      }),
    ).toHaveAttribute("href", "/projects/42/skid");

    expect(
      screen.getByRole("link", {
        name: "Open Compressor Engineering",
      }),
    ).toHaveAttribute("href", "/projects/42/compressor");
  });

  it("separates project records and governance navigation", () => {
    renderPage();

    expect(
      screen.getByRole("heading", {
        name: "Engineering Records & Governance",
      }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("link", {
        name: "Open Calculation Records",
      }),
    ).toHaveAttribute("href", "/projects/42/calculations");

    expect(
      screen.getByRole("link", {
        name: "Open Assessments",
      }),
    ).toHaveAttribute("href", "/assessments");

    expect(
      screen.getByRole("link", {
        name: "Open Reports",
      }),
    ).toHaveAttribute("href", "/reports");

    expect(
      screen.getByRole("link", {
        name: "Return to Projects",
      }),
    ).toHaveAttribute("href", "/projects");
  });

  it("renders safe fallbacks for optional project metadata", () => {
    configureProjectContext({
      ...projectFixture,
      client_name: null,
      plant_name: null,
      location: null,
      service_description: null,
    });

    renderPage();

    expect(screen.getAllByText("Not specified")).toHaveLength(3);

    expect(
      screen.getByText(
        "Select the engineering workflow required for this project. Calculations, assessments, revisions, and reports remain linked to the authenticated project context.",
      ),
    ).toBeInTheDocument();
  });
});
