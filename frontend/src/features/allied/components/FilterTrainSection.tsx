import { Filter, Plus, Trash2 } from "lucide-react";

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

import { createFilterStage } from "../alliedFormState";
import type {
  FilterStageConfigurationInput,
  FilterStageType,
} from "../alliedTypes";

type FilterTrainSectionProps = {
  stages: FilterStageConfigurationInput[];
  onChange: (stages: FilterStageConfigurationInput[]) => void;
};

const filterTypeOptions: {
  value: FilterStageType;
  label: string;
}[] = [
  { value: "PARTICULATE", label: "Particulate" },
  { value: "COALESCING", label: "Coalescing" },
  { value: "FINE_COALESCING", label: "Fine Coalescing" },
  { value: "ACTIVATED_CARBON", label: "Activated Carbon" },
  { value: "STERILE", label: "Sterile" },
  { value: "OTHER", label: "Other" },
];

export function FilterTrainSection({
  stages,
  onChange,
}: FilterTrainSectionProps) {
  function addStage(): void {
    onChange([
      ...stages,
      createFilterStage(stages.length),
    ]);
  }

  function removeStage(index: number): void {
    onChange(
      stages.filter((_, stageIndex) => stageIndex !== index),
    );
  }

  function updateStage(
    index: number,
    changes: Partial<FilterStageConfigurationInput>,
  ): void {
    onChange(
      stages.map((stage, stageIndex) =>
        stageIndex === index
          ? {
              ...stage,
              ...changes,
            }
          : stage,
      ),
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex items-start gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
              <Filter className="size-5" />
            </div>

            <div>
              <CardTitle>Compressed-Air Filter Train</CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Define individual filter stages and evaluate selected
                airflow capacity and pressure-drop contribution across
                the compressed-air treatment train.
              </CardDescription>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            onClick={addStage}
          >
            <Plus className="size-4" />
            Add Filter Stage
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-5">
        {stages.length === 0 ? (
          <div className="rounded-lg border border-dashed border-slate-300 p-5">
            <p className="text-sm font-medium text-slate-800">
              No filter stages recorded
            </p>

            <p className="mt-1 text-xs leading-5 text-slate-500">
              Add one or more filter stages when filtration equipment
              is part of the allied-equipment engineering scope.
            </p>
          </div>
        ) : (
          stages.map((stage, index) => (
            <div
              key={`${stage.stage_code}-${index}`}
              className="rounded-xl border border-slate-200 p-5"
            >
              <div className="mb-5 flex items-center justify-between gap-4">
                <div>
                  <p className="text-sm font-semibold text-slate-900">
                    Filter Stage {index + 1}
                  </p>

                  <p className="text-xs text-slate-500">
                    Capacity and pressure-loss engineering record
                  </p>
                </div>

                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => removeStage(index)}
                >
                  <Trash2 className="size-4" />
                  Remove
                </Button>
              </div>

              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                <div className="space-y-2">
                  <Label htmlFor={`filter-code-${index}`}>
                    Stage Code
                  </Label>

                  <Input
                    id={`filter-code-${index}`}
                    value={stage.stage_code}
                    onChange={(event) =>
                      updateStage(index, {
                        stage_code: event.target.value,
                      })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`filter-type-${index}`}>
                    Filter Type
                  </Label>

                  <select
                    id={`filter-type-${index}`}
                    value={stage.stage_type}
                    onChange={(event) =>
                      updateStage(index, {
                        stage_type:
                          event.target.value as FilterStageType,
                      })
                    }
                    className="h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
                  >
                    {filterTypeOptions.map((option) => (
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
                  <Label htmlFor={`filter-capacity-${index}`}>
                    Selected Flow Capacity
                  </Label>

                  <Input
                    id={`filter-capacity-${index}`}
                    type="number"
                    min="0"
                    step="any"
                    value={
                      stage.selected_flow_capacity_nm3_per_hr ?? ""
                    }
                    onChange={(event) =>
                      updateStage(index, {
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
                  <Label htmlFor={`filter-drop-${index}`}>
                    Pressure Drop
                  </Label>

                  <Input
                    id={`filter-drop-${index}`}
                    type="number"
                    min="0"
                    step="any"
                    value={stage.pressure_drop_bar ?? "0"}
                    onChange={(event) =>
                      updateStage(index, {
                        pressure_drop_bar:
                          event.target.value,
                      })
                    }
                  />

                  <p className="text-xs text-slate-500">
                    bar
                  </p>
                </div>
              </div>

              <div className="mt-4 grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor={`filter-reference-${index}`}>
                    Equipment Reference
                  </Label>

                  <Input
                    id={`filter-reference-${index}`}
                    value={stage.equipment_reference ?? ""}
                    placeholder="Example: F-101"
                    onChange={(event) =>
                      updateStage(index, {
                        equipment_reference:
                          event.target.value || null,
                      })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`filter-notes-${index}`}>
                    Filter Notes
                  </Label>

                  <Input
                    id={`filter-notes-${index}`}
                    value={stage.notes ?? ""}
                    placeholder="Grade, location, operating basis..."
                    onChange={(event) =>
                      updateStage(index, {
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
            Each filter stage is evaluated independently against the
            common compressed-air flow basis. Stage pressure drops are
            also accumulated in the additional allied-equipment
            pressure-drop assessment.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
