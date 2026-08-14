import { Gauge, TrendingUp } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export type GreenfieldDesignBasis = {
  minimumPointOfUsePressureBarG: string;
  leakageFraction: string;
  futureExpansionFraction: string;
  otherAllowanceFraction: string;
  controlMarginBar: string;
  annualOperatingDays: string;
  electricityTariffPerKwh: string;
};

type DesignBasisSectionProps = {
  value: GreenfieldDesignBasis;
  onChange: (
    field: keyof GreenfieldDesignBasis,
    value: string,
  ) => void;
};

type DecimalFieldProps = {
  id: string;
  label: string;
  value: string;
  description: string;
  unit?: string;
  min?: string;
  max?: string;
  step?: string;
  onChange: (value: string) => void;
};

function DecimalField({
  id,
  label,
  value,
  description,
  unit,
  min,
  max,
  step = "any",
  onChange,
}: DecimalFieldProps) {
  return (
    <div className="space-y-2">
      <Label htmlFor={id}>
        {label}
      </Label>

      <div className="relative">
        <Input
          id={id}
          type="number"
          inputMode="decimal"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          className={unit ? "pr-20" : undefined}
        />

        {unit && (
          <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-xs font-medium text-slate-500">
            {unit}
          </span>
        )}
      </div>

      <p className="text-xs leading-5 text-slate-500">
        {description}
      </p>
    </div>
  );
}

export function DesignBasisSection({
  value,
  onChange,
}: DesignBasisSectionProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <Gauge className="size-5" />
          </div>

          <div>
            <CardTitle>
              Design Basis
            </CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Establish the pressure, demand allowances, operating schedule,
              and electricity-cost basis used by the Greenfield compressed-air
              system design engine.
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <section>
          <div className="mb-4 flex items-center gap-2">
            <Gauge className="size-4 text-slate-500" />

            <h3 className="text-sm font-semibold text-slate-900">
              Pressure Basis
            </h3>
          </div>

          <div className="grid gap-5 md:grid-cols-2">
            <DecimalField
              id="minimum-point-of-use-pressure"
              label="Minimum Point-of-Use Pressure"
              value={value.minimumPointOfUsePressureBarG}
              unit="bar(g)"
              min="0"
              description="Minimum pressure that must remain available at the critical consumer."
              onChange={(nextValue) =>
                onChange(
                  "minimumPointOfUsePressureBarG",
                  nextValue,
                )
              }
            />

            <DecimalField
              id="control-margin"
              label="Control Margin"
              value={value.controlMarginBar}
              unit="bar"
              min="0"
              description="Additional pressure allowance for stable compressor-station and system control."
              onChange={(nextValue) =>
                onChange("controlMarginBar", nextValue)
              }
            />
          </div>
        </section>

        <section className="border-t border-slate-100 pt-6">
          <div className="mb-4 flex items-center gap-2">
            <TrendingUp className="size-4 text-slate-500" />

            <h3 className="text-sm font-semibold text-slate-900">
              Demand Allowances
            </h3>
          </div>

          <div className="grid gap-5 md:grid-cols-3">
            <DecimalField
              id="leakage-fraction"
              label="Design Leakage Allowance"
              value={value.leakageFraction}
              min="0"
              max="1"
              step="0.01"
              description="Fractional allowance included in the new-system design demand."
              onChange={(nextValue) =>
                onChange("leakageFraction", nextValue)
              }
            />

            <DecimalField
              id="future-expansion-fraction"
              label="Future Expansion Allowance"
              value={value.futureExpansionFraction}
              min="0"
              max="1"
              step="0.01"
              description="Capacity allowance reserved for planned or foreseeable future production growth."
              onChange={(nextValue) =>
                onChange(
                  "futureExpansionFraction",
                  nextValue,
                )
              }
            />

            <DecimalField
              id="other-allowance-fraction"
              label="Other Design Allowance"
              value={value.otherAllowanceFraction}
              min="0"
              max="1"
              step="0.01"
              description="Additional engineering allowance where the design basis requires it."
              onChange={(nextValue) =>
                onChange(
                  "otherAllowanceFraction",
                  nextValue,
                )
              }
            />
          </div>
        </section>

        <section className="border-t border-slate-100 pt-6">
          <h3 className="mb-4 text-sm font-semibold text-slate-900">
            Operating & Cost Basis
          </h3>

          <div className="grid gap-5 md:grid-cols-2">
            <DecimalField
              id="annual-operating-days"
              label="Annual Operating Days"
              value={value.annualOperatingDays}
              unit="days/yr"
              min="1"
              max="366"
              step="1"
              description="Operating days used by the annual energy calculation."
              onChange={(nextValue) =>
                onChange("annualOperatingDays", nextValue)
              }
            />

            <DecimalField
              id="electricity-tariff"
              label="Electricity Tariff"
              value={value.electricityTariffPerKwh}
              unit="/kWh"
              min="0"
              description="Electricity cost basis used for annual operating-cost evaluation."
              onChange={(nextValue) =>
                onChange(
                  "electricityTariffPerKwh",
                  nextValue,
                )
              }
            />
          </div>
        </section>
      </CardContent>
    </Card>
  );
}
