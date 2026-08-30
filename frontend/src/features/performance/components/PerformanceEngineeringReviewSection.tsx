import {
  AlertTriangle,
  CircleDashed,
  Gauge,
  TrendingDown,
  Zap,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

import type {
  CompressedAirPerformanceAnalysisResponse,
} from "../performanceTypes";

type PerformanceEngineeringReviewSectionProps = {
  result: CompressedAirPerformanceAnalysisResponse | null;
  isPending: boolean;
  errorMessage: string | null;
};

type MetricProps = {
  label: string;
  value: string;
  unit?: string;
};

function formatDecimal(
  value: string | null,
  maximumFractionDigits = 2,
): string {
  if (value === null) {
    return "Not evaluated";
  }

  const numericValue = Number(value);

  if (!Number.isFinite(numericValue)) {
    return value;
  }

  return numericValue.toLocaleString("en-IN", {
    maximumFractionDigits,
  });
}

function formatPercent(
  value: string | null,
  maximumFractionDigits = 1,
): string {
  if (value === null) {
    return "Not evaluated";
  }

  const numericValue = Number(value);

  if (!Number.isFinite(numericValue)) {
    return value;
  }

  return `${(numericValue * 100).toLocaleString("en-IN", {
    maximumFractionDigits,
  })}%`;
}

function Metric({
  label,
  value,
  unit,
}: MetricProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <p className="text-xs font-medium text-slate-500">
        {label}
      </p>

      <p className="mt-2 text-2xl font-bold tracking-tight text-slate-950">
        {value}
      </p>

      {unit && (
        <p className="mt-1 text-xs font-medium text-slate-500">
          {unit}
        </p>
      )}
    </div>
  );
}

