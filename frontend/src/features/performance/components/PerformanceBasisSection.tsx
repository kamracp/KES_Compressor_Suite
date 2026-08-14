import {
  Clock,
  FileText,
  IndianRupee,
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

type PerformanceBasisSectionProps = {
  state: PerformanceFormState;
  onChange: (
    changes: Partial<PerformanceFormState>,
  ) => void;
};

export function PerformanceBasisSection({
  state,
  onChange,
}: PerformanceBasisSectionProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <FileText className="size-5" />
          </div>

          <div>
            <CardTitle>
              Performance Analysis Basis
            </CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Define the analysis reference, annual operating basis,
              electricity tariff, and engineering notes used to annualize the
              measured compressed-air performance.
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          <div className="space-y-2">
            <Label htmlFor="performance-analysis-code">
              Analysis Code
            </Label>

            <Input
              id="performance-analysis-code"
              value={state.analysisCode}
              placeholder="Example: PERF-2026-001"
              onChange={(event) =>
                onChange({
                  analysisCode: event.target.value,
                })
              }
            />

            <p className="text-xs leading-5 text-slate-500">
              Unique engineering reference for this performance study.
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="performance-annual-hours">
              Annual Operating Hours
            </Label>

            <div className="relative">
              <Clock className="absolute left-3 top-2.5 size-4 text-slate-400" />

              <Input
                id="performance-annual-hours"
                type="number"
                min="0"
                step="any"
                className="pl-9"
                value={state.annualOperatingHours}
                placeholder="Example: 8000"
                onChange={(event) =>
                  onChange({
                    annualOperatingHours:
                      event.target.value,
                  })
                }
              />
            </div>

            <p className="text-xs leading-5 text-slate-500">
              Used to extrapolate measured average power into annual energy
              consumption.
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="performance-electricity-tariff">
              Electricity Tariff
            </Label>

            <div className="relative">
              <IndianRupee className="absolute left-3 top-2.5 size-4 text-slate-400" />

              <Input
                id="performance-electricity-tariff"
                type="number"
                min="0"
                step="any"
                className="pl-9"
                value={state.electricityTariffPerKwh}
                placeholder="Example: 8.00"
                onChange={(event) =>
                  onChange({
                    electricityTariffPerKwh:
                      event.target.value,
                  })
                }
              />
            </div>

            <p className="text-xs leading-5 text-slate-500">
              Currency per kWh. Current local workflow uses the entered plant
              tariff without applying escalation.
            </p>
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="performance-notes">
            Engineering Notes
          </Label>

          <textarea
            id="performance-notes"
            rows={4}
            value={state.notes}
            placeholder="Measurement method, operating conditions, production context, instrument references, exclusions..."
            className="flex min-h-24 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm shadow-xs outline-none transition-colors placeholder:text-slate-400 focus-visible:border-slate-400 focus-visible:ring-2 focus-visible:ring-slate-200"
            onChange={(event) =>
              onChange({
                notes: event.target.value,
              })
            }
          />

          <p className="text-xs leading-5 text-slate-500">
            Record assumptions and measurement context required to interpret
            the calculated performance indicators.
          </p>
        </div>

        <div className="rounded-lg border border-dashed border-slate-300 p-4">
          <p className="text-sm font-medium text-slate-800">
            Annualization basis
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            Annual energy and cost are calculated by extrapolating the
            arithmetic average measured power across the entered annual
            operating hours. Measurement points should therefore represent the
            intended operating baseline.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
