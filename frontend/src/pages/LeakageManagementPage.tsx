import { useState } from "react";

import {
  AlertTriangle,
  ClipboardList,
  Play,
  RotateCcw,
} from "lucide-react";
import { useMutation } from "@tanstack/react-query";
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

import { useAuth } from "../features/auth/AuthProvider";
import { LeakageEnergyBasisSection } from "../features/leakage/components/LeakageEnergyBasisSection";
import { LeakageEngineeringReviewSection } from "../features/leakage/components/LeakageEngineeringReviewSection";
import { LeakageStudyBasisSection } from "../features/leakage/components/LeakageStudyBasisSection";
import { LeakRegisterSection } from "../features/leakage/components/LeakRegisterSection";
import { RepairVerificationSection } from "../features/leakage/components/RepairVerificationSection";
import {
  buildLeakageManagementRequest,
  createInitialLeakageFormState,
  validateLeakageFormState,
  type LeakageFormState,
} from "../features/leakage/leakageFormState";
import { analyzeCompressedAirLeakage } from "../features/leakage/leakageService";
import { useProjectContext } from "../features/projects/useProjectContext";
import { useInputOptions } from "../features/reference/useInputOptions";
import { ApiError } from "../services/apiClient";

function extractErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    const details = error.details;

    if (
      typeof details === "object" &&
      details !== null &&
      "detail" in details
    ) {
      const detail = (details as { detail?: unknown }).detail;

      if (typeof detail === "string") {
        return detail;
      }
    }

    return `Leakage API request failed with status ${error.status}.`;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Compressed-air leakage analysis could not be completed.";
}

export function LeakageManagementPage() {
  const { accessToken } = useAuth();
  const inputOptionsQuery = useInputOptions(accessToken);
  const {
    projectId: projectIdNumber,
    hasValidProjectId,
    project,
    projectQuery,
  } = useProjectContext();

  const [formState, setFormState] = useState<LeakageFormState>(
    createInitialLeakageFormState,
  );

  const [validationErrors, setValidationErrors] = useState<string[]>(
    [],
  );

  const leakageMutation = useMutation({
    mutationFn: () => {
      if (!accessToken) {
        throw new Error(
          "Authenticated access token is required.",
        );
      }

      if (
        !hasValidProjectId
      ) {
        throw new Error("A valid project ID is required.");
      }

      return analyzeCompressedAirLeakage(
        accessToken,
        buildLeakageManagementRequest(formState),
      );
    },
  });

  function changeState(
    updater: (current: LeakageFormState) => LeakageFormState,
  ): void {
    leakageMutation.reset();
    setValidationErrors([]);
    setFormState(updater);
  }

  function applyChanges(
    changes: Partial<LeakageFormState>,
  ): void {
    changeState((current) => ({
      ...current,
      ...changes,
    }));
  }

  function runLeakageAnalysis(): void {
    const errors = validateLeakageFormState(formState);

    if (
      !hasValidProjectId
    ) {
      errors.unshift("A valid project ID is required.");
    }

    if (errors.length > 0) {
      setValidationErrors(errors);
      leakageMutation.reset();
      return;
    }

    setValidationErrors([]);
    leakageMutation.mutate();
  }

  function resetAnalysis(): void {
    leakageMutation.reset();
    setValidationErrors([]);
    setFormState(createInitialLeakageFormState());
  }

  return (
    <main className="space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <Badge variant="outline">
              Leakage Management
            </Badge>

            <h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">
              Compressed-Air Leakage Management
            </h1>

            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">
              Build a traceable plant leakage register, quantify
              compressed-air and energy losses, prioritize repair
              opportunities, estimate recoverable savings, and
              verify post-repair leakage reduction.
            </p>

            <div className="mt-4 flex flex-wrap gap-2">
              <Badge variant="secondary">
                {project
                  ? `${project.project_code} · ${project.project_name}`
                  : projectQuery.isPending
                    ? "Loading project..."
                    : `Project ${projectIdNumber}`}
              </Badge>

              {project && (
                <Badge variant="outline">
                  {project.status}
                </Badge>
              )}

              <Badge variant="outline">
                Leak Register
              </Badge>

              <Badge variant="outline">
                Energy & Cost
              </Badge>

              <Badge variant="outline">
                Repair Verification
              </Badge>

              <Badge variant="outline">
                Vendor Neutral
              </Badge>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={resetAnalysis}
            >
              <RotateCcw className="size-4" />
              Reset
            </Button>

            <Button
              type="button"
              onClick={runLeakageAnalysis}
              disabled={leakageMutation.isPending}
            >
              <Play className="size-4" />

              {leakageMutation.isPending
                ? "Analyzing..."
                : "Run Leakage Analysis"}
            </Button>
          </div>
        </div>
      </section>

      <Card>
        <CardHeader>
          <div className="flex items-start gap-3">
            <ClipboardList className="mt-0.5 size-5 text-slate-500" />

            <div>
              <CardTitle>
                Leakage Management Workflow
              </CardTitle>

              <CardDescription className="mt-1 leading-6">
                Establish the study basis, register individual
                leaks, apply the plant energy basis, record repair
                verification, and review engineering priorities
                and savings.
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="flex flex-wrap gap-2">
          {[
            "01 Study Basis",
            "02 Leak Register",
            "03 Energy Basis",
            "04 Repair Verification",
            "05 Engineering Review",
          ].map((stage) => (
            <Badge
              key={stage}
              variant="outline"
            >
              {stage}
            </Badge>
          ))}
        </CardContent>
      </Card>

      {validationErrors.length > 0 && (
        <Card className="border-amber-200 bg-amber-50">
          <CardHeader>
            <div className="flex items-start gap-3">
              <AlertTriangle className="mt-0.5 size-5 shrink-0 text-amber-700" />

              <div>
                <CardTitle className="text-base text-amber-950">
                  Leakage inputs require review
                </CardTitle>

                <CardDescription className="mt-1 text-amber-800">
                  Correct the following inputs before running the
                  compressed-air leakage analysis.
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent>
            <ul className="list-disc space-y-1 pl-5 text-sm text-amber-900">
              {validationErrors.map((error, index) => (
                <li key={`${error}-${index}`}>
                  {error}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      <LeakageStudyBasisSection
        state={formState}
        onChange={applyChanges}
      />

      <LeakRegisterSection
        leaks={formState.leaks}
        onChange={(leaks) =>
          changeState((current) => ({
            ...current,
            leaks,
          }))
        }
      />

      <LeakageEnergyBasisSection
        state={formState}
        onChange={applyChanges}
        inputOptions={inputOptionsQuery.data}
      />

      <RepairVerificationSection
        leaks={formState.leaks}
        onChange={(leaks) =>
          changeState((current) => ({
            ...current,
            leaks,
          }))
        }
      />

      <section className="flex justify-end">
        <Button
          type="button"
          size="lg"
          onClick={runLeakageAnalysis}
          disabled={leakageMutation.isPending}
        >
          <Play className="size-4" />

          {leakageMutation.isPending
            ? "Running Leakage Analysis..."
            : "Analyze Leakage Register"}
        </Button>
      </section>

      <LeakageEngineeringReviewSection
        result={leakageMutation.data ?? null}
        isPending={leakageMutation.isPending}
        errorMessage={
          leakageMutation.isError
            ? extractErrorMessage(leakageMutation.error)
            : null
        }
      />

      <div className="flex justify-start">
        <Button
          asChild
          variant="ghost"
        >
          <Link to={`/projects/${projectIdNumber}`}>
            Return to Project Workspace
          </Link>
        </Button>
      </div>
    </main>
  );
}
