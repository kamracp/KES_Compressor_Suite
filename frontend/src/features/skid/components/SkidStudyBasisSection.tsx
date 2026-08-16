import { ClipboardCheck } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import { dryerTypeOptions } from "../../greenfield/greenfieldOptions";
import type { SkidFormState } from "../skidFormState";
import type {
  DryerType,
  SkidArrangement,
} from "../skidTypes";

type SkidStudyBasisSectionProps = {
  state: SkidFormState;
  onChange: (changes: Partial<SkidFormState>) => void;
};

const arrangementOptions: {
  value: SkidArrangement;
  label: string;
}[] = [
  { value: "CENTRALIZED", label: "Centralized" },
  { value: "DECENTRALIZED", label: "Decentralized" },
  { value: "HYBRID", label: "Hybrid" },
];

export function SkidStudyBasisSection({
  state,
  onChange,
}: SkidStudyBasisSectionProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <ClipboardCheck className="size-5" />
          </div>

          <div>
            <CardTitle>
              Skid Engineering Study Basis
            </CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Define the compressed-air skid reference, station
              arrangement, design flow, design pressure, dryer
              technology, and engineering scope.
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          <div className="space-y-2">
            <Label htmlFor="skid-code">
              Skid Code
            </Label>

            <Input
              id="skid-code"
              value={state.skidCode}
              placeholder="Example: SKID-001"
              onChange={(event) =>
                onChange({
                  skidCode: event.target.value,
                })
              }
            />

            <p className="text-xs leading-5 text-slate-500">
              Unique engineering reference for the skid or
              compressed-air station configuration.
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="skid-arrangement">
              Station Arrangement
            </Label>

            <select
              id="skid-arrangement"
              value={state.arrangement}
              onChange={(event) =>
                onChange({
                  arrangement:
                    event.target.value as SkidArrangement,
                })
              }
              className="h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
            >
              {arrangementOptions.map((option) => (
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
            <Label htmlFor="skid-dryer-type">
              Dryer Technology
            </Label>

            <select
              id="skid-dryer-type"
              value={state.dryerType}
              onChange={(event) =>
                onChange({
                  dryerType:
                    event.target.value as DryerType,
                })
              }
              className="h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
            >
              {dryerTypeOptions.map((option) => (
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

        <div className="grid gap-5 md:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="skid-design-flow">
              Design Flow
            </Label>

            <Input
              id="skid-design-flow"
              type="number"
              min="0"
              step="any"
              value={state.designFlowNm3PerHr}
              placeholder="Example: 5000"
              onChange={(event) =>
                onChange({
                  designFlowNm3PerHr: event.target.value,
                })
              }
            />

            <p className="text-xs text-slate-500">
              Nm³/h
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="skid-design-pressure">
              Design Pressure
            </Label>

            <Input
              id="skid-design-pressure"
              type="number"
              min="0"
              step="any"
              value={state.designPressureBarG}
              placeholder="Example: 7.0"
              onChange={(event) =>
                onChange({
                  designPressureBarG: event.target.value,
                })
              }
            />

            <p className="text-xs text-slate-500">
              bar(g)
            </p>
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="skid-description">
            Engineering Description
          </Label>

          <Input
            id="skid-description"
            value={state.description}
            placeholder="System boundary, operating philosophy, skid scope..."
            onChange={(event) =>
              onChange({
                description: event.target.value,
              })
            }
          />
        </div>

        <div className="rounded-lg border border-dashed border-slate-300 p-4">
          <p className="text-sm font-medium text-slate-800">
            Assessment basis
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            The skid assessment compares recorded component flow
            capacities and pressure ratings with the stated design
            basis and evaluates configured instrumentation and receiver
            provisions. Results remain vendor-neutral engineering
            guidance.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
