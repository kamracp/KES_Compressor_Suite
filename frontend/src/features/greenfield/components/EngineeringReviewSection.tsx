import {
  AlertTriangle,
  CheckCircle2,
  CircleDashed,
  Gauge,
  ServerCog,
  Zap,
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

import type { GreenfieldSystemDesignResponse } from "../greenfieldTypes";

type EngineeringReviewSectionProps = {
  result: GreenfieldSystemDesignResponse | null;
  isPending: boolean;
  errorMessage: string | null;
};

type ResultMetricProps = {
  label: string;
  value: string;
  unit?: string;
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

function ResultMetric({
  label,
  value,
  unit,
}: ResultMetricProps) {
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

function adequacyLabel(
  value: boolean | null,
): string {
  if (value === null) {
    return "Not evaluated";
  }

  return value ? "Adequate" : "Not adequate";
}

export function EngineeringReviewSection({
  result,
  isPending,
  errorMessage,
}: EngineeringReviewSectionProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <ServerCog className="size-5" />
          </div>

          <div>
            <CardTitle>
              Engineering Review
            </CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Review calculated system duty, pressure requirement,
              capacity adequacy, storage, treatment, energy performance,
              and engineering messages from the Greenfield design engine.
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
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
                  Greenfield calculation failed
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
            <CircleDashed className="mx-auto mb-3 size-7 text-slate-400" />

            <p className="text-sm font-semibold text-slate-800">
              Engineering calculation not yet executed
            </p>

            <p className="mx-auto mt-2 max-w-xl text-xs leading-5 text-slate-500">
              Complete the applicable Greenfield design inputs and run the
              system design calculation to generate engineering results.
            </p>
          </div>
        )}

        {!isPending && !errorMessage && result && (
          <>
            <section className="flex flex-col gap-4 rounded-xl border border-slate-200 bg-slate-50 p-5 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                  Overall Design Status
                </p>

                <p className="mt-2 text-lg font-semibold text-slate-950">
                  {result.system_design_is_feasible
                    ? "Greenfield system design is feasible"
                    : "Greenfield system design requires engineering review"}
                </p>
              </div>

              <Badge
                variant={
                  result.system_design_is_feasible
                    ? "secondary"
                    : "destructive"
                }
                className="self-start sm:self-auto"
              >
                {result.system_design_is_feasible
                  ? "FEASIBLE"
                  : "REVIEW REQUIRED"}
              </Badge>
            </section>

            <section>
              <div className="mb-4 flex items-center gap-2">
                <Gauge className="size-4 text-slate-500" />

                <h3 className="text-sm font-semibold text-slate-900">
                  System Duty
                </h3>
              </div>

              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <ResultMetric
                  label="Required Design Flow"
                  value={formatDecimal(
                    result.required_design_flow_nm3_per_hr,
                  )}
                  unit="Nm³/h"
                />

                <ResultMetric
                  label="Required Compressor Discharge Pressure"
                  value={formatDecimal(
                    result.required_compressor_discharge_pressure_bar_g,
                    3,
                  )}
                  unit="bar(g)"
                />

                <ResultMetric
                  label="Simultaneous Demand"
                  value={formatDecimal(
                    result.simultaneous_demand_nm3_per_hr,
                  )}
                  unit="Nm³/h"
                />

                <ResultMetric
                  label="Peak Profile Demand"
                  value={formatDecimal(
                    result.peak_profile_demand_nm3_per_hr,
                  )}
                  unit="Nm³/h"
                />
              </div>
            </section>

            <section>
              <h3 className="mb-4 text-sm font-semibold text-slate-900">
                Design Allowances
              </h3>

              <div className="grid gap-4 sm:grid-cols-2">
                <ResultMetric
                  label="Leakage Allowance"
                  value={formatDecimal(
                    result.leakage_allowance_nm3_per_hr,
                  )}
                  unit="Nm³/h"
                />

                <ResultMetric
                  label="Future Expansion Allowance"
                  value={formatDecimal(
                    result.future_expansion_allowance_nm3_per_hr,
                  )}
                  unit="Nm³/h"
                />
              </div>
            </section>

            <section>
              <h3 className="mb-4 text-sm font-semibold text-slate-900">
                Equipment & System Evaluation
              </h3>

              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <ResultMetric
                  label="Treatment Capacity"
                  value={formatDecimal(
                    result.treatment_capacity_nm3_per_hr,
                  )}
                  unit={
                    result.treatment_capacity_nm3_per_hr
                      ? "Nm³/h"
                      : undefined
                  }
                />

                <ResultMetric
                  label="Available Station Capacity"
                  value={formatDecimal(
                    result.station_available_capacity_nm3_per_hr,
                  )}
                  unit={
                    result.station_available_capacity_nm3_per_hr
                      ? "Nm³/h"
                      : undefined
                  }
                />

                <ResultMetric
                  label="Station Capacity"
                  value={adequacyLabel(
                    result.station_capacity_is_adequate,
                  )}
                />

                <ResultMetric
                  label="Receiver Volume"
                  value={formatDecimal(
                    result.receiver_volume_m3,
                    3,
                  )}
                  unit={
                    result.receiver_volume_m3
                      ? "m³"
                      : undefined
                  }
                />
              </div>

              {result.receiver_storage_required !== null && (
                <div className="mt-4">
                  <Badge
                    variant={
                      result.receiver_storage_required
                        ? "outline"
                        : "secondary"
                    }
                  >
                    {result.receiver_storage_required
                      ? "Receiver storage required"
                      : "Additional receiver storage not required"}
                  </Badge>
                </div>
              )}
            </section>

            <section>
              <div className="mb-4 flex items-center gap-2">
                <Zap className="size-4 text-slate-500" />

                <h3 className="text-sm font-semibold text-slate-900">
                  Energy & Operating Cost
                </h3>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <ResultMetric
                  label="Annual Energy Consumption"
                  value={formatDecimal(
                    result.annual_energy_kwh,
                    0,
                  )}
                  unit={
                    result.annual_energy_kwh
                      ? "kWh/year"
                      : undefined
                  }
                />

                <ResultMetric
                  label="Annual Energy Cost"
                  value={formatDecimal(
                    result.annual_energy_cost,
                    2,
                  )}
                  unit={
                    result.annual_energy_cost
                      ? "currency units/year"
                      : undefined
                  }
                />
              </div>
            </section>

            <section>
              <div className="mb-4 flex items-center gap-2">
                <CheckCircle2 className="size-4 text-slate-500" />

                <h3 className="text-sm font-semibold text-slate-900">
                  Engineering Messages
                </h3>
              </div>

              {result.engineering_messages.length === 0 ? (
                <p className="rounded-lg border border-dashed border-slate-300 p-4 text-sm text-slate-500">
                  No additional engineering messages were returned.
                </p>
              ) : (
                <div className="space-y-3">
                  {result.engineering_messages.map(
                    (message, index) => (
                      <div
                        key={`${message}-${index}`}
                        className="flex items-start gap-3 rounded-lg border border-slate-200 p-4"
                      >
                        <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-slate-500" />

                        <p className="text-sm leading-6 text-slate-700">
                          {message}
                        </p>
                      </div>
                    ),
                  )}
                </div>
              )}
            </section>
          </>
        )}
      </CardContent>
    </Card>
  );
}
