import {
  Plus,
  Settings2,
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
  compressorDutyRoleOptions,
  compressorTechnologyOptions,
  redundancyPhilosophyOptions,
} from "../greenfieldOptions";
import type {
  CompressorControlMode,
  CompressorDutyRole,
  CompressorStationInput,
  CompressorTechnology,
  CompressorUnitInput,
  RedundancyPhilosophy,
} from "../greenfieldTypes";

type CompressorStationSectionProps = {
  station: CompressorStationInput | null;
  onChange: (station: CompressorStationInput | null) => void;
};

function createUnit(index: number): CompressorUnitInput {
  return {
    unit_code: `AC-${String(index + 1).padStart(2, "0")}`,
    technology: "ROTARY_SCREW_OIL_INJECTED",
    control_mode: "FIXED_SPEED",
    duty_role: index === 0 ? "BASE_LOAD" : "TRIM",
    rated_fad_nm3_per_hr: "",
    minimum_stable_flow_fraction: "0.6",
    rated_discharge_pressure_bar_g: "7",
    rated_motor_power_kw: null,
    specific_power_kw_per_nm3_per_min: null,
    available: true,
    notes: null,
  };
}

function createStation(): CompressorStationInput {
  return {
    station_code: "CAS-GF-001",
    units: [createUnit(0)],
    redundancy_philosophy: "N_PLUS_1",
    minimum_required_pressure_bar_g: "6.5",
    design_flow_nm3_per_hr: "",
    master_control_enabled: false,
  };
}

