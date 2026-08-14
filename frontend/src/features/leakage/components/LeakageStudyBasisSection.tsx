import { ClipboardCheck } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import type { LeakageFormState } from "../leakageFormState";

type LeakageStudyBasisSectionProps = {
  state: LeakageFormState;
  onChange: (changes: Partial<LeakageFormState>) => void;
};

export function LeakageStudyBasisSection({
  state,
  onChange,
}: LeakageStudyBasisSectionProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <ClipboardCheck className="size-5" />
          </div>

          <div>
            <CardTitle>Leakage Study Basis</CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Define the leakage-management study reference,
              representative plant demand, and engineering notes
              before registering individual compressed-air leaks.
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <div className="grid gap-5 md:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="leakage-analysis-code">
              Analysis Code
            </Label>

            <Input
              id="leakage-analysis-code"
              value={state.analysisCode}
              placeholder="Example: LEAK-2026-001"
              onChange={(event) =>
                onChange({
                  analysisCode: event.target.value,
                })
              }
            />

            <p className="text-xs leading-5 text-slate-500">
              Unique engineering reference for this leakage study.
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="average-system-demand">
              Average System Demand
            </Label>

            <Input
              id="average-system-demand"
              type="number"
              min="0"
              step="any"
              value={state.averageSystemDemandNm3PerHr}
              placeholder="Example: 5000"
              onChange={(event) =>
                onChange({
                  averageSystemDemandNm3PerHr:
                    event.target.value,
                })
              }
            />

            <p className="text-xs leading-5 text-slate-500">
              Nm³/h — optional representative plant demand used
              to calculate leakage as a fraction of system demand.
            </p>
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="leakage-study-notes">
            Study Notes
          </Label>

          <Input
            id="leakage-study-notes"
            value={state.notes}
            placeholder="Survey scope, operating condition, measurement basis..."
            onChange={(event) =>
              onChange({
                notes: event.target.value,
              })
            }
          />

          <p className="text-xs leading-5 text-slate-500">
            Record the survey boundary, production condition,
            instrumentation basis, or other engineering context.
          </p>
        </div>

        <div className="rounded-lg border border-dashed border-slate-300 p-4">
          <p className="text-sm font-medium text-slate-800">
            Engineering basis
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            Average system demand is optional. When supplied, the
            analysis will express total registered leakage relative
            to representative compressed-air demand. This is an
            engineering indicator and not a standards-compliance
            declaration.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
