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
  createBrownfieldSystemMeasurement,
} from "../brownfieldFormState";
import type {
  SystemMeasurementInput,
} from "../brownfieldTypes";

type SystemMeasurementsSectionProps = {
  measurements: SystemMeasurementInput[];
  onChange: (measurements: SystemMeasurementInput[]) => void;
};

export function SystemMeasurementsSection({
  measurements,
  onChange,
}: SystemMeasurementsSectionProps) {
  function addMeasurement(): void {
    onChange([
      ...measurements,
      createBrownfieldSystemMeasurement(),
    ]);
  }

  function updateMeasurement(
    index: number,
    changes: Partial<SystemMeasurementInput>,
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
                Plant System Measurements
              </CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Record plant-level compressed-air flow, header pressure, total
                compressor power, and production condition for representative
                operating periods.
              </CardDescription>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            onClick={addMeasurement}
          >
            <Plus className="size-4" />
            Add System Measurement
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
                  System Measurement {index + 1}
                </p>

                <h3 className="mt-1 text-base font-semibold text-slate-950">
                  {measurement.timestamp_label ||
                    `Operating Period ${index + 1}`}
                </h3>
              </div>

              <Button
                type="button"
                variant="ghost"
                size="icon"
                disabled={measurements.length <= 1}
                aria-label={`Remove system measurement ${index + 1}`}
                onClick={() => removeMeasurement(index)}
              >
                <Trash2 className="size-4" />
              </Button>
            </div>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <div className="space-y-2">
                <Label htmlFor={`system-period-${index}`}>
                  Timestamp / Operating Period
                </Label>

                <Input
                  id={`system-period-${index}`}
                  value={measurement.timestamp_label}
                  placeholder="Example: Shift A - Normal Production"
                  onChange={(event) =>
                    updateMeasurement(index, {
                      timestamp_label: event.target.value,
                    })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`system-flow-${index}`}>
                  Total System Flow
                </Label>

                <Input
                  id={`system-flow-${index}`}
                  type="number"
                  min="0"
                  step="any"
                  value={measurement.total_flow_nm3_per_hr}
                  onChange={(event) =>
                    updateMeasurement(index, {
                      total_flow_nm3_per_hr:
                        event.target.value,
                    })
                  }
                />

                <p className="text-xs text-slate-500">
                  Nm³/h
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor={`header-pressure-${index}`}>
                  Header Pressure
                </Label>

                <Input
                  id={`header-pressure-${index}`}
                  type="number"
                  min="0"
                  step="any"
                  value={measurement.header_pressure_bar_g}
                  onChange={(event) =>
                    updateMeasurement(index, {
                      header_pressure_bar_g:
                        event.target.value,
                    })
                  }
                />

                <p className="text-xs text-slate-500">
                  bar(g)
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor={`system-power-${index}`}>
                  Total Compressor Power
                </Label>

                <Input
                  id={`system-power-${index}`}
                  type="number"
                  min="0"
                  step="any"
                  value={measurement.total_power_kw}
                  onChange={(event) =>
                    updateMeasurement(index, {
                      total_power_kw:
                        event.target.value,
                    })
                  }
                />

                <p className="text-xs text-slate-500">
                  kW
                </p>
              </div>
            </div>

            <div className="mt-5 grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor={`production-state-${index}`}>
                  Production State
                </Label>

                <Input
                  id={`production-state-${index}`}
                  value={measurement.production_state ?? ""}
                  placeholder="Example: Full Production, Idle, Weekend"
                  onChange={(event) =>
                    updateMeasurement(index, {
                      production_state:
                        event.target.value || null,
                    })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`system-notes-${index}`}>
                  Engineering Notes
                </Label>

                <Input
                  id={`system-notes-${index}`}
                  value={measurement.notes ?? ""}
                  placeholder="Operating condition, instruments, abnormalities..."
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
            Measured system baseline
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            The Brownfield engine uses these measurements to establish average,
            peak, and minimum system demand; average and peak power; header
            pressure range; compressor-station utilisation; and measured
            specific power.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
