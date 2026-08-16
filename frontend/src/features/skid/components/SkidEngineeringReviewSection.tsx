import {
  AlertTriangle,
  CheckCircle2,
  CircleDashed,
  Gauge,
  ShieldCheck,
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

import type { AirSkidAssessmentResponse } from "../skidTypes";

type SkidEngineeringReviewSectionProps = {
  result: AirSkidAssessmentResponse | null;
  isPending: boolean;
  errorMessage: string | null;
};

type MetricProps = {
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

function StatusCard({
  label,
  passed,
  description,
}: {
  label: string;
  passed: boolean;
  description: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-slate-900">
            {label}
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            {description}
          </p>
        </div>

        <Badge variant={passed ? "default" : "destructive"}>
          {passed ? "Adequate" : "Review Required"}
        </Badge>
      </div>
    </div>
  );
}

export function SkidEngineeringReviewSection({
  result,
  isPending,
  errorMessage,
}: SkidEngineeringReviewSectionProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <Gauge className="size-5" />
          </div>

          <div>
            <CardTitle>
              Skid Engineering Review
            </CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Review skid capacity, pressure rating, component
              pressure loss, receiver provisions, instrumentation,
              controls, and overall engineering adequacy.
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
                  Skid assessment failed
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
              Skid assessment not yet calculated
            </p>

            <p className="mx-auto mt-1 max-w-2xl text-sm leading-6 text-slate-500">
              Complete the skid study basis, component register,
              and configuration before running the engineering
              assessment.
            </p>
          </div>
        )}

        {!isPending && !errorMessage && result && (
          <>
            <section>
              <div className="mb-4 flex items-center gap-2">
                <Gauge className="size-5 text-slate-600" />

                <h3 className="font-semibold text-slate-950">
                  Design & Capacity Summary
                </h3>
              </div>

              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <Metric
                  label="Design Flow"
                  value={formatDecimal(
                    result.design_flow_nm3_per_hr,
                  )}
                  unit="Nm³/h"
                />

                <Metric
                  label="Minimum Component Flow"
                  value={formatDecimal(
                    result.minimum_component_flow_capacity_nm3_per_hr,
                  )}
                  unit="Nm³/h"
                />

                <Metric
                  label="Design Pressure"
                  value={formatDecimal(
                    result.design_pressure_bar_g,
                  )}
                  unit="bar(g)"
                />

                <Metric
                  label="Minimum Pressure Rating"
                  value={formatDecimal(
                    result.minimum_component_pressure_rating_bar_g,
                  )}
                  unit="bar(g)"
                />
              </div>

              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                <Metric
                  label="Total Component Count"
                  value={result.total_component_count.toLocaleString(
                    "en-IN",
                  )}
                  unit="installed items"
                />

                <Metric
                  label="Total Skid Pressure Drop"
                  value={formatDecimal(
                    result.total_pressure_drop_bar,
                  )}
                  unit="bar"
                />
              </div>
            </section>

            <section>
              <div className="mb-4 flex items-center gap-2">
                <ShieldCheck className="size-5 text-slate-600" />

                <h3 className="font-semibold text-slate-950">
                  Capacity & Receiver Adequacy
                </h3>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <StatusCard
                  label="Flow Capacity"
                  passed={result.flow_capacity_is_adequate}
                  description="Minimum recorded flow capacity is compared with skid design flow."
                />

                <StatusCard
                  label="Pressure Rating"
                  passed={result.pressure_rating_is_adequate}
                  description="Minimum recorded pressure rating is compared with skid design pressure."
                />

                <StatusCard
                  label="Wet Receiver"
                  passed={result.has_wet_receiver}
                  description="A wet receiver must be selected and present in the component register."
                />

                <StatusCard
                  label="Dry Receiver"
                  passed={result.has_dry_receiver}
                  description="A dry receiver must be selected and present in the component register."
                />
              </div>
            </section>

            <section>
              <div className="mb-4 flex items-center gap-2">
                <CheckCircle2 className="size-5 text-slate-600" />

                <h3 className="font-semibold text-slate-950">
                  Instrumentation & Control
                </h3>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <StatusCard
                  label="Flow Metering"
                  passed={result.has_flow_metering}
                  description="Flow metering is enabled and represented by a registered flow-meter component."
                />

                <StatusCard
                  label="Pressure Monitoring"
                  passed={result.has_pressure_monitoring}
                  description="Pressure monitoring is enabled and represented by a registered pressure sensor."
                />

                <StatusCard
                  label="Dew-Point Monitoring"
                  passed={result.has_dew_point_monitoring}
                  description="Dew-point monitoring is enabled and represented by a registered dew-point sensor."
                />

                <StatusCard
                  label="Master Control"
                  passed={result.master_control_enabled}
                  description="Master control is enabled and represented by a registered master-controller component."
                />
              </div>
            </section>

            <section>
              <div className="mb-4 flex items-center gap-2">
                <ShieldCheck className="size-5 text-slate-600" />

                <h3 className="font-semibold text-slate-950">
                  Overall Engineering Assessment
                </h3>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <StatusCard
                  label="Instrumentation Completeness"
                  passed={result.instrumentation_is_complete}
                  description="Flow, pressure, and dew-point monitoring must all be confirmed by the assessment."
                />

                <StatusCard
                  label="Overall Skid Adequacy"
                  passed={result.skid_is_adequate}
                  description="KES assessment combines capacity, pressure rating, instrumentation, and receiver provisions."
                />
              </div>

              <div className="mt-4 rounded-xl border border-dashed border-slate-300 p-4">
                <p className="text-sm font-semibold text-slate-900">
                  Assessment interpretation
                </p>

                <p className="mt-1 text-xs leading-5 text-slate-500">
                  This result is deterministic engineering guidance
                  based on the entered design basis and component
                  register. Master control status is reported separately
                  and is not included in the current overall skid
                  adequacy rule.
                </p>
              </div>
            </section>
          </>
        )}
      </CardContent>
    </Card>
  );
}
