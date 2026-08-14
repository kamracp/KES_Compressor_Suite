import { useMemo } from "react";

import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  Calculator,
  CheckCircle2,
  CircleDashed,
  FolderKanban,
  Gauge,
  Layers3,
  Server,
} from "lucide-react";
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
import { Skeleton } from "@/components/ui/skeleton";

import { useAuth } from "../features/auth/AuthProvider";
import { listCalculationCases } from "../features/projects/calculationCaseService";
import { listProjects } from "../features/projects/projectService";
import { getHealth } from "../services/healthService";

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
  }).format(new Date(value));
}

export function DashboardPage() {
  const {
    accessToken,
    currentUser,
  } = useAuth();

  if (!accessToken) {
    throw new Error("Authenticated access token is required.");
  }

  const healthQuery = useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
  });

  const projectsQuery = useQuery({
    queryKey: ["projects"],
    queryFn: () => listProjects(accessToken),
  });

  const calculationsQuery = useQuery({
    queryKey: ["calculation-cases"],
    queryFn: () => listCalculationCases(accessToken),
  });

  const projects = projectsQuery.data ?? [];
  const calculations = calculationsQuery.data ?? [];

  const completedCalculations = useMemo(
    () =>
      calculations.filter(
        (calculation) => calculation.status === "COMPLETED",
      ),
    [calculations],
  );

  const draftCalculations = useMemo(
    () =>
      calculations.filter(
        (calculation) => calculation.status === "DRAFT",
      ),
    [calculations],
  );

  const recentProjects = useMemo(
    () =>
      [...projects]
        .sort(
          (left, right) =>
            new Date(right.updated_at).getTime() -
            new Date(left.updated_at).getTime(),
        )
        .slice(0, 5),
    [projects],
  );

  const recentCalculations = useMemo(
    () =>
      [...calculations]
        .sort(
          (left, right) =>
            new Date(right.updated_at).getTime() -
            new Date(left.updated_at).getTime(),
        )
        .slice(0, 5),
    [calculations],
  );

  const calculationTypeCounts = useMemo(() => {
    const counts = new Map<string, number>();

    for (const calculation of calculations) {
      counts.set(
        calculation.calculation_type,
        (counts.get(calculation.calculation_type) ?? 0) + 1,
      );
    }

    return Array.from(counts.entries()).sort(
      (left, right) => right[1] - left[1],
    );
  }, [calculations]);

  const dashboardLoading =
    projectsQuery.isPending || calculationsQuery.isPending;

  const dashboardError =
    projectsQuery.isError || calculationsQuery.isError;

  return (
    <main className="space-y-6">
      <section className="flex flex-col gap-4 border-0 bg-transparent p-0 shadow-none lg:flex-row lg:items-end lg:justify-between">
        <div className="max-w-3xl">
          <Badge
            variant="outline"
            className="mb-3"
          >
            Engineering Command Center
          </Badge>

          <h1 className="text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">
            KES Compressor Engineering Suite
          </h1>

          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">
            Tenant-scoped compressor engineering, calculation management,
            and compressed-air system workflows from one secure workspace.
          </p>
        </div>

        <Button asChild>
          <Link to="/projects">
            <FolderKanban className="size-4" />
            Open Projects
          </Link>
        </Button>
      </section>

      <section className="grid gap-4 border-0 bg-transparent p-0 shadow-none sm:grid-cols-2 xl:grid-cols-4">
        {dashboardLoading ? (
          Array.from({ length: 4 }).map((_, index) => (
            <Card key={index}>
              <CardHeader>
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-8 w-16" />
              </CardHeader>
            </Card>
          ))
        ) : (
          <>
            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardDescription>
                    Total Projects
                  </CardDescription>
                  <FolderKanban className="size-4 text-slate-400" />
                </div>

                <CardTitle className="text-3xl">
                  {projects.length}
                </CardTitle>
              </CardHeader>

              <CardContent className="text-xs text-slate-500">
                Tenant-scoped engineering projects
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardDescription>
                    Saved Calculations
                  </CardDescription>
                  <Calculator className="size-4 text-slate-400" />
                </div>

                <CardTitle className="text-3xl">
                  {calculations.length}
                </CardTitle>
              </CardHeader>

              <CardContent className="text-xs text-slate-500">
                Revision-controlled calculation cases
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardDescription>
                    Completed
                  </CardDescription>
                  <CheckCircle2 className="size-4 text-emerald-600" />
                </div>

                <CardTitle className="text-3xl">
                  {completedCalculations.length}
                </CardTitle>
              </CardHeader>

              <CardContent className="text-xs text-slate-500">
                Engineering calculations completed
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardDescription>
                    Draft / In Progress
                  </CardDescription>
                  <CircleDashed className="size-4 text-amber-600" />
                </div>

                <CardTitle className="text-3xl">
                  {draftCalculations.length}
                </CardTitle>
              </CardHeader>

              <CardContent className="text-xs text-slate-500">
                Calculations still being developed
              </CardContent>
            </Card>
          </>
        )}
      </section>

      {dashboardError && (
        <Card className="border-red-200 bg-red-50">
          <CardHeader>
            <CardTitle className="text-base text-red-900">
              Dashboard data unavailable
            </CardTitle>

            <CardDescription className="text-red-700">
              One or more tenant-scoped dashboard requests could not be loaded.
            </CardDescription>
          </CardHeader>
        </Card>
      )}

      <section className="grid gap-4 border-0 bg-transparent p-0 shadow-none xl:grid-cols-[1.45fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>
              Recent Projects
            </CardTitle>

            <CardDescription>
              Recently updated engineering projects in this organization.
            </CardDescription>
          </CardHeader>

          <CardContent>
            {projectsQuery.isPending ? (
              <div className="space-y-3">
                {Array.from({ length: 4 }).map((_, index) => (
                  <Skeleton
                    key={index}
                    className="h-14 w-full"
                  />
                ))}
              </div>
            ) : recentProjects.length === 0 ? (
              <div className="rounded-lg border border-dashed border-slate-300 p-6 text-center">
                <FolderKanban className="mx-auto mb-3 size-6 text-slate-400" />

                <p className="text-sm font-medium text-slate-800">
                  No projects yet
                </p>

                <p className="mt-1 text-sm text-slate-500">
                  Create the first engineering project to begin calculations.
                </p>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {recentProjects.map((project) => (
                  <Link
                    key={project.id}
                    to={`/projects/${project.id}`}
                    className="flex items-center justify-between gap-4 py-3 first:pt-0 last:pb-0"
                  >
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-slate-900">
                        {project.project_name}
                      </p>

                      <p className="mt-1 truncate text-xs text-slate-500">
                        {project.project_code}
                        {project.client_name
                          ? ` · ${project.client_name}`
                          : ""}
                      </p>
                    </div>

                    <div className="shrink-0 text-right">
                      <Badge variant="outline">
                        {project.status}
                      </Badge>

                      <p className="mt-1 text-[11px] text-slate-400">
                        {formatDate(project.updated_at)}
                      </p>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>
              Platform Status
            </CardTitle>

            <CardDescription>
              Current API and tenant workspace context.
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            <div className="flex items-center justify-between rounded-lg border border-slate-200 p-3">
              <div className="flex items-center gap-3">
                <Server className="size-4 text-slate-500" />

                <div>
                  <p className="text-sm font-medium">
                    Backend API
                  </p>

                  <p className="text-xs text-slate-500">
                    {healthQuery.data?.service ?? "KES API"}
                  </p>
                </div>
              </div>

              <Badge
                variant={
                  healthQuery.isError
                    ? "destructive"
                    : "secondary"
                }
              >
                {healthQuery.isPending
                  ? "Checking"
                  : healthQuery.isError
                    ? "Unavailable"
                    : healthQuery.data?.status ?? "Unknown"}
              </Badge>
            </div>

            <div className="flex items-center justify-between rounded-lg border border-slate-200 p-3">
              <div className="flex items-center gap-3">
                <Layers3 className="size-4 text-slate-500" />

                <div>
                  <p className="text-sm font-medium">
                    Organization
                  </p>

                  <p className="text-xs text-slate-500">
                    Tenant-scoped engineering data
                  </p>
                </div>
              </div>

              <Badge variant="outline">
                {currentUser?.organization_id ?? "-"}
              </Badge>
            </div>

            <div className="flex items-center justify-between rounded-lg border border-slate-200 p-3">
              <div className="flex items-center gap-3">
                <Activity className="size-4 text-slate-500" />

                <div className="min-w-0">
                  <p className="text-sm font-medium">
                    Signed-in User
                  </p>

                  <p className="max-w-48 truncate text-xs text-slate-500">
                    {currentUser?.email}
                  </p>
                </div>
              </div>

              <Badge variant="secondary">
                Active
              </Badge>
            </div>
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-4 border-0 bg-transparent p-0 shadow-none xl:grid-cols-[1.45fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>
              Recent Calculations
            </CardTitle>

            <CardDescription>
              Latest saved compressor engineering calculation cases.
            </CardDescription>
          </CardHeader>

          <CardContent>
            {calculationsQuery.isPending ? (
              <div className="space-y-3">
                {Array.from({ length: 4 }).map((_, index) => (
                  <Skeleton
                    key={index}
                    className="h-14 w-full"
                  />
                ))}
              </div>
            ) : recentCalculations.length === 0 ? (
              <div className="rounded-lg border border-dashed border-slate-300 p-6 text-center">
                <Calculator className="mx-auto mb-3 size-6 text-slate-400" />

                <p className="text-sm font-medium text-slate-800">
                  No saved calculations
                </p>

                <p className="mt-1 text-sm text-slate-500">
                  Persist an engineering calculation to see it here.
                </p>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {recentCalculations.map((calculation) => (
                  <Link
                    key={calculation.id}
                    to={`/projects/${calculation.project_id}/calculations/${calculation.id}`}
                    className="flex items-center justify-between gap-4 py-3 first:pt-0 last:pb-0"
                  >
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-slate-900">
                        {calculation.title}
                      </p>

                      <p className="mt-1 truncate text-xs text-slate-500">
                        {calculation.calculation_code}
                        {" · "}
                        {calculation.calculation_type}
                        {" · Rev "}
                        {calculation.revision}
                      </p>
                    </div>

                    <div className="shrink-0 text-right">
                      <Badge
                        variant={
                          calculation.status === "COMPLETED"
                            ? "secondary"
                            : "outline"
                        }
                      >
                        {calculation.status}
                      </Badge>

                      <p className="mt-1 text-[11px] text-slate-400">
                        {formatDate(calculation.updated_at)}
                      </p>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>
              Calculation Mix
            </CardTitle>

            <CardDescription>
              Saved calculations grouped by engineering type.
            </CardDescription>
          </CardHeader>

          <CardContent>
            {calculationTypeCounts.length === 0 ? (
              <p className="text-sm text-slate-500">
                No calculation distribution is available yet.
              </p>
            ) : (
              <div className="space-y-3">
                {calculationTypeCounts.map(([type, count]) => (
                  <div
                    key={type}
                    className="flex items-center justify-between rounded-lg border border-slate-200 px-3 py-2.5"
                  >
                    <div className="flex items-center gap-2">
                      <Gauge className="size-4 text-slate-400" />

                      <span className="text-sm font-medium text-slate-700">
                        {type}
                      </span>
                    </div>

                    <Badge variant="secondary">
                      {count}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </section>

      <Card>
        <CardHeader>
          <CardTitle>
            Engineering Workspaces
          </CardTitle>

          <CardDescription>
            Continue into project, assessment, or report workflows.
          </CardDescription>
        </CardHeader>

        <CardContent className="grid gap-3 md:grid-cols-3">
          <Button
            asChild
            variant="outline"
            className="h-auto justify-start p-4"
          >
            <Link to="/projects">
              <FolderKanban className="size-5" />

              <span className="text-left">
                <span className="block font-semibold">
                  Projects
                </span>
                <span className="mt-1 block text-xs font-normal text-slate-500">
                  Engineering project workspace
                </span>
              </span>
            </Link>
          </Button>

          <Button
            asChild
            variant="outline"
            className="h-auto justify-start p-4"
          >
            <Link to="/assessments">
              <Gauge className="size-5" />

              <span className="text-left">
                <span className="block font-semibold">
                  Assessments
                </span>
                <span className="mt-1 block text-xs font-normal text-slate-500">
                  Compressed-air assessment workspace
                </span>
              </span>
            </Link>
          </Button>

          <Button
            asChild
            variant="outline"
            className="h-auto justify-start p-4"
          >
            <Link to="/reports">
              <Activity className="size-5" />

              <span className="text-left">
                <span className="block font-semibold">
                  Reports
                </span>
                <span className="mt-1 block text-xs font-normal text-slate-500">
                  Engineering reporting workspace
                </span>
              </span>
            </Link>
          </Button>
        </CardContent>
      </Card>
    </main>
  );
}
