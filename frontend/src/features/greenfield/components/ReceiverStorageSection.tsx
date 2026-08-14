import {
  Cylinder,
  Plus,
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

import type { ReceiverSizingInput } from "../greenfieldTypes";

type ReceiverStorageSectionProps = {
  receiver: ReceiverSizingInput | null;
  onChange: (receiver: ReceiverSizingInput | null) => void;
};

function createReceiver(): ReceiverSizingInput {
  return {
    peak_demand_nm3_per_hr: "",
    available_compressor_flow_nm3_per_hr: "",
    event_duration_seconds: "30",
    receiver_high_pressure_bar_g: "7",
    receiver_low_pressure_bar_g: "6.5",
    reserve_fraction: "0.20",
  };
}

export function ReceiverStorageSection({
  receiver,
  onChange,
}: ReceiverStorageSectionProps) {
  if (!receiver) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-start gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
              <Cylinder className="size-5" />
            </div>

            <div>
              <CardTitle>
                Receiver & Storage Engineering
              </CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Evaluate compressed-air storage for short-duration peak demand,
                compressor response, usable pressure band, and reserve
                requirement.
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          <Button
            type="button"
            variant="outline"
            onClick={() => onChange(createReceiver())}
          >
            <Plus className="size-4" />
            Add Receiver Evaluation
          </Button>
        </CardContent>
      </Card>
    );
  }

  function updateReceiver(
    changes: Partial<ReceiverSizingInput>,
  ): void {
    onChange({
      ...receiver!,
      ...changes,
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
              <CardTitle>
                Receiver & Storage Engineering
              </CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Define the transient demand event and usable receiver pressure
                band. The Greenfield engine will determine whether additional
                storage is required and calculate the required receiver volume.
              </CardDescription>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            onClick={() => onChange(null)}
          >
            Remove Receiver Evaluation
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <section>
          <h3 className="mb-4 text-sm font-semibold text-slate-900">
            Peak Demand Event
          </h3>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="receiver-peak-demand">
                Peak Demand
              </Label>

              <Input
                id="receiver-peak-demand"
                type="number"
                min="0"
                step="any"
                value={receiver.peak_demand_nm3_per_hr}
                onChange={(event) =>
                  updateReceiver({
                    peak_demand_nm3_per_hr:
                      event.target.value,
                  })
                }
              />

              <p className="text-xs text-slate-500">
                Nm³/h
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="receiver-compressor-flow">
                Available Compressor Flow
              </Label>

              <Input
                id="receiver-compressor-flow"
                type="number"
                min="0"
                step="any"
                value={
                  receiver.available_compressor_flow_nm3_per_hr
                }
                onChange={(event) =>
                  updateReceiver({
                    available_compressor_flow_nm3_per_hr:
                      event.target.value,
                  })
                }
              />

              <p className="text-xs text-slate-500">
                Nm³/h
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="receiver-event-duration">
                Peak Event Duration
              </Label>

              <Input
                id="receiver-event-duration"
                type="number"
                min="0.01"
                step="any"
                value={receiver.event_duration_seconds}
                onChange={(event) =>
                  updateReceiver({
                    event_duration_seconds:
                      event.target.value,
                  })
                }
              />

              <p className="text-xs text-slate-500">
                seconds
              </p>
            </div>
          </div>
        </section>

        <section className="border-t border-slate-100 pt-6">
          <h3 className="mb-4 text-sm font-semibold text-slate-900">
            Usable Pressure Band
          </h3>

          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="receiver-high-pressure">
                Receiver High Pressure
              </Label>

              <Input
                id="receiver-high-pressure"
                type="number"
                min="0"
                step="any"
                value={
                  receiver.receiver_high_pressure_bar_g
                }
                onChange={(event) =>
                  updateReceiver({
                    receiver_high_pressure_bar_g:
                      event.target.value,
                  })
                }
              />

              <p className="text-xs text-slate-500">
                bar(g)
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="receiver-low-pressure">
                Receiver Low Pressure
              </Label>

              <Input
                id="receiver-low-pressure"
                type="number"
                min="0"
                step="any"
                value={
                  receiver.receiver_low_pressure_bar_g
                }
                onChange={(event) =>
                  updateReceiver({
                    receiver_low_pressure_bar_g:
                      event.target.value,
                  })
                }
              />

              <p className="text-xs text-slate-500">
                bar(g)
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="receiver-reserve">
                Storage Reserve Fraction
              </Label>

              <Input
                id="receiver-reserve"
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={receiver.reserve_fraction ?? "0"}
                onChange={(event) =>
                  updateReceiver({
                    reserve_fraction:
                      event.target.value,
                  })
                }
              />

              <p className="text-xs text-slate-500">
                Additional storage margin
              </p>
            </div>
          </div>
        </section>

        <div className="rounded-lg border border-dashed border-slate-300 p-4">
          <p className="text-sm font-medium text-slate-800">
            Engineering interpretation
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            Storage requirement depends on the flow deficit between peak demand
            and available compressor capacity, the event duration, and the
            usable receiver pressure band.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
