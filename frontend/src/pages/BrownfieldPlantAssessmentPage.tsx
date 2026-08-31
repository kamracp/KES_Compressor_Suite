import { useState } from "react";

import {
  AlertTriangle,
  ClipboardCheck,
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
import { BrownfieldEngineeringReviewSection } from "../features/brownfield/components/BrownfieldEngineeringReviewSection";
import { CompressorMeasurementsSection } from "../features/brownfield/components/CompressorMeasurementsSection";
import { ExistingCompressorSection } from "../features/brownfield/components/ExistingCompressorSection";
import { LeakageSurveySection } from "../features/brownfield/components/LeakageSurveySection";
import { AirTreatmentSection } from "../features/brownfield/components/AirTreatmentSection";
import { MotorPfcSection } from "../features/brownfield/components/MotorPfcSection";
import { OptimizationBasisSection } from "../features/brownfield/components/OptimizationBasisSection";
import { SystemMeasurementsSection } from "../features/brownfield/components/SystemMeasurementsSection";
import {
  buildBrownfieldAuditRequest,
  createInitialBrownfieldFormState,
  validateBrownfieldFormState,
  type BrownfieldFormState,
} from "../features/brownfield/brownfieldFormState";
import { analyzeBrownfieldSystem } from "../features/brownfield/brownfieldService";
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

    return `Brownfield API request failed with status ${error.status}.`;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Brownfield plant assessment could not be completed.";
}

