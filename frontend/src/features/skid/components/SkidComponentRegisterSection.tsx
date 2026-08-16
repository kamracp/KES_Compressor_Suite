import {
  Boxes,
  Plus,
  Trash2,
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

import { createSkidComponent } from "../skidFormState";
import type {
  SkidComponentInput,
  SkidComponentType,
} from "../skidTypes";

type SkidComponentRegisterSectionProps = {
  components: SkidComponentInput[];
  onChange: (components: SkidComponentInput[]) => void;
};

const componentTypeOptions: {
  value: SkidComponentType;
  label: string;
}[] = [
  { value: "COMPRESSOR", label: "Compressor" },
  { value: "AFTERCOOLER", label: "Aftercooler" },
  { value: "MOISTURE_SEPARATOR", label: "Moisture Separator" },
  { value: "WET_RECEIVER", label: "Wet Receiver" },
  { value: "PREFILTER", label: "Prefilter" },
  { value: "DRYER", label: "Dryer" },
  { value: "AFTERFILTER", label: "Afterfilter" },
  { value: "DRY_RECEIVER", label: "Dry Receiver" },
  { value: "CONDENSATE_DRAIN", label: "Condensate Drain" },
  { value: "OIL_WATER_SEPARATOR", label: "Oil-Water Separator" },
  { value: "FLOW_METER", label: "Flow Meter" },
  { value: "PRESSURE_SENSOR", label: "Pressure Sensor" },
  { value: "DEW_POINT_SENSOR", label: "Dew Point Sensor" },
  { value: "MASTER_CONTROLLER", label: "Master Controller" },
  { value: "ISOLATION_VALVE", label: "Isolation Valve" },
  { value: "CHECK_VALVE", label: "Check Valve" },
  { value: "OTHER", label: "Other" },
];

export function SkidComponentRegisterSection({
  components,
  onChange,
}: SkidComponentRegisterSectionProps) {
  function addComponent(): void {
    onChange([
      ...components,
      createSkidComponent(components.length),
    ]);
  }

  function removeComponent(index: number): void {
    onChange(
      components.filter(
        (_, componentIndex) => componentIndex !== index,
      ),
    );
  }

  function updateComponent(
    index: number,
    changes: Partial<SkidComponentInput>,
  ): void {
    onChange(
      components.map((component, componentIndex) =>
        componentIndex === index
          ? {
              ...component,
              ...changes,
            }
          : component,
      ),
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex items-start gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
              <Boxes className="size-5" />
            </div>

            <div>
              <CardTitle>
                Skid Component Register
              </CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Register equipment, instrumentation, valves, receivers,
                treatment components, controls, and other items forming
                the compressed-air skid or station.
              </CardDescription>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            onClick={addComponent}
          >
            <Plus className="size-4" />
            Add Component
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-5">
        {components.length === 0 ? (
          <div className="rounded-lg border border-dashed border-slate-300 p-6 text-center">
            <p className="text-sm font-medium text-slate-800">
              No skid components registered
            </p>

            <p className="mx-auto mt-1 max-w-2xl text-xs leading-5 text-slate-500">
              Add the equipment and instrumentation that form the
              compressed-air skid before running the engineering
              assessment.
            </p>
          </div>
        ) : (
          components.map((component, index) => (
            <div
              key={`${component.component_code}-${index}`}
              className="rounded-xl border border-slate-200 p-5"
            >
              <div className="mb-5 flex items-center justify-between gap-4">
                <div>
                  <p className="text-sm font-semibold text-slate-950">
                    Component {index + 1}
                  </p>

                  <p className="text-xs text-slate-500">
                    Equipment and engineering rating record
                  </p>
                </div>

                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={() => removeComponent(index)}
                >
                  <Trash2 className="size-4" />
                  Remove
                </Button>
              </div>

              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                <div className="space-y-2">
                  <Label htmlFor={`skid-component-code-${index}`}>
                    Component Code
                  </Label>

                  <Input
                    id={`skid-component-code-${index}`}
                    value={component.component_code}
                    onChange={(event) =>
                      updateComponent(index, {
                        component_code: event.target.value,
                      })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`skid-component-name-${index}`}>
                    Component Name
                  </Label>

                  <Input
                    id={`skid-component-name-${index}`}
                    value={component.name}
                    placeholder="Example: Main Air Dryer"
                    onChange={(event) =>
                      updateComponent(index, {
                        name: event.target.value,
                      })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`skid-component-type-${index}`}>
                    Component Type
                  </Label>

                  <select
                    id={`skid-component-type-${index}`}
                    value={component.component_type}
                    onChange={(event) =>
                      updateComponent(index, {
                        component_type:
                          event.target.value as SkidComponentType,
                      })
                    }
                    className="h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
                  >
                    {componentTypeOptions.map((option) => (
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
                  <Label htmlFor={`skid-component-quantity-${index}`}>
                    Quantity
                  </Label>

                  <Input
                    id={`skid-component-quantity-${index}`}
                    type="number"
                    min="1"
                    step="1"
                    value={component.quantity ?? 1}
                    onChange={(event) =>
                      updateComponent(index, {
                        quantity: Number(event.target.value),
                      })
                    }
                  />
                </div>
              </div>

              <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                <div className="space-y-2">
                  <Label htmlFor={`skid-component-flow-${index}`}>
                    Rated Flow
                  </Label>

                  <Input
                    id={`skid-component-flow-${index}`}
                    type="number"
                    min="0"
                    step="any"
                    value={component.rated_flow_nm3_per_hr ?? ""}
                    onChange={(event) =>
                      updateComponent(index, {
                        rated_flow_nm3_per_hr:
                          event.target.value || null,
                      })
                    }
                  />

                  <p className="text-xs text-slate-500">
                    Nm³/h
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`skid-component-pressure-${index}`}>
                    Rated Pressure
                  </Label>

                  <Input
                    id={`skid-component-pressure-${index}`}
                    type="number"
                    min="0"
                    step="any"
                    value={component.rated_pressure_bar_g ?? ""}
                    onChange={(event) =>
                      updateComponent(index, {
                        rated_pressure_bar_g:
                          event.target.value || null,
                      })
                    }
                  />

                  <p className="text-xs text-slate-500">
                    bar(g)
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`skid-component-drop-${index}`}>
                    Pressure Drop
                  </Label>

                  <Input
                    id={`skid-component-drop-${index}`}
                    type="number"
                    min="0"
                    step="any"
                    value={component.pressure_drop_bar ?? "0"}
                    onChange={(event) =>
                      updateComponent(index, {
                        pressure_drop_bar: event.target.value,
                      })
                    }
                  />

                  <p className="text-xs text-slate-500">
                    bar
                  </p>
                </div>
              </div>

              <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                <div className="space-y-2">
                  <Label htmlFor={`skid-component-source-${index}`}>
                    Equipment Source
                  </Label>

                  <Input
                    id={`skid-component-source-${index}`}
                    value={component.equipment_source ?? ""}
                    placeholder="Engineering schedule, datasheet..."
                    onChange={(event) =>
                      updateComponent(index, {
                        equipment_source:
                          event.target.value || null,
                      })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`skid-component-model-${index}`}>
                    Model / Reference
                  </Label>

                  <Input
                    id={`skid-component-model-${index}`}
                    value={component.model ?? ""}
                    placeholder="Generic model or reference"
                    onChange={(event) =>
                      updateComponent(index, {
                        model: event.target.value || null,
                      })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`skid-component-notes-${index}`}>
                    Component Notes
                  </Label>

                  <Input
                    id={`skid-component-notes-${index}`}
                    value={component.notes ?? ""}
                    placeholder="Duty, location, selection basis..."
                    onChange={(event) =>
                      updateComponent(index, {
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
            Flow and pressure ratings are assessed where applicable.
            Total skid pressure drop is calculated from the recorded
            component pressure-drop values. Component source and model
            fields are engineering references and do not imply vendor
            endorsement.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
