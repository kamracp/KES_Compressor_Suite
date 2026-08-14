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

import {
  createPerformanceMeasurement,
} from "../performanceFormState";
import type {
  PerformanceMeasurementInput,
  PerformanceOperatingState,
} from "../performanceTypes";

type OperatingMeasurementsSectionProps = {
  measurements: PerformanceMeasurementInput[];
  onChange: (measurements: PerformanceMeasurementInput[]) => void;
};

const operatingStateOptions: Array<{
  value: PerformanceOperatingState;
  label: string;
}> = [
  {
    value: "LOADED",
    label: "Loaded",
  },
  {
    value: "PART_LOAD",
    label: "Part Load",
  },
  {
    value: "UNLOADED",
    label: "Unloaded",
  },
  {
    value: "STOPPED",
    label: "Stopped",
  },
];

export function OperatingMeasurementsSection({
  measurements,
  onChange,
}: OperatingMeasurementsSectionProps) {
  function addMeasurement(): void {
    onChange([
      ...measurements,
      createPerformanceMeasurement(measurements.length),
    ]);
  }

  function updateMeasurement(
    index: number,
    changes: Partial<PerformanceMeasurementInput>,
  ): void {
    onChange(
      measurements.map((measurement, measurementIndex) =>
        measurementIndex === index
          ? {
              ...measurement,
              ...changes,
            }
          : measurement,
      ),
    );
  }

  function removeMeasurement(index: number): void {
    if (measurements.length <= 1) {
      return;
    }

    onChange(
      measurements.filter(
        (_, measurementIndex) => measurementIndex !== index,
      ),
    );
  }

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
                Operating Measurements
              </CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Record representative compressed-air flow, header pressure,
                electrical power, operating state, and production condition.
                Use consistent measurement intervals when the results are
                intended to represent an operating baseline.
              </CardDescription>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            onClick={addMeasurement}
          >
            <Plus className="size-4" />
            Add Measurement
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-5">
        {measurements.map((measurement, index) => (
          <section
            key={`${measurement.timestamp_label}-${index}`}
            className="rounded-xl border border-slate-200 p-5"
          >
            <div className="mb-5 flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                  Measurement {index + 1}
                </p>

                <h3 className="mt-1 text-base font-semibold text-slate-950">
                  {measurement.timestamp_label ||
                    `Operating Point ${index + 1}`}
                </h3>
              </div>

              <Button
                type="button"
                variant="ghost"
                size="icon"
                disabled={measurements.length <= 1}
                aria-label={`Remove measurement ${index + 1}`}
                onClick={() => removeMeasurement(index)}
              >
                <Trash2 className="size-4" />
              </Button>
            </div>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <div className="space-y-2">
                <Label htmlFor={`performance-period-${index}`}>
                  Timestamp / Operating Period
                </Label>

                <Input
                  id={`performance-period-${index}`}
                  value={measurement.timestamp_label}
                  placeholder="Example: Shift A - Full Production"
                  onChange={(event) =>
                    updateMeasurement(index, {
                      timestamp_label: event.target.value,
                    })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`performance-flow-${index}`}>
                  Measured Flow
                </Label>

                <Input
                  id={`performance-flow-${index}`}
                  type="number"
                  min="0"
                  step="any"
                  value={measurement.flow_nm3_per_hr}
                  onChange={(event) =>
                    updateMeasurement(index, {
                      flow_nm3_per_hr: event.target.value,
                    })
                  }
                />

                <p className="text-xs text-slate-500">
                  Nm³/h
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor={`performance-pressure-${index}`}>
                  Header Pressure
                </Label>

                <Input
                  id={`performance-pressure-${index}`}
                  type="number"
                  min="0"
                  step="any"
                  value={measurement.pressure_bar_g}
                  onChange={(event) =>
                    updateMeasurement(index, {
                      pressure_bar_g: event.target.value,
                    })
                  }
                />

                <p className="text-xs text-slate-500">
                  bar(g)
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor={`performance-power-${index}`}>
                  Measured Power
                </Label>

                <Input
                  id={`performance-power-${index}`}
                  type="number"
                  min="0"
                  step="any"
                  value={measurement.power_kw}
                  onChange={(event) =>
                    updateMeasurement(index, {
                      power_kw: event.target.value,
                    })
                  }
                />

                <p className="text-xs text-slate-500">
                  kW
                </p>
              </div>
            </div>

            <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <div className="space-y-2">
                <Label htmlFor={`performance-state-${index}`}>
                  Operating State
                </Label>

                <select
                  id={`performance-state-${index}`}
                  value={measurement.operating_state ?? ""}
                  className="flex h-9 w-full rounded-md border border-slate-200 bg-white px-3 py-1 text-sm shadow-xs outline-none transition-colors focus-visible:border-slate-400 focus-visible:ring-2 focus-visible:ring-slate-200"
                  onChange={(event) =>
                    updateMeasurement(index, {
                      operating_state:
                        event.target.value === ""
                          ? null
                          : (
                              event.target
                                .value as PerformanceOperatingState
                            ),
                    })
                  }
                >
                  <option value="">
                    Not Classified
                  </option>

                  {operatingStateOptions.map((option) => (
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
                <Label htmlFor={`performance-load-${index}`}>
                  Load Fraction
                </Label>

                <Input
                  id={`performance-load-${index}`}
                  type="number"
                  min="0"
                  max="1"
                  step="any"
                  value={measurement.load_fraction ?? ""}
                  placeholder="0.00 to 1.00"
                  onChange={(event) =>
                    updateMeasurement(index, {
                      load_fraction:
                        event.target.value === ""
                          ? null
                          : event.target.value,
                    })
                  }
                />

                <p className="text-xs text-slate-500">
                  Fraction of full load
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor={`performance-production-${index}`}>
                  Production State
                </Label>

                <Input
                  id={`performance-production-${index}`}
                  value={measurement.production_state ?? ""}
                  placeholder="Example: Full Production"
                  onChange={(event) =>
                    updateMeasurement(index, {
                      production_state:
                        event.target.value || null,
                    })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`performance-notes-${index}`}>
                  Engineering Notes
                </Label>

                <Input
                  id={`performance-notes-${index}`}
                  value={measurement.notes ?? ""}
                  placeholder="Instrument, condition, observations..."
                  onChange={(event) =>
                    updateMeasurement(index, {
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
            Measured performance basis
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            These operating points establish average, peak, and minimum flow;
            pressure range; measured power; specific power; specific energy;
            utilization indicators; unloaded-observation fraction; and the
            annualized energy baseline.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
