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
        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">
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

          <div className="space-y-2">
            <Label htmlFor="leakage-control-factor">
              Control Factor
            </Label>

            <Input
              id="leakage-control-factor"
              type="number"
              min="0"
              max="1"
              step="0.05"
              value={state.demandSavingControlFactor}
              placeholder="Example: 0.5"
              onChange={(event) =>
                onChange({
                  demandSavingControlFactor:
                    event.target.value,
                })
              }
            />

            <p className="text-xs leading-5 text-slate-500">
              0 – 1 &nbsp;·&nbsp; VSD/on-off ≈ 1.0, load/unload 0.3 – 0.6,
              inlet modulation ≈ 0.3
            </p>
          </div>
        </div>

        <div className="mt-6 rounded-lg border border-dashed border-slate-300 p-4">
          <p className="text-sm font-medium text-slate-800">
            Energy calculation basis
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            The leakage engine converts registered leakage flow to
            equivalent compressor power using specific power, then
            annualizes energy and cost using operating hours and
            electricity tariff. Recoverable electrical savings are
            scaled by the control factor — the fraction of reduced
            air demand that the compressor controls actually convert
            into reduced power draw. Air flow quantities remain
            physical regardless of the factor.
          </p>

          <p className="mt-2 text-xs leading-5 text-slate-400">
            Guidance: US DOE / Compressed Air Challenge, &ldquo;Improving
            Compressed Air System Performance: A Sourcebook for
            Industry.&rdquo; VSD or on/off ≈ 1.0 · load/unload 0.3 – 0.6
            · inlet modulation without unloading ≈ 0.3.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
