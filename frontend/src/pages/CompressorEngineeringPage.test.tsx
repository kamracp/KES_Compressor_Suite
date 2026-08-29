import { render, screen, within } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useProjectContext } from "../features/projects/useProjectContext";
import type { Project } from "../types/project";
import { CompressorEngineeringPage } from "./CompressorEngineeringPage";

vi.mock("../features/projects/useProjectContext", () => ({
  useProjectContext: vi.fn(),
}));

type ProjectContextValue = ReturnType<typeof useProjectContext>;
type ProjectQuery = ProjectContextValue["projectQuery"];

const projectFixture: Project = {
  id: 42,
  organization_id: 6406,
  project_code: "S15-M13-TEST",
  project_name: "Professional Compressor Engineering Hub",
  client_name: "KES Test Client",
  plant_name: null,
  location: null,
  service_description: null,
  status: "DRAFT",
  created_at: "2026-08-29T00:00:00Z",
  updated_at: "2026-08-29T00:00:00Z",
};

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

function renderPage(): void {
  render(
    <MemoryRouter initialEntries={["/projects/42/compressor/engineering"]}>
      <Routes>
        <Route
          path="/projects/:projectId/compressor/engineering"
          element={<CompressorEngineeringPage />}
        />
      </Routes>
    </MemoryRouter>,
  );
}

describe("CompressorEngineeringPage", () => {
  beforeEach(() => {
    configureProjectContext();
  });

  it("renders the active project and ordered engineering workflow", () => {
    renderPage();

    expect(
      screen.getByRole("heading", {
        name: "Advanced Compressor Engineering",
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "S15-M13-TEST · Professional Compressor Engineering Hub",
      ),
    ).toBeInTheDocument();
    expect(screen.getByText("Operational")).toBeInTheDocument();

    const workflow = screen.getByRole("list");
    const steps = within(workflow).getAllByRole("listitem");

    expect(steps).toHaveLength(5);
    expect(steps[0]).toHaveTextContent("Step 1 · Define Gas");
    expect(steps[0]).toHaveTextContent("Gas Properties");
    expect(steps[1]).toHaveTextContent("Step 2 · Select Technology");
    expect(steps[1]).toHaveTextContent("Compressor Technology Selection");
    expect(steps[2]).toHaveTextContent("Step 3 · Establish Duty");
    expect(steps[2]).toHaveTextContent("Compression Engineering");
    expect(steps[3]).toHaveTextContent("Step 4 · Detailed Engineering");
    expect(steps[3]).toHaveTextContent("Reciprocating Compressor");
    expect(steps[4]).toHaveTextContent("Step 5 · Detailed Engineering");
    expect(steps[4]).toHaveTextContent("Centrifugal Compressor");
    expect(within(workflow).getAllByText("Ready")).toHaveLength(5);
  });

  it("provides project-scoped links for every engineering workspace", () => {
    renderPage();

    expect(
      screen.getByRole("link", { name: "Project Workspace" }),
    ).toHaveAttribute("href", "/projects/42");
    expect(
      screen.getByRole("link", { name: "Open Gas Properties" }),
    ).toHaveAttribute("href", "/projects/42/compressor/gas");
    expect(
      screen.getByRole("link", {
        name: "Open Compressor Technology Selection",
      }),
    ).toHaveAttribute("href", "/projects/42/compressor/selection");
    expect(
      screen.getByRole("link", { name: "Open Compression Engineering" }),
    ).toHaveAttribute("href", "/projects/42/compressor/compression");
    expect(
      screen.getByRole("link", { name: "Open Reciprocating Compressor" }),
    ).toHaveAttribute("href", "/projects/42/compressor/reciprocating");
    expect(
      screen.getByRole("link", { name: "Open Centrifugal Compressor" }),
    ).toHaveAttribute("href", "/projects/42/compressor/centrifugal");
  });

  it("separates calculation records as governance and audit", () => {
    renderPage();

    expect(screen.getByText("Governance and audit")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", {
        name: "Engineering Calculation Records",
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: "Open calculation records" }),
    ).toHaveAttribute("href", "/projects/42/calculations");
    expect(screen.queryByText("Available")).not.toBeInTheDocument();
    expect(screen.queryByText("Greenfield")).not.toBeInTheDocument();
    expect(screen.queryByText("Brownfield")).not.toBeInTheDocument();
  });
});
