import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  ArrowLeft,
  Calculator,
  CheckCircle2,
  FileInput,
  FileOutput,
  FileText,
  History,
  RefreshCw,
  ShieldAlert,
} from "lucide-react";
import { Link, useParams } from "react-router";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import { useAuth } from "../features/auth/AuthProvider";
import { getCalculationCase } from "../features/projects/calculationCaseService";
import type {
  CalculationStatus,
  CalculationType,
} from "../features/projects/calculationCaseTypes";
import { useProjectContext } from "../features/projects/useProjectContext";
import { ApiError } from "../services/apiClient";

const CALCULATION_TYPE_LABELS: Record<CalculationType, string> = {
  COMPRESSION: "Compression Engineering",
  RECIPROCATING: "Reciprocating Compressor",
  CENTRIFUGAL: "Centrifugal Compressor",
  ROTARY_SCREW: "Rotary Screw Compressor",
  SELECTION: "Compressor Technology Selection",
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

function modulePath(
  projectId: number,
  calculationType: CalculationType,
): string {
  if (calculationType === "COMPRESSION") {
    return `/projects/${projectId}/compressor/compression`;
  }

  if (calculationType === "RECIPROCATING") {
    return `/projects/${projectId}/compressor/reciprocating`;
  }

  if (calculationType === "CENTRIFUGAL") {
    return `/projects/${projectId}/compressor/centrifugal`;
  }

  if (calculationType === "ROTARY_SCREW") {
    return `/projects/${projectId}/compressor/rotary-screw`;
  }

  if (calculationType === "DISTRIBUTION") {
    return `/projects/${projectId}/compressor/distribution`;
  }

  return `/projects/${projectId}/compressor/selection`;
}

function getCalculationErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (
      typeof error.details === "object" &&
      error.details !== null &&
      "detail" in error.details &&
      typeof error.details.detail === "string"
    ) {
      return error.details.detail;
    }

    return `Calculation record service returned HTTP ${error.status}.`;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Unable to load calculation.";
}

function payloadEntryCount(value: Record<string, unknown> | null): number {
  return value ? Object.keys(value).length : 0;
}