export function CompressorStationSection({
  station,
  onChange,
}: CompressorStationSectionProps) {
  if (!station) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Proposed Compressor Station</CardTitle>

          <CardDescription className="leading-6">
            Add a proposed compressor configuration when you want the
            Greenfield engine to evaluate installed capacity, duty roles,
            discharge pressure, and redundancy adequacy.
          </CardDescription>
        </CardHeader>

        <CardContent>
          <Button
            type="button"
            variant="outline"
            onClick={() => onChange(createStation())}
          >
            <Plus className="size-4" />
            Add Proposed Station
          </Button>
        </CardContent>
      </Card>
    );
  }

  function updateStation(
    changes: Partial<CompressorStationInput>,
  ): void {
    onChange({
      ...station!,
      ...changes,
    });
  }

  function updateUnit(
    index: number,
    changes: Partial<CompressorUnitInput>,
  ): void {
    updateStation({
      units: station!.units.map((unit, unitIndex) =>
        unitIndex === index
          ? {
              ...unit,
              ...changes,
            }
          : unit,
      ),
    });
  }

  function addUnit(): void {
    updateStation({
      units: [
        ...station!.units,
        createUnit(station!.units.length),
      ],
    });
  }

  function removeUnit(index: number): void {
    if (station!.units.length <= 1) {
      return;
    }

    updateStation({
      units: station!.units.filter(
        (_, unitIndex) => unitIndex !== index,
      ),
    });
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex items-start gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
              <Settings2 className="size-5" />
            </div>

            <div>
              <CardTitle>
                Proposed Compressor Station
              </CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Define the proposed compressor arrangement for capacity,
                pressure, duty-role, and redundancy evaluation. This is an
                engineering configuration input, not an automatic optimum
                equipment recommendation.
              </CardDescription>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            onClick={() => onChange(null)}
          >
            Remove Station Evaluation
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div className="space-y-2">
            <Label htmlFor="station-code">
              Station Code
            </Label>

            <Input
              id="station-code"
              value={station.station_code}
              onChange={(event) =>
                updateStation({
                  station_code: event.target.value,
                })
              }
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="station-design-flow">
              Design Flow
            </Label>

            <Input
              id="station-design-flow"
              type="number"
              min="0"
              step="any"
              value={station.design_flow_nm3_per_hr}
              onChange={(event) =>
                updateStation({
                  design_flow_nm3_per_hr:
                    event.target.value,
                })
              }
            />

            <p className="text-xs text-slate-500">
              Nm³/h
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="station-pressure">
              Minimum Required Pressure
            </Label>

            <Input
              id="station-pressure"
              type="number"
              min="0"
              step="any"
              value={station.minimum_required_pressure_bar_g}
              onChange={(event) =>
                updateStation({
                  minimum_required_pressure_bar_g:
                    event.target.value,
                })
              }
            />

            <p className="text-xs text-slate-500">
              bar(g)
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="station-redundancy">
              Redundancy Philosophy
            </Label>

            <select
              id="station-redundancy"
              value={station.redundancy_philosophy}
              onChange={(event) =>
                updateStation({
                  redundancy_philosophy:
                    event.target.value as RedundancyPhilosophy,
                })
              }
              className="h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
            >
              {redundancyPhilosophyOptions.map((option) => (
                <option
                  key={option.value}
                  value={option.value}
                >
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </section>

        <label className="flex items-center gap-3 rounded-lg border border-slate-200 p-3 text-sm">
          <input
            type="checkbox"
            checked={station.master_control_enabled ?? false}
            onChange={(event) =>
              updateStation({
                master_control_enabled:
                  event.target.checked,
              })
            }
          />

          <span>
            Master compressor-station control enabled
          </span>
        </label>

        <section className="space-y-4">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-900">
                Compressor Units
              </h3>

              <p className="mt-1 text-xs text-slate-500">
                Define proposed Base, Trim, Duty, and Standby units.
              </p>
            </div>

            <Button
              type="button"
              variant="outline"
              onClick={addUnit}
            >
              <Plus className="size-4" />
              Add Compressor
            </Button>
          </div>

          {station.units.map((unit, index) => (
            <div
              key={`${unit.unit_code}-${index}`}
              className="rounded-xl border border-slate-200 bg-slate-50/40 p-4"
            >
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                    Compressor {index + 1}
                  </p>

                  <p className="mt-1 text-sm font-medium text-slate-900">
                    {unit.unit_code}
                  </p>
                </div>

                <Button
                  type="button"
                  size="icon-sm"
                  variant="ghost"
                  disabled={station.units.length <= 1}
                  onClick={() => removeUnit(index)}
                  aria-label={`Remove compressor ${index + 1}`}
                >
                  <Trash2 className="size-4" />
                </Button>
              </div>

              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                <div className="space-y-2">
                  <Label htmlFor={`unit-code-${index}`}>
                    Unit Code
                  </Label>

                  <Input
                    id={`unit-code-${index}`}
                    value={unit.unit_code}
                    onChange={(event) =>
                      updateUnit(index, {
                        unit_code: event.target.value,
                      })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`technology-${index}`}>
                    Technology
                  </Label>

                  <select
                    id={`technology-${index}`}
                    value={unit.technology}
                    onChange={(event) =>
                      updateUnit(index, {
                        technology:
                          event.target.value as CompressorTechnology,
                      })
                    }
                    className="h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm"
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
                  <Label htmlFor={`control-${index}`}>
                    Control Mode
                  </Label>

                  <select
                    id={`control-${index}`}
                    value={unit.control_mode}
                    onChange={(event) =>
                      updateUnit(index, {
                        control_mode:
                          event.target.value as CompressorControlMode,
                      })
                    }
                    className="h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm"
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
                  <Label htmlFor={`role-${index}`}>
                    Duty Role
                  </Label>

                  <select
                    id={`role-${index}`}
                    value={unit.duty_role}
                    onChange={(event) =>
                      updateUnit(index, {
                        duty_role:
                          event.target.value as CompressorDutyRole,
                      })
                    }
                    className="h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm"
                  >
                    {compressorDutyRoleOptions.map((option) => (
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
                  <Label htmlFor={`fad-${index}`}>
                    Rated FAD
                  </Label>

                  <Input
                    id={`fad-${index}`}
                    type="number"
                    min="0"
                    step="any"
                    value={unit.rated_fad_nm3_per_hr}
                    onChange={(event) =>
                      updateUnit(index, {
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
                  <Label htmlFor={`stable-flow-${index}`}>
                    Minimum Stable Flow
                  </Label>

                  <Input
                    id={`stable-flow-${index}`}
                    type="number"
                    min="0"
                    max="1"
                    step="0.01"
                    value={unit.minimum_stable_flow_fraction}
                    onChange={(event) =>
                      updateUnit(index, {
                        minimum_stable_flow_fraction:
                          event.target.value,
                      })
                    }
                  />

                  <p className="text-xs text-slate-500">
                    Fraction of rated FAD
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`discharge-pressure-${index}`}>
                    Rated Discharge Pressure
                  </Label>

                  <Input
                    id={`discharge-pressure-${index}`}
                    type="number"
                    min="0"
                    step="any"
                    value={unit.rated_discharge_pressure_bar_g}
                    onChange={(event) =>
                      updateUnit(index, {
                        rated_discharge_pressure_bar_g:
                          event.target.value,
                      })
                    }
                  />

                  <p className="text-xs text-slate-500">
                    bar(g)
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`motor-power-${index}`}>
                    Rated Motor Power
                  </Label>

                  <Input
                    id={`motor-power-${index}`}
                    type="number"
                    min="0"
                    step="any"
                    value={unit.rated_motor_power_kw ?? ""}
                    onChange={(event) =>
                      updateUnit(index, {
                        rated_motor_power_kw:
                          event.target.value || null,
                      })
                    }
                  />

                  <p className="text-xs text-slate-500">
                    kW
                  </p>
                </div>
              </div>
            </div>
          ))}
        </section>
      </CardContent>
    </Card>
  );
}
