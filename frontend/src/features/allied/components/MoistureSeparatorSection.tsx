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

import { createMoistureSeparatorConfiguration } from "../alliedFormState";
import type {
  MoistureSeparatorConfigurationInput,
  MoistureSeparatorType,
} from "../alliedTypes";

type MoistureSeparatorSectionProps = {
  separator: MoistureSeparatorConfigurationInput | null;
  onChange: (
    separator: MoistureSeparatorConfigurationInput | null,
  ) => void;
};

const separatorTypeOptions: {
  value: MoistureSeparatorType;
  label: string;
}[] = [
  { value: "CENTRIFUGAL", label: "Centrifugal" },
  { value: "CYCLONIC", label: "Cyclonic" },
  { value: "DEMISTER", label: "Demister" },
  { value: "INTEGRATED", label: "Integrated" },
  { value: "NONE", label: "None" },
];

export function MoistureSeparatorSection({
  separator,
  onChange,
}: MoistureSeparatorSectionProps) {
  if (!separator) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-start gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
              <Droplets className="size-5" />
            </div>

            <div>
              <CardTitle>Moisture Separator Engineering</CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Record moisture-separation arrangement, selected
                airflow capacity, and pressure loss for engineering
                adequacy review.
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          <Button
            type="button"
            variant="outline"
            onClick={() =>
              onChange(createMoistureSeparatorConfiguration())
            }
          >
            <Plus className="size-4" />
            Add Moisture Separator
          </Button>
        </CardContent>
      </Card>
    );
  }

  function updateSeparator(
    changes: Partial<MoistureSeparatorConfigurationInput>,
  ): void {
    onChange({
      ...separator!,
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
              <CardTitle>Moisture Separator Engineering</CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Compare selected separator flow capacity with the
                allied-system flow basis and account for separator
                pressure drop.
              </CardDescription>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            onClick={() => onChange(null)}
          >
            Remove Separator
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div className="space-y-2">
            <Label htmlFor="allied-separator-type">
              Separator Type
            </Label>

            <select
              id="allied-separator-type"
              value={separator.separator_type}
              onChange={(event) =>
                updateSeparator({
                  separator_type:
                    event.target.value as MoistureSeparatorType,
                })
              }
              className="h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
            >
              {separatorTypeOptions.map((option) => (
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
            <Label htmlFor="allied-separator-capacity">
              Selected Flow Capacity
            </Label>

            <Input
              id="allied-separator-capacity"
              type="number"
              min="0"
              step="any"
              value={
                separator.selected_flow_capacity_nm3_per_hr ?? ""
              }
              onChange={(event) =>
                updateSeparator({
                  selected_flow_capacity_nm3_per_hr:
                    event.target.value || null,
                })
              }
            />

            <p className="text-xs text-slate-500">
              Nm³/h
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="allied-separator-drop">
              Pressure Drop
            </Label>

            <Input
              id="allied-separator-drop"
              type="number"
              min="0"
              step="any"
              value={separator.pressure_drop_bar ?? "0"}
              onChange={(event) =>
                updateSeparator({
                  pressure_drop_bar: event.target.value,
                })
              }
            />

            <p className="text-xs text-slate-500">
              bar
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="allied-separator-reference">
              Equipment Reference
            </Label>

            <Input
              id="allied-separator-reference"
              value={separator.equipment_reference ?? ""}
              placeholder="Example: MS-101"
              onChange={(event) =>
                updateSeparator({
                  equipment_reference:
                    event.target.value || null,
                })
              }
            />
          </div>
        </div>

        <div className="space-y-2 border-t border-slate-100 pt-6">
          <Label htmlFor="allied-separator-notes">
            Separator Notes
          </Label>

          <Input
            id="allied-separator-notes"
            value={separator.notes ?? ""}
            placeholder="Location, separator arrangement, operating basis..."
            onChange={(event) =>
              updateSeparator({
                notes: event.target.value || null,
              })
            }
          />
        </div>

        <div className="rounded-lg border border-dashed border-slate-300 p-4">
          <p className="text-sm font-medium text-slate-800">
            Engineering interpretation
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            Current analysis evaluates separator flow capacity and
            pressure-drop contribution. Condensate generation rate
            remains outside this R1.6 calculation scope.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
