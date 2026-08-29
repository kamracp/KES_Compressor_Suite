import { useMemo, useState, type FormEvent } from "react";

import {
  BriefcaseBusiness,
  CheckCircle2,
  CirclePlus,
  ExternalLink,
  FolderKanban,
  LoaderCircle,
  RefreshCw,
  TriangleAlert,
} from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import { useAuth } from "../features/auth/AuthProvider";
import {
  createProject,
  listProjects,
} from "../features/projects/projectService";
import { ApiError } from "../services/apiClient";
import type { Project } from "../types/project";

function getErrorMessage(error: unknown, fallback: string): string {
  if (
    error instanceof ApiError &&
    typeof error.details === "object" &&
    error.details !== null &&
    "detail" in error.details &&
    typeof error.details.detail === "string"
  ) {
    return error.details.detail;
  }

  return fallback;
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(value));
}

function getStatusClassName(status: string): string {
  switch (status.trim().toUpperCase()) {
    case "ACTIVE":
      return "border-emerald-200 bg-emerald-50 text-emerald-700";
    case "COMPLETED":
      return "border-sky-200 bg-sky-50 text-sky-700";
    case "DRAFT":
      return "border-amber-200 bg-amber-50 text-amber-700";
    case "ARCHIVED":
      return "border-slate-200 bg-slate-100 text-slate-600";
    default:
      return "border-slate-200 bg-white text-slate-700";
  }
}

function ProjectStatusBadge({ status }: { status: string }) {
  return (
    <Badge variant="outline" className={getStatusClassName(status)}>
      {status}
    </Badge>
  );
}

