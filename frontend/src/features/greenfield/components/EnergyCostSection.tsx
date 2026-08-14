import {
  IndianRupee,
  Zap,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

type EnergyCostSectionProps = {
  specificPowerKwPerNm3PerMin: string;
  annualOperatingDays: string;
  electricityTariffPerKwh: string;
  onSpecificPowerChange: (value: string) => void;
};

export function EnergyCostSection({
  specificPowerKwPerNm3PerMin,
  annualOperatingDays,
  electricityTariffPerKwh,
  onSpecificPowerChange,
}: EnergyCostSectionProps) {
  const energyCalculationEnabled =
    specificPowerKwPerNm3PerMin.trim() !== "";

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <Zap className="size-5" />
          </div>

          <div>
            <CardTitle>
              Energy & Operating Cost
            </CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Provide the compressor-station specific power when annual
              electrical energy consumption and operating cost are required
              from the Greenfield design engine.
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <section className="grid gap-5 lg:grid-cols-[1fr_1.3fr]">
          <div className="space-y-2">
            <Label htmlFor="greenfield-specific-power">
              Specific Power
            </Label>

            <div className="relative">
              <Input
                id="greenfield-specific-power"
                type="number"
                min="0.0001"
                step="any"
                value={specificPowerKwPerNm3PerMin}
                placeholder="Example: 6.5"
                onChange={(event) =>
                  onSpecificPowerChange(event.target.value)
                }
                className="pr-32"
              />

              <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-xs font-medium text-slate-500">
                kW/(Nm³/min)
              </span>
            </div>

            <p className="text-xs leading-5 text-slate-500">
              Use the applicable compressor or station specific-power basis
              for the proposed operating condition.
            </p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
              Cost Calculation Basis
            </p>

            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <div>
                <p className="text-xs text-slate-500">
                  Annual Operating Days
                </p>

                <p className="mt-1 text-lg font-semibold text-slate-900">
                  {annualOperatingDays || "Not defined"}
                </p>
              </div>

              <div>
                <p className="text-xs text-slate-500">
                  Electricity Tariff
                </p>

                <div className="mt-1 flex items-center gap-1">
                  <IndianRupee className="size-4 text-slate-500" />

                  <p className="text-lg font-semibold text-slate-900">
                    {electricityTariffPerKwh || "Not defined"}
                  </p>

                  <span className="text-xs text-slate-500">
                    /kWh
                  </span>
                </div>
              </div>
            </div>

            <p className="mt-4 text-xs leading-5 text-slate-500">
              Operating days and electricity tariff are maintained in the
              Design Basis and reused here to avoid duplicate engineering
              inputs.
            </p>
          </div>
        </section>

        <div
          className={
            energyCalculationEnabled
              ? "rounded-lg border border-emerald-200 bg-emerald-50 p-4"
              : "rounded-lg border border-dashed border-slate-300 p-4"
          }
        >
          <p className="text-sm font-medium text-slate-800">
            {energyCalculationEnabled
              ? "Annual energy evaluation enabled"
              : "Annual energy evaluation optional"}
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            {energyCalculationEnabled
              ? "The Greenfield request will include specific power and use the annual operating basis to calculate annual energy and electricity cost."
              : "Leave specific power blank when only hydraulic and capacity design is required. The backend will omit annual energy and cost results."}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
