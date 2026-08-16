import { Droplet, Plus, Trash2 } from "lucide-react";

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

import { createCondensateDrain } from "../alliedFormState";
import type {
  CondensateDrainConfigurationInput,
  CondensateDrainType,
} from "../alliedTypes";

type CondensateDrainSectionProps = {
  drains: CondensateDrainConfigurationInput[];
  onChange: (drains: CondensateDrainConfigurationInput[]) => void;
};

const drainTypeOptions: {
  value: CondensateDrainType;
  label: string;
}[] = [
  { value: "MANUAL", label: "Manual" },
  { value: "TIMER", label: "Timer Operated" },
  { value: "FLOAT", label: "Float Operated" },
  { value: "ZERO_LOSS", label: "Zero-Loss" },
  { value: "OTHER", label: "Other" },
];

export function CondensateDrainSection({
  drains,
  onChange,
}: CondensateDrainSectionProps) {
  function addDrain(): void {
    onChange([
      ...drains,
      createCondensateDrain(drains.length),
    ]);
  }

  function removeDrain(index: number): void {
    onChange(
      drains.filter((_, drainIndex) => drainIndex !== index),
    );
  }

  function updateDrain(
    index: number,
    changes: Partial<CondensateDrainConfigurationInput>,
  ): void {
    onChange(
      drains.map((drain, drainIndex) =>
        drainIndex === index
          ? {
              ...drain,
              ...changes,
            }
          : drain,
      ),
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex items-start gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
              <Droplet className="size-5" />
            </div>

            <div>
              <CardTitle>Condensate Drain Management</CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Record condensate-drain locations, drain technology,
                selected capacity, and equipment references associated
                with compressed-air allied equipment.
              </CardDescription>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            onClick={addDrain}
          >
            <Plus className="size-4" />
            Add Condensate Drain
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-5">
        {drains.length === 0 ? (
          <div className="rounded-lg border border-dashed border-slate-300 p-5">
            <p className="text-sm font-medium text-slate-800">
              No condensate drains recorded
            </p>

            <p className="mt-1 text-xs leading-5 text-slate-500">
              Add drain records where aftercoolers, moisture
              separators, receivers, filters, or other equipment
              generate or collect condensate.
            </p>
          </div>
        ) : (
          drains.map((drain, index) => (
            <div
              key={`${drain.drain_code}-${index}`}
              className="rounded-xl border border-slate-200 p-5"
            >
              <div className="mb-5 flex items-center justify-between gap-4">
                <div>
                  <p className="text-sm font-semibold text-slate-900">
                    Condensate Drain {index + 1}
                  </p>

                  <p className="text-xs text-slate-500">
                    Drain arrangement and engineering record
                  </p>
                </div>

                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => removeDrain(index)}
                >
                  <Trash2 className="size-4" />
                  Remove
                </Button>
              </div>

              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                <div className="space-y-2">
                  <Label htmlFor={`drain-code-${index}`}>
                    Drain Code
                  </Label>

                  <Input
                    id={`drain-code-${index}`}
                    value={drain.drain_code}
                    onChange={(event) =>
                      updateDrain(index, {
                        drain_code: event.target.value,
                      })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`drain-type-${index}`}>
                    Drain Type
                  </Label>

                  <select
                    id={`drain-type-${index}`}
                    value={drain.drain_type}
                    onChange={(event) =>
                      updateDrain(index, {
                        drain_type:
                          event.target.value as CondensateDrainType,
                      })
                    }
                    className="h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
                  >
                    {drainTypeOptions.map((option) => (
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
                  <Label htmlFor={`drain-location-${index}`}>
                    Drain Location
                  </Label>

                  <Input
                    id={`drain-location-${index}`}
                    value={drain.location}
                    placeholder="Example: Aftercooler outlet"
                    onChange={(event) =>
                      updateDrain(index, {
                        location: event.target.value,
                      })
                    }
                  />
                </div>
              </div>

              <div className="mt-4 grid gap-4 md:grid-cols-3">
                <div className="space-y-2">
                  <Label htmlFor={`drain-capacity-${index}`}>
                    Selected Condensate Capacity
                  </Label>

                  <Input
                    id={`drain-capacity-${index}`}
                    type="number"
                    min="0"
                    step="any"
                    value={
                      drain.selected_condensate_capacity_l_per_hr ?? ""
                    }
                    onChange={(event) =>
                      updateDrain(index, {
                        selected_condensate_capacity_l_per_hr:
                          event.target.value || null,
                      })
                    }
                  />

                  <p className="text-xs text-slate-500">
                    L/h
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`drain-reference-${index}`}>
                    Equipment Reference
                  </Label>

                  <Input
                    id={`drain-reference-${index}`}
                    value={drain.equipment_reference ?? ""}
                    placeholder="Example: CD-101"
                    onChange={(event) =>
                      updateDrain(index, {
                        equipment_reference:
                          event.target.value || null,
                      })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`drain-notes-${index}`}>
                    Drain Notes
                  </Label>

                  <Input
                    id={`drain-notes-${index}`}
                    value={drain.notes ?? ""}
                    placeholder="Drain service, operating basis, maintenance notes..."
                    onChange={(event) =>
                      updateDrain(index, {
                        notes: event.target.value || null,
                      })
                    }
                  />
                </div>
              </div>
            </div>
          ))
        )}

        <div className="rounded-lg border border-dashed border-slate-300 p-4">
          <p className="text-sm font-medium text-slate-800">
            Engineering interpretation
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            Drain records document condensate-removal provisions
            associated with allied equipment. Current R1.6 analysis
            checks whether drain provision has been recorded where
            condensate-producing equipment is present; it does not
            calculate condensate generation rate.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
