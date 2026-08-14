import {
  LocateFixed,
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

import {
  createLeakRegisterItem,
} from "../leakageFormState";
import type {
  LeakQuantificationBasis,
  LeakRegisterItemInput,
  LeakRepairStatus,
  LeakSourceCategory,
} from "../leakageTypes";

type LeakRegisterSectionProps = {
  leaks: LeakRegisterItemInput[];
  onChange: (leaks: LeakRegisterItemInput[]) => void;
};

const quantificationBasisOptions: readonly {
  value: LeakQuantificationBasis;
  label: string;
}[] = [
  {
    value: "FLOW_METER",
    label: "Flow Meter",
  },
  {
    value: "ULTRASONIC_ESTIMATE",
    label: "Ultrasonic Estimate",
  },
  {
    value: "DECAY_TEST",
    label: "Pressure Decay Test",
  },
  {
    value: "LOAD_UNLOAD_TEST",
    label: "Load / Unload Test",
  },
  {
    value: "ORIFICE_ESTIMATE",
    label: "Orifice Estimate",
  },
  {
    value: "ENGINEERING_ESTIMATE",
    label: "Engineering Estimate",
  },
  {
    value: "OTHER",
    label: "Other",
  },
];

const sourceCategoryOptions: readonly {
  value: LeakSourceCategory;
  label: string;
}[] = [
  {
    value: "PIPE_JOINT",
    label: "Pipe Joint",
  },
  {
    value: "HOSE",
    label: "Hose",
  },
  {
    value: "FITTING",
    label: "Fitting",
  },
  {
    value: "QUICK_COUPLING",
    label: "Quick Coupling",
  },
  {
    value: "VALVE",
    label: "Valve",
  },
  {
    value: "FRL",
    label: "FRL",
  },
  {
    value: "CYLINDER",
    label: "Cylinder",
  },
  {
    value: "ACTUATOR",
    label: "Actuator",
  },
  {
    value: "DRAIN",
    label: "Drain",
  },
  {
    value: "EQUIPMENT_INTERNAL",
    label: "Equipment Internal",
  },
  {
    value: "OTHER",
    label: "Other",
  },
];

const repairStatusOptions: readonly {
  value: LeakRepairStatus;
  label: string;
}[] = [
  {
    value: "OPEN",
    label: "Open",
  },
  {
    value: "PLANNED",
    label: "Planned",
  },
  {
    value: "REPAIRED",
    label: "Repaired",
  },
  {
    value: "VERIFIED",
    label: "Verified",
  },
  {
    value: "DEFERRED",
    label: "Deferred",
  },
];

function nextLeakItem(
  leaks: LeakRegisterItemInput[],
): LeakRegisterItemInput {
  let index = leaks.length;

  while (true) {
    const candidate = createLeakRegisterItem(index);

    const duplicate = leaks.some(
      (item) => item.leak_code === candidate.leak_code,
    );

    if (!duplicate) {
      return candidate;
    }

    index += 1;
  }
}

export function LeakRegisterSection({
  leaks,
  onChange,
}: LeakRegisterSectionProps) {
  function addLeak(): void {
    onChange([
      ...leaks,
      nextLeakItem(leaks),
    ]);
  }

  function updateLeak(
    index: number,
    changes: Partial<LeakRegisterItemInput>,
  ): void {
    onChange(
      leaks.map((leak, leakIndex) =>
        leakIndex === index
          ? {
              ...leak,
              ...changes,
            }
          : leak,
      ),
    );
  }

  function removeLeak(index: number): void {
    if (leaks.length <= 1) {
      return;
    }

    onChange(
      leaks.filter(
        (_, leakIndex) => leakIndex !== index,
      ),
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex items-start gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
              <LocateFixed className="size-5" />
            </div>

            <div>
              <CardTitle>Leak Register</CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Register individual compressed-air leakage points,
                their locations, quantified leakage rates, repair
                status, and engineering survey basis.
              </CardDescription>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            onClick={addLeak}
          >
            <Plus className="size-4" />
            Add Leak
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-5">
        {leaks.map((leak, index) => (
          <section
            key={`${leak.leak_code}-${index}`}
            className="rounded-xl border border-slate-200 p-5"
          >
            <div className="mb-5 flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                  Registered Leak {index + 1}
                </p>

                <h3 className="mt-1 text-base font-semibold text-slate-950">
                  {leak.leak_code || `Leak ${index + 1}`}
                </h3>
              </div>

              <Button
                type="button"
                variant="ghost"
                size="icon"
                disabled={leaks.length <= 1}
                onClick={() => removeLeak(index)}
                aria-label={`Remove leak ${index + 1}`}
              >
                <Trash2 className="size-4" />
              </Button>
            </div>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <div className="space-y-2">
                <Label htmlFor={`leak-code-${index}`}>
                  Leak Code
                </Label>

                <Input
                  id={`leak-code-${index}`}
                  value={leak.leak_code}
                  placeholder="Example: L-001"
                  onChange={(event) =>
                    updateLeak(index, {
                      leak_code: event.target.value,
                    })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`leak-location-${index}`}>
                  Location
                </Label>

                <Input
                  id={`leak-location-${index}`}
                  value={leak.location}
                  placeholder="Example: Compressor House"
                  onChange={(event) =>
                    updateLeak(index, {
                      location: event.target.value,
                    })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`leak-area-${index}`}>
                  Area
                </Label>

                <Input
                  id={`leak-area-${index}`}
                  value={leak.area ?? ""}
                  placeholder="Example: Utilities"
                  onChange={(event) =>
                    updateLeak(index, {
                      area: event.target.value || null,
                    })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`equipment-tag-${index}`}>
                  Equipment Tag
                </Label>

                <Input
                  id={`equipment-tag-${index}`}
                  value={leak.equipment_tag ?? ""}
                  placeholder="Example: AIR-HDR-01"
                  onChange={(event) =>
                    updateLeak(index, {
                      equipment_tag:
                        event.target.value || null,
                    })
                  }
                />
              </div>
            </div>

            <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <div className="space-y-2">
                <Label htmlFor={`source-category-${index}`}>
                  Source Category
                </Label>

                <select
                  id={`source-category-${index}`}
                  value={leak.source_category}
                  onChange={(event) =>
                    updateLeak(index, {
                      source_category:
                        event.target.value as LeakSourceCategory,
                    })
                  }
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs outline-none transition-[color,box-shadow] focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
                >
                  {sourceCategoryOptions.map((option) => (
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
                <Label htmlFor={`quantification-basis-${index}`}>
                  Quantification Basis
                </Label>

                <select
                  id={`quantification-basis-${index}`}
                  value={leak.quantification_basis}
                  onChange={(event) =>
                    updateLeak(index, {
                      quantification_basis:
                        event.target.value as LeakQuantificationBasis,
                    })
                  }
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs outline-none transition-[color,box-shadow] focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
                >
                  {quantificationBasisOptions.map((option) => (
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
                <Label htmlFor={`leak-flow-${index}`}>
                  Baseline Leakage Flow
                </Label>

                <Input
                  id={`leak-flow-${index}`}
                  type="number"
                  min="0"
                  step="any"
                  value={
                    leak.baseline_leakage_flow_nm3_per_hr
                  }
                  placeholder="Example: 120"
                  onChange={(event) =>
                    updateLeak(index, {
                      baseline_leakage_flow_nm3_per_hr:
                        event.target.value,
                    })
                  }
                />

                <p className="text-xs text-slate-500">
                  Nm³/h
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor={`survey-pressure-${index}`}>
                  Survey Pressure
                </Label>

                <Input
                  id={`survey-pressure-${index}`}
                  type="number"
                  min="0"
                  step="any"
                  value={leak.survey_pressure_bar_g ?? ""}
                  placeholder="Example: 6.5"
                  onChange={(event) =>
                    updateLeak(index, {
                      survey_pressure_bar_g:
                        event.target.value || null,
                    })
                  }
                />

                <p className="text-xs text-slate-500">
                  bar(g)
                </p>
              </div>
            </div>

            <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <div className="space-y-2">
                <Label htmlFor={`repair-fraction-${index}`}>
                  Expected Repair Fraction
                </Label>

                <Input
                  id={`repair-fraction-${index}`}
                  type="number"
                  min="0"
                  max="1"
                  step="any"
                  value={leak.expected_repair_fraction}
                  placeholder="Example: 0.80"
                  onChange={(event) =>
                    updateLeak(index, {
                      expected_repair_fraction:
                        event.target.value,
                    })
                  }
                />

                <p className="text-xs text-slate-500">
                  Fraction from 0 to 1
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor={`repair-cost-${index}`}>
                  Estimated Repair Cost
                </Label>

                <Input
                  id={`repair-cost-${index}`}
                  type="number"
                  min="0"
                  step="any"
                  value={leak.estimated_repair_cost ?? ""}
                  placeholder="Optional"
                  onChange={(event) =>
                    updateLeak(index, {
                      estimated_repair_cost:
                        event.target.value || null,
                    })
                  }
                />

                <p className="text-xs text-slate-500">
                  Project currency
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor={`repair-status-${index}`}>
                  Repair Status
                </Label>

                <select
                  id={`repair-status-${index}`}
                  value={leak.repair_status}
                  onChange={(event) =>
                    updateLeak(index, {
                      repair_status:
                        event.target.value as LeakRepairStatus,
                    })
                  }
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs outline-none transition-[color,box-shadow] focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
                >
                  {repairStatusOptions.map((option) => (
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
                <Label htmlFor={`method-reference-${index}`}>
                  Survey Method Reference
                </Label>

                <Input
                  id={`method-reference-${index}`}
                  value={
                    leak.survey_method_reference ?? ""
                  }
                  placeholder="Instrument, test, worksheet..."
                  onChange={(event) =>
                    updateLeak(index, {
                      survey_method_reference:
                        event.target.value || null,
                    })
                  }
                />
              </div>
            </div>

            <div className="mt-4 grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor={`component-description-${index}`}>
                  Component Description
                </Label>

                <Input
                  id={`component-description-${index}`}
                  value={
                    leak.component_description ?? ""
                  }
                  placeholder="Example: 1/2-inch quick coupling at machine inlet"
                  onChange={(event) =>
                    updateLeak(index, {
                      component_description:
                        event.target.value || null,
                    })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`leak-notes-${index}`}>
                  Engineering Notes
                </Label>

                <Input
                  id={`leak-notes-${index}`}
                  value={leak.notes ?? ""}
                  placeholder="Observed condition, access, repair remarks..."
                  onChange={(event) =>
                    updateLeak(index, {
                      notes: event.target.value || null,
                    })
                  }
                />
              </div>
            </div>
          </section>
        ))}

        <div className="rounded-lg border border-dashed border-slate-300 p-4">
          <p className="text-sm font-medium text-slate-800">
            Leak register methodology
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            Each leakage point remains individually traceable.
            Quantification basis records how the leakage flow was
            established, while repair fraction represents the
            expected recoverable portion used for the energy and
            economic opportunity calculation.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
