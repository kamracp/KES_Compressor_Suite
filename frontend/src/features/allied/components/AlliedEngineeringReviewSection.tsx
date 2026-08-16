import {
  AlertTriangle,
  CheckCircle2,
  CircleDashed,
  Gauge,
  ShieldCheck,
  SlidersHorizontal,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

import type {
  AlliedEquipmentAnalysisResponse,
  EquipmentAdequacyStatus,
  EquipmentCapacityEvaluation,
  RecommendationSeverity,
} from "../alliedTypes";

type AlliedEngineeringReviewSectionProps = {
  result: AlliedEquipmentAnalysisResponse | null;
  isPending: boolean;
  errorMessage: string | null;
};

type MetricProps = {
  label: string;
  value: string;
  unit?: string;
};

type EvaluationCardProps = {
  evaluation: EquipmentCapacityEvaluation;
  unit: string;
};

function formatDecimal(
  value: string | null,
  maximumFractionDigits = 2,
): string {
  if (value === null) {
    return "Not evaluated";
  }

  const numericValue = Number(value);

  if (!Number.isFinite(numericValue)) {
    return value;
  }

  return numericValue.toLocaleString("en-IN", {
    maximumFractionDigits,
  });
}

function formatPercent(
  value: string | null,
  maximumFractionDigits = 1,
): string {
  if (value === null) {
    return "Not evaluated";
  }

  const numericValue = Number(value);

  if (!Number.isFinite(numericValue)) {
    return value;
  }

  return `${(numericValue * 100).toLocaleString("en-IN", {
    maximumFractionDigits,
  })}%`;
}

function enumLabel(value: string): string {
  return value
    .split("_")
    .map(
      (part) =>
        part.charAt(0).toUpperCase() +
        part.slice(1).toLowerCase(),
    )
    .join(" ");
}

function statusVariant(
  status: EquipmentAdequacyStatus,
): "default" | "destructive" | "secondary" | "outline" {
  if (status === "ADEQUATE") {
    return "default";
  }

  if (status === "UNDERSIZED") {
    return "destructive";
  }

  if (status === "NOT_SELECTED") {
    return "secondary";
  }

  return "outline";
}

function severityVariant(
  severity: RecommendationSeverity,
): "destructive" | "secondary" | "outline" {
  if (
    severity === "CRITICAL" ||
    severity === "WARNING"
  ) {
    return "destructive";
  }

  if (severity === "ADVISORY") {
    return "secondary";
  }

  return "outline";
}

function Metric({
  label,
  value,
  unit,
}: MetricProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <p className="text-xs font-medium text-slate-500">
        {label}
      </p>

      <p className="mt-2 text-2xl font-bold tracking-tight text-slate-950">
        {value}
      </p>

      {unit && (
        <p className="mt-1 text-xs font-medium text-slate-500">
          {unit}
        </p>
      )}
    </div>
  );
}

function EvaluationCard({
  evaluation,
  unit,
}: EvaluationCardProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-slate-950">
            {enumLabel(evaluation.equipment_code)}
          </p>

          <p className="mt-1 text-xs text-slate-500">
            Required versus selected capacity
          </p>
        </div>

        <Badge variant={statusVariant(evaluation.status)}>
          {enumLabel(evaluation.status)}
        </Badge>
      </div>

      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <div>
          <p className="text-xs font-medium text-slate-500">
            Required Capacity
          </p>

          <p className="mt-1 font-semibold text-slate-950">
            {formatDecimal(evaluation.required_capacity)} {unit}
          </p>
        </div>

        <div>
          <p className="text-xs font-medium text-slate-500">
            Selected Capacity
          </p>

          <p className="mt-1 font-semibold text-slate-950">
            {evaluation.selected_capacity === null
              ? "Not selected"
              : `${formatDecimal(
                  evaluation.selected_capacity,
                )} ${unit}`}
          </p>
        </div>

        <div>
          <p className="text-xs font-medium text-slate-500">
            Capacity Margin
          </p>

          <p className="mt-1 font-semibold text-slate-950">
            {evaluation.capacity_margin === null
              ? "Not evaluated"
              : `${formatDecimal(
                  evaluation.capacity_margin,
                )} ${unit}`}
          </p>
        </div>

        <div>
          <p className="text-xs font-medium text-slate-500">
            Capacity Margin %
          </p>

          <p className="mt-1 font-semibold text-slate-950">
            {formatPercent(
              evaluation.capacity_margin_fraction,
            )}
          </p>
        </div>
      </div>
    </div>
  );
}

