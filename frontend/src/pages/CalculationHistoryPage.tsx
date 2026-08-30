import { useState } from "react";

import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  Calculator,
  CheckCircle2,
  FileText,
  History,
  RefreshCw,
  Search,
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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import { useAuth } from "../features/auth/AuthProvider";
import { listProjectCalculationCases } from "../features/projects/calculationCaseService";
import type {
  CalculationCase,
  CalculationStatus,
  CalculationType,
} from "../features/projects/calculationCaseTypes";
import { useProjectContext } from "../features/projects/useProjectContext";
import { ApiError } from "../services/apiClient";

type CalculationTypeFilter = CalculationType | "ALL";
type CalculationStatusFilter = CalculationStatus | "ALL";

const CALCULATION_TYPE_LABELS: Record<CalculationType, string> = {
  COMPRESSION: "Compression",
  RECIPROCATING: "Reciprocating",
  CENTRIFUGAL: "Centrifugal",
  ROTARY_SCREW: "Rotary Screw",
  SELECTION: "Technology Selection",
  DISTRIBUTION: "Distribution Network",
};

function formatDateTime(value: string | null): string {
  if (!value) {
    return "Not completed";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function formatCalculationType(value: CalculationType): string {
  return CALCULATION_TYPE_LABELS[value];
}

function statusClassName(status: CalculationStatus): string {
  if (status === "COMPLETED") {
    return "border-emerald-300 bg-emerald-50 text-emerald-900";
  }

  if (status === "FAILED") {
    return "border-red-300 bg-red-50 text-red-900";
  }

  if (status === "ARCHIVED") {
    return "border-slate-300 bg-slate-100 text-slate-700";
  }

  return "border-amber-300 bg-amber-50 text-amber-900";
}

function getHistoryErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (
      typeof error.details === "object" &&
      error.details !== null &&
      "detail" in error.details &&
      typeof error.details.detail === "string"
    ) {
      return error.details.detail;
    }

    return `Calculation history service returned HTTP ${error.status}.`;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Calculation history could not be loaded.";
}

function matchesSearch(
  calculationCase: CalculationCase,
  normalizedSearch: string,
): boolean {
  if (!normalizedSearch) {
    return true;
  }

  return [
    calculationCase.calculation_code,
    calculationCase.title,
    calculationCase.description ?? "",
    calculationCase.engineering_notes ?? "",
    formatCalculationType(calculationCase.calculation_type),
    calculationCase.status,
  ].some((value) => value.toLowerCase().includes(normalizedSearch));
}

export function CalculationHistoryPage() {
  const { accessToken } = useAuth();
  const {
    projectId,
    hasValidProjectId,
    project,
    projectQuery,
  } = useProjectContext();

  const [searchText, setSearchText] = useState("");
  const [typeFilter, setTypeFilter] =
    useState<CalculationTypeFilter>("ALL");
  const [statusFilter, setStatusFilter] =
    useState<CalculationStatusFilter>("ALL");

  if (!accessToken) {
    throw new Error("Authenticated access token is required.");
  }

  if (!hasValidProjectId) {
    throw new Error("Valid project ID is required.");
  }

  const calculationCasesQuery = useQuery({
    queryKey: [
      "projects",
      projectId,
      "calculation-cases",
    ],
    queryFn: () =>
      listProjectCalculationCases(
        accessToken,
        projectId,
      ),
  });

  const calculationCases = calculationCasesQuery.data ?? [];
  const normalizedSearch = searchText.trim().toLowerCase();

  const filteredCalculationCases = [...calculationCases]
    .filter(
      (calculationCase) =>
        (typeFilter === "ALL" ||
          calculationCase.calculation_type === typeFilter) &&
        (statusFilter === "ALL" ||
          calculationCase.status === statusFilter) &&
        matchesSearch(calculationCase, normalizedSearch),
    )
    .sort(
      (left, right) =>
        new Date(right.created_at).getTime() -
        new Date(left.created_at).getTime(),
    );

  const completedCount = calculationCases.filter(
    (calculationCase) => calculationCase.status === "COMPLETED",
  ).length;
  const reviewCount = calculationCases.filter(
    (calculationCase) =>
      calculationCase.status === "DRAFT" ||
      calculationCase.status === "FAILED",
  ).length;
  const activeFilters =
    Boolean(normalizedSearch) ||
    typeFilter !== "ALL" ||
    statusFilter !== "ALL";

  function clearFilters(): void {
    setSearchText("");
    setTypeFilter("ALL");
    setStatusFilter("ALL");
  }

  return (
    <main className="mx-auto w-full max-w-7xl space-y-6 pb-12">
      <Card className="bg-white">
        <CardHeader>
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="space-y-3">
              <Badge variant="outline">
                Project Calculation Records
              </Badge>

              <div>
                <h1 className="text-3xl font-bold tracking-tight text-slate-950">
                  Calculation History
                </h1>

                <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
                  Review project-scoped compressor calculations, verify their
                  completion state and revision, and reopen stored engineering
                  inputs, results, and notes for audit review.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-2 text-xs">
                <span className="font-semibold text-slate-900">
                  {project
                    ? `${project.project_code} · ${project.project_name}`
                    : projectQuery.isPending
                      ? "Loading project..."
                      : `Project ${projectId}`}
                </span>

                {project && (
                  <Badge variant="outline">{project.status}</Badge>
                )}

                <Badge variant="outline">Authenticated Scope</Badge>
                <Badge variant="outline">Revision Traceability</Badge>
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              <Button
                asChild
                variant="outline"
              >
                <Link to={`/projects/${projectId}/compressor`}>
                  <Calculator className="size-4" />
                  Engineering Workbench
                </Link>
              </Button>

              <Button
                type="button"
                variant="outline"
                onClick={() => void calculationCasesQuery.refetch()}
                disabled={calculationCasesQuery.isFetching}
              >
                <RefreshCw
                  className={`size-4 ${
                    calculationCasesQuery.isFetching ? "animate-spin" : ""
                  }`}
                />
                {calculationCasesQuery.isFetching
                  ? "Refreshing..."
                  : "Refresh Records"}
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      <section
        aria-label="Calculation record summary"
        className="grid gap-4 md:grid-cols-3"
      >
        <Card>
          <CardContent className="flex items-center gap-4 p-5">
            <div className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
              <History className="size-5" />
            </div>
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Total Records
              </p>
              <p className="mt-1 text-2xl font-semibold text-slate-950">
                {calculationCases.length.toLocaleString("en-IN")}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center gap-4 p-5">
            <div className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
              <CheckCircle2 className="size-5" />
            </div>
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Completed
              </p>
              <p className="mt-1 text-2xl font-semibold text-slate-950">
                {completedCount.toLocaleString("en-IN")}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center gap-4 p-5">
            <div className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-amber-50 text-amber-700">
              <AlertTriangle className="size-5" />
            </div>
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Requiring Review
              </p>
              <p className="mt-1 text-2xl font-semibold text-slate-950">
                {reviewCount.toLocaleString("en-IN")}
              </p>
            </div>
          </CardContent>
        </Card>
      </section>

      <Card>
        <CardHeader>
          <div className="flex items-start gap-3">
            <Search className="mt-0.5 size-5 shrink-0 text-slate-500" />
            <div>
              <CardTitle>Find Calculation Records</CardTitle>
              <CardDescription className="mt-1 leading-6">
                Search project records by calculation code, title, notes, type,
                or status, then narrow the register using the structured
                filters.
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          <div className="grid gap-5 lg:grid-cols-[2fr_1fr_1fr_auto] lg:items-end">
            <div className="space-y-2">
              <Label htmlFor="calculation-history-search">
                Search Records
              </Label>
              <Input
                id="calculation-history-search"
                type="search"
                placeholder="Code, title, type, status, or notes"
                value={searchText}
                onChange={(event) => setSearchText(event.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="calculation-type-filter">
                Calculation Type
              </Label>
              <select
                id="calculation-type-filter"
                className="h-9 w-full rounded-md border border-slate-200 bg-white px-3 text-sm shadow-sm outline-none transition focus-visible:border-slate-400 focus-visible:ring-2 focus-visible:ring-slate-200"
                value={typeFilter}
                onChange={(event) =>
                  setTypeFilter(event.target.value as CalculationTypeFilter)
                }
              >
                <option value="ALL">All types</option>
                <option value="COMPRESSION">Compression</option>
                <option value="RECIPROCATING">Reciprocating</option>
                <option value="CENTRIFUGAL">Centrifugal</option>
                <option value="ROTARY_SCREW">Rotary Screw</option>
                <option value="SELECTION">Technology Selection</option>
                <option value="DISTRIBUTION">Distribution Network</option>
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="calculation-status-filter">
                Record Status
              </Label>
              <select
                id="calculation-status-filter"
                className="h-9 w-full rounded-md border border-slate-200 bg-white px-3 text-sm shadow-sm outline-none transition focus-visible:border-slate-400 focus-visible:ring-2 focus-visible:ring-slate-200"
                value={statusFilter}
                onChange={(event) =>
                  setStatusFilter(
                    event.target.value as CalculationStatusFilter,
                  )
                }
              >
                <option value="ALL">All statuses</option>
                <option value="DRAFT">Draft</option>
                <option value="COMPLETED">Completed</option>
                <option value="FAILED">Failed</option>
                <option value="ARCHIVED">Archived</option>
              </select>
            </div>

            <Button
              type="button"
              variant="outline"
              onClick={clearFilters}
              disabled={!activeFilters}
            >
              Clear Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {calculationCasesQuery.isPending && (
        <Card>
          <CardContent className="flex items-center gap-3 p-6 text-sm text-slate-600">
            <RefreshCw className="size-5 animate-spin text-slate-500" />
            Loading calculation history...
          </CardContent>
        </Card>
      )}

      {calculationCasesQuery.isError && (
        <Card className="border-red-300 bg-red-50">
          <CardHeader>
            <div className="flex items-start gap-3">
              <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-700" />
              <div>
                <CardTitle className="text-red-950">
                  Calculation History Unavailable
                </CardTitle>
                <CardDescription className="mt-1 leading-6 text-red-800">
                  {getHistoryErrorMessage(calculationCasesQuery.error)}
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <Button
              type="button"
              variant="outline"
              className="border-red-300 bg-white"
              onClick={() => void calculationCasesQuery.refetch()}
            >
              <RefreshCw className="size-4" />
              Retry History Load
            </Button>
          </CardContent>
        </Card>
      )}

      {calculationCasesQuery.isSuccess && calculationCases.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center px-6 py-12 text-center">
            <div className="flex size-14 items-center justify-center rounded-2xl bg-slate-100 text-slate-600">
              <FileText className="size-6" />
            </div>
            <h2 className="mt-4 text-lg font-semibold text-slate-950">
              No Saved Calculations
            </h2>
            <p className="mt-2 max-w-xl text-sm leading-6 text-slate-600">
              No saved calculations are available for this project. Run an
              engineering module with project persistence enabled to create the
              first auditable record.
            </p>
            <Button
              asChild
              className="mt-5"
            >
              <Link to={`/projects/${projectId}/compressor`}>
                Open Engineering Workbench
              </Link>
            </Button>
          </CardContent>
        </Card>
      )}

      {calculationCasesQuery.isSuccess &&
        calculationCases.length > 0 &&
        filteredCalculationCases.length === 0 && (
          <Card>
            <CardContent className="flex flex-col items-center px-6 py-10 text-center">
              <Search className="size-7 text-slate-500" />
              <h2 className="mt-3 text-lg font-semibold text-slate-950">
                No Matching Records
              </h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                No calculation records match the current search and filter
                criteria.
              </p>
              <Button
                type="button"
                variant="outline"
                className="mt-4"
                onClick={clearFilters}
              >
                Clear Filters
              </Button>
            </CardContent>
          </Card>
        )}

      {calculationCasesQuery.isSuccess &&
        filteredCalculationCases.length > 0 && (
          <Card>
            <CardHeader>
              <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <CardTitle>Calculation Register</CardTitle>
                  <CardDescription className="mt-1">
                    Project-scoped engineering records ordered newest first.
                  </CardDescription>
                </div>
                <p className="text-sm font-medium text-slate-600">
                  Showing {filteredCalculationCases.length.toLocaleString("en-IN")} of{" "}
                  {calculationCases.length.toLocaleString("en-IN")}
                </p>
              </div>
            </CardHeader>

            <CardContent>
              <div className="overflow-hidden rounded-xl border border-slate-200">
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[72rem] text-left text-sm">
                    <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                      <tr>
                        <th className="px-4 py-3 font-medium">Code</th>
                        <th className="px-4 py-3 font-medium">Type</th>
                        <th className="px-4 py-3 font-medium">Title</th>
                        <th className="px-4 py-3 font-medium">Revision</th>
                        <th className="px-4 py-3 font-medium">Status</th>
                        <th className="px-4 py-3 font-medium">Created</th>
                        <th className="px-4 py-3 font-medium">Completed</th>
                        <th className="px-4 py-3 text-right font-medium">
                          Action
                        </th>
                      </tr>
                    </thead>

                    <tbody className="divide-y divide-slate-100 bg-white">
                      {filteredCalculationCases.map((calculationCase) => (
                        <tr
                          key={calculationCase.id}
                          className="align-top transition-colors hover:bg-slate-50"
                        >
                          <td className="px-4 py-4 font-mono text-xs font-semibold text-slate-950">
                            {calculationCase.calculation_code}
                          </td>
                          <td className="px-4 py-4 text-slate-700">
                            {formatCalculationType(
                              calculationCase.calculation_type,
                            )}
                          </td>
                          <td className="max-w-xs px-4 py-4">
                            <p className="font-semibold text-slate-950">
                              {calculationCase.title}
                            </p>
                            {calculationCase.description && (
                              <p className="mt-1 line-clamp-2 text-xs leading-5 text-slate-500">
                                {calculationCase.description}
                              </p>
                            )}
                          </td>
                          <td className="px-4 py-4 text-slate-700">
                            Rev {calculationCase.revision}
                          </td>
                          <td className="px-4 py-4">
                            <Badge
                              variant="outline"
                              className={statusClassName(
                                calculationCase.status,
                              )}
                            >
                              {calculationCase.status}
                            </Badge>
                          </td>
                          <td className="whitespace-nowrap px-4 py-4 text-xs leading-5 text-slate-600">
                            {formatDateTime(calculationCase.created_at)}
                          </td>
                          <td className="whitespace-nowrap px-4 py-4 text-xs leading-5 text-slate-600">
                            {formatDateTime(calculationCase.completed_at)}
                          </td>
                          <td className="px-4 py-4 text-right">
                            <Button
                              asChild
                              size="sm"
                              variant="outline"
                            >
                              <Link
                                to={`/projects/${projectId}/calculations/${calculationCase.id}`}
                              >
                                Open
                              </Link>
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
    </main>
  );
}