export function CalculationDetailPage() {
  const { calculationCaseId } = useParams();
  const { accessToken } = useAuth();
  const {
    projectId,
    hasValidProjectId,
    project,
    projectQuery,
  } = useProjectContext();

  if (!accessToken) {
    throw new Error("Authenticated access token is required.");
  }

  const numericCalculationCaseId = Number(calculationCaseId);

  if (
    !hasValidProjectId ||
    !Number.isInteger(numericCalculationCaseId) ||
    numericCalculationCaseId <= 0
  ) {
    throw new Error(
      "Valid project ID and calculation case ID are required.",
    );
  }

  const calculationQuery = useQuery({
    queryKey: [
      "projects",
      projectId,
      "calculation-case",
      numericCalculationCaseId,
    ],
    queryFn: () =>
      getCalculationCase(
        accessToken,
        numericCalculationCaseId,
      ),
  });

  if (calculationQuery.isPending) {
    return (
      <main className="mx-auto w-full max-w-7xl space-y-6 pb-12">
        <Card>
          <CardContent className="flex items-center gap-3 p-8 text-sm text-slate-600">
            <RefreshCw className="size-5 animate-spin text-slate-500" />
            Loading calculation...
          </CardContent>
        </Card>
      </main>
    );
  }

  if (calculationQuery.isError) {
    return (
      <main className="mx-auto w-full max-w-7xl space-y-6 pb-12">
        <Card className="border-red-300 bg-red-50">
          <CardHeader>
            <div className="flex items-start gap-3">
              <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-700" />
              <div>
                <CardTitle className="text-red-950">
                  Calculation Record Unavailable
                </CardTitle>
                <CardDescription className="mt-1 leading-6 text-red-800">
                  {getCalculationErrorMessage(calculationQuery.error)}
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant="outline"
              className="border-red-300 bg-white"
              onClick={() => void calculationQuery.refetch()}
            >
              <RefreshCw className="size-4" />
              Retry Record Load
            </Button>
            <Button
              asChild
              variant="outline"
              className="border-red-300 bg-white"
            >
              <Link to={`/projects/${projectId}/calculations`}>
                <History className="size-4" />
                Return to Calculation History
              </Link>
            </Button>
          </CardContent>
        </Card>
      </main>
    );
  }

  const calculation = calculationQuery.data;

  if (calculation.project_id !== projectId) {
    return (
      <main className="mx-auto w-full max-w-4xl space-y-6 pb-12">
        <Card className="border-red-300 bg-red-50">
          <CardHeader>
            <div className="flex items-start gap-3">
              <ShieldAlert className="mt-0.5 size-6 shrink-0 text-red-700" />
              <div>
                <h1 className="text-lg font-semibold leading-none text-red-950">
                  Calculation Project Mismatch
                </h1>
                <CardDescription className="mt-2 leading-6 text-red-800">
                  This calculation does not belong to the requested project.
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <p className="mb-4 text-sm leading-6 text-red-800">
              The record has been blocked from display to preserve authenticated
              project isolation. Return to the active project history and select
              a calculation listed within that scope.
            </p>
            <Button
              asChild
              variant="outline"
              className="border-red-300 bg-white"
            >
              <Link to={`/projects/${projectId}/calculations`}>
                <ArrowLeft className="size-4" />
                Return to Calculation History
              </Link>
            </Button>
          </CardContent>
        </Card>
      </main>
    );
  }

  const inputEntryCount = payloadEntryCount(calculation.input_data);
  const resultEntryCount = payloadEntryCount(calculation.result_data);

  return (
    <main className="mx-auto w-full max-w-7xl space-y-6 pb-12">
      <Card className="bg-white">
        <CardHeader>
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="space-y-3">
              <Button
                asChild
                variant="ghost"
                className="-ml-3 w-fit"
              >
                <Link to={`/projects/${projectId}/calculations`}>
                  <ArrowLeft className="size-4" />
                  Back to Calculation History
                </Link>
              </Button>

              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="outline">
                  Calculation Record #{calculation.id}
                </Badge>
                <Badge
                  variant="outline"
                  className={statusClassName(calculation.status)}
                >
                  {calculation.status}
                </Badge>
              </div>

              <div>
                <h1 className="text-3xl font-bold tracking-tight text-slate-950">
                  {calculation.title}
                </h1>
                <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
                  Review the immutable project context, calculation metadata,
                  engineering notes, submitted inputs, and stored result payload
                  for this completed calculation case.
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

                <Badge variant="outline">Project Verified</Badge>
                <Badge variant="outline">Audit Trace</Badge>
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              <Button
                asChild
                variant="outline"
              >
                <Link
                  to={modulePath(
                    projectId,
                    calculation.calculation_type,
                  )}
                >
                  <Calculator className="size-4" />
                  Open Source Module
                </Link>
              </Button>

              <Button
                type="button"
                variant="outline"
                onClick={() => void calculationQuery.refetch()}
                disabled={calculationQuery.isFetching}
              >
                <RefreshCw
                  className={`size-4 ${
                    calculationQuery.isFetching ? "animate-spin" : ""
                  }`}
                />
                {calculationQuery.isFetching
                  ? "Refreshing..."
                  : "Refresh Record"}
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      <section
        aria-label="Calculation metadata"
        className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"
      >
        <Card>
          <CardContent className="p-5">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
              Calculation Code
            </p>
            <p className="mt-2 break-words font-mono text-sm font-semibold text-slate-950">
              {calculation.calculation_code}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
              Engineering Module
            </p>
            <p className="mt-2 text-sm font-semibold text-slate-950">
              {CALCULATION_TYPE_LABELS[calculation.calculation_type]}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
              Revision
            </p>
            <p className="mt-2 text-sm font-semibold text-slate-950">
              Revision {calculation.revision}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
              Record Status
            </p>
            <div className="mt-2">
              <Badge
                variant="outline"
                className={statusClassName(calculation.status)}
              >
                {calculation.status}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </section>

      <Card>
        <CardHeader>
          <div className="flex items-start gap-3">
            <History className="mt-0.5 size-5 shrink-0 text-slate-500" />
            <div>
              <CardTitle>Record Timeline and Traceability</CardTitle>
              <CardDescription className="mt-1 leading-6">
                Review creation, completion, update, and project ownership
                markers retained with this calculation case.
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <dl className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Created
              </dt>
              <dd className="mt-2 text-sm font-semibold text-slate-950">
                {formatDateTime(calculation.created_at)}
              </dd>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Completed
              </dt>
              <dd className="mt-2 text-sm font-semibold text-slate-950">
                {formatDateTime(calculation.completed_at)}
              </dd>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Last Updated
              </dt>
              <dd className="mt-2 text-sm font-semibold text-slate-950">
                {formatDateTime(calculation.updated_at)}
              </dd>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Project ID
              </dt>
              <dd className="mt-2 text-sm font-semibold text-slate-950">
                {calculation.project_id}
              </dd>
            </div>
          </dl>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-start gap-3">
            <FileText className="mt-0.5 size-5 shrink-0 text-slate-500" />
            <div>
              <CardTitle>Engineering Notes</CardTitle>
              <CardDescription className="mt-1 leading-6">
                Project-specific review notes retained when the calculation was
                saved.
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">
            <p className="whitespace-pre-wrap text-sm leading-7 text-slate-700">
              {calculation.engineering_notes ?? "No engineering notes."}
            </p>
          </div>

          {calculation.description && (
            <div className="mt-4 rounded-xl border border-blue-200 bg-blue-50 p-5">
              <p className="text-xs font-semibold uppercase tracking-wide text-blue-700">
                Record Description
              </p>
              <p className="mt-2 text-sm leading-6 text-blue-900">
                {calculation.description}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      <section className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-start gap-3">
                <FileInput className="mt-0.5 size-5 shrink-0 text-slate-500" />
                <div>
                  <CardTitle>Input Data</CardTitle>
                  <CardDescription className="mt-1 leading-6">
                    Submitted engineering basis stored with the record.
                  </CardDescription>
                </div>
              </div>
              <Badge variant="outline">
                {inputEntryCount} top-level fields
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <pre className="max-h-[36rem] overflow-auto rounded-xl border border-slate-800 bg-slate-950 p-4 text-xs leading-6 text-slate-100">
              {JSON.stringify(calculation.input_data, null, 2)}
            </pre>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-start gap-3">
                <FileOutput className="mt-0.5 size-5 shrink-0 text-slate-500" />
                <div>
                  <CardTitle>Result Data</CardTitle>
                  <CardDescription className="mt-1 leading-6">
                    Deterministic calculation output stored for audit review.
                  </CardDescription>
                </div>
              </div>
              <Badge variant="outline">
                {resultEntryCount} top-level fields
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            {calculation.result_data ? (
              <pre className="max-h-[36rem] overflow-auto rounded-xl border border-slate-800 bg-slate-950 p-4 text-xs leading-6 text-slate-100">
                {JSON.stringify(calculation.result_data, null, 2)}
              </pre>
            ) : (
              <div className="flex min-h-40 flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-center">
                <AlertTriangle className="size-6 text-amber-600" />
                <p className="mt-3 text-sm font-semibold text-slate-950">
                  No result data available.
                </p>
                <p className="mt-1 text-xs leading-5 text-slate-600">
                  Review the record status and source module before relying on
                  this calculation case.
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </section>

      <Card className="border-emerald-200 bg-emerald-50/40">
        <CardContent className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-emerald-700" />
            <div>
              <p className="text-sm font-semibold text-emerald-950">
                Project Scope Verified
              </p>
              <p className="mt-1 text-sm leading-6 text-emerald-800">
                This calculation record belongs to the active authenticated
                project and is safe to review within this workspace.
              </p>
            </div>
          </div>

          <Button
            asChild
            variant="outline"
            className="border-emerald-300 bg-white"
          >
            <Link to={`/projects/${projectId}/calculations`}>
              <History className="size-4" />
              Calculation History
            </Link>
          </Button>
        </CardContent>
      </Card>
    </main>
  );
}
