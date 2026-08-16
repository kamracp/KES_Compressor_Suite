import {
  Activity,
  Gauge,
  Settings2,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";

import type { SkidFormState } from "../skidFormState";

type SkidConfigurationSectionProps = {
  state: SkidFormState;
  onChange: (changes: Partial<SkidFormState>) => void;
};

type ConfigurationItem = {
  key:
    | "hasWetReceiver"
    | "hasDryReceiver"
    | "hasFlowMetering"
    | "hasPressureMonitoring"
    | "hasDewPointMonitoring"
    | "masterControlEnabled";
  label: string;
  description: string;
};

const configurationItems: ConfigurationItem[] = [
  {
    key: "hasWetReceiver",
    label: "Wet Receiver Provided",
    description:
      "Confirm that a wet receiver is included in the skid or station arrangement.",
  },
  {
    key: "hasDryReceiver",
    label: "Dry Receiver Provided",
    description:
      "Confirm that a dry receiver is included downstream of treatment where applicable.",
  },
  {
    key: "hasFlowMetering",
    label: "Flow Metering Provided",
    description:
      "Confirm that compressed-air flow measurement is included in the configuration.",
  },
  {
    key: "hasPressureMonitoring",
    label: "Pressure Monitoring Provided",
    description:
      "Confirm that system pressure monitoring is included in the configuration.",
  },
  {
    key: "hasDewPointMonitoring",
    label: "Dew-Point Monitoring Provided",
    description:
      "Confirm that compressed-air dew-point monitoring is included.",
  },
  {
    key: "masterControlEnabled",
    label: "Master Control Enabled",
    description:
      "Record whether supervisory or master compressor-station control is enabled.",
  },
];

export function SkidConfigurationSection({
  state,
  onChange,
}: SkidConfigurationSectionProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <Settings2 className="size-5" />
          </div>

          <div>
            <CardTitle>
              Skid Configuration & Instrumentation
            </CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Record receiver provisions, measurement instrumentation,
              dew-point monitoring, and master-control configuration
              used by the skid adequacy assessment.
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2">
          {configurationItems.map((item) => (
            <label
              key={item.key}
              className="flex cursor-pointer items-start gap-4 rounded-xl border border-slate-200 p-4 transition-colors hover:bg-slate-50"
            >
              <input
                type="checkbox"
                checked={state[item.key]}
                onChange={(event) =>
                  onChange({
                    [item.key]: event.target.checked,
                  })
                }
                className="mt-1 size-4 rounded border-slate-300"
              />

              <div>
                <Label className="cursor-pointer text-sm font-semibold text-slate-900">
                  {item.label}
                </Label>

                <p className="mt-1 text-xs leading-5 text-slate-500">
                  {item.description}
                </p>
              </div>
            </label>
          ))}
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-xl border border-slate-200 p-4">
            <div className="flex items-center gap-2">
              <Gauge className="size-4 text-slate-600" />

              <p className="text-sm font-semibold text-slate-900">
                Instrumentation completeness
              </p>
            </div>

            <p className="mt-2 text-xs leading-5 text-slate-500">
              Flow metering, pressure monitoring, and dew-point
              monitoring must all be configured and represented by
              corresponding registered skid components for the backend
              assessment to report instrumentation as complete.
            </p>
          </div>

          <div className="rounded-xl border border-slate-200 p-4">
            <div className="flex items-center gap-2">
              <Activity className="size-4 text-slate-600" />

              <p className="text-sm font-semibold text-slate-900">
                Configuration cross-check
              </p>
            </div>

            <p className="mt-2 text-xs leading-5 text-slate-500">
              Receiver and instrumentation selections are cross-checked
              against the component register. A selected option without
              its corresponding component does not satisfy the skid
              assessment.
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
