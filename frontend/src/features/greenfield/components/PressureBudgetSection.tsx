import {
  Gauge,
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

import type { PressureLossComponentInput } from "../greenfieldTypes";

type PressureBudgetSectionProps = {
  components: PressureLossComponentInput[];
  onChange: (components: PressureLossComponentInput[]) => void;
};

function createPressureLossComponent(
  index: number,
): PressureLossComponentInput {
  return {
    component_code: `LOSS-${String(index + 1).padStart(2, "0")}`,
    name: "",
    pressure_drop_bar: "0",
    category: "DISTRIBUTION",
    notes: null,
  };
}

function calculateInputSubtotal(
  components: PressureLossComponentInput[],
): number {
  return components.reduce((total, component) => {
    const pressureDrop = Number(component.pressure_drop_bar);

    return total + (
      Number.isFinite(pressureDrop)
        ? pressureDrop
        : 0
    );
  }, 0);
}

export function PressureBudgetSection({
  components,
  onChange,
}: PressureBudgetSectionProps) {
  function updateComponent(
    index: number,
    changes: Partial<PressureLossComponentInput>,
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

  function addComponent(): void {
    onChange([
      ...components,
      createPressureLossComponent(components.length),
    ]);
  }

  function removeComponent(index: number): void {
    onChange(
      components.filter(
        (_, componentIndex) => componentIndex !== index,
      ),
    );
  }

  const subtotalBar = calculateInputSubtotal(components);

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex items-start gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
              <Gauge className="size-5" />
            </div>

            <div>
              <CardTitle>
                Pressure Budget
              </CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Define pressure losses through treatment equipment,
                headers, distribution piping, filters, dryers, and other
                compressed-air system components.
              </CardDescription>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            onClick={addComponent}
          >
            <Plus className="size-4" />
            Add Pressure Loss
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-5">
        {components.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-300 p-6 text-center">
            <Gauge className="mx-auto mb-3 size-6 text-slate-400" />

            <p className="text-sm font-medium text-slate-800">
              No pressure-loss components defined
            </p>

            <p className="mt-1 text-xs leading-5 text-slate-500">
              Add dryer, filter, header, distribution, or other known
              pressure losses that must be included in the compressor
              discharge-pressure requirement.
            </p>

            <Button
              type="button"
              variant="outline"
              className="mt-4"
              onClick={addComponent}
            >
              <Plus className="size-4" />
              Add First Component
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {components.map((component, index) => (
              <section
                key={`${component.component_code}-${index}`}
                className="rounded-xl border border-slate-200 bg-slate-50/40 p-4"
              >
                <div className="mb-4 flex items-center justify-between gap-4">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                      Pressure Loss {index + 1}
                    </p>

                    <p className="mt-1 text-sm font-medium text-slate-900">
                      {component.name || "System Component"}
                    </p>
                  </div>

                  <Button
                    type="button"
                    size="icon-sm"
                    variant="ghost"
                    onClick={() => removeComponent(index)}
                    aria-label={`Remove pressure loss ${index + 1}`}
                  >
                    <Trash2 className="size-4" />
                  </Button>
                </div>

                <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                  <div className="space-y-2">
                    <Label htmlFor={`loss-code-${index}`}>
                      Component Code
                    </Label>

                    <Input
                      id={`loss-code-${index}`}
                      value={component.component_code}
                      onChange={(event) =>
                        updateComponent(index, {
                          component_code: event.target.value,
                        })
                      }
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor={`loss-name-${index}`}>
                      Component Name
                    </Label>

                    <Input
                      id={`loss-name-${index}`}
                      value={component.name}
                      placeholder="Example: Main Header"
                      onChange={(event) =>
                        updateComponent(index, {
                          name: event.target.value,
                        })
                      }
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor={`loss-category-${index}`}>
                      Category
                    </Label>

                    <Input
                      id={`loss-category-${index}`}
                      value={component.category}
                      placeholder="DISTRIBUTION"
                      onChange={(event) =>
                        updateComponent(index, {
                          category: event.target.value,
                        })
                      }
                    />

                    <p className="text-xs text-slate-500">
                      Example: TREATMENT or DISTRIBUTION
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor={`loss-value-${index}`}>
                      Pressure Drop
                    </Label>

                    <div className="relative">
                      <Input
                        id={`loss-value-${index}`}
                        type="number"
                        min="0"
                        step="any"
                        value={component.pressure_drop_bar}
                        onChange={(event) =>
                          updateComponent(index, {
                            pressure_drop_bar:
                              event.target.value,
                          })
                        }
                        className="pr-14"
                      />

                      <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-xs text-slate-500">
                        bar
                      </span>
                    </div>
                  </div>
                </div>

                <div className="mt-4 space-y-2">
                  <Label htmlFor={`loss-notes-${index}`}>
                    Engineering Notes
                  </Label>

                  <Input
                    id={`loss-notes-${index}`}
                    value={component.notes ?? ""}
                    placeholder="Optional design assumption or basis"
                    onChange={(event) =>
                      updateComponent(index, {
                        notes: event.target.value || null,
                      })
                    }
                  />
                </div>
              </section>
            ))}
          </div>
        )}

        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-semibold text-slate-900">
                Input Pressure-Loss Subtotal
              </p>

              <p className="mt-1 text-xs leading-5 text-slate-500">
                Sum of the pressure-drop components entered above.
                Control margin is maintained separately in the Design Basis.
              </p>
            </div>

            <div className="shrink-0 text-right">
              <p className="text-2xl font-bold tracking-tight text-slate-950">
                {subtotalBar.toFixed(3)}
              </p>

              <p className="text-xs font-medium text-slate-500">
                bar
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