export function AlliedEngineeringReviewSection({
  result,
  isPending,
  errorMessage,
}: AlliedEngineeringReviewSectionProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <Gauge className="size-5" />
          </div>

          <div>
            <CardTitle>
              Allied Equipment Engineering Review
            </CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Review receiver storage, air-treatment duty,
              equipment capacity adequacy, additional pressure
              losses, and deterministic engineering recommendations.
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-7">
        {isPending && (
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {Array.from({ length: 8 }).map((_, index) => (
              <Skeleton
                key={index}
                className="h-28 w-full"
              />
            ))}
          </div>
        )}

        {!isPending && errorMessage && (
          <div
            className="rounded-xl border border-red-200 bg-red-50 p-5"
            role="alert"
          >
            <div className="flex items-start gap-3">
              <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-700" />

              <div>
                <p className="font-semibold text-red-900">
                  Allied equipment analysis failed
                </p>

                <p className="mt-1 text-sm leading-6 text-red-700">
                  {errorMessage}
                </p>
              </div>
            </div>
          </div>
        )}

        {!isPending && !errorMessage && !result && (
          <div className="rounded-xl border border-dashed border-slate-300 p-8 text-center">
            <CircleDashed className="mx-auto size-8 text-slate-400" />

            <p className="mt-3 font-semibold text-slate-900">
              Allied equipment analysis not yet calculated
            </p>

            <p className="mx-auto mt-1 max-w-2xl text-sm leading-6 text-slate-500">
              Configure at least one allied-equipment item and
              run the engineering analysis to review sizing,
              adequacy, pressure losses, and recommendations.
            </p>
          </div>
        )}

        {!isPending && !errorMessage && result && (
          <>
            {result.receiver_result && (
              <section>
                <div className="mb-4 flex items-center gap-2">
                  <SlidersHorizontal className="size-5 text-slate-600" />

                  <h3 className="font-semibold text-slate-950">
                    Receiver Storage Sizing
                  </h3>
                </div>

                <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                  <Metric
                    label="Flow Deficit"
                    value={formatDecimal(
                      result.receiver_result
                        .flow_deficit_nm3_per_hr,
                    )}
                    unit="Nm³/h"
                  />

                  <Metric
                    label="Pressure Band"
                    value={formatDecimal(
                      result.receiver_result.pressure_band_bar,
                    )}
                    unit="bar"
                  />

                  <Metric
                    label="Base Receiver Volume"
                    value={formatDecimal(
                      result.receiver_result
                        .base_receiver_volume_m3,
                    )}
                    unit="m³"
                  />

                  <Metric
                    label="Recommended Receiver Volume"
                    value={formatDecimal(
                      result.receiver_result
                        .recommended_receiver_volume_m3,
                    )}
                    unit="m³"
                  />
                </div>

                <div className="mt-4 flex items-center gap-2 text-sm text-slate-600">
                  {result.receiver_result.storage_required ? (
                    <AlertTriangle className="size-4" />
                  ) : (
                    <CheckCircle2 className="size-4" />
                  )}

                  <span>
                    {result.receiver_result.storage_required
                      ? "Transient storage is required for the evaluated demand event."
                      : "No additional transient storage requirement was identified from the supplied demand basis."}
                  </span>
                </div>
              </section>
            )}

            {result.treatment_result && (
              <section>
                <div className="mb-4 flex items-center gap-2">
                  <ShieldCheck className="size-5 text-slate-600" />

                  <h3 className="font-semibold text-slate-950">
                    Air Treatment Sizing
                  </h3>
                </div>

                <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                  <Metric
                    label="Delivered Flow"
                    value={formatDecimal(
                      result.treatment_result
                        .required_delivered_flow_nm3_per_hr,
                    )}
                    unit="Nm³/h"
                  />

                  <Metric
                    label="Dryer Purge Loss"
                    value={formatDecimal(
                      result.treatment_result
                        .dryer_purge_loss_nm3_per_hr,
                    )}
                    unit="Nm³/h"
                  />

                  <Metric
                    label="Gross Flow Before Purge"
                    value={formatDecimal(
                      result.treatment_result
                        .gross_flow_before_purge_nm3_per_hr,
                    )}
                    unit="Nm³/h"
                  />

                  <Metric
                    label="Recommended Treatment Capacity"
                    value={formatDecimal(
                      result.treatment_result
                        .recommended_treatment_capacity_nm3_per_hr,
                    )}
                    unit="Nm³/h"
                  />
                </div>

                <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                  <Metric
                    label="Treatment Pressure Drop"
                    value={formatDecimal(
                      result.treatment_result
                        .total_treatment_pressure_drop_bar,
                    )}
                    unit="bar"
                  />

                  <Metric
                    label="Purge Loss Fraction"
                    value={formatPercent(
                      result.treatment_result
                        .purge_loss_fraction,
                    )}
                  />

                  <Metric
                    label="Dryer Type"
                    value={enumLabel(
                      result.treatment_result.dryer_type,
                    )}
                  />

                  <Metric
                    label="Required Air Quality"
                    value={enumLabel(
                      result.treatment_result
                        .required_air_quality,
                    )}
                  />
                </div>
              </section>
            )}

            <section>
              <div className="mb-4 flex items-center gap-2">
                <CheckCircle2 className="size-5 text-slate-600" />

                <h3 className="font-semibold text-slate-950">
                  Equipment Capacity Adequacy
                </h3>
              </div>

              <div className="grid gap-4 xl:grid-cols-2">
                {result.receiver_evaluation && (
                  <EvaluationCard
                    evaluation={result.receiver_evaluation}
                    unit="m³"
                  />
                )}

                {result.treatment_evaluation && (
                  <EvaluationCard
                    evaluation={result.treatment_evaluation}
                    unit="Nm³/h"
                  />
                )}

                {result.aftercooler_evaluation && (
                  <EvaluationCard
                    evaluation={result.aftercooler_evaluation}
                    unit="Nm³/h"
                  />
                )}

                {result.moisture_separator_evaluation && (
                  <EvaluationCard
                    evaluation={result.moisture_separator_evaluation}
                    unit="Nm³/h"
                  />
                )}

                {result.filter_evaluations.map(
                  (evaluation, index) => (
                    <EvaluationCard
                      key={`${evaluation.equipment_code}-${index}`}
                      evaluation={evaluation}
                      unit="Nm³/h"
                    />
                  ),
                )}
              </div>

              {!result.receiver_evaluation &&
                !result.treatment_evaluation &&
                !result.aftercooler_evaluation &&
                !result.moisture_separator_evaluation &&
                result.filter_evaluations.length === 0 && (
                  <div className="rounded-lg border border-dashed border-slate-300 p-5">
                    <p className="text-sm text-slate-600">
                      No equipment-capacity evaluations were generated
                      for the supplied configuration.
                    </p>
                  </div>
                )}
            </section>

            <section>
              <div className="mb-4 flex items-center gap-2">
                <Gauge className="size-5 text-slate-600" />

                <h3 className="font-semibold text-slate-950">
                  Allied Equipment Pressure Loss
                </h3>
              </div>

              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <Metric
                  label="Additional Pressure Drop"
                  value={formatDecimal(
                    result.total_additional_pressure_drop_bar,
                  )}
                  unit="bar"
                />

                {result.treatment_result && (
                  <Metric
                    label="Treatment Pressure Drop"
                    value={formatDecimal(
                      result.treatment_result
                        .total_treatment_pressure_drop_bar,
                    )}
                    unit="bar"
                  />
                )}
              </div>

              <p className="mt-3 max-w-3xl text-xs leading-5 text-slate-500">
                Additional pressure drop represents configured
                aftercooler, moisture-separator, and filter-stage
                losses. Treatment pressure drop is reported separately
                by the air-treatment sizing engine.
              </p>
            </section>

            <section>
              <div className="mb-4 flex items-center gap-2">
                <ShieldCheck className="size-5 text-slate-600" />

                <h3 className="font-semibold text-slate-950">
                  Engineering Recommendations
                </h3>
              </div>

              {result.recommendations.length === 0 ? (
                <div className="rounded-xl border border-slate-200 p-5">
                  <div className="flex items-start gap-3">
                    <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-slate-600" />

                    <div>
                      <p className="font-semibold text-slate-900">
                        No additional recommendations
                      </p>

                      <p className="mt-1 text-sm leading-6 text-slate-500">
                        No deterministic engineering recommendation
                        was generated from the supplied equipment
                        configuration and sizing basis.
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {result.recommendations.map(
                    (recommendation, index) => (
                      <div
                        key={`${recommendation.recommendation_code}-${index}`}
                        className="rounded-xl border border-slate-200 p-5"
                      >
                        <div className="flex flex-wrap items-start justify-between gap-3">
                          <div>
                            <p className="font-semibold text-slate-950">
                              {recommendation.message}
                            </p>

                            <p className="mt-1 text-xs font-medium text-slate-500">
                              {recommendation.recommendation_code}
                              {" · "}
                              {recommendation.equipment_code}
                            </p>
                          </div>

                          <Badge
                            variant={severityVariant(
                              recommendation.severity,
                            )}
                          >
                            {enumLabel(
                              recommendation.severity,
                            )}
                          </Badge>
                        </div>

                        <div className="mt-4 rounded-lg bg-slate-50 p-4">
                          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                            Engineering rationale
                          </p>

                          <p className="mt-2 text-sm leading-6 text-slate-700">
                            {recommendation.rationale}
                          </p>
                        </div>
                      </div>
                    ),
                  )}
                </div>
              )}
            </section>

            {result.notes && (
              <section className="rounded-xl border border-slate-200 p-5">
                <p className="text-sm font-semibold text-slate-900">
                  Analysis Notes
                </p>

                <p className="mt-2 text-sm leading-6 text-slate-600">
                  {result.notes}
                </p>
              </section>
            )}

            <div className="rounded-lg border border-dashed border-slate-300 p-4">
              <p className="text-sm font-medium text-slate-800">
                Engineering traceability
              </p>

              <p className="mt-1 text-xs leading-5 text-slate-500">
                Results are generated from the supplied engineering
                inputs and deterministic calculation rules. Equipment
                adequacy and recommendations are engineering guidance,
                not a manufacturer-selection or formal
                standards-compliance declaration.
              </p>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
