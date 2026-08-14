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
  airQualityClassOptions,
  dryerTypeOptions,
} from "../greenfieldOptions";
import type {
  AirQualityClass,
  AirTreatmentInput,
  DryerType,
} from "../greenfieldTypes";

type AirTreatmentSectionProps = {
  treatment: AirTreatmentInput | null;
  onChange: (treatment: AirTreatmentInput | null) => void;
};

function createTreatment(): AirTreatmentInput {
  return {
    required_delivered_flow_nm3_per_hr: "",
    required_air_quality: "GENERAL_PLANT_AIR",
    dryer_type: "REFRIGERATED",
    dryer_correction_factor: "1",
    dryer_purge_fraction: "0",
    prefilter_pressure_drop_bar: "0",
    afterfilter_pressure_drop_bar: "0",
    dryer_pressure_drop_bar: "0",
    treatment_capacity_margin_fraction: "0.10",
  };
}

export function AirTreatmentSection({
  treatment,
  onChange,
}: AirTreatmentSectionProps) {
  if (!treatment) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-start gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
              <Droplets className="size-5" />
            </div>

            <div>
              <CardTitle>
                Air Treatment & Dryer Engineering
              </CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Add treatment engineering when the Greenfield design requires
                dryer capacity, purge allowance, treatment margin, air-quality
                classification, and treatment pressure-drop evaluation.
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          <Button
            type="button"
            variant="outline"
            onClick={() => onChange(createTreatment())}
          >
            <Plus className="size-4" />
            Add Air Treatment
          </Button>
        </CardContent>
      </Card>
    );
  }

  function updateTreatment(
    changes: Partial<AirTreatmentInput>,
  ): void {
    onChange({
      ...treatment!,
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
                Air Treatment & Dryer Engineering
              </CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Establish delivered-air quality, dryer technology,
                correction and purge factors, treatment capacity margin,
                and treatment-system pressure losses.
              </CardDescription>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            onClick={() => onChange(null)}
          >
            Remove Treatment Evaluation
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <section>
          <h3 className="mb-4 text-sm font-semibold text-slate-900">
            Treatment Duty
          </h3>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div className="space-y-2">
              <Label htmlFor="treatment-flow">
                Required Delivered Flow
              </Label>

              <div className="relative">
                <Input
                  id="treatment-flow"
                  type="number"
                  min="0"
                  step="any"
                  value={
                    treatment.required_delivered_flow_nm3_per_hr
                  }
                  onChange={(event) =>
                    updateTreatment({
                      required_delivered_flow_nm3_per_hr:
                        event.target.value,
                    })
                  }
                  className="pr-16"
                />

                <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-xs text-slate-500">
                  Nm³/h
                </span>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="treatment-air-quality">
                Required Air Quality
              </Label>

              <select
                id="treatment-air-quality"
                value={treatment.required_air_quality}
                onChange={(event) =>
                  updateTreatment({
                    required_air_quality:
                      event.target.value as AirQualityClass,
                  })
                }
                className="h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
              >
                {airQualityClassOptions.map((option) => (
                  <option
                    key={option.value}
                    value={option.value}
                  >
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="dryer-type">
                Dryer Technology
              </Label>

              <select
                id="dryer-type"
                value={treatment.dryer_type}
                onChange={(event) =>
                  updateTreatment({
                    dryer_type:
                      event.target.value as DryerType,
                  })
                }
                className="h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
              >
                {dryerTypeOptions.map((option) => (
                  <option
                    key={option.value}
                    value={option.value}
                  >
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="treatment-margin">
                Capacity Margin
              </Label>

              <Input
                id="treatment-margin"
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={
                  treatment.treatment_capacity_margin_fraction ??
                  "0"
                }
                onChange={(event) =>
                  updateTreatment({
                    treatment_capacity_margin_fraction:
                      event.target.value,
                  })
                }
              />

              <p className="text-xs text-slate-500">
                Fraction of calculated treatment capacity
              </p>
            </div>
          </div>
        </section>

        <section className="border-t border-slate-100 pt-6">
          <h3 className="mb-4 text-sm font-semibold text-slate-900">
            Dryer Correction & Purge
          </h3>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="dryer-correction-factor">
                Dryer Correction Factor
              </Label>

              <Input
                id="dryer-correction-factor"
                type="number"
                min="0.0001"
                step="any"
                value={
                  treatment.dryer_correction_factor ?? "1"
                }
                onChange={(event) =>
                  updateTreatment({
                    dryer_correction_factor:
                      event.target.value,
                  })
                }
              />

              <p className="text-xs leading-5 text-slate-500">
                Correction factor applied to required treatment
                capacity for actual operating conditions.
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="dryer-purge-fraction">
                Dryer Purge Fraction
              </Label>

              <Input
                id="dryer-purge-fraction"
                type="number"
                min="0"
                max="0.999"
                step="0.01"
                value={
                  treatment.dryer_purge_fraction ?? "0"
                }
                onChange={(event) =>
                  updateTreatment({
                    dryer_purge_fraction:
                      event.target.value,
                  })
                }
              />

              <p className="text-xs leading-5 text-slate-500">
                Fraction of compressed air consumed by dryer purge.
              </p>
            </div>
          </div>
        </section>

        <section className="border-t border-slate-100 pt-6">
          <h3 className="mb-4 text-sm font-semibold text-slate-900">
            Treatment Pressure Losses
          </h3>

          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="prefilter-pressure-drop">
                Prefilter Pressure Drop
              </Label>

              <Input
                id="prefilter-pressure-drop"
                type="number"
                min="0"
                step="any"
                value={
                  treatment.prefilter_pressure_drop_bar ?? "0"
                }
                onChange={(event) =>
                  updateTreatment({
                    prefilter_pressure_drop_bar:
                      event.target.value,
                  })
                }
              />

              <p className="text-xs text-slate-500">
                bar
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="dryer-pressure-drop">
                Dryer Pressure Drop
              </Label>

              <Input
                id="dryer-pressure-drop"
                type="number"
                min="0"
                step="any"
                value={
                  treatment.dryer_pressure_drop_bar ?? "0"
                }
                onChange={(event) =>
                  updateTreatment({
                    dryer_pressure_drop_bar:
                      event.target.value,
                  })
                }
              />

              <p className="text-xs text-slate-500">
                bar
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="afterfilter-pressure-drop">
                Afterfilter Pressure Drop
              </Label>

              <Input
                id="afterfilter-pressure-drop"
                type="number"
                min="0"
                step="any"
                value={
                  treatment.afterfilter_pressure_drop_bar ?? "0"
                }
                onChange={(event) =>
                  updateTreatment({
                    afterfilter_pressure_drop_bar:
                      event.target.value,
                  })
                }
              />

              <p className="text-xs text-slate-500">
                bar
              </p>
            </div>
          </div>
        </section>

        <div className="rounded-lg border border-dashed border-slate-300 p-4">
          <p className="text-sm font-medium text-slate-800">
            Current engineering scope
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            This stage evaluates treatment capacity, dryer purge,
            correction factor, capacity margin, air-quality requirement,
            and treatment pressure loss. Detailed filter element selection
            and advanced dew-point design will remain separate engineering
            capabilities.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
