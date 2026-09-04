import {
  BadgeIndianRupee,
  Settings2,
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

type OptimizationBasisSectionProps = {
  auditCode: string;
  annualOperatingHours: string;
  electricityTariffPerKwh: string;
  inputOptions?: InputOptionsResponse;
  supplyPhase: SupplyPhase;
  nominalSupplyVoltageV: number;
  supplyFrequencyHz: number;
  optimizedDischargePressureBarG: string;
  expectedLeakRepairFraction: string;
  demandSavingControlFactor: string;
  powerPenaltyFractionPerBar: string;
  notes: string;

  onAuditCodeChange: (value: string) => void;
  onAnnualOperatingHoursChange: (value: string) => void;
  onElectricityTariffChange: (value: string) => void;
  onSupplyBasisChange: (changes: {
    supplyPhase?: SupplyPhase;
    nominalSupplyVoltageV?: number;
    supplyFrequencyHz?: number;
  }) => void;
  onOptimizedPressureChange: (value: string) => void;
  onExpectedLeakRepairFractionChange: (value: string) => void;
  onDemandSavingControlFactorChange: (value: string) => void;
  onPowerPenaltyFractionPerBarChange: (value: string) => void;
  onNotesChange: (value: string) => void;
};

export function OptimizationBasisSection({
  auditCode,
  annualOperatingHours,
  electricityTariffPerKwh,
  inputOptions,
  supplyPhase,
  nominalSupplyVoltageV,
  supplyFrequencyHz,
  optimizedDischargePressureBarG,
  expectedLeakRepairFraction,
  demandSavingControlFactor,
  powerPenaltyFractionPerBar,
  notes,
  onAuditCodeChange,
  onAnnualOperatingHoursChange,
  onElectricityTariffChange,
  onSupplyBasisChange,
  onOptimizedPressureChange,
  onExpectedLeakRepairFractionChange,
  onDemandSavingControlFactorChange,
  onPowerPenaltyFractionPerBarChange,
  onNotesChange,
}: OptimizationBasisSectionProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <Settings2 className="size-5" />
          </div>

          <div>
            <CardTitle>
              Audit & Optimization Basis
            </CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Define the Brownfield audit reference, annual operating basis,
              electricity cost, and optional optimization assumptions used for
              energy and opportunity analysis.
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <section>
          <h3 className="mb-4 text-sm font-semibold text-slate-900">
            Audit Identification
          </h3>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="brownfield-audit-code">
                Audit Code
              </Label>

              <Input
                id="brownfield-audit-code"
                value={auditCode}
                placeholder="Example: BF-2026-001"
                onChange={(event) =>
                  onAuditCodeChange(event.target.value)
                }
              />

              <p className="text-xs text-slate-500">
                Unique engineering reference for this Brownfield assessment.
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="brownfield-notes">
                Audit Notes
              </Label>

              <Input
                id="brownfield-notes"
                value={notes}
                placeholder="Plant condition, audit scope, operating assumptions..."
                onChange={(event) =>
                  onNotesChange(event.target.value)
                }
              />
            </div>
          </div>
        </section>

        <section className="border-t border-slate-100 pt-6">
          <div className="mb-4 flex items-center gap-2">
            <BadgeIndianRupee className="size-4 text-slate-500" />

            <h3 className="text-sm font-semibold text-slate-900">
              Annual Energy & Cost Basis
            </h3>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="brownfield-annual-hours">
                Annual Operating Hours
              </Label>

              <Input
                id="brownfield-annual-hours"
                type="number"
                min="0.01"
                step="any"
                value={annualOperatingHours}
                onChange={(event) =>
                  onAnnualOperatingHoursChange(
                    event.target.value,
                  )
                }
              />

              <p className="text-xs text-slate-500">
                hours/year
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="brownfield-tariff">
                Electricity Tariff
              </Label>

              <select
                id="brownfield-tariff"
                className={SELECT_CLASS}
                value={electricityTariffPerKwh}
                disabled={!inputOptions}
                onChange={(event) => onElectricityTariffChange(event.target.value)}
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

              <p className="text-xs text-slate-500">
                INR/kWh
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="brownfield-supply-phase">Supply Phase</Label>
              <select
                id="brownfield-supply-phase"
                className={SELECT_CLASS}
                value={supplyPhase}
                disabled={!inputOptions}
                onChange={(event) => {
                  const phase = event.target.value as SupplyPhase;
                  onSupplyBasisChange({
                    supplyPhase: phase,
                    nominalSupplyVoltageV: defaultVoltageForPhase(phase),
                  });
                }}
              >
                {inputOptions?.supply_phase.map((phase) => (
                  <option key={phase} value={phase}>
                    {phaseLabel(phase)}
                  </option>
                ))}
              </select>
              <p className="text-xs text-slate-500">IS 12360</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="brownfield-supply-voltage">Nominal Voltage</Label>
              <select
                id="brownfield-supply-voltage"
                className={SELECT_CLASS}
                value={String(nominalSupplyVoltageV)}
                disabled={!inputOptions}
                onChange={(event) =>
                  onSupplyBasisChange({
                    nominalSupplyVoltageV: Number(event.target.value),
                  })
                }
              >
                {voltagesForPhase(
                  inputOptions?.nominal_supply_voltage_v ?? [],
                  supplyPhase,
                ).map((voltage) => (
                  <option key={voltage} value={voltage}>
                    {voltageLabel(voltage)}
                  </option>
                ))}
              </select>
              <p className="text-xs text-slate-500">Line-to-line, IS 12360</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="brownfield-supply-frequency">Frequency</Label>
              <select
                id="brownfield-supply-frequency"
                className={SELECT_CLASS}
                value={String(supplyFrequencyHz)}
                disabled={!inputOptions}
                onChange={(event) =>
                  onSupplyBasisChange({
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
              <p className="text-xs text-slate-500">Hz</p>
            </div>
          </div>
        </section>

        <section className="border-t border-slate-100 pt-6">
          <h3 className="mb-4 text-sm font-semibold text-slate-900">
            Optimization Assumptions
          </h3>

          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="brownfield-optimized-pressure">
                Optimized Discharge Pressure
              </Label>

              <Input
                id="brownfield-optimized-pressure"
                type="number"
                min="0"
                step="any"
                value={optimizedDischargePressureBarG}
                placeholder="Optional"
                onChange={(event) =>
                  onOptimizedPressureChange(
                    event.target.value,
                  )
                }
              />

              <p className="text-xs leading-5 text-slate-500">
                bar(g). Leave blank when pressure-reduction analysis is not
                required.
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="brownfield-leak-repair">
                Expected Leak Repair Fraction
              </Label>

              <Input
                id="brownfield-leak-repair"
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={expectedLeakRepairFraction}
                onChange={(event) =>
                  onExpectedLeakRepairFractionChange(
                    event.target.value,
                  )
                }
              />

              <p className="text-xs leading-5 text-slate-500">
                Fraction of identified leakage expected to be recoverable.
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="brownfield-control-factor">
                Control Factor
              </Label>

              <Input
                id="brownfield-control-factor"
                type="number"
                min="0"
                max="1"
                step="0.05"
                value={demandSavingControlFactor}
                onChange={(event) =>
                  onDemandSavingControlFactorChange(
                    event.target.value,
                  )
                }
              />

              <p className="text-xs leading-5 text-slate-500">
                0–1 · VSD/on-off ≈ 1.0,
                load/unload 0.3–0.6,
                inlet modulation ≈ 0.3
                (DOE / Compressed Air Challenge)
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="brownfield-pressure-penalty">
                Power Penalty Fraction / bar
              </Label>

              <Input
                id="brownfield-pressure-penalty"
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={powerPenaltyFractionPerBar}
                onChange={(event) =>
                  onPowerPenaltyFractionPerBarChange(
                    event.target.value,
                  )
                }
              />

              <p className="text-xs leading-5 text-slate-500">
                Leave blank to use the adiabatic isentropic-work method
                (recommended); enter a fraction per bar only to force the
                legacy linear rule of thumb.
              </p>
            </div>
          </div>
        </section>

        <div className="rounded-lg border border-dashed border-slate-300 p-4">
          <p className="text-sm font-medium text-slate-800">
            Engineering-use boundary
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            The optimized pressure is an engineering scenario input, not an
            automatically determined safe operating pressure. Distribution
            losses, point-of-use requirements, controls, and process pressure
            requirements must be reviewed before adopting a lower pressure
            setpoint.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
