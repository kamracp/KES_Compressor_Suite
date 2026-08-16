import { Cylinder, Plus } from "lucide-react";

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

import { createReceiverConfiguration } from "../alliedFormState";
import type {
  AlliedRedundancyPhilosophy,
  ReceiverConfigurationInput,
  ReceiverSizingInput,
} from "../alliedTypes";

type ReceiverEngineeringSectionProps = {
  receiver: ReceiverConfigurationInput | null;
  onChange: (receiver: ReceiverConfigurationInput | null) => void;
};

const redundancyOptions: {
  value: AlliedRedundancyPhilosophy;
  label: string;
}[] = [
  { value: "NONE", label: "None" },
  { value: "DUTY_STANDBY", label: "Duty / Standby" },
  { value: "N_PLUS_1", label: "N + 1" },
  { value: "MULTIPLE_DUTY", label: "Multiple Duty" },
];

export function ReceiverEngineeringSection({
  receiver,
  onChange,
}: ReceiverEngineeringSectionProps) {
  if (!receiver) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-start gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
              <Cylinder className="size-5" />
            </div>

            <div>
              <CardTitle>Air Receiver Engineering</CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Size compressed-air storage for transient demand and
                evaluate the selected receiver arrangement against the
                calculated storage requirement.
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          <Button
            type="button"
            variant="outline"
            onClick={() => onChange(createReceiverConfiguration())}
          >
            <Plus className="size-4" />
            Add Receiver Engineering
          </Button>
        </CardContent>
      </Card>
    );
  }

  function updateReceiver(
    changes: Partial<ReceiverConfigurationInput>,
  ): void {
    onChange({
      ...receiver!,
      ...changes,
    });
  }

  function updateSizing(
    changes: Partial<ReceiverSizingInput>,
  ): void {
    updateReceiver({
      sizing_input: {
        ...receiver!.sizing_input,
        ...changes,
      },
    });
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex items-start gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
              <Cylinder className="size-5" />
            </div>

            <div>
              <CardTitle>Air Receiver Engineering</CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Establish transient storage duty and compare calculated
                receiver volume with the selected installed arrangement.
              </CardDescription>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            onClick={() => onChange(null)}
          >
            Remove Receiver
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <section>
          <h3 className="mb-4 text-sm font-semibold text-slate-900">
            Transient Demand Basis
          </h3>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="allied-receiver-peak-demand">
                Peak Demand
              </Label>
              <Input
                id="allied-receiver-peak-demand"
                type="number"
                min="0"
                step="any"
                value={receiver.sizing_input.peak_demand_nm3_per_hr}
                onChange={(event) =>
                  updateSizing({
                    peak_demand_nm3_per_hr: event.target.value,
                  })
                }
              />
              <p className="text-xs text-slate-500">Nm³/h</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="allied-receiver-compressor-flow">
                Available Compressor Flow
              </Label>
              <Input
                id="allied-receiver-compressor-flow"
                type="number"
                min="0"
                step="any"
                value={
                  receiver.sizing_input
                    .available_compressor_flow_nm3_per_hr
                }
                onChange={(event) =>
                  updateSizing({
                    available_compressor_flow_nm3_per_hr:
                      event.target.value,
                  })
                }
              />
              <p className="text-xs text-slate-500">Nm³/h</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="allied-receiver-duration">
                Peak Event Duration
              </Label>
              <Input
                id="allied-receiver-duration"
                type="number"
                min="0.01"
                step="any"
                value={receiver.sizing_input.event_duration_seconds}
                onChange={(event) =>
                  updateSizing({
                    event_duration_seconds: event.target.value,
                  })
                }
              />
              <p className="text-xs text-slate-500">seconds</p>
            </div>
          </div>
        </section>

        <section className="border-t border-slate-100 pt-6">
          <h3 className="mb-4 text-sm font-semibold text-slate-900">
            Pressure Band & Reserve
          </h3>

          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="allied-receiver-high-pressure">
                High Pressure
              </Label>
              <Input
                id="allied-receiver-high-pressure"
                type="number"
                min="0"
                step="any"
                value={
                  receiver.sizing_input.receiver_high_pressure_bar_g
                }
                onChange={(event) =>
                  updateSizing({
                    receiver_high_pressure_bar_g:
                      event.target.value,
                  })
                }
              />
              <p className="text-xs text-slate-500">bar(g)</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="allied-receiver-low-pressure">
                Low Pressure
              </Label>
              <Input
                id="allied-receiver-low-pressure"
                type="number"
                min="0"
                step="any"
                value={
                  receiver.sizing_input.receiver_low_pressure_bar_g
                }
                onChange={(event) =>
                  updateSizing({
                    receiver_low_pressure_bar_g:
                      event.target.value,
                  })
                }
              />
              <p className="text-xs text-slate-500">bar(g)</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="allied-receiver-reserve">
                Reserve Fraction
              </Label>
              <Input
                id="allied-receiver-reserve"
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={receiver.sizing_input.reserve_fraction ?? "0"}
                onChange={(event) =>
                  updateSizing({
                    reserve_fraction: event.target.value,
                  })
                }
              />
            </div>
          </div>
        </section>

        <section className="border-t border-slate-100 pt-6">
          <h3 className="mb-4 text-sm font-semibold text-slate-900">
            Selected Receiver Arrangement
          </h3>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div className="space-y-2">
              <Label htmlFor="allied-selected-receiver-volume">
                Selected Volume / Receiver
              </Label>
              <Input
                id="allied-selected-receiver-volume"
                type="number"
                min="0"
                step="any"
                value={receiver.selected_receiver_volume_m3 ?? ""}
                onChange={(event) =>
                  updateReceiver({
                    selected_receiver_volume_m3:
                      event.target.value || null,
                  })
                }
              />
              <p className="text-xs text-slate-500">m³</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="allied-receiver-quantity">
                Receiver Quantity
              </Label>
              <Input
                id="allied-receiver-quantity"
                type="number"
                min="1"
                step="1"
                value={receiver.receiver_quantity ?? 1}
                onChange={(event) =>
                  updateReceiver({
                    receiver_quantity: Number(event.target.value),
                  })
                }
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="allied-receiver-design-pressure">
                Design Pressure
              </Label>
              <Input
                id="allied-receiver-design-pressure"
                type="number"
                min="0"
                step="any"
                value={receiver.design_pressure_bar_g ?? ""}
                onChange={(event) =>
                  updateReceiver({
                    design_pressure_bar_g:
                      event.target.value || null,
                  })
                }
              />
              <p className="text-xs text-slate-500">bar(g)</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="allied-receiver-redundancy">
                Redundancy Philosophy
              </Label>
              <select
                id="allied-receiver-redundancy"
                value={receiver.redundancy_philosophy ?? "NONE"}
                onChange={(event) =>
                  updateReceiver({
                    redundancy_philosophy:
                      event.target.value as AlliedRedundancyPhilosophy,
                  })
                }
                className="h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
              >
                {redundancyOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </section>

        <section className="border-t border-slate-100 pt-6">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="allied-receiver-reference">
                Equipment Reference
              </Label>
              <Input
                id="allied-receiver-reference"
                value={receiver.equipment_reference ?? ""}
                placeholder="Example: AR-101"
                onChange={(event) =>
                  updateReceiver({
                    equipment_reference:
                      event.target.value || null,
                  })
                }
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="allied-receiver-notes">
                Receiver Notes
              </Label>
              <Input
                id="allied-receiver-notes"
                value={receiver.notes ?? ""}
                placeholder="Location, arrangement, selection basis..."
                onChange={(event) =>
                  updateReceiver({
                    notes: event.target.value || null,
                  })
                }
              />
            </div>
          </div>
        </section>
      </CardContent>
    </Card>
  );
}
