import { Droplets, Plus } from "lucide-react";

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
} from "../../greenfield/greenfieldOptions";
import { createTreatmentConfiguration } from "../alliedFormState";
import type {
  AirQualityClass,
  AirTreatmentInput,
  AlliedRedundancyPhilosophy,
  DryerType,
  TreatmentConfigurationInput,
} from "../alliedTypes";

type TreatmentEngineeringSectionProps = {
  treatment: TreatmentConfigurationInput | null;
  onChange: (
    treatment: TreatmentConfigurationInput | null,
  ) => void;
};

const redundancyOptions: {
  value: AlliedRedundancyPhilosophy;
  label: string;
}[] = [
  { value: "NONE", label: "None" },
  { value: "DUTY_STANDBY", label: "Duty / Standby" },
  { value: "N_PLUS_1", label: "N + 1" },
  { value: "MULTIPLE_DUTY", label: "Multiple Duty" },
];

export function TreatmentEngineeringSection({
  treatment,
  onChange,
}: TreatmentEngineeringSectionProps) {
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
                Evaluate dryer and treatment capacity, purge
                allowance, operating correction factors, pressure
                losses, and the selected treatment arrangement.
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          <Button
            type="button"
            variant="outline"
            onClick={() =>
              onChange(createTreatmentConfiguration())
            }
          >
            <Plus className="size-4" />
            Add Treatment Engineering
          </Button>
        </CardContent>
      </Card>
    );
  }

  function updateTreatment(
    changes: Partial<TreatmentConfigurationInput>,
  ): void {
    onChange({
      ...treatment!,
      ...changes,
    });
  }

  function updateSizing(
    changes: Partial<AirTreatmentInput>,
  ): void {
    updateTreatment({
      sizing_input: {
        ...treatment!.sizing_input,
        ...changes,
      },
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
                Establish delivered-air quality, dryer duty,
                capacity derating, purge demand and treatment
                pressure loss before evaluating selected equipment.
              </CardDescription>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            onClick={() => onChange(null)}
          >
            Remove Treatment
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
              <Label htmlFor="allied-treatment-flow">
                Required Delivered Flow
              </Label>

              <Input
                id="allied-treatment-flow"
                type="number"
                min="0"
                step="any"
                value={
                  treatment.sizing_input
                    .required_delivered_flow_nm3_per_hr
                }
                onChange={(event) =>
                  updateSizing({
                    required_delivered_flow_nm3_per_hr:
                      event.target.value,
                  })
                }
              />

              <p className="text-xs text-slate-500">
                Nm³/h
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="allied-treatment-quality">
                Required Air Quality
              </Label>

              <select
                id="allied-treatment-quality"
                value={treatment.sizing_input.required_air_quality}
                onChange={(event) =>
                  updateSizing({
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
              <Label htmlFor="allied-dryer-type">
                Dryer Technology
              </Label>

              <select
                id="allied-dryer-type"
                value={treatment.sizing_input.dryer_type}
                onChange={(event) =>
                  updateSizing({
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
              <Label htmlFor="allied-treatment-margin">
                Capacity Margin
              </Label>

              <Input
                id="allied-treatment-margin"
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={
                  treatment.sizing_input
                    .treatment_capacity_margin_fraction ?? "0"
                }
                onChange={(event) =>
                  updateSizing({
                    treatment_capacity_margin_fraction:
                      event.target.value,
                  })
                }
              />
            </div>
          </div>
        </section>

        <section className="border-t border-slate-100 pt-6">
          <h3 className="mb-4 text-sm font-semibold text-slate-900">
            Dryer Correction & Purge
          </h3>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="allied-dryer-correction">
                Dryer Correction Factor
              </Label>

              <Input
                id="allied-dryer-correction"
                type="number"
                min="0.0001"
                step="any"
                value={
                  treatment.sizing_input
                    .dryer_correction_factor ?? "1"
                }
                onChange={(event) =>
                  updateSizing({
                    dryer_correction_factor:
                      event.target.value,
                  })
                }
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="allied-dryer-purge">
                Dryer Purge Fraction
              </Label>

              <Input
                id="allied-dryer-purge"
                type="number"
                min="0"
                max="0.999"
                step="0.01"
                value={
                  treatment.sizing_input
                    .dryer_purge_fraction ?? "0"
                }
                onChange={(event) =>
                  updateSizing({
                    dryer_purge_fraction:
                      event.target.value,
                  })
                }
              />
            </div>
          </div>
        </section>

        <section className="border-t border-slate-100 pt-6">
          <h3 className="mb-4 text-sm font-semibold text-slate-900">
            Treatment Pressure Losses
          </h3>

          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="allied-prefilter-drop">
                Prefilter Pressure Drop
              </Label>

              <Input
                id="allied-prefilter-drop"
                type="number"
                min="0"
                step="any"
                value={
                  treatment.sizing_input
                    .prefilter_pressure_drop_bar ?? "0"
                }
                onChange={(event) =>
                  updateSizing({
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
              <Label htmlFor="allied-dryer-drop">
                Dryer Pressure Drop
              </Label>

              <Input
                id="allied-dryer-drop"
                type="number"
                min="0"
                step="any"
                value={
                  treatment.sizing_input
                    .dryer_pressure_drop_bar ?? "0"
                }
                onChange={(event) =>
                  updateSizing({
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
              <Label htmlFor="allied-afterfilter-drop">
                Afterfilter Pressure Drop
              </Label>

              <Input
                id="allied-afterfilter-drop"
                type="number"
                min="0"
                step="any"
                value={
                  treatment.sizing_input
                    .afterfilter_pressure_drop_bar ?? "0"
                }
                onChange={(event) =>
                  updateSizing({
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

        <section className="border-t border-slate-100 pt-6">
          <h3 className="mb-4 text-sm font-semibold text-slate-900">
            Selected Treatment Arrangement
          </h3>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div className="space-y-2">
              <Label htmlFor="allied-treatment-selected-capacity">
                Capacity / Unit
              </Label>

              <Input
                id="allied-treatment-selected-capacity"
                type="number"
                min="0"
                step="any"
                value={
                  treatment.selected_treatment_capacity_nm3_per_hr ?? ""
                }
                onChange={(event) =>
                  updateTreatment({
                    selected_treatment_capacity_nm3_per_hr:
                      event.target.value || null,
                  })
                }
              />

              <p className="text-xs text-slate-500">
                Nm³/h per unit
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="allied-treatment-installed-units">
                Installed Units
              </Label>

              <Input
                id="allied-treatment-installed-units"
                type="number"
                min="1"
                step="1"
                value={treatment.installed_unit_count ?? 1}
                onChange={(event) =>
                  updateTreatment({
                    installed_unit_count:
                      Number(event.target.value),
                  })
                }
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="allied-treatment-duty-units">
                Duty Units
              </Label>

              <Input
                id="allied-treatment-duty-units"
                type="number"
                min="1"
                step="1"
                value={treatment.duty_unit_count ?? 1}
                onChange={(event) =>
                  updateTreatment({
                    duty_unit_count:
                      Number(event.target.value),
                  })
                }
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="allied-treatment-redundancy">
                Redundancy Philosophy
              </Label>

              <select
                id="allied-treatment-redundancy"
                value={
                  treatment.redundancy_philosophy ?? "NONE"
                }
                onChange={(event) =>
                  updateTreatment({
                    redundancy_philosophy:
                      event.target.value as AlliedRedundancyPhilosophy,
                  })
                }
                className="h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
              >
                {redundancyOptions.map((option) => (
                  <option
                    key={option.value}
                    value={option.value}
                  >
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </section>

        <section className="border-t border-slate-100 pt-6">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="allied-treatment-reference">
                Equipment Reference
              </Label>

              <Input
                id="allied-treatment-reference"
                value={treatment.equipment_reference ?? ""}
                placeholder="Example: DRY-101"
                onChange={(event) =>
                  updateTreatment({
                    equipment_reference:
                      event.target.value || null,
                  })
                }
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="allied-treatment-notes">
                Treatment Notes
              </Label>

              <Input
                id="allied-treatment-notes"
                value={treatment.notes ?? ""}
                placeholder="Arrangement, operating basis, selection notes..."
                onChange={(event) =>
                  updateTreatment({
                    notes: event.target.value || null,
                  })
                }
              />
            </div>
          </div>
        </section>

        <div className="rounded-lg border border-dashed border-slate-300 p-4">
          <p className="text-sm font-medium text-slate-800">
            Engineering interpretation
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            Treatment adequacy is evaluated using corrected flow
            requirement, dryer purge, capacity margin, selected
            capacity per unit, and the number of duty units.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
