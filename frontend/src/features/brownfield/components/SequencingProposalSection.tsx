import { ListOrdered } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import { createCompressorSequencingSettings } from "../brownfieldFormState";
import type {
  CompressorSequencingInput,
  ExistingCompressorInput,
} from "../brownfieldTypes";

export type SequencingProposalField =
  | "sequencingProposedLoadPressureBarG"
  | "sequencingProposedUnloadPressureBarG"
  | "sequencingReceiverVolumeM3";

type SequencingProposalSectionProps = {
  enabled: boolean;
  proposedLoadPressureBarG: string;
  proposedUnloadPressureBarG: string;
  receiverVolumeM3: string;
  compressors: ExistingCompressorInput[];

  onEnabledChange: (enabled: boolean) => void;
  onProposalChange: (field: SequencingProposalField, value: string) => void;
  onCompressorsChange: (compressors: ExistingCompressorInput[]) => void;
};

export function SequencingProposalSection({
  enabled,
  proposedLoadPressureBarG,
  proposedUnloadPressureBarG,
  receiverVolumeM3,
  compressors,
  onEnabledChange,
  onProposalChange,
  onCompressorsChange,
}: SequencingProposalSectionProps) {
  function patchSettings(
    index: number,
    patch: Partial<CompressorSequencingInput>,
  ): void {
    onCompressorsChange(
      compressors.map((compressor, compressorIndex) =>
        compressorIndex === index
          ? {
              ...compressor,
              sequencing: {
                ...(compressor.sequencing ?? createCompressorSequencingSettings()),
                ...patch,
              },
            }
          : compressor,
      ),
    );
  }

  function patchBand(
    index: number,
    key: "load_pressure_bar_g" | "unload_pressure_bar_g",
    value: string,
  ): void {
    const current =
      compressors[index].sequencing ?? createCompressorSequencingSettings();

    patchSettings(index, { band: { ...current.band, [key]: value } });
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <ListOrdered className="size-5" />
          </div>

          <div className="flex-1">
            <CardTitle>Central Sequencer Proposal</CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Optional. Simulates the as-found pressure bands against a single
              common band with base/trim/standby assignment, using the system
              measurement points as equal-duration demand periods. Every
              available compressor needs its current control settings.
            </CardDescription>
          </div>
        </div>

        <label className="mt-4 flex items-center gap-3 text-sm font-medium text-slate-800">
          <input
            id="brownfield-sequencing-enabled"
            type="checkbox"
            className="size-4 rounded border-slate-300"
            checked={enabled}
            onChange={(event) => onEnabledChange(event.target.checked)}
          />
          Evaluate a central sequencer for this station
        </label>
      </CardHeader>

      {enabled && (
        <CardContent className="space-y-6">
          <section>
            <h3 className="mb-4 text-sm font-semibold text-slate-900">
              Proposed Common Band & Storage
            </h3>

            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <Label htmlFor="brownfield-seq-proposed-load">
                  Proposed Load Setpoint
                </Label>
                <Input
                  id="brownfield-seq-proposed-load"
                  type="number"
                  min="0"
                  step="0.1"
                  value={proposedLoadPressureBarG}
                  placeholder="Example: 6.5"
                  onChange={(event) =>
                    onProposalChange(
                      "sequencingProposedLoadPressureBarG",
                      event.target.value,
                    )
                  }
                />
                <p className="text-xs leading-5 text-slate-500">
                  bar g. Lowest pressure the header may fall to before the
                  next unit loads.
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="brownfield-seq-proposed-unload">
                  Proposed Unload Setpoint
                </Label>
                <Input
                  id="brownfield-seq-proposed-unload"
                  type="number"
                  min="0"
                  step="0.1"
                  value={proposedUnloadPressureBarG}
                  placeholder="Example: 7.0"
                  onChange={(event) =>
                    onProposalChange(
                      "sequencingProposedUnloadPressureBarG",
                      event.target.value,
                    )
                  }
                />
                <p className="text-xs leading-5 text-slate-500">
                  bar g. Plant ceiling 25 bar g; a narrower band lowers the
                  average header pressure.
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="brownfield-seq-receiver">
                  Receiver Volume
                </Label>
                <Input
                  id="brownfield-seq-receiver"
                  type="number"
                  min="0"
                  step="any"
                  value={receiverVolumeM3}
                  placeholder="Example: 10"
                  onChange={(event) =>
                    onProposalChange(
                      "sequencingReceiverVolumeM3",
                      event.target.value,
                    )
                  }
                />
                <p className="text-xs leading-5 text-slate-500">
                  m³ of wet plus dry storage available to the sequencer.
                </p>
              </div>
            </div>
          </section>

          <section className="border-t border-slate-100 pt-6">
            <h3 className="mb-1 text-sm font-semibold text-slate-900">
              As-Found Control Settings per Compressor
            </h3>
            <p className="mb-4 text-xs leading-5 text-slate-500">
              Unload power fraction 0.15–0.35 (DOE CAC Sourcebook). Priority is
              optional: set it on every unit or on none (1 loads first).
            </p>

            <div className="space-y-4">
              {compressors.map((compressor, index) => {
                const settings =
                  compressor.sequencing ?? createCompressorSequencingSettings();
                const isVsd = compressor.control_mode === "VSD";
                const isIgv = compressor.control_mode === "INLET_GUIDE_VANE";
                const isModulation = compressor.control_mode === "MODULATION";
                const isLoadUnload =
                  compressor.control_mode === "LOAD_UNLOAD" ||
                  compressor.control_mode === "FIXED_SPEED";
                const idBase = `brownfield-seq-${index}`;

                if (!compressor.available) {
                  return (
                    <div
                      key={idBase}
                      className="rounded-lg border border-dashed border-slate-200 p-4 text-sm text-slate-500"
                    >
                      {compressor.unit_code || `Compressor ${index + 1}`} — not
                      available; excluded from sequencing.
                    </div>
                  );
                }

                return (
                  <div
                    key={idBase}
                    className="rounded-lg border border-slate-200 p-4"
                  >
                    <div className="mb-3 flex items-center justify-between">
                      <p className="text-sm font-medium text-slate-900">
                        {compressor.unit_code || `Compressor ${index + 1}`}
                        <span className="ml-2 text-xs font-normal text-slate-500">
                          {compressor.control_mode} ·{" "}
                          {compressor.rated_fad_nm3_per_hr || "?"} Nm³/h ·{" "}
                          {compressor.rated_motor_power_kw || "?"} kW
                        </span>
                      </p>

                      <label className="flex items-center gap-2 text-xs text-slate-700">
                        <input
                          type="checkbox"
                          className="size-4 rounded border-slate-300"
                          checked={settings.standby_runs_unloaded}
                          onChange={(event) =>
                            patchSettings(index, {
                              standby_runs_unloaded: event.target.checked,
                            })
                          }
                        />
                        Standby runs unloaded today
                      </label>
                    </div>

                    <div className="grid gap-3 md:grid-cols-4">
                      <div className="space-y-1">
                        <Label htmlFor={`${idBase}-load`}>Load setpoint</Label>
                        <Input
                          id={`${idBase}-load`}
                          type="number"
                          min="0"
                          step="0.1"
                          value={settings.band.load_pressure_bar_g}
                          placeholder="bar g"
                          onChange={(event) =>
                            patchBand(index, "load_pressure_bar_g", event.target.value)
                          }
                        />
                      </div>

                      <div className="space-y-1">
                        <Label htmlFor={`${idBase}-unload`}>Unload setpoint</Label>
                        <Input
                          id={`${idBase}-unload`}
                          type="number"
                          min="0"
                          step="0.1"
                          value={settings.band.unload_pressure_bar_g}
                          placeholder="bar g"
                          onChange={(event) =>
                            patchBand(index, "unload_pressure_bar_g", event.target.value)
                          }
                        />
                      </div>

                      <div className="space-y-1">
                        <Label htmlFor={`${idBase}-unload-fraction`}>
                          {isIgv ? "Off-loaded power fraction" : "Unload power fraction"}
                        </Label>
                        <Input
                          id={`${idBase}-unload-fraction`}
                          type="number"
                          min={isIgv ? "0.05" : "0.15"}
                          max="0.35"
                          step="0.01"
                          placeholder={isIgv ? "Auto-dual only" : undefined}
                          value={settings.unload_power_fraction ?? ""}
                          onChange={(event) =>
                            patchSettings(index, {
                              unload_power_fraction: event.target.value,
                            })
                          }
                        />
                      </div>

                      <div className="space-y-1">
                        <Label htmlFor={`${idBase}-priority`}>Priority</Label>
                        <Input
                          id={`${idBase}-priority`}
                          type="number"
                          min="1"
                          max="20"
                          step="1"
                          value={settings.priority ?? ""}
                          placeholder="Optional"
                          onChange={(event) =>
                            patchSettings(index, {
                              priority:
                                event.target.value === ""
                                  ? null
                                  : Number(event.target.value),
                            })
                          }
                        />
                      </div>

                      {isModulation && (
                        <div className="space-y-1">
                          <Label htmlFor={`${idBase}-mod-floor`}>Modulation floor</Label>
                          <Input
                            id={`${idBase}-mod-floor`}
                            type="number"
                            min="0.1"
                            max="0.4"
                            step="0.01"
                            value={settings.modulation_floor_capacity_fraction ?? ""}
                            placeholder="Default 0.40 (DOE)"
                            onChange={(event) =>
                              patchSettings(index, {
                                modulation_floor_capacity_fraction: event.target.value,
                              })
                            }
                          />
                        </div>
                      )}

                      {isLoadUnload && (
                        <div className="space-y-1">
                          <Label htmlFor={`${idBase}-blowdown`}>Unload blowdown (s)</Label>
                          <Input
                            id={`${idBase}-blowdown`}
                            type="number"
                            min="0"
                            max="600"
                            step="1"
                            value={settings.unload_blowdown_seconds ?? ""}
                            placeholder="Optional, manufacturer"
                            onChange={(event) =>
                              patchSettings(index, {
                                unload_blowdown_seconds: event.target.value,
                              })
                            }
                          />
                        </div>
                      )}

                      {isIgv && (
                        <>
                          <div className="space-y-1">
                            <Label htmlFor={`${idBase}-turndown`}>Turndown fraction</Label>
                            <Input
                              id={`${idBase}-turndown`}
                              type="number"
                              min="0.1"
                              max="0.45"
                              step="0.01"
                              value={settings.turndown_flow_fraction ?? ""}
                              placeholder="Example: 0.30"
                              onChange={(event) =>
                                patchSettings(index, {
                                  turndown_flow_fraction: event.target.value,
                                })
                              }
                            />
                          </div>

                          <div className="space-y-1">
                            <Label htmlFor={`${idBase}-turndown-power`}>
                              Power at turndown
                            </Label>
                            <Input
                              id={`${idBase}-turndown-power`}
                              type="number"
                              min="0.6"
                              max="1"
                              step="0.01"
                              value={settings.power_fraction_at_turndown ?? ""}
                              placeholder="fraction of rated"
                              onChange={(event) =>
                                patchSettings(index, {
                                  power_fraction_at_turndown: event.target.value,
                                })
                              }
                            />
                          </div>

                          <div className="space-y-1">
                            <Label htmlFor={`${idBase}-below-turndown`}>Below turndown</Label>
                            <select
                              id={`${idBase}-below-turndown`}
                              className="h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
                              value={settings.below_turndown ?? "BLOW_OFF"}
                              onChange={(event) =>
                                patchSettings(index, {
                                  below_turndown:
                                    event.target.value === "UNLOAD" ? "UNLOAD" : "BLOW_OFF",
                                })
                              }
                            >
                              <option value="BLOW_OFF">Blow-off (power unchanged)</option>
                              <option value="UNLOAD">Auto-dual unload</option>
                            </select>
                          </div>
                        </>
                      )}

                      {isVsd && (
                        <>
                          <div className="space-y-1">
                            <Label htmlFor={`${idBase}-min-flow`}>
                              Minimum flow fraction
                            </Label>
                            <Input
                              id={`${idBase}-min-flow`}
                              type="number"
                              min="0.14"
                              max="1"
                              step="0.01"
                              value={settings.minimum_flow_fraction ?? ""}
                              placeholder="Example: 0.3"
                              onChange={(event) =>
                                patchSettings(index, {
                                  minimum_flow_fraction: event.target.value,
                                })
                              }
                            />
                          </div>

                          <div className="space-y-1">
                            <Label htmlFor={`${idBase}-min-flow-power`}>
                              Power at minimum flow
                            </Label>
                            <Input
                              id={`${idBase}-min-flow-power`}
                              type="number"
                              min="0"
                              max="1"
                              step="0.01"
                              value={settings.minimum_flow_power_fraction ?? ""}
                              placeholder="fraction of rated"
                              onChange={(event) =>
                                patchSettings(index, {
                                  minimum_flow_power_fraction: event.target.value,
                                })
                              }
                            />
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        </CardContent>
      )}
    </Card>
  );
}