export function ProjectsPage() {
  const queryClient = useQueryClient();
  const { accessToken } = useAuth();

  const [projectCode, setProjectCode] = useState("");
  const [projectName, setProjectName] = useState("");
  const [clientName, setClientName] = useState("");
  const [createdProject, setCreatedProject] = useState<Project | null>(null);

  if (!accessToken) {
    throw new Error("Authenticated access token is required.");
  }

  const projectsQuery = useQuery({
    queryKey: ["projects"],
    queryFn: () => listProjects(accessToken),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      createProject(accessToken, {
        project_code: projectCode.trim(),
        project_name: projectName.trim(),
        client_name: clientName.trim() || null,
        status: "DRAFT",
      }),
    onSuccess: async (project) => {
      setCreatedProject(project);
      setProjectCode("");
      setProjectName("");
      setClientName("");

      await queryClient.invalidateQueries({
        queryKey: ["projects"],
      });
    },
  });

  const projectSummary = useMemo(() => {
    const projects = projectsQuery.data ?? [];

    return {
      total: projects.length,
      draft: projects.filter(
        (project) => project.status.trim().toUpperCase() === "DRAFT",
      ).length,
      active: projects.filter(
        (project) => project.status.trim().toUpperCase() === "ACTIVE",
      ).length,
    };
  }, [projectsQuery.data]);

  const canCreateProject =
    projectCode.trim().length > 0 &&
    projectName.trim().length > 0 &&
    !createMutation.isPending;

  function handleSubmit(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();

    if (!canCreateProject) {
      return;
    }

    setCreatedProject(null);
    createMutation.mutate();
  }

  return (
    <main className="space-y-8">
      <section
        aria-labelledby="projects-title"
        className="overflow-hidden rounded-2xl bg-slate-950 text-white shadow-sm"
      >
        <div className="grid gap-6 p-6 sm:p-8 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end">
          <div className="max-w-3xl">
            <Badge className="border-sky-400/30 bg-sky-400/10 text-sky-100 hover:bg-sky-400/10">
              Project Administration
            </Badge>

            <h1
              id="projects-title"
              className="mt-5 text-3xl font-bold tracking-tight sm:text-4xl"
            >
              Compressor Engineering Projects
            </h1>

            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300 sm:text-base">
              Create and manage tenant-controlled engineering projects, then
              continue into each project&apos;s calculations, assessments, and
              audit records.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-2 sm:gap-3">
            <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-center">
              <p className="text-2xl font-semibold">{projectSummary.total}</p>
              <p className="mt-1 text-xs text-slate-400">Total</p>
            </div>

            <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-center">
              <p className="text-2xl font-semibold">{projectSummary.draft}</p>
              <p className="mt-1 text-xs text-slate-400">Draft</p>
            </div>

            <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-center">
              <p className="text-2xl font-semibold">{projectSummary.active}</p>
              <p className="mt-1 text-xs text-slate-400">Active</p>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(320px,0.38fr)_minmax(0,1fr)] xl:items-start">
        <Card className="border-slate-200/80 shadow-sm">
          <CardHeader>
            <div className="flex size-11 items-center justify-center rounded-xl bg-sky-50 text-sky-700">
              <CirclePlus aria-hidden="true" className="size-5" />
            </div>

            <div className="pt-2">
              <CardTitle>Create Project</CardTitle>
              <CardDescription className="mt-2 leading-6">
                Establish a controlled project identity before beginning
                engineering calculations.
              </CardDescription>
            </div>
          </CardHeader>

          <CardContent>
            <form className="space-y-5" onSubmit={handleSubmit}>
              <div className="space-y-2">
                <Label htmlFor="project-code">
                  Project Code
                  <span aria-hidden="true" className="ml-1 text-rose-600">
                    *
                  </span>
                </Label>

                <Input
                  id="project-code"
                  autoComplete="off"
                  maxLength={50}
                  placeholder="e.g. KES-COMP-001"
                  required
                  value={projectCode}
                  onChange={(event) => {
                    setProjectCode(event.target.value);
                    setCreatedProject(null);
                    createMutation.reset();
                  }}
                />

                <p className="text-xs leading-5 text-slate-500">
                  Use a stable organization-specific reference.
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="project-name">
                  Project Name
                  <span aria-hidden="true" className="ml-1 text-rose-600">
                    *
                  </span>
                </Label>

                <Input
                  id="project-name"
                  autoComplete="off"
                  maxLength={200}
                  placeholder="Compressor Engineering Study"
                  required
                  value={projectName}
                  onChange={(event) => {
                    setProjectName(event.target.value);
                    setCreatedProject(null);
                    createMutation.reset();
                  }}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="client-name">
                  Client Name
                  <span className="ml-2 text-xs font-normal text-slate-500">
                    Optional
                  </span>
                </Label>

                <Input
                  id="client-name"
                  autoComplete="organization"
                  maxLength={200}
                  placeholder="Client or operating company"
                  value={clientName}
                  onChange={(event) => {
                    setClientName(event.target.value);
                    setCreatedProject(null);
                    createMutation.reset();
                  }}
                />
              </div>

              <Button
                type="submit"
                className="w-full"
                disabled={!canCreateProject}
              >
                {createMutation.isPending ? (
                  <>
                    <LoaderCircle
                      aria-hidden="true"
                      className="mr-2 size-4 animate-spin"
                    />
                    Creating project...
                  </>
                ) : (
                  <>
                    <CirclePlus aria-hidden="true" className="mr-2 size-4" />
                    Create Project
                  </>
                )}
              </Button>

              {createMutation.isError && (
                <div
                  role="alert"
                  className="flex items-start gap-3 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800"
                >
                  <TriangleAlert
                    aria-hidden="true"
                    className="mt-0.5 size-4 shrink-0"
                  />

                  <div>
                    <p className="font-semibold">Project creation failed</p>
                    <p className="mt-1 leading-5">
                      {getErrorMessage(
                        createMutation.error,
                        "Unable to create the project. Review the project details and try again.",
                      )}
                    </p>
                  </div>
                </div>
              )}

              {createdProject && (
                <div
                  role="status"
                  className="flex items-start gap-3 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800"
                >
                  <CheckCircle2
                    aria-hidden="true"
                    className="mt-0.5 size-4 shrink-0"
                  />

                  <div>
                    <p className="font-semibold">Project created</p>
                    <p className="mt-1 leading-5">
                      {createdProject.project_code} ·{" "}
                      {createdProject.project_name}
                    </p>
                  </div>
                </div>
              )}
            </form>
          </CardContent>
        </Card>

        <Card className="min-w-0 border-slate-200/80 shadow-sm">
          <CardHeader className="border-b border-slate-100">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <FolderKanban
                    aria-hidden="true"
                    className="size-5 text-slate-500"
                  />
                  Project Register
                </CardTitle>

                <CardDescription className="mt-2 leading-6">
                  Open an authorized project to continue its engineering
                  workflow and calculation records.
                </CardDescription>
              </div>

              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={projectsQuery.isFetching}
                onClick={() => {
                  void projectsQuery.refetch();
                }}
              >
                <RefreshCw
                  aria-hidden="true"
                  className={`mr-2 size-4 ${
                    projectsQuery.isFetching ? "animate-spin" : ""
                  }`}
                />
                Refresh
              </Button>
            </div>
          </CardHeader>

          <CardContent className="p-0">
            {projectsQuery.isPending && (
              <div
                role="status"
                className="flex min-h-64 flex-col items-center justify-center p-8 text-center"
              >
                <LoaderCircle
                  aria-hidden="true"
                  className="size-7 animate-spin text-sky-700"
                />
                <p className="mt-4 font-medium text-slate-900">
                  Loading projects
                </p>
                <p className="mt-1 text-sm text-slate-500">
                  Retrieving the authorized project register.
                </p>
              </div>
            )}

            {projectsQuery.isError && (
              <div
                role="alert"
                className="m-5 flex min-h-48 flex-col items-center justify-center rounded-xl border border-rose-200 bg-rose-50 p-6 text-center"
              >
                <TriangleAlert
                  aria-hidden="true"
                  className="size-7 text-rose-700"
                />
                <p className="mt-3 font-semibold text-rose-900">
                  Unable to load projects
                </p>
                <p className="mt-1 max-w-md text-sm leading-6 text-rose-700">
                  {getErrorMessage(
                    projectsQuery.error,
                    "The project register could not be retrieved. Try refreshing the page.",
                  )}
                </p>
              </div>
            )}

            {projectsQuery.data?.length === 0 && (
              <div className="flex min-h-64 flex-col items-center justify-center p-8 text-center">
                <div className="flex size-14 items-center justify-center rounded-2xl bg-slate-100 text-slate-500">
                  <BriefcaseBusiness aria-hidden="true" className="size-6" />
                </div>
                <p className="mt-4 font-semibold text-slate-900">
                  No projects found
                </p>
                <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
                  Create the first compressor engineering project using the
                  controlled form.
                </p>
              </div>
            )}

            {projectsQuery.data && projectsQuery.data.length > 0 && (
              <div className="overflow-x-auto">
                <table className="w-full min-w-190 border-collapse text-left text-sm">
                  <caption className="sr-only">
                    Authorized compressor engineering projects
                  </caption>

                  <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                    <tr>
                      <th scope="col" className="px-5 py-3 font-semibold">
                        Project
                      </th>
                      <th scope="col" className="px-5 py-3 font-semibold">
                        Client
                      </th>
                      <th scope="col" className="px-5 py-3 font-semibold">
                        Status
                      </th>
                      <th scope="col" className="px-5 py-3 font-semibold">
                        Updated
                      </th>
                      <th
                        scope="col"
                        className="px-5 py-3 text-right font-semibold"
                      >
                        Action
                      </th>
                    </tr>
                  </thead>

                  <tbody className="divide-y divide-slate-100">
                    {projectsQuery.data.map((project) => (
                      <tr
                        key={project.id}
                        className="transition-colors hover:bg-slate-50/80"
                      >
                        <td className="px-5 py-4">
                          <p className="font-mono text-xs font-semibold tracking-wide text-sky-700">
                            {project.project_code}
                          </p>
                          <p className="mt-1 font-semibold text-slate-950">
                            {project.project_name}
                          </p>
                        </td>

                        <td className="px-5 py-4 text-slate-600">
                          {project.client_name ?? "Not specified"}
                        </td>

                        <td className="px-5 py-4">
                          <ProjectStatusBadge status={project.status} />
                        </td>

                        <td className="whitespace-nowrap px-5 py-4 text-slate-600">
                          {formatDate(project.updated_at)}
                        </td>

                        <td className="px-5 py-4 text-right">
                          <Button asChild variant="outline" size="sm">
                            <Link
                              aria-label={`Open project ${project.project_code}`}
                              to={`/projects/${project.id}`}
                            >
                              Open Project
                              <ExternalLink
                                aria-hidden="true"
                                className="ml-2 size-3.5"
                              />
                            </Link>
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </section>
    </main>
  );
}
