import {
  Activity,
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
  auditOperatingStateOptions,
} from "../brownfieldOptions";
import {
  createBrownfieldCompressorMeasurement,
} from "../brownfieldFormState";
import type {
  AuditOperatingState,
  CompressorMeasurementInput,
  ExistingCompressorInput,
} from "../brownfieldTypes";

type CompressorMeasurementsSectionProps = {
  compressors: ExistingCompressorInput[];
  measurements: CompressorMeasurementInput[];
  onChange: (measurements: CompressorMeasurementInput[]) => void;
};

export function CompressorMeasurementsSection({
  compressors,
  measurements,
  onChange,
}: CompressorMeasurementsSectionProps) {
  function addMeasurement(): void {
    const defaultUnitCode =
      compressors.length > 0
        ? compressors[0].unit_code
        : "";

    onChange([
      ...measurements,
      createBrownfieldCompressorMeasurement(defaultUnitCode),
    ]);
  }

  function updateMeasurement(
    index: number,
    changes: Partial<CompressorMeasurementInput>,
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
              <Activity className="size-5" />
            </div>

            <div>
              <CardTitle>
                Compressor Operating Measurements
              </CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Record measured operating points for individual compressors.
                These observations support loaded, unloaded, part-load, and
                stopped-state analysis of the existing compressor station.
              </CardDescription>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            onClick={addMeasurement}
            disabled={compressors.length === 0}
          >
            <Plus className="size-4" />
            Add Measurement
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-5">
        {measurements.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-300 p-6">
            <p className="text-sm font-medium text-slate-800">
              No compressor-level measurements added
            </p>

            <p className="mt-2 max-w-2xl text-xs leading-5 text-slate-500">
              Compressor measurements are optional in the current Brownfield
              API. Add them when individual unit operating-state data is
              available so unloaded-running behavior can be evaluated.
            </p>
          </div>
        ) : (
          measurements.map((measurement, index) => (
            <section
              key={`${measurement.unit_code}-${index}`}
              className="rounded-xl border border-slate-200 p-5"
            >
              <div className="mb-5 flex items-start justify-between gap-4">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                    Operating Point {index + 1}
                  </p>

                  <h3 className="mt-1 text-base font-semibold text-slate-950">
                    {measurement.unit_code || "Unassigned Compressor"}
                  </h3>
                </div>

                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  aria-label={`Remove compressor measurement ${index + 1}`}
                  onClick={() => removeMeasurement(index)}
                >
                  <Trash2 className="size-4" />
                </Button>
              </div>

              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                <div className="space-y-2">
                  <Label htmlFor={`measurement-unit-${index}`}>
                    Compressor Unit
                  </Label>

                  <select
                    id={`measurement-unit-${index}`}
                    value={measurement.unit_code}
                    onChange={(event) =>
                      updateMeasurement(index, {
                        unit_code: event.target.value,
                      })
                    }
                    className="h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
                  >
                    <option value="">
                      Select compressor
                    </option>

                    {compressors.map((compressor) => (
                      <option
                        key={compressor.unit_code}
                        value={compressor.unit_code}
                      >
                        {compressor.unit_code}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`measurement-period-${index}`}>
                    Timestamp / Operating Period
                  </Label>

                  <Input
                    id={`measurement-period-${index}`}
                    value={measurement.timestamp_label}
                    placeholder="Example: Shift A - 10:30"
                    onChange={(event) =>
                      updateMeasurement(index, {
                        timestamp_label:
                          event.target.value,
                      })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`operating-state-${index}`}>
                    Operating State
                  </Label>

                  <select
                    id={`operating-state-${index}`}
                    value={measurement.operating_state}
                    onChange={(event) =>
                      updateMeasurement(index, {
                        operating_state:
                          event.target.value as AuditOperatingState,
                      })
                    }
                    className="h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
                  >
                    {auditOperatingStateOptions.map((option) => (
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

              <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                <div className="space-y-2">
                  <Label htmlFor={`measured-flow-${index}`}>
                    Measured Flow
                  </Label>

                  <Input
                    id={`measured-flow-${index}`}
                    type="number"
                    min="0"
                    step="any"
                    value={
                      measurement.measured_flow_nm3_per_hr
                    }
                    onChange={(event) =>
                      updateMeasurement(index, {
                        measured_flow_nm3_per_hr:
                          event.target.value,
                      })
                    }
                  />

                  <p className="text-xs text-slate-500">
                    Nm³/h
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`measured-pressure-${index}`}>
                    Discharge Pressure
                  </Label>

                  <Input
                    id={`measured-pressure-${index}`}
                    type="number"
                    min="0"
                    step="any"
                    value={
                      measurement.measured_discharge_pressure_bar_g
                    }
                    onChange={(event) =>
                      updateMeasurement(index, {
                        measured_discharge_pressure_bar_g:
                          event.target.value,
                      })
                    }
                  />

                  <p className="text-xs text-slate-500">
                    bar(g)
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`measured-power-${index}`}>
                    Measured Power
                  </Label>

                  <Input
                    id={`measured-power-${index}`}
                    type="number"
                    min="0"
                    step="any"
                    value={measurement.measured_power_kw}
                    onChange={(event) =>
                      updateMeasurement(index, {
                        measured_power_kw:
                          event.target.value,
                      })
                    }
                  />

                  <p className="text-xs text-slate-500">
                    kW
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`load-fraction-${index}`}>
                    Load Fraction
                  </Label>

                  <Input
                    id={`load-fraction-${index}`}
                    type="number"
                    min="0"
                    max="1"
                    step="0.01"
                    value={measurement.load_fraction ?? ""}
                    placeholder="Optional"
                    onChange={(event) =>
                      updateMeasurement(index, {
                        load_fraction:
                          event.target.value || null,
                      })
                    }
                  />

                  <p className="text-xs text-slate-500">
                    0 to 1
                  </p>
                </div>
              </div>
            </section>
          ))
        )}

        <div className="rounded-lg border border-dashed border-slate-300 p-4">
          <p className="text-sm font-medium text-slate-800">
            Operating-state analysis
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            The current Brownfield engine evaluates the fraction of individual
            compressor observations recorded in the UNLOADED state. This
            supports identification of excessive unloaded running and related
            control or sequencing opportunities.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
