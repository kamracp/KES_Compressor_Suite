import {
  Gauge,
  TrendingDown,
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

type PressureOptimizationSectionProps = {
  state: PerformanceFormState;
  onChange: (
    changes: Partial<PerformanceFormState>,
  ) => void;
};

export function PressureOptimizationSection({
  state,
  onChange,
}: PressureOptimizationSectionProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <TrendingDown className="size-5" />
          </div>

          <div>
            <CardTitle>
              Pressure Optimization Scenario
            </CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Evaluate the estimated energy impact of a user-defined lower
              compressor discharge pressure. The entered pressure is a study
              scenario, not an automatically recommended operating setpoint.
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <div className="grid gap-5 md:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="performance-optimized-pressure">
              Optimized Discharge Pressure
            </Label>

            <div className="relative">
              <Gauge className="absolute left-3 top-2.5 size-4 text-slate-400" />

              <Input
                id="performance-optimized-pressure"
                type="number"
                min="0"
                step="any"
                className="pl-9"
                value={state.optimizedDischargePressureBarG}
                placeholder="Example: 6.0"
                onChange={(event) =>
                  onChange({
                    optimizedDischargePressureBarG:
                      event.target.value,
                  })
                }
              />
            </div>

            <p className="text-xs text-slate-500">
              bar(g)
            </p>

            <p className="text-xs leading-5 text-slate-500">
              Leave blank when no pressure-reduction scenario is to be
              evaluated.
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="performance-pressure-penalty">
              Power Penalty Fraction per Bar
            </Label>

            <Input
              id="performance-pressure-penalty"
              type="number"
              min="0"
              max="1"
              step="any"
              value={state.powerPenaltyFractionPerBar}
              placeholder="Example: 0.07"
              onChange={(event) =>
                onChange({
                  powerPenaltyFractionPerBar:
                    event.target.value,
                })
              }
            />

            <p className="text-xs text-slate-500">
              Fraction / bar
            </p>

            <p className="text-xs leading-5 text-slate-500">
              The default value of 0.07 represents a 7% power relationship per
              bar for scenario calculation. Replace it with the engineering
              basis applicable to the assessed system when available.
            </p>
          </div>
        </div>

        <div className="rounded-lg border border-dashed border-slate-300 p-4">
          <p className="text-sm font-medium text-slate-800">
            Engineering safeguard
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            Any pressure reduction must be checked against point-of-use
            pressure requirements, distribution losses, treatment pressure
            drop, control stability, and production reliability before an
            operating change is implemented.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
