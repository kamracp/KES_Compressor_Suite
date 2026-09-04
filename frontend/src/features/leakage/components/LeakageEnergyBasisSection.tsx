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
import type {
  InputOptionsResponse,
  SupplyPhase,
} from "../../reference/referenceTypes";
import {
  SELECT_CLASS,
  defaultVoltageForPhase,
  phaseLabel,
  voltageLabel,
  voltagesForPhase,
} from "../../reference/supplyBasis";

type LeakageEnergyBasisSectionProps = {
  state: LeakageFormState;
  onChange: (changes: Partial<LeakageFormState>) => void;
  inputOptions?: InputOptionsResponse;
};

export function LeakageEnergyBasisSection({
  state,
  onChange,
  inputOptions,
}: LeakageEnergyBasisSectionProps) {
  const voltageOptions = voltagesForPhase(
    inputOptions?.nominal_supply_voltage_v ?? [],
    state.supplyPhase,
  );
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

            <select
              id="leakage-electricity-tariff"
              className={SELECT_CLASS}
              value={state.electricityTariffPerKwh}
              disabled={!inputOptions}
              onChange={(event) =>
                onChange({
                  electricityTariffPerKwh: event.target.value,
                })
              }
            >
              <option value="">
                {inputOptions ? "Select tariff" : "Loading..."}
              </option>
              {inputOptions?.electricity_tariff_inr_per_kwh.map((tariff) => (
                <option key={tariff} value={tariff}>
                  {tariff}
                </option>
              ))}
            </select>

            <p className="text-xs leading-5 text-slate-500">
              INR/kWh
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="leakage-supply-phase">Supply Phase</Label>

            <select
              id="leakage-supply-phase"
              className={SELECT_CLASS}
              value={state.supplyPhase}
              disabled={!inputOptions}
              onChange={(event) => {
                const supplyPhase = event.target.value as SupplyPhase;
                onChange({
                  supplyPhase,
                  nominalSupplyVoltageV: defaultVoltageForPhase(supplyPhase),
                });
              }}
            >
              {inputOptions?.supply_phase.map((phase) => (
                <option key={phase} value={phase}>
                  {phaseLabel(phase)}
                </option>
              ))}
            </select>

            <p className="text-xs leading-5 text-slate-500">IS 12360</p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="leakage-supply-voltage">Nominal Voltage</Label>

            <select
              id="leakage-supply-voltage"
              className={SELECT_CLASS}
              value={String(state.nominalSupplyVoltageV)}
              disabled={!inputOptions}
              onChange={(event) =>
                onChange({
                  nominalSupplyVoltageV: Number(event.target.value),
                })
              }
            >
              {voltageOptions.map((voltage) => (
                <option key={voltage} value={voltage}>
                  {voltageLabel(voltage)}
                </option>
              ))}
            </select>

            <p className="text-xs leading-5 text-slate-500">
              Line-to-line, IS 12360
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="leakage-supply-frequency">Frequency</Label>

            <select
              id="leakage-supply-frequency"
              className={SELECT_CLASS}
              value={String(state.supplyFrequencyHz)}
              disabled={!inputOptions}
              onChange={(event) =>
                onChange({
                  supplyFrequencyHz: Number(event.target.value),
                })
              }
            >
              {inputOptions?.supply_frequency_hz.map((hz) => (
                <option key={hz} value={hz}>
                  {hz} Hz
                </option>
              ))}
            </select>

            <p className="text-xs leading-5 text-slate-500">Hz</p>
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
