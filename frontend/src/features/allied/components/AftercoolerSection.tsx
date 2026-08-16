import { Plus, Wind } from "lucide-react";

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

import { createAftercoolerConfiguration } from "../alliedFormState";
import type {
  AftercoolerConfigurationInput,
  AftercoolerType,
} from "../alliedTypes";

type AftercoolerSectionProps = {
  aftercooler: AftercoolerConfigurationInput | null;
  onChange: (
    aftercooler: AftercoolerConfigurationInput | null,
  ) => void;
};

const aftercoolerTypeOptions: {
  value: AftercoolerType;
  label: string;
}[] = [
  { value: "AIR_COOLED", label: "Air Cooled" },
  { value: "WATER_COOLED", label: "Water Cooled" },
  { value: "INTEGRATED", label: "Integrated" },
  { value: "NONE", label: "None" },
];

export function AftercoolerSection({
  aftercooler,
  onChange,
}: AftercoolerSectionProps) {
  if (!aftercooler) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-start gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
              <Wind className="size-5" />
            </div>

            <div>
              <CardTitle>Aftercooler Engineering</CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Record aftercooler arrangement, selected airflow
                capacity, pressure loss, and operating temperatures
                for engineering adequacy review.
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          <Button
            type="button"
            variant="outline"
            onClick={() =>
              onChange(createAftercoolerConfiguration())
            }
          >
            <Plus className="size-4" />
            Add Aftercooler
          </Button>
        </CardContent>
      </Card>
    );
  }

  function updateAftercooler(
    changes: Partial<AftercoolerConfigurationInput>,
  ): void {
    onChange({
      ...aftercooler!,
      ...changes,
    });
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex items-start gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
              <Wind className="size-5" />
            </div>

            <div>
              <CardTitle>Aftercooler Engineering</CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Compare selected aftercooler flow capacity with the
                compressed-air system flow basis and account for its
                pressure-drop contribution.
              </CardDescription>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            onClick={() => onChange(null)}
          >
            Remove Aftercooler
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div className="space-y-2">
            <Label htmlFor="allied-aftercooler-type">
              Aftercooler Type
            </Label>

            <select
              id="allied-aftercooler-type"
              value={aftercooler.aftercooler_type}
              onChange={(event) =>
                updateAftercooler({
                  aftercooler_type:
                    event.target.value as AftercoolerType,
                })
              }
              className="h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
            >
              {aftercoolerTypeOptions.map((option) => (
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
            <Label htmlFor="allied-aftercooler-capacity">
              Selected Flow Capacity
            </Label>

            <Input
              id="allied-aftercooler-capacity"
              type="number"
              min="0"
              step="any"
              value={
                aftercooler.selected_flow_capacity_nm3_per_hr ?? ""
              }
              onChange={(event) =>
                updateAftercooler({
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
            <Label htmlFor="allied-aftercooler-drop">
              Pressure Drop
            </Label>

            <Input
              id="allied-aftercooler-drop"
              type="number"
              min="0"
              step="any"
              value={aftercooler.pressure_drop_bar ?? "0"}
              onChange={(event) =>
                updateAftercooler({
                  pressure_drop_bar: event.target.value,
                })
              }
            />

            <p className="text-xs text-slate-500">
              bar
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="allied-aftercooler-reference">
              Equipment Reference
            </Label>

            <Input
              id="allied-aftercooler-reference"
              value={aftercooler.equipment_reference ?? ""}
              placeholder="Example: AC-101"
              onChange={(event) =>
                updateAftercooler({
                  equipment_reference:
                    event.target.value || null,
                })
              }
            />
          </div>
        </div>

        <section className="border-t border-slate-100 pt-6">
          <h3 className="mb-4 text-sm font-semibold text-slate-900">
            Temperature Record
          </h3>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="allied-aftercooler-inlet-temp">
                Inlet Temperature
              </Label>

              <Input
                id="allied-aftercooler-inlet-temp"
                type="number"
                step="any"
                value={aftercooler.inlet_temperature_c ?? ""}
                onChange={(event) =>
                  updateAftercooler({
                    inlet_temperature_c:
                      event.target.value || null,
                  })
                }
              />

              <p className="text-xs text-slate-500">
                °C
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="allied-aftercooler-outlet-temp">
                Outlet Temperature
              </Label>

              <Input
                id="allied-aftercooler-outlet-temp"
                type="number"
                step="any"
                value={aftercooler.outlet_temperature_c ?? ""}
                onChange={(event) =>
                  updateAftercooler({
                    outlet_temperature_c:
                      event.target.value || null,
                  })
                }
              />

              <p className="text-xs text-slate-500">
                °C
              </p>
            </div>
          </div>
        </section>

        <div className="space-y-2 border-t border-slate-100 pt-6">
          <Label htmlFor="allied-aftercooler-notes">
            Aftercooler Notes
          </Label>

          <Input
            id="allied-aftercooler-notes"
            value={aftercooler.notes ?? ""}
            placeholder="Cooling arrangement, operating condition, selection basis..."
            onChange={(event) =>
              updateAftercooler({
                notes: event.target.value || null,
              })
            }
          />
        </div>

        <div className="rounded-lg border border-dashed border-slate-300 p-4">
          <p className="text-sm font-medium text-slate-800">
            Engineering limitation
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            Current R1.6 analysis evaluates aftercooler flow capacity
            and pressure drop. Temperature values are recorded as
            engineering context; condensate or psychrometric duty is
            not calculated by this workflow.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
