import {
  Factory,
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
  compressorControlModeOptions,
  compressorTechnologyOptions,
} from "../brownfieldOptions";
import {
  createBrownfieldCompressor,
} from "../brownfieldFormState";
import type {
  CompressorControlMode,
  CompressorTechnology,
  ExistingCompressorInput,
} from "../brownfieldTypes";

type ExistingCompressorSectionProps = {
  compressors: ExistingCompressorInput[];
  onChange: (compressors: ExistingCompressorInput[]) => void;
};

export function ExistingCompressorSection({
  compressors,
  onChange,
}: ExistingCompressorSectionProps) {
  function addCompressor(): void {
    onChange([
      ...compressors,
      createBrownfieldCompressor(compressors.length),
    ]);
  }

  function updateCompressor(
    index: number,
    changes: Partial<ExistingCompressorInput>,
  ): void {
    onChange(
      compressors.map((compressor, compressorIndex) =>
        compressorIndex === index
          ? {
              ...compressor,
              ...changes,
            }
          : compressor,
      ),
    );
  }

  function removeCompressor(index: number): void {
    if (compressors.length <= 1) {
      return;
    }

    onChange(
      compressors.filter(
        (_, compressorIndex) => compressorIndex !== index,
      ),
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex items-start gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
              <Factory className="size-5" />
            </div>

            <div>
              <CardTitle>
                Existing Compressor Inventory
              </CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Record the installed compressor station nameplate and operating
                basis. Use traceable equipment identification while keeping the
                engineering workflow vendor neutral.
              </CardDescription>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            onClick={addCompressor}
          >
            <Plus className="size-4" />
            Add Compressor
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-5">
        {compressors.map((compressor, index) => (
          <section
            key={`${compressor.unit_code}-${index}`}
            className="rounded-xl border border-slate-200 p-5"
          >
            <div className="mb-5 flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                  Existing Unit {index + 1}
                </p>

                <h3 className="mt-1 text-base font-semibold text-slate-950">
                  {compressor.unit_code || `Compressor ${index + 1}`}
                </h3>
              </div>

              <Button
                type="button"
                variant="ghost"
                size="icon"
                disabled={compressors.length <= 1}
                aria-label={`Remove compressor ${index + 1}`}
                onClick={() => removeCompressor(index)}
              >
                <Trash2 className="size-4" />
              </Button>
            </div>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <div className="space-y-2">
                <Label htmlFor={`compressor-code-${index}`}>
                  Unit Code
                </Label>

                <Input
                  id={`compressor-code-${index}`}
                  value={compressor.unit_code}
                  onChange={(event) =>
                    updateCompressor(index, {
                      unit_code: event.target.value,
                    })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`equipment-source-${index}`}>
                  Equipment Source / Identification
                </Label>

                <Input
                  id={`equipment-source-${index}`}
                  value={compressor.equipment_source ?? ""}
                  placeholder="Optional traceable reference"
                  onChange={(event) =>
                    updateCompressor(index, {
                      equipment_source:
                        event.target.value || null,
                    })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`compressor-model-${index}`}>
                  Model / Asset Reference
                </Label>

                <Input
                  id={`compressor-model-${index}`}
                  value={compressor.model ?? ""}
                  placeholder="Optional"
                  onChange={(event) =>
                    updateCompressor(index, {
                      model: event.target.value || null,
                    })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`installation-year-${index}`}>
                  Installation Year
                </Label>

                <Input
                  id={`installation-year-${index}`}
                  type="number"
                  min="1900"
                  step="1"
                  value={compressor.installation_year ?? ""}
                  onChange={(event) =>
                    updateCompressor(index, {
                      installation_year:
                        event.target.value === ""
                          ? null
                          : Number(event.target.value),
                    })
                  }
                />
              </div>
            </div>

            <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <div className="space-y-2">
                <Label htmlFor={`technology-${index}`}>
                  Compressor Technology
                </Label>

                <select
                  id={`technology-${index}`}
                  value={compressor.technology}
                  onChange={(event) =>
                    updateCompressor(index, {
                      technology:
                        event.target.value as CompressorTechnology,
                    })
                  }
                  className="h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
                >
                  {compressorTechnologyOptions.map((option) => (
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
                <Label htmlFor={`control-mode-${index}`}>
                  Control Mode
                </Label>

                <select
                  id={`control-mode-${index}`}
                  value={compressor.control_mode}
                  onChange={(event) =>
                    updateCompressor(index, {
                      control_mode:
                        event.target.value as CompressorControlMode,
                    })
                  }
                  className="h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
                >
                  {compressorControlModeOptions.map((option) => (
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
                <Label htmlFor={`rated-fad-${index}`}>
                  Rated FAD
                </Label>

                <Input
                  id={`rated-fad-${index}`}
                  type="number"
                  min="0"
                  step="any"
                  value={compressor.rated_fad_nm3_per_hr}
                  onChange={(event) =>
                    updateCompressor(index, {
                      rated_fad_nm3_per_hr:
                        event.target.value,
                    })
                  }
                />

                <p className="text-xs text-slate-500">
                  Nm³/h
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor={`rated-pressure-${index}`}>
                  Rated Discharge Pressure
                </Label>

                <Input
                  id={`rated-pressure-${index}`}
                  type="number"
                  min="0"
                  step="any"
                  value={
                    compressor.rated_discharge_pressure_bar_g
                  }
                  onChange={(event) =>
                    updateCompressor(index, {
                      rated_discharge_pressure_bar_g:
                        event.target.value,
                    })
                  }
                />

                <p className="text-xs text-slate-500">
                  bar(g)
                </p>
              </div>
            </div>

            <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <div className="space-y-2">
                <Label htmlFor={`motor-power-${index}`}>
                  Rated Motor Power
                </Label>

                <Input
                  id={`motor-power-${index}`}
                  type="number"
                  min="0"
                  step="any"
                  value={compressor.rated_motor_power_kw}
                  onChange={(event) =>
                    updateCompressor(index, {
                      rated_motor_power_kw:
                        event.target.value,
                    })
                  }
                />

                <p className="text-xs text-slate-500">
                  kW
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor={`operating-hours-${index}`}>
                  Recorded Operating Hours
                </Label>

                <Input
                  id={`operating-hours-${index}`}
                  type="number"
                  min="0"
                  step="any"
                  value={compressor.operating_hours ?? ""}
                  placeholder="Optional"
                  onChange={(event) =>
                    updateCompressor(index, {
                      operating_hours:
                        event.target.value || null,
                    })
                  }
                />

                <p className="text-xs text-slate-500">
                  Equipment-hour meter reading
                </p>
              </div>

              <div className="space-y-2 xl:col-span-2">
                <Label htmlFor={`compressor-notes-${index}`}>
                  Engineering Notes
                </Label>

                <Input
                  id={`compressor-notes-${index}`}
                  value={compressor.notes ?? ""}
                  placeholder="Condition, maintenance status, limitations, observations..."
                  onChange={(event) =>
                    updateCompressor(index, {
                      notes: event.target.value || null,
                    })
                  }
                />
              </div>
            </div>

            <div className="mt-5 flex items-center gap-3 rounded-lg border border-slate-200 bg-slate-50 p-4">
              <input
                id={`available-${index}`}
                type="checkbox"
                checked={compressor.available}
                onChange={(event) =>
                  updateCompressor(index, {
                    available: event.target.checked,
                  })
                }
                className="size-4 rounded border-slate-300"
              />

              <div>
                <Label htmlFor={`available-${index}`}>
                  Available for Plant Operation
                </Label>

                <p className="mt-1 text-xs leading-5 text-slate-500">
                  Unavailable units remain part of installed capacity but are
                  excluded from currently available station capacity.
                </p>
              </div>
            </div>
          </section>
        ))}

        <div className="rounded-lg border border-dashed border-slate-300 p-4">
          <p className="text-sm font-medium text-slate-800">
            Brownfield engineering basis
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            Rated FAD, motor power, pressure, availability, technology, and
            control mode feed the existing-system capacity and utilization
            analysis. Equipment source is retained only as a traceable asset
            reference and is not used for manufacturer-specific engineering
            recommendations.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
