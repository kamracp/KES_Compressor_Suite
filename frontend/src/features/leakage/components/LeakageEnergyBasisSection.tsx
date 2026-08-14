import { Zap } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import type { LeakageFormState } from "../leakageFormState";

type LeakageEnergyBasisSectionProps = {
  state: LeakageFormState;
  onChange: (changes: Partial<LeakageFormState>) => void;
};

export function LeakageEnergyBasisSection({
  state,
  onChange,
}: LeakageEnergyBasisSectionProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <Zap className="size-5" />
          </div>

          <div>
            <CardTitle>Leakage Energy Basis</CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Define the compressed-air specific power, annual operating
              period, and electricity tariff used to quantify leakage
              power, energy loss, operating cost, and recoverable savings.
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div className="grid gap-5 md:grid-cols-3">
          <div className="space-y-2">
            <Label htmlFor="leakage-specific-power">
              Specific Power
            </Label>

            <Input
              id="leakage-specific-power"
              type="number"
              min="0"
              step="any"
              value={state.specificPowerKwPerNm3PerMin}
              placeholder="Example: 6.5"
              onChange={(event) =>
                onChange({
                  specificPowerKwPerNm3PerMin:
                    event.target.value,
                })
              }
            />

            <p className="text-xs leading-5 text-slate-500">
              kW/(Nm³/min)
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="leakage-operating-hours">
              Annual Operating Hours
            </Label>

            <Input
              id="leakage-operating-hours"
              type="number"
              min="0"
              step="any"
              value={state.annualOperatingHours}
              placeholder="Example: 8000"
              onChange={(event) =>
                onChange({
                  annualOperatingHours: event.target.value,
                })
              }
            />

            <p className="text-xs leading-5 text-slate-500">
              h/year
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="leakage-electricity-tariff">
              Electricity Tariff
            </Label>

            <Input
              id="leakage-electricity-tariff"
              type="number"
              min="0"
              step="any"
              value={state.electricityTariffPerKwh}
              placeholder="Example: 8"
              onChange={(event) =>
                onChange({
                  electricityTariffPerKwh:
                    event.target.value,
                })
              }
            />

            <p className="text-xs leading-5 text-slate-500">
              Currency/kWh
            </p>
          </div>
        </div>

        <div className="mt-6 rounded-lg border border-dashed border-slate-300 p-4">
          <p className="text-sm font-medium text-slate-800">
            Energy calculation basis
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            The leakage engine converts registered leakage flow to
            equivalent compressor power using the entered specific
            power, then annualizes energy and cost using operating
            hours and electricity tariff.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
