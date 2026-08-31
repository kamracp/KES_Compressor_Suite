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

export type MotorPfcField =
  | "motorMeasuredVoltageV"
  | "motorMeasuredCurrentA"
  | "motorMeasuredPowerFactor"
  | "motorTargetPowerFactor"
  | "motorRatedPowerKw"
  | "pfPenaltyAnnualCost";

type MotorPfcSectionProps = {
  motorMeasuredVoltageV: string;
  motorMeasuredCurrentA: string;
  motorMeasuredPowerFactor: string;
  motorTargetPowerFactor: string;
  motorRatedPowerKw: string;
  pfPenaltyAnnualCost: string;

  onChange: (field: MotorPfcField, value: string) => void;
};

export function MotorPfcSection({
  motorMeasuredVoltageV,
  motorMeasuredCurrentA,
  motorMeasuredPowerFactor,
  motorTargetPowerFactor,
  motorRatedPowerKw,
  pfPenaltyAnnualCost,
  onChange,
}: MotorPfcSectionProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <Zap className="size-5" />
          </div>

          <div>
            <CardTitle>
              Motor Measurement & Power Factor
            </CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Optional. Enter clamp-meter readings at the compressor motor to
              compute measured active power and size the power-factor
              correction capacitor bank. Voltage, current and power factor
              must all be present for the analysis to run.
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <section>
          <h3 className="mb-4 text-sm font-semibold text-slate-900">
            Field Measurements (three-phase)
          </h3>

          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="brownfield-motor-voltage">
                Measured Voltage
              </Label>

              <Input
                id="brownfield-motor-voltage"
                type="number"
                min="0"
                step="any"
                value={motorMeasuredVoltageV}
                placeholder="Example: 415"
                onChange={(event) =>
                  onChange("motorMeasuredVoltageV", event.target.value)
                }
              />

              <p className="text-xs leading-5 text-slate-500">
                Line-to-line volts at the motor terminals.
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="brownfield-motor-current">
                Measured Current
              </Label>

              <Input
                id="brownfield-motor-current"
                type="number"
                min="0"
                step="any"
                value={motorMeasuredCurrentA}
                placeholder="Example: 78"
                onChange={(event) =>
                  onChange("motorMeasuredCurrentA", event.target.value)
                }
              />

              <p className="text-xs leading-5 text-slate-500">
                Line amps under the load condition being assessed.
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="brownfield-motor-pf">
                Measured Power Factor
              </Label>

              <Input
                id="brownfield-motor-pf"
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={motorMeasuredPowerFactor}
                placeholder="Example: 0.82"
                onChange={(event) =>
                  onChange("motorMeasuredPowerFactor", event.target.value)
                }
              />

              <p className="text-xs leading-5 text-slate-500">
                0–1 · P = √3 × V × I × PF (IEEE Std 141)
              </p>
            </div>
          </div>
        </section>

        <section className="border-t border-slate-100 pt-6">
          <h3 className="mb-4 text-sm font-semibold text-slate-900">
            Correction Target & Tariff Penalty
          </h3>

          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="brownfield-motor-target-pf">
                Target Power Factor
              </Label>

              <Input
                id="brownfield-motor-target-pf"
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={motorTargetPowerFactor}
                onChange={(event) =>
                  onChange("motorTargetPowerFactor", event.target.value)
                }
              />

              <p className="text-xs leading-5 text-slate-500">
                Capacitor sizing: Qc = P × (tan φ₁ − tan φ₂), IS 15167.
                Set this to whatever your own utility tariff requires.
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="brownfield-motor-nameplate">
                Motor Nameplate Power
              </Label>

              <Input
                id="brownfield-motor-nameplate"
                type="number"
                min="0"
                step="any"
                value={motorRatedPowerKw}
                placeholder="Optional"
                onChange={(event) =>
                  onChange("motorRatedPowerKw", event.target.value)
                }
              />

              <p className="text-xs leading-5 text-slate-500">
                kW. Used only to report how far measured power sits from
                nameplate.
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="brownfield-pf-penalty">
                Annual PF Penalty Billed
              </Label>

              <Input
                id="brownfield-pf-penalty"
                type="number"
                min="0"
                step="any"
                value={pfPenaltyAnnualCost}
                placeholder="Optional"
                onChange={(event) =>
                  onChange("pfPenaltyAnnualCost", event.target.value)
                }
              />

              <p className="text-xs leading-5 text-slate-500">
                Currency units/year, from your electricity bill. Left blank,
                no penalty saving is claimed.
              </p>
            </div>
          </div>
        </section>

        <div className="rounded-lg border border-dashed border-slate-300 p-4">
          <p className="text-sm font-medium text-slate-800">
            What power-factor correction does and does not save
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            A capacitor bank supplies reactive current locally, reducing line
            current, cable and transformer loading, distribution losses and
            the utility power-factor penalty. It does not reduce the motor's
            active power draw, so no kW or kWh saving is reported for this
            opportunity. The only rupee figure carried into the register is
            the penalty you enter above.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