export function BrownfieldPlantAssessmentPage() {
  const { accessToken } = useAuth();
  const {
    projectId: projectIdNumber,
    hasValidProjectId,
    project,
    projectQuery,
  } = useProjectContext();

  const [formState, setFormState] = useState<BrownfieldFormState>(
    createInitialBrownfieldFormState,
  );
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  const auditMutation = useMutation({
    mutationFn: () => {
      if (!accessToken) {
        throw new Error("Authenticated access token is required.");
      }

      if (
        !hasValidProjectId
      ) {
        throw new Error("A valid project ID is required.");
      }

      return analyzeBrownfieldSystem(
        accessToken,
        buildBrownfieldAuditRequest(
          formState,
          projectIdNumber,
        ),
      );
    },
  });

  function changeState(
    updater: (current: BrownfieldFormState) => BrownfieldFormState,
  ): void {
    auditMutation.reset();
    setValidationErrors([]);
    setFormState(updater);
  }

  function runBrownfieldAssessment(): void {
    const errors = validateBrownfieldFormState(formState);

    if (
      !hasValidProjectId
    ) {
      errors.unshift("A valid project ID is required.");
    }

    if (errors.length > 0) {
      setValidationErrors(errors);
      auditMutation.reset();
      return;
    }

    setValidationErrors([]);
    auditMutation.mutate();
  }

  function resetAssessment(): void {
    auditMutation.reset();
    setValidationErrors([]);
    setFormState(createInitialBrownfieldFormState());
  }

  return (
    <main className="space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <Badge variant="outline">
              Brownfield Engineering
            </Badge>

            <h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">
              Existing Plant Compressed-Air Assessment
            </h1>

            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">
              Assess an operating compressed-air system using installed
              equipment data and measured plant performance to identify
              capacity, utilization, leakage, unloaded-running, pressure,
              energy, and optimization opportunities.
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
                Measured Performance
              </Badge>

              <Badge variant="outline">
                Rule-Based Opportunities
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
              onClick={runBrownfieldAssessment}
              disabled={auditMutation.isPending}
            >
              <Play className="size-4" />

              {auditMutation.isPending
                ? "Analyzing..."
                : "Run Plant Assessment"}
            </Button>
          </div>
        </div>
      </section>

      <Card>
        <CardHeader>
          <div className="flex items-start gap-3">
            <ClipboardCheck className="mt-0.5 size-5 text-slate-500" />

            <div>
              <CardTitle>
                Brownfield Assessment Workflow
              </CardTitle>

              <CardDescription className="mt-1 leading-6">
                Build the measured plant baseline first, then evaluate
                operating losses and engineering opportunities from the
                existing system.
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="flex flex-wrap gap-2">
          {[
            "01 Audit Basis",
            "02 Existing Equipment",
            "03 Compressor Measurements",
            "04 System Measurements",
            "05 Leakage Survey",
            "06 Optimization",
            "07 Engineering Review",
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
                  Audit inputs require review
                </CardTitle>

                <CardDescription className="mt-1 text-amber-800">
                  Correct the following inputs before running the Brownfield
                  plant assessment.
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

      <OptimizationBasisSection
        auditCode={formState.auditCode}
        annualOperatingHours={formState.annualOperatingHours}
        electricityTariffPerKwh={formState.electricityTariffPerKwh}
        optimizedDischargePressureBarG={
          formState.optimizedDischargePressureBarG
        }
        expectedLeakRepairFraction={
          formState.expectedLeakRepairFraction
        }
        demandSavingControlFactor={
          formState.demandSavingControlFactor
        }
        powerPenaltyFractionPerBar={
          formState.powerPenaltyFractionPerBar
        }
        notes={formState.notes}
        onAuditCodeChange={(auditCode) =>
          changeState((current) => ({
            ...current,
            auditCode,
          }))
        }
        onAnnualOperatingHoursChange={(annualOperatingHours) =>
          changeState((current) => ({
            ...current,
            annualOperatingHours,
          }))
        }
        onElectricityTariffChange={(electricityTariffPerKwh) =>
          changeState((current) => ({
            ...current,
            electricityTariffPerKwh,
          }))
        }
        onOptimizedPressureChange={(optimizedDischargePressureBarG) =>
          changeState((current) => ({
            ...current,
            optimizedDischargePressureBarG,
          }))
        }
        onExpectedLeakRepairFractionChange={(
          expectedLeakRepairFraction,
        ) =>
          changeState((current) => ({
            ...current,
            expectedLeakRepairFraction,
          }))
        }
        onDemandSavingControlFactorChange={(
          demandSavingControlFactor,
        ) =>
          changeState((current) => ({
            ...current,
            demandSavingControlFactor,
          }))
        }
        onPowerPenaltyFractionPerBarChange={(
          powerPenaltyFractionPerBar,
        ) =>
          changeState((current) => ({
            ...current,
            powerPenaltyFractionPerBar,
          }))
        }
        onNotesChange={(notes) =>
          changeState((current) => ({
            ...current,
            notes,
          }))
        }
      />

      <ExistingCompressorSection
        compressors={formState.compressors}
        onChange={(compressors) =>
          changeState((current) => ({
            ...current,
            compressors,
          }))
        }
      />

      <CompressorMeasurementsSection
        compressors={formState.compressors}
        measurements={formState.compressorMeasurements}
        onChange={(compressorMeasurements) =>
          changeState((current) => ({
            ...current,
            compressorMeasurements,
          }))
        }
      />

      <SystemMeasurementsSection
        measurements={formState.systemMeasurements}
        onChange={(systemMeasurements) =>
          changeState((current) => ({
            ...current,
            systemMeasurements,
          }))
        }
      />

      <LeakageSurveySection
        leakageSummary={formState.leakageSummary}
        onChange={(leakageSummary) =>
          changeState((current) => ({
            ...current,
            leakageSummary,
          }))
        }
      />

      <AirTreatmentSection
        condensateDrainAirLossNm3PerHr={
          formState.condensateDrainAirLossNm3PerHr
        }
        filterExcessPressureDropBar={
          formState.filterExcessPressureDropBar
        }
        onChange={(field, value) =>
          changeState((current) => ({
            ...current,
            [field]: value,
          }))
        }
      />

      <MotorPfcSection
        motorMeasuredVoltageV={formState.motorMeasuredVoltageV}
        motorMeasuredCurrentA={formState.motorMeasuredCurrentA}
        motorMeasuredPowerFactor={formState.motorMeasuredPowerFactor}
        motorTargetPowerFactor={formState.motorTargetPowerFactor}
        motorRatedPowerKw={formState.motorRatedPowerKw}
        pfPenaltyAnnualCost={formState.pfPenaltyAnnualCost}
        onChange={(field, value) =>
          changeState((current) => ({
            ...current,
            [field]: value,
          }))
        }
      />

      <section className="flex justify-end">
        <Button
          type="button"
          size="lg"
          onClick={runBrownfieldAssessment}
          disabled={auditMutation.isPending}
        >
          <Play className="size-4" />

          {auditMutation.isPending
            ? "Running Brownfield Analysis..."
            : "Analyze Existing Plant"}
        </Button>
      </section>

      <BrownfieldEngineeringReviewSection
        result={auditMutation.data ?? null}
        isPending={auditMutation.isPending}
        errorMessage={
          auditMutation.isError
            ? extractErrorMessage(auditMutation.error)
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
