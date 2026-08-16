import { useState } from "react";

import {
  AlertTriangle,
  ClipboardList,
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
import { AftercoolerSection } from "../features/allied/components/AftercoolerSection";
import { AlliedEngineeringReviewSection } from "../features/allied/components/AlliedEngineeringReviewSection";
import { AlliedStudyBasisSection } from "../features/allied/components/AlliedStudyBasisSection";
import { CondensateDrainSection } from "../features/allied/components/CondensateDrainSection";
import { FilterTrainSection } from "../features/allied/components/FilterTrainSection";
import { MoistureSeparatorSection } from "../features/allied/components/MoistureSeparatorSection";
import { ReceiverEngineeringSection } from "../features/allied/components/ReceiverEngineeringSection";
import { TreatmentEngineeringSection } from "../features/allied/components/TreatmentEngineeringSection";
import {
  buildAlliedEquipmentAnalysisRequest,
  createInitialAlliedFormState,
  validateAlliedFormState,
  type AlliedFormState,
} from "../features/allied/alliedFormState";
import { analyzeCompressedAirAlliedEquipment } from "../features/allied/alliedService";
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

    return `Allied equipment API request failed with status ${error.status}.`;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Compressed-air allied equipment analysis could not be completed.";
}

export function AlliedEquipmentEngineeringPage() {
  const { projectId } = useParams();
  const { accessToken } = useAuth();

  const [formState, setFormState] = useState<AlliedFormState>(
    createInitialAlliedFormState,
  );

  const [validationErrors, setValidationErrors] = useState<string[]>(
    [],
  );

  const projectIdNumber = Number(projectId);

  const alliedMutation = useMutation({
    mutationFn: () => {
      if (!accessToken) {
        throw new Error(
          "Authenticated access token is required.",
        );
      }

      if (
        !Number.isInteger(projectIdNumber) ||
        projectIdNumber <= 0
      ) {
        throw new Error("A valid project ID is required.");
      }

      return analyzeCompressedAirAlliedEquipment(
        accessToken,
        buildAlliedEquipmentAnalysisRequest(formState),
      );
    },
  });

  function changeState(
    updater: (current: AlliedFormState) => AlliedFormState,
  ): void {
    alliedMutation.reset();
    setValidationErrors([]);
    setFormState(updater);
  }

  function applyChanges(
    changes: Partial<AlliedFormState>,
  ): void {
    changeState((current) => ({
      ...current,
      ...changes,
    }));
  }

  function runAlliedAnalysis(): void {
    const errors = validateAlliedFormState(formState);

    if (
      !Number.isInteger(projectIdNumber) ||
      projectIdNumber <= 0
    ) {
      errors.unshift("A valid project ID is required.");
    }

    if (errors.length > 0) {
      setValidationErrors(errors);
      alliedMutation.reset();
      return;
    }

    setValidationErrors([]);
    alliedMutation.mutate();
  }

  function resetAnalysis(): void {
    alliedMutation.reset();
    setValidationErrors([]);
    setFormState(createInitialAlliedFormState());
  }

  return (
    <main className="space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <Badge variant="outline">
              Allied Equipment Engineering
            </Badge>

            <h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">
              Compressed-Air Allied Equipment Engineering
            </h1>

            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">
              Engineer compressed-air receivers, treatment systems,
              aftercoolers, moisture separators, filter trains, and
              condensate-drain provisions using a traceable,
              vendor-neutral calculation workflow.
            </p>

            <div className="mt-4 flex flex-wrap gap-2">
              <Badge variant="secondary">
                Project {projectId ?? "Unknown"}
              </Badge>

              <Badge variant="outline">
                Storage
              </Badge>

              <Badge variant="outline">
                Air Treatment
              </Badge>

              <Badge variant="outline">
                Pressure Drop
              </Badge>

              <Badge variant="outline">
                Capacity Adequacy
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
              onClick={runAlliedAnalysis}
              disabled={alliedMutation.isPending}
            >
              <Play className="size-4" />

              {alliedMutation.isPending
                ? "Analyzing..."
                : "Run Allied Analysis"}
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
                Allied Equipment Engineering Workflow
              </CardTitle>

              <CardDescription className="mt-1 leading-6">
                Establish the study basis, configure storage and air
                treatment, document downstream allied equipment,
                evaluate capacity and pressure losses, and review
                deterministic engineering recommendations.
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="flex flex-wrap gap-2">
          {[
            "01 Study Basis",
            "02 Receiver",
            "03 Treatment",
            "04 Aftercooler",
            "05 Moisture Separation",
            "06 Filter Train",
            "07 Condensate Drains",
            "08 Engineering Review",
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
                  Allied equipment inputs require review
                </CardTitle>

                <CardDescription className="mt-1 text-amber-800">
                  Correct the following inputs before running the
                  compressed-air allied-equipment analysis.
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

      <AlliedStudyBasisSection
        state={formState}
        onChange={applyChanges}
      />

      <ReceiverEngineeringSection
        receiver={formState.receiver}
        onChange={(receiver) =>
          changeState((current) => ({
            ...current,
            receiver,
          }))
        }
      />

      <TreatmentEngineeringSection
        treatment={formState.treatment}
        onChange={(treatment) =>
          changeState((current) => ({
            ...current,
            treatment,
          }))
        }
      />

      <AftercoolerSection
        aftercooler={formState.aftercooler}
        onChange={(aftercooler) =>
          changeState((current) => ({
            ...current,
            aftercooler,
          }))
        }
      />

      <MoistureSeparatorSection
        separator={formState.moistureSeparator}
        onChange={(moistureSeparator) =>
          changeState((current) => ({
            ...current,
            moistureSeparator,
          }))
        }
      />

      <FilterTrainSection
        stages={formState.filterStages}
        onChange={(filterStages) =>
          changeState((current) => ({
            ...current,
            filterStages,
          }))
        }
      />

      <CondensateDrainSection
        drains={formState.condensateDrains}
        onChange={(condensateDrains) =>
          changeState((current) => ({
            ...current,
            condensateDrains,
          }))
        }
      />

      <section className="flex justify-end">
        <Button
          type="button"
          size="lg"
          onClick={runAlliedAnalysis}
          disabled={alliedMutation.isPending}
        >
          <Play className="size-4" />

          {alliedMutation.isPending
            ? "Running Allied Analysis..."
            : "Analyze Allied Equipment"}
        </Button>
      </section>

      <AlliedEngineeringReviewSection
        result={alliedMutation.data ?? null}
        isPending={alliedMutation.isPending}
        errorMessage={
          alliedMutation.isError
            ? extractErrorMessage(alliedMutation.error)
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
