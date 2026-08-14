import {
  BarChart3,
  Gauge,
  Zap,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import type {
  PerformanceFormState,
} from "../performanceFormState";

type ReferenceBenchmarkSectionProps = {
  state: PerformanceFormState;
  onChange: (
    changes: Partial<PerformanceFormState>,
  ) => void;
};

export function ReferenceBenchmarkSection({
  state,
  onChange,
}: ReferenceBenchmarkSectionProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <BarChart3 className="size-5" />
          </div>

          <div>
            <CardTitle>
              Rated & Reference Performance
            </CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Enter available rated or verified reference data to evaluate
              capacity utilization, power utilization, and measured specific
              power deviation.
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          <div className="space-y-2">
            <Label htmlFor="performance-rated-capacity">
              Rated Capacity
            </Label>

            <div className="relative">
              <Gauge className="absolute left-3 top-2.5 size-4 text-slate-400" />

              <Input
                id="performance-rated-capacity"
                type="number"
                min="0"
                step="any"
                className="pl-9"
                value={state.ratedCapacityNm3PerHr}
                placeholder="Example: 600"
                onChange={(event) =>
                  onChange({
                    ratedCapacityNm3PerHr:
                      event.target.value,
                  })
                }
              />
            </div>

            <p className="text-xs text-slate-500">
              Nm³/h
            </p>

            <p className="text-xs leading-5 text-slate-500">
              Optional reference used to calculate average and peak capacity
              utilization.
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="performance-rated-power">
              Rated Power
            </Label>

            <div className="relative">
              <Zap className="absolute left-3 top-2.5 size-4 text-slate-400" />

              <Input
                id="performance-rated-power"
                type="number"
                min="0"
                step="any"
                className="pl-9"
                value={state.ratedPowerKw}
                placeholder="Example: 100"
                onChange={(event) =>
                  onChange({
                    ratedPowerKw:
                      event.target.value,
                  })
                }
              />
            </div>

            <p className="text-xs text-slate-500">
              kW
            </p>

            <p className="text-xs leading-5 text-slate-500">
              Optional reference used to evaluate average measured power
              utilization.
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="performance-reference-specific-power">
              Reference Specific Power
            </Label>

            <Input
              id="performance-reference-specific-power"
              type="number"
              min="0"
              step="any"
              value={
                state.referenceSpecificPowerKwPerNm3PerMin
              }
              placeholder="Example: 10.0"
              onChange={(event) =>
                onChange({
                  referenceSpecificPowerKwPerNm3PerMin:
                    event.target.value,
                })
              }
            />

            <p className="text-xs text-slate-500">
              kW/(Nm³/min)
            </p>

            <p className="text-xs leading-5 text-slate-500">
              Optional verified baseline for comparing measured specific
              power. Use a reference derived under comparable operating
              conditions.
            </p>
          </div>
        </div>

        <div className="rounded-lg border border-dashed border-slate-300 p-4">
          <p className="text-sm font-medium text-slate-800">
            Reference-data interpretation
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            Rated and reference values are engineering comparison inputs.
            They do not by themselves establish equipment acceptance,
            guaranteed performance, or standards compliance.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
