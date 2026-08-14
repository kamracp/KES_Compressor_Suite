import { useState } from "react";

import {
  Activity,
  AlertTriangle,
  Play,
  RotateCcw,
} from "lucide-react";
import { useMutation } from "@tanstack/react-query";
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
import { OperatingMeasurementsSection } from "../features/performance/components/OperatingMeasurementsSection";
import { PerformanceBasisSection } from "../features/performance/components/PerformanceBasisSection";
import { PerformanceEngineeringReviewSection } from "../features/performance/components/PerformanceEngineeringReviewSection";
import { PressureOptimizationSection } from "../features/performance/components/PressureOptimizationSection";
import { ReferenceBenchmarkSection } from "../features/performance/components/ReferenceBenchmarkSection";
import {
  buildPerformanceAnalysisRequest,
  createInitialPerformanceFormState,
  validatePerformanceFormState,
  type PerformanceFormState,
} from "../features/performance/performanceFormState";
import { analyzeCompressedAirPerformance } from "../features/performance/performanceService";
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

    return `Performance API request failed with status ${error.status}.`;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Performance and energy analysis could not be completed.";
}

export function PerformanceEnergyAnalysisPage() {
  const { projectId } = useParams();
  const { accessToken } = useAuth();

  const [formState, setFormState] = useState<PerformanceFormState>(
    createInitialPerformanceFormState,
  );

  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  const performanceMutation = useMutation({
    mutationFn: () => {
      if (!accessToken) {
        throw new Error("Authenticated access token is required.");
      }

      return analyzeCompressedAirPerformance(
        accessToken,
        buildPerformanceAnalysisRequest(formState),
      );
    },
  });

  function changeState(
    updater: (
      current: PerformanceFormState,
    ) => PerformanceFormState,
  ): void {
    performanceMutation.reset();
    setValidationErrors([]);
    setFormState(updater);
  }

  function applyStateChanges(
    changes: Partial<PerformanceFormState>,
  ): void {
    changeState((current) => ({
      ...current,
      ...changes,
    }));
  }

  function runPerformanceAnalysis(): void {
    const errors = validatePerformanceFormState(formState);

    if (errors.length > 0) {
      setValidationErrors(errors);
      performanceMutation.reset();
      return;
    }

    setValidationErrors([]);
    performanceMutation.mutate();
  }

  function resetAnalysis(): void {
    performanceMutation.reset();
    setValidationErrors([]);
    setFormState(createInitialPerformanceFormState());
  }

  return (
    <main className="space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <Badge variant="outline">
              Performance Engineering
            </Badge>

            <h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">
              Compressed-Air Performance & Energy Analysis
            </h1>

            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">
              Analyze measured compressed-air flow, pressure, and electrical
              power to establish specific performance, utilization, annual
              energy consumption, operating cost, and pressure-optimization
              potential.
            </p>

            <div className="mt-4 flex flex-wrap gap-2">
              <Badge variant="secondary">
                Project {projectId ?? "Unknown"}
              </Badge>

              <Badge variant="outline">
                Measured Performance
              </Badge>

              <Badge variant="outline">
                Energy Baseline
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
              onClick={runPerformanceAnalysis}
              disabled={performanceMutation.isPending}
            >
              <Play className="size-4" />

              {performanceMutation.isPending
                ? "Analyzing..."
                : "Run Performance Analysis"}
            </Button>
          </div>
        </div>
      </section>

      <Card>
        <CardHeader>
          <div className="flex items-start gap-3">
            <Activity className="mt-0.5 size-5 text-slate-500" />

            <div>
              <CardTitle>
                Performance Analysis Workflow
              </CardTitle>

              <CardDescription className="mt-1 leading-6">
                Establish the measurement basis first, compare measured
                performance with available reference data, annualize the energy
                baseline, and then evaluate an optional pressure-reduction
                scenario.
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="flex flex-wrap gap-2">
          {[
            "01 Analysis Basis",
            "02 Operating Measurements",
            "03 Rated & Reference Data",
            "04 Pressure Scenario",
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
                  Performance inputs require review
                </CardTitle>

                <CardDescription className="mt-1 text-amber-800">
                  Correct the following inputs before running the performance
                  and energy analysis.
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

      <PerformanceBasisSection
        state={formState}
        onChange={applyStateChanges}
      />

      <OperatingMeasurementsSection
        measurements={formState.measurements}
        onChange={(measurements) =>
          changeState((current) => ({
            ...current,
            measurements,
          }))
        }
      />

      <ReferenceBenchmarkSection
        state={formState}
        onChange={applyStateChanges}
      />

      <PressureOptimizationSection
        state={formState}
        onChange={applyStateChanges}
      />

      <section className="flex justify-end">
        <Button
          type="button"
          size="lg"
          onClick={runPerformanceAnalysis}
          disabled={performanceMutation.isPending}
        >
          <Play className="size-4" />

          {performanceMutation.isPending
            ? "Running Performance Analysis..."
            : "Analyze Performance & Energy"}
        </Button>
      </section>

      <PerformanceEngineeringReviewSection
        result={performanceMutation.data ?? null}
        isPending={performanceMutation.isPending}
        errorMessage={
          performanceMutation.isError
            ? extractErrorMessage(performanceMutation.error)
            : null
        }
      />

      <div className="flex justify-start">
        <Button
          asChild
          variant="ghost"
        >
          <Link to={`/projects/${projectId}`}>
            Return to Project Workspace
          </Link>
        </Button>
      </div>
    </main>
  );
}
