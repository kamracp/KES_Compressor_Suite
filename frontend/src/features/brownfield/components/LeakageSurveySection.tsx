import {
  Droplets,
  Plus,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import {
  createBrownfieldLeakageSurvey,
} from "../brownfieldFormState";
import type {
  LeakageSurveyInput,
} from "../brownfieldTypes";

type LeakageSurveySectionProps = {
  leakageSummary: LeakageSurveyInput | null;
  onChange: (leakageSummary: LeakageSurveyInput | null) => void;
};

export function LeakageSurveySection({
  leakageSummary,
  onChange,
}: LeakageSurveySectionProps) {
  if (!leakageSummary) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-start gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
              <Droplets className="size-5" />
            </div>

            <div>
              <CardTitle>
                Leakage Survey
              </CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Add measured or estimated compressed-air leakage when a
                shutdown test, flow-meter study, load/unload method, or other
                plant leakage survey is available.
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          <Button
            type="button"
            variant="outline"
            onClick={() => onChange(createBrownfieldLeakageSurvey())}
          >
            <Plus className="size-4" />
            Add Leakage Survey
          </Button>
        </CardContent>
      </Card>
    );
  }

  function updateLeakage(
    changes: Partial<LeakageSurveyInput>,
  ): void {
    onChange({
      ...leakageSummary!,
      ...changes,
    });
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex items-start gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
              <Droplets className="size-5" />
            </div>

            <div>
              <CardTitle>
                Leakage Survey
              </CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Quantify measured leakage and define the expected recoverable
                fraction for Brownfield energy opportunity analysis.
              </CardDescription>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            onClick={() => onChange(null)}
          >
            Remove Leakage Survey
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <section>
          <h3 className="mb-4 text-sm font-semibold text-slate-900">
            Leakage Measurement
          </h3>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="brownfield-leakage-flow">
                Measured Leakage Flow
              </Label>

              <Input
                id="brownfield-leakage-flow"
                type="number"
                min="0"
                step="any"
                value={
                  leakageSummary.measured_leakage_flow_nm3_per_hr
                }
                onChange={(event) =>
                  updateLeakage({
                    measured_leakage_flow_nm3_per_hr:
                      event.target.value,
                  })
                }
              />

              <p className="text-xs text-slate-500">
                Nm³/h
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="brownfield-leakage-method">
                Survey Method
              </Label>

              <Input
                id="brownfield-leakage-method"
                value={leakageSummary.survey_method}
                placeholder="Example: Shutdown flow-meter test"
                onChange={(event) =>
                  updateLeakage({
                    survey_method: event.target.value,
                  })
                }
              />

              <p className="text-xs leading-5 text-slate-500">
                Record the actual measurement or estimation method used.
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="brownfield-repair-fraction">
                Estimated Repair Fraction
              </Label>

              <Input
                id="brownfield-repair-fraction"
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={
                  leakageSummary.estimated_repair_fraction
                }
                onChange={(event) =>
                  updateLeakage({
                    estimated_repair_fraction:
                      event.target.value,
                  })
                }
              />

              <p className="text-xs leading-5 text-slate-500">
                Fraction of measured leakage expected to be recoverable.
              </p>
            </div>
          </div>
        </section>

        <section className="border-t border-slate-100 pt-6">
          <div className="space-y-2">
            <Label htmlFor="brownfield-leakage-notes">
              Survey Notes
            </Label>

            <Input
              id="brownfield-leakage-notes"
              value={leakageSummary.survey_notes ?? ""}
              placeholder="Survey condition, production status, instrument basis..."
              onChange={(event) =>
                updateLeakage({
                  survey_notes:
                    event.target.value || null,
                })
              }
            />
          </div>
        </section>

        <div className="rounded-lg border border-dashed border-slate-300 p-4">
          <p className="text-sm font-medium text-slate-800">
            Current leakage-analysis scope
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            The current Brownfield engine compares measured leakage flow with
            average system demand. When leakage is significant, it estimates
            recoverable power, annual energy saving, and annual electricity
            cost saving using measured system specific power and the expected
            repair fraction.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
