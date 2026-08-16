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

import type { AlliedFormState } from "../alliedFormState";

type AlliedStudyBasisSectionProps = {
  state: AlliedFormState;
  onChange: (changes: Partial<AlliedFormState>) => void;
};

export function AlliedStudyBasisSection({
  state,
  onChange,
}: AlliedStudyBasisSectionProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <ClipboardCheck className="size-5" />
          </div>

          <div>
            <CardTitle>Allied Equipment Study Basis</CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Define the engineering reference and study context for
              compressed-air receivers, treatment equipment, aftercoolers,
              moisture separation, filters, and condensate management.
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="allied-analysis-code">
            Analysis Code
          </Label>

          <Input
            id="allied-analysis-code"
            value={state.analysisCode}
            placeholder="Example: ALLIED-2026-001"
            onChange={(event) =>
              onChange({
                analysisCode: event.target.value,
              })
            }
          />

          <p className="text-xs leading-5 text-slate-500">
            Unique engineering reference for this allied-equipment analysis.
          </p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="allied-study-notes">
            Study Notes
          </Label>

          <Input
            id="allied-study-notes"
            value={state.notes}
            placeholder="System boundary, operating condition, equipment basis..."
            onChange={(event) =>
              onChange({
                notes: event.target.value,
              })
            }
          />

          <p className="text-xs leading-5 text-slate-500">
            Record the operating basis, equipment selection context,
            engineering assumptions, or relevant project notes.
          </p>
        </div>

        <div className="rounded-lg border border-dashed border-slate-300 p-4">
          <p className="text-sm font-medium text-slate-800">
            Engineering basis
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            This workflow evaluates required versus selected equipment
            capacity, pressure-drop contribution, redundancy arrangements,
            and deterministic engineering recommendations. It does not
            constitute a manufacturer selection or standards-compliance
            declaration.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