export function PerformanceEngineeringReviewSection({
  result,
  isPending,
  errorMessage,
}: PerformanceEngineeringReviewSectionProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <Gauge className="size-5" />
          </div>

          <div>
            <CardTitle>
              Performance & Energy Engineering Review
            </CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Review measured demand, pressure, power, specific performance,
              utilization, unloaded-operation indicators, annualized energy
              and cost, and the optional pressure-optimization scenario.
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-7">
        {isPending && (
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {Array.from({ length: 8 }).map((_, index) => (
              <Skeleton
                key={index}
                className="h-28 w-full"
              />
            ))}
          </div>
        )}

        {!isPending && errorMessage && (
          <div
            className="rounded-xl border border-red-200 bg-red-50 p-5"
            role="alert"
          >
            <div className="flex items-start gap-3">
              <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-700" />

              <div>
                <p className="font-semibold text-red-900">
                  Performance analysis failed
                </p>

                <p className="mt-1 text-sm leading-6 text-red-700">
                  {errorMessage}
                </p>
              </div>
            </div>
          </div>
        )}

        {!isPending && !errorMessage && !result && (
          <div className="rounded-xl border border-dashed border-slate-300 p-8 text-center">
            <CircleDashed className="mx-auto mb-3 size-7 text-slate-400" />

            <p className="text-sm font-semibold text-slate-800">
              Performance analysis not yet executed
            </p>

            <p className="mx-auto mt-2 max-w-xl text-xs leading-5 text-slate-500">
              Complete the measured operating points and annual energy basis,
              then run the analysis to generate performance and energy
              indicators.
            </p>
          </div>
        )}

        {!isPending && !errorMessage && result && (
          <>
            <section>
              <div className="mb-4 flex items-center gap-2">
                <Gauge className="size-4 text-slate-500" />

                <h3 className="text-sm font-semibold text-slate-900">
                  Flow & Pressure
                </h3>
              </div>

              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <Metric
                  label="Average Flow"
                  value={formatDecimal(
                    result.average_flow_nm3_per_hr,
                  )}
                  unit="Nm³/h"
                />

                <Metric
                  label="Peak Flow"
                  value={formatDecimal(
                    result.peak_flow_nm3_per_hr,
                  )}
                  unit="Nm³/h"
                />

                <Metric
                  label="Minimum Flow"
                  value={formatDecimal(
                    result.minimum_flow_nm3_per_hr,
                  )}
                  unit="Nm³/h"
                />

                <Metric
                  label="Average Pressure"
                  value={formatDecimal(
                    result.average_pressure_bar_g,
                    3,
                  )}
                  unit="bar(g)"
                />
              </div>

              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                <Metric
                  label="Minimum Pressure"
                  value={formatDecimal(
                    result.minimum_pressure_bar_g,
                    3,
                  )}
                  unit="bar(g)"
                />

                <Metric
                  label="Maximum Pressure"
                  value={formatDecimal(
                    result.maximum_pressure_bar_g,
                    3,
                  )}
                  unit="bar(g)"
                />
              </div>
            </section>

            <section className="border-t border-slate-100 pt-6">
              <div className="mb-4 flex items-center gap-2">
                <Zap className="size-4 text-slate-500" />

                <h3 className="text-sm font-semibold text-slate-900">
                  Measured Performance
                </h3>
              </div>

              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <Metric
                  label="Average Power"
                  value={formatDecimal(
                    result.average_power_kw,
                  )}
                  unit="kW"
                />

                <Metric
                  label="Peak Power"
                  value={formatDecimal(
                    result.peak_power_kw,
                  )}
                  unit="kW"
                />

                <Metric
                  label="Measured Specific Power"
                  value={formatDecimal(
                    result.measured_specific_power_kw_per_nm3_per_min,
                    3,
                  )}
                  unit={
                    result.measured_specific_power_kw_per_nm3_per_min
                      ? "kW/(Nm³/min)"
                      : undefined
                  }
                />

                <Metric
                  label="Measured Specific Energy"
                  value={formatDecimal(
                    result.measured_specific_energy_kwh_per_1000_nm3,
                    3,
                  )}
                  unit={
                    result.measured_specific_energy_kwh_per_1000_nm3
                      ? "kWh/1000 Nm³"
                      : undefined
                  }
                />
              </div>
            </section>

            <section className="border-t border-slate-100 pt-6">
              <h3 className="mb-4 text-sm font-semibold text-slate-900">
                Utilization & Operating State
              </h3>

              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <Metric
                  label="Average Capacity Utilization"
                  value={formatPercent(
                    result.average_capacity_utilization_fraction,
                  )}
                />

                <Metric
                  label="Peak Capacity Utilization"
                  value={formatPercent(
                    result.peak_capacity_utilization_fraction,
                  )}
                />

                <Metric
                  label="Average Power Utilization"
                  value={formatPercent(
                    result.average_power_utilization_fraction,
                  )}
                />

                <Metric
                  label="Unloaded Observations"
                  value={formatPercent(
                    result.unloaded_measurement_fraction,
                  )}
                />
              </div>

              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                <Metric
                  label="Average Load Fraction"
                  value={formatPercent(
                    result.average_load_fraction,
                  )}
                />

                <Metric
                  label="Specific Power Deviation"
                  value={formatPercent(
                    result.specific_power_deviation_fraction,
                  )}
                />
              </div>
            </section>

            <section className="border-t border-slate-100 pt-6">
              <div className="mb-4 flex items-center gap-2">
                <Zap className="size-4 text-slate-500" />

                <h3 className="text-sm font-semibold text-slate-900">
                  Annual Energy Baseline
                </h3>
              </div>

              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <Metric
                  label="Annual Operating Hours"
                  value={formatDecimal(
                    result.annual_operating_hours,
                    0,
                  )}
                  unit="h/year"
                />

                <Metric
                  label="Annual Energy"
                  value={formatDecimal(
                    result.annual_energy_kwh,
                    0,
                  )}
                  unit="kWh/year"
                />

                <Metric
                  label="Electricity Tariff"
                  value={formatDecimal(
                    result.electricity_tariff_per_kwh,
                    3,
                  )}
                  unit="currency/kWh"
                />

                <Metric
                  label="Annual Energy Cost"
                  value={formatDecimal(
                    result.annual_energy_cost,
                    0,
                  )}
                  unit="currency/year"
                />
              </div>
            </section>

            <section className="border-t border-slate-100 pt-6">
              <div className="mb-4 flex items-center gap-2">
                <TrendingDown className="size-4 text-slate-500" />

                <h3 className="text-sm font-semibold text-slate-900">
                  Pressure Optimization Scenario
                </h3>
              </div>

              {result.pressure_energy ? (
                <>
                  <p className="text-xs text-slate-500">
                    {result.pressure_energy.power_saving_method ===
                    "ADIABATIC_ISENTROPIC"
                      ? "Saving basis: adiabatic isentropic work ratio (air, k = 1.4)."
                      : "Saving basis: linear per-bar override supplied by the user."}
                  </p>

                  <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                    <Metric
                      label="Current Pressure"
                      value={formatDecimal(
                        result.pressure_energy
                          .current_discharge_pressure_bar_g,
                        3,
                      )}
                      unit="bar(g)"
                    />

                    <Metric
                      label="Scenario Pressure"
                      value={formatDecimal(
                        result.pressure_energy
                          .optimized_discharge_pressure_bar_g,
                        3,
                      )}
                      unit="bar(g)"
                    />

                    <Metric
                      label="Pressure Reduction"
                      value={formatDecimal(
                        result.pressure_energy
                          .pressure_reduction_bar,
                        3,
                      )}
                      unit="bar"
                    />

                    <Metric
                      label="Estimated Power Saving"
                      value={formatDecimal(
                        result.pressure_energy
                          .estimated_power_saving_kw,
                        3,
                      )}
                      unit="kW"
                    />
                  </div>

                  <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                    <Metric
                      label="Estimated Optimized Power"
                      value={formatDecimal(
                        result.pressure_energy
                          .estimated_optimized_power_kw,
                        3,
                      )}
                      unit="kW"
                    />

                    <Metric
                      label="Power Saving"
                      value={formatPercent(
                        result.pressure_energy
                          .power_saving_fraction,
                      )}
                    />

                    <Metric
                      label="Annual Energy Saving"
                      value={formatDecimal(
                        result.pressure_energy
                          .annual_energy_saving_kwh,
                        0,
                      )}
                      unit="kWh/year"
                    />

                    <Metric
                      label="Annual Cost Saving"
                      value={formatDecimal(
                        result.pressure_energy
                          .annual_cost_saving,
                        0,
                      )}
                      unit="currency/year"
                    />
                  </div>

                  <div className="mt-4 rounded-lg border border-dashed border-slate-300 p-4">
                    <p className="text-sm font-medium text-slate-800">
                      Scenario interpretation
                    </p>

                    <p className="mt-1 text-xs leading-5 text-slate-500">
                      {result.pressure_energy
                        .pressure_reduction_is_beneficial
                        ? "The entered lower-pressure scenario produces a positive calculated energy saving."
                        : "The entered pressure scenario does not produce a positive calculated energy saving."}
                      {" "}
                      Validate point-of-use pressure, network losses,
                      treatment pressure drop, control stability, and
                      production requirements before implementing any
                      pressure change.
                    </p>
                  </div>
                </>
              ) : (
                <div className="rounded-xl border border-dashed border-slate-300 p-6">
                  <p className="text-sm font-semibold text-slate-800">
                    No pressure scenario evaluated
                  </p>

                  <p className="mt-1 text-xs leading-5 text-slate-500">
                    Enter an optimized discharge-pressure scenario to evaluate
                    the corresponding estimated power, annual energy, and
                    annual cost impact.
                  </p>
                </div>
              )}
            </section>

            <div className="rounded-lg border border-dashed border-slate-300 p-4">
              <p className="text-sm font-medium text-slate-800">
                Engineering interpretation
              </p>

              <p className="mt-1 text-xs leading-5 text-slate-500">
                Results are calculated from the entered measurement points and
                reference values. The annual energy baseline extrapolates the
                arithmetic average measured power across the supplied annual
                operating hours; it is not a time-weighted result unless the
                measurement set itself represents equal time intervals.
              </p>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
