import { useState } from "react";

import {
  AlertTriangle,
  Boxes,
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
import { SkidComponentRegisterSection } from "../features/skid/components/SkidComponentRegisterSection";
import { SkidConfigurationSection } from "../features/skid/components/SkidConfigurationSection";
import { SkidEngineeringReviewSection } from "../features/skid/components/SkidEngineeringReviewSection";
import { SkidStudyBasisSection } from "../features/skid/components/SkidStudyBasisSection";
import {
  buildAirSkidAssessmentRequest,
  createInitialSkidFormState,
  validateSkidFormState,
  type SkidFormState,
} from "../features/skid/skidFormState";
import { assessCompressedAirSkid } from "../features/skid/skidService";
import { useProjectContext } from "../features/projects/useProjectContext";
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

    return `Skid assessment API request failed with status ${error.status}.`;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Compressed-air skid assessment could not be completed.";
}

export function SkidEngineeringPage() {
  const { accessToken } = useAuth();
  const {
    projectId: projectIdNumber,
    hasValidProjectId,
    project,
    projectQuery,
  } = useProjectContext();

  const [formState, setFormState] = useState<SkidFormState>(
    createInitialSkidFormState,
  );

  const [validationErrors, setValidationErrors] = useState<string[]>(
    [],
  );

  const skidMutation = useMutation({
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

      return assessCompressedAirSkid(
        accessToken,
        buildAirSkidAssessmentRequest(formState),
      );
    },
  });

  function changeState(
    updater: (current: SkidFormState) => SkidFormState,
  ): void {
    skidMutation.reset();
    setValidationErrors([]);
    setFormState(updater);
  }

  function applyChanges(
    changes: Partial<SkidFormState>,
  ): void {
    changeState((current) => ({
      ...current,
      ...changes,
    }));
  }

  function runSkidAssessment(): void {
    const errors = validateSkidFormState(formState);

    if (
      !hasValidProjectId
    ) {
      errors.unshift("A valid project ID is required.");
    }

    if (errors.length > 0) {
      setValidationErrors(errors);
      skidMutation.reset();
      return;
    }

    setValidationErrors([]);
    skidMutation.mutate();
  }

  function resetAssessment(): void {
    skidMutation.reset();
    setValidationErrors([]);
    setFormState(createInitialSkidFormState());
  }

  return (
    <main className="space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <Badge variant="outline">
              Compressed-Air Skid Engineering
            </Badge>

            <h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">
              Compressed-Air Skid Engineering Assessment
            </h1>

            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">
              Configure the skid design basis, register installed
              components, document receiver and instrumentation
              provisions, and evaluate deterministic engineering
              adequacy.
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
                Capacity
              </Badge>

              <Badge variant="outline">
                Pressure Rating
              </Badge>

              <Badge variant="outline">
                Pressure Drop
              </Badge>

              <Badge variant="outline">
                Instrumentation
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
              onClick={resetAssessment}
            >
              <RotateCcw className="size-4" />
              Reset
            </Button>

            <Button
              type="button"
              onClick={runSkidAssessment}
              disabled={skidMutation.isPending}
            >
              <Play className="size-4" />

              {skidMutation.isPending
                ? "Assessing..."
                : "Run Skid Assessment"}
            </Button>
          </div>
        </div>
      </section>

      <Card>
        <CardHeader>
          <div className="flex items-start gap-3">
            <Boxes className="mt-0.5 size-5 text-slate-500" />

            <div>
              <CardTitle>
                Skid Engineering Workflow
              </CardTitle>

              <CardDescription className="mt-1 leading-6">
                Establish the design basis, document the component
                register, confirm receiver and instrumentation
                configuration, and review the calculated skid
                engineering assessment.
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="flex flex-wrap gap-2">
          {[
            "01 Study Basis",
            "02 Component Register",
            "03 Configuration",
            "04 Engineering Review",
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
                  Skid inputs require review
                </CardTitle>

                <CardDescription className="mt-1 text-amber-800">
                  Correct the following inputs before running the
                  compressed-air skid engineering assessment.
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

      <SkidStudyBasisSection
        state={formState}
        onChange={applyChanges}
      />

      <SkidComponentRegisterSection
        components={formState.components}
        onChange={(components) =>
          changeState((current) => ({
            ...current,
            components,
          }))
        }
      />

      <SkidConfigurationSection
        state={formState}
        onChange={applyChanges}
      />

      <section className="flex justify-end">
        <Button
          type="button"
          size="lg"
          onClick={runSkidAssessment}
          disabled={skidMutation.isPending}
        >
          <Play className="size-4" />

          {skidMutation.isPending
            ? "Running Skid Assessment..."
            : "Assess Compressed-Air Skid"}
        </Button>
      </section>

      <SkidEngineeringReviewSection
        result={skidMutation.data ?? null}
        isPending={skidMutation.isPending}
        errorMessage={
          skidMutation.isError
            ? extractErrorMessage(skidMutation.error)
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
