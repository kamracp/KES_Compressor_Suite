import { useState } from "react";

import {
  AlertTriangle,
  Factory,
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
import { AirConsumersSection } from "../features/greenfield/components/AirConsumersSection";
import { AirTreatmentSection } from "../features/greenfield/components/AirTreatmentSection";
import { CompressorStationSection } from "../features/greenfield/components/CompressorStationSection";
import { DemandProfileSection } from "../features/greenfield/components/DemandProfileSection";
import { DesignBasisSection } from "../features/greenfield/components/DesignBasisSection";
import { EnergyCostSection } from "../features/greenfield/components/EnergyCostSection";
import { EngineeringReviewSection } from "../features/greenfield/components/EngineeringReviewSection";
import { PressureBudgetSection } from "../features/greenfield/components/PressureBudgetSection";
import { ReceiverStorageSection } from "../features/greenfield/components/ReceiverStorageSection";
import {
  buildGreenfieldDesignRequest,
  createInitialGreenfieldFormState,
  validateGreenfieldFormState,
  type GreenfieldFormState,
} from "../features/greenfield/greenfieldFormState";
import { designGreenfieldSystem } from "../features/greenfield/greenfieldService";
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

    return `Greenfield API request failed with status ${error.status}.`;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Greenfield system design could not be calculated.";
}

export function GreenfieldSystemDesignPage() {
  const { accessToken } = useAuth();
  const inputOptionsQuery = useInputOptions(accessToken);
  const {
    projectId,
    hasValidProjectId,
    project,
    projectQuery,
  } = useProjectContext();

  const [formState, setFormState] = useState<GreenfieldFormState>(
    createInitialGreenfieldFormState,
  );
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  if (!hasValidProjectId) {
    throw new Error("Valid project ID is required.");
  }

  if (!accessToken) {
    throw new Error("Authenticated access token is required.");
  }

  const designMutation = useMutation({
    mutationFn: () =>
      designGreenfieldSystem(
        accessToken,
        buildGreenfieldDesignRequest(formState),
      ),
  });

  function changeState(
    updater: (current: GreenfieldFormState) => GreenfieldFormState,
  ): void {
    designMutation.reset();
    setValidationErrors([]);
    setFormState(updater);
  }

  function runEngineeringDesign(): void {
    const errors = validateGreenfieldFormState(formState);

    if (errors.length > 0) {
      setValidationErrors(errors);
      designMutation.reset();
      return;
    }

    setValidationErrors([]);
    designMutation.mutate();
  }

  function resetDesign(): void {
    designMutation.reset();
    setValidationErrors([]);
    setFormState(createInitialGreenfieldFormState());
  }

  return (
    <main className="space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <Badge variant="outline">
              Greenfield Engineering
            </Badge>

            <h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">
              Greenfield Compressed-Air System Design
            </h1>

            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">
              Design a new factory compressed-air system from consumer demand
              through pressure requirements, proposed compressor station,
              treatment, storage, energy performance, and engineering review.
            </p>

            <div className="mt-4 flex flex-wrap gap-2">
              <Badge variant="secondary">
                {project
                  ? `${project.project_code} · ${project.project_name}`
                  : projectQuery.isPending
                    ? "Loading project..."
                    : `Project ${projectId}`}
              </Badge>

              {project && (
                <Badge variant="outline">
                  {project.status}
                </Badge>
              )}

              <Badge variant="outline">
                Vendor Neutral
              </Badge>

              <Badge variant="outline">
                System-Level Engineering
              </Badge>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={resetDesign}
            >
              <RotateCcw className="size-4" />
              Reset
            </Button>

            <Button
              type="button"
              onClick={runEngineeringDesign}
              disabled={designMutation.isPending}
            >
              <Play className="size-4" />
              {designMutation.isPending
                ? "Calculating..."
                : "Run System Design"}
            </Button>
          </div>
        </div>
      </section>

      <Card>
        <CardHeader>
          <div className="flex items-start gap-3">
            <Factory className="mt-0.5 size-5 text-slate-500" />

            <div>
              <CardTitle>
                Guided Engineering Workflow
              </CardTitle>

              <CardDescription className="mt-1 leading-6">
                Complete only the applicable optional modules. Consumer demand
                and demand profile remain the minimum Greenfield engineering
                basis.
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="flex flex-wrap gap-2">
          {[
            "01 Design Basis",
            "02 Air Consumers",
            "03 Demand Profile",
            "04 Pressure Budget",
            "05 Compressor Station",
            "06 Air Treatment",
            "07 Receiver / Storage",
            "08 Energy & Cost",
            "09 Engineering Review",
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
                  Engineering inputs require review
                </CardTitle>

                <CardDescription className="mt-1 text-amber-800">
                  Correct the following inputs before running the system design.
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent>
            <ul className="list-disc space-y-1 pl-5 text-sm text-amber-900">
              {validationErrors.map((error) => (
                <li key={error}>
                  {error}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      <DesignBasisSection
        inputOptions={inputOptionsQuery.data}
        value={formState.designBasis}
        onChange={(field, value) =>
          changeState((current) => ({
            ...current,
            designBasis: {
              ...current.designBasis,
              [field]: value,
            },
          }))
        }
      />

      <AirConsumersSection
        consumers={formState.consumers}
        onChange={(consumers) =>
          changeState((current) => ({
            ...current,
            consumers,
          }))
        }
      />

      <DemandProfileSection
        points={formState.demandProfilePoints}
        onChange={(demandProfilePoints) =>
          changeState((current) => ({
            ...current,
            demandProfilePoints,
          }))
        }
      />

      <PressureBudgetSection
        components={formState.pressureLossComponents}
        onChange={(pressureLossComponents) =>
          changeState((current) => ({
            ...current,
            pressureLossComponents,
          }))
        }
      />

      <CompressorStationSection
        station={formState.station}
        onChange={(station) =>
          changeState((current) => ({
            ...current,
            station,
          }))
        }
      />

      <AirTreatmentSection
        treatment={formState.treatment}
        onChange={(treatment) =>
          changeState((current) => ({
            ...current,
            treatment,
          }))
        }
      />

      <ReceiverStorageSection
        receiver={formState.receiver}
        onChange={(receiver) =>
          changeState((current) => ({
            ...current,
            receiver,
          }))
        }
      />

      <EnergyCostSection
        specificPowerKwPerNm3PerMin={
          formState.specificPowerKwPerNm3PerMin
        }
        annualOperatingDays={
          formState.designBasis.annualOperatingDays
        }
        electricityTariffPerKwh={
          formState.designBasis.electricityTariffPerKwh
        }
        onSpecificPowerChange={(specificPowerKwPerNm3PerMin) =>
          changeState((current) => ({
            ...current,
            specificPowerKwPerNm3PerMin,
          }))
        }
      />

      <section className="flex justify-end">
        <Button
          type="button"
          size="lg"
          onClick={runEngineeringDesign}
          disabled={designMutation.isPending}
        >
          <Play className="size-4" />

          {designMutation.isPending
            ? "Running Engineering Design..."
            : "Calculate Greenfield System"}
        </Button>
      </section>

      <EngineeringReviewSection
        result={designMutation.data ?? null}
        isPending={designMutation.isPending}
        errorMessage={
          designMutation.isError
            ? extractErrorMessage(designMutation.error)
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
