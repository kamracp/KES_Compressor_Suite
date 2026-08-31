import {
  AlertTriangle,
  CheckCircle2,
  CircleDashed,
  Gauge,
  Lightbulb,
  TrendingDown,
  Zap,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

import {
  opportunityCategoryLabels,
  opportunityPriorityLabels,
} from "../brownfieldOptions";
import type {
  BrownfieldOpportunityPriority,
  BrownfieldSystemAuditResponse,
} from "../brownfieldTypes";

type BrownfieldEngineeringReviewSectionProps = {
  result: BrownfieldSystemAuditResponse | null;
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
  value: string,
  maximumFractionDigits = 1,
): string {
  const numericValue = Number(value);

  if (!Number.isFinite(numericValue)) {
    return value;
  }

  return (numericValue * 100).toLocaleString("en-IN", {
    maximumFractionDigits,
  });
}

function priorityVariant(
  priority: BrownfieldOpportunityPriority,
): "destructive" | "secondary" | "outline" {
  if (priority === "HIGH") {
    return "destructive";
  }

  if (priority === "MEDIUM") {
    return "secondary";
  }

  return "outline";
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

export function BrownfieldEngineeringReviewSection({
  result,
  isPending,
  errorMessage,
}: BrownfieldEngineeringReviewSectionProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <Gauge className="size-5" />
          </div>

          <div>
            <CardTitle>
              Brownfield Engineering Review
            </CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Review measured plant performance, compressor-station
              utilization, leakage and unloaded-running indicators, current
              energy baseline, optimization potential, and prioritized
              engineering opportunities.
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
                  Brownfield analysis failed
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
              Brownfield analysis not yet executed
            </p>

            <p className="mx-auto mt-2 max-w-xl text-xs leading-5 text-slate-500">
              Complete the existing-equipment and plant measurement basis,
              then run the Brownfield audit to generate measured performance
              and opportunity results.
            </p>
          </div>
        )}

        {!isPending && !errorMessage && result && (
          <>
            <section>
              <div className="mb-4 flex items-center gap-2">
                <Gauge className="size-4 text-slate-500" />

                <h3 className="text-sm font-semibold text-slate-900">
                  Capacity & Demand
                </h3>
              </div>

              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <Metric
                  label="Installed Capacity"
                  value={formatDecimal(
                    result.installed_capacity_nm3_per_hr,
                  )}
                  unit="Nm³/h"
                />

                <Metric
                  label="Available Capacity"
                  value={formatDecimal(
                    result.available_capacity_nm3_per_hr,
                  )}
                  unit="Nm³/h"
                />

                <Metric
                  label="Average System Flow"
                  value={formatDecimal(
                    result.average_system_flow_nm3_per_hr,
                  )}
                  unit="Nm³/h"
                />

                <Metric
                  label="Peak System Flow"
                  value={formatDecimal(
                    result.peak_system_flow_nm3_per_hr,
                  )}
                  unit="Nm³/h"
                />
              </div>

              <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <Metric
                  label="Minimum System Flow"
                  value={formatDecimal(
                    result.minimum_system_flow_nm3_per_hr,
                  )}
                  unit="Nm³/h"
                />

                <Metric
                  label="Average Utilization"
                  value={`${formatPercent(
                    result.average_capacity_utilization_fraction,
                  )}%`}
                />

                <Metric
                  label="Peak Utilization"
                  value={`${formatPercent(
                    result.peak_capacity_utilization_fraction,
                  )}%`}
                />

                <Metric
                  label="Peak Capacity Status"
                  value={
                    result.installed_capacity_is_sufficient_for_peak
                      ? "Sufficient"
                      : "Review Required"
                  }
                />
              </div>
            </section>

            <section className="border-t border-slate-100 pt-6">
              <h3 className="mb-4 text-sm font-semibold text-slate-900">
                Measured Performance
              </h3>

              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <Metric
                  label="Average System Power"
                  value={formatDecimal(
                    result.average_system_power_kw,
                  )}
                  unit="kW"
                />

                <Metric
                  label="Peak System Power"
                  value={formatDecimal(
                    result.peak_system_power_kw,
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
                  label="Unloaded Observations"
                  value={`${formatPercent(
                    result.unloaded_measurement_fraction,
                  )}%`}
                />
              </div>

              <div className="mt-4 grid gap-4 sm:grid-cols-3">
                <Metric
                  label="Average Header Pressure"
                  value={formatDecimal(
                    result.average_header_pressure_bar_g,
                    3,
                  )}
                  unit="bar(g)"
                />

                <Metric
                  label="Minimum Header Pressure"
                  value={formatDecimal(
                    result.minimum_header_pressure_bar_g,
                    3,
                  )}
                  unit="bar(g)"
                />

                <Metric
                  label="Maximum Header Pressure"
                  value={formatDecimal(
                    result.maximum_header_pressure_bar_g,
                    3,
                  )}
                  unit="bar(g)"
                />
              </div>
            </section>

            <section className="border-t border-slate-100 pt-6">
              <h3 className="mb-4 text-sm font-semibold text-slate-900">
                System Loss Indicators
              </h3>

              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <Metric
                  label="Leakage Flow"
                  value={formatDecimal(
                    result.leakage_flow_nm3_per_hr,
                  )}
                  unit="Nm³/h"
                />

                <Metric
                  label="Leakage vs Average Demand"
                  value={`${formatPercent(
                    result.leakage_fraction_of_average_demand,
                  )}%`}
                />

                <Metric
                  label="Leakage Status"
                  value={
                    result.significant_leakage_detected
                      ? "Significant"
                      : "No Significant Flag"
                  }
                />

                <Metric
                  label="Unloaded Running Status"
                  value={
                    result.high_unloaded_running_detected
                      ? "High"
                      : "No High-Unload Flag"
                  }
                />
              </div>

              <div className="mt-4 flex flex-wrap gap-2">
                <Badge
                  variant={
                    result.significant_leakage_detected
                      ? "destructive"
                      : "secondary"
                  }
                >
                  {result.significant_leakage_detected
                    ? "Leakage Review Required"
                    : "Leakage Threshold Not Triggered"}
                </Badge>

                <Badge
                  variant={
                    result.high_unloaded_running_detected
                      ? "destructive"
                      : "secondary"
                  }
                >
                  {result.high_unloaded_running_detected
                    ? "Unloaded Running Review Required"
                    : "Unload Threshold Not Triggered"}
                </Badge>

                <Badge
                  variant={
                    result.installed_capacity_is_sufficient_for_peak
                      ? "secondary"
                      : "destructive"
                  }
                >
                  {result.installed_capacity_is_sufficient_for_peak
                    ? "Peak Capacity Adequate"
                    : "Peak Capacity Deficit"}
                </Badge>
              </div>
            </section>

            <section className="border-t border-slate-100 pt-6">
              <div className="mb-4 flex items-center gap-2">
                <Zap className="size-4 text-slate-500" />

                <h3 className="text-sm font-semibold text-slate-900">
                  Current Energy Baseline
                </h3>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <Metric
                  label="Current Annual Energy"
                  value={formatDecimal(
                    result.current_annual_energy_kwh,
                    0,
                  )}
                  unit="kWh/year"
                />

                <Metric
                  label="Current Annual Energy Cost"
                  value={formatDecimal(
                    result.current_annual_energy_cost,
                    2,
                  )}
                  unit="currency units/year"
                />
              </div>
            </section>

            <section className="border-t border-slate-100 pt-6">
              <div className="mb-4 flex items-center gap-2">
                <TrendingDown className="size-4 text-slate-500" />

                <h3 className="text-sm font-semibold text-slate-900">
                  Estimated Optimization Potential
                </h3>
              </div>

              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <Metric
                  label="Estimated Power Saving"
                  value={formatDecimal(
                    result.estimated_total_power_saving_kw,
                  )}
                  unit="kW"
                />

                <Metric
                  label="Annual Energy Saving"
                  value={formatDecimal(
                    result.estimated_total_annual_energy_saving_kwh,
                    0,
                  )}
                  unit="kWh/year"
                />

                <Metric
                  label="Annual Cost Saving"
                  value={formatDecimal(
                    result.estimated_total_annual_cost_saving,
                    2,
                  )}
                  unit="currency units/year"
                />

                <Metric
                  label="Estimated Energy Reduction"
                  value={`${formatPercent(
                    result.estimated_energy_reduction_fraction,
                  )}%`}
                />
              </div>

              <div className="mt-4 grid gap-4 sm:grid-cols-3">
                <Metric
                  label="Optimized Average Power"
                  value={formatDecimal(
                    result.estimated_optimized_average_power_kw,
                  )}
                  unit="kW"
                />

                <Metric
                  label="Optimized Annual Energy"
                  value={formatDecimal(
                    result.estimated_optimized_annual_energy_kwh,
                    0,
                  )}
                  unit="kWh/year"
                />

                <Metric
                  label="Optimized Annual Energy Cost"
                  value={formatDecimal(
                    result.estimated_optimized_annual_energy_cost,
                    2,
                  )}
                  unit="currency units/year"
                />
              </div>
            </section>

            {result.motor_pfc && (
              <section className="border-t border-slate-100 pt-6">
                <div className="mb-4 flex items-center gap-2">
                  <Zap className="size-4 text-slate-500" />

                  <h3 className="text-sm font-semibold text-slate-900">
                    Motor Measurement & Power Factor
                  </h3>
                </div>

                <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                  <Metric
                    label="Measured Active Power"
                    value={formatDecimal(
                      result.motor_pfc.measured_active_power_kw,
                    )}
                    unit="kW · P = sqrt3 x V x I x PF"
                  />

                  <Metric
                    label="Measured Reactive Power"
                    value={formatDecimal(
                      result.motor_pfc.measured_reactive_power_kvar,
                    )}
                    unit="kVAr at measured PF"
                  />

                  <Metric
                    label="Required Capacitor Bank"
                    value={formatDecimal(
                      result.motor_pfc.required_capacitor_kvar,
                    )}
                    unit="kVAr · IS 15167"
                  />

                  <Metric
                    label="Measured / Target PF"
                    value={`${result.motor_pfc.measured_power_factor} / ${result.motor_pfc.target_power_factor}`}
                  />
                </div>

                {result.motor_pfc.power_deviation_from_nameplate && (
                  <div className="mt-4 sm:max-w-xs">
                    <Metric
                      label="Deviation from Nameplate"
                      value={`${formatPercent(
                        result.motor_pfc.power_deviation_from_nameplate,
                      )}%`}
                    />
                  </div>
                )}

                <p className="mt-4 text-xs leading-5 text-slate-500">
                  Power-factor correction reduces reactive current, cable and
                  transformer loading and the utility power-factor penalty. It
                  does not reduce the motor active power draw, so no kW or kWh
                  saving is reported against this finding.
                </p>
              </section>
            )}

            <section className="border-t border-slate-100 pt-6">
              <div className="mb-4 flex items-center gap-2">
                <Lightbulb className="size-4 text-slate-500" />

                <h3 className="text-sm font-semibold text-slate-900">
                  Prioritized Engineering Opportunities
                </h3>
              </div>

              {result.opportunities.length === 0 ? (
                <div className="rounded-xl border border-dashed border-slate-300 p-5">
                  <div className="flex items-start gap-3">
                    <CheckCircle2 className="mt-0.5 size-5 text-slate-500" />

                    <div>
                      <p className="text-sm font-medium text-slate-800">
                        No current rule-based opportunities triggered
                      </p>

                      <p className="mt-1 text-xs leading-5 text-slate-500">
                        The current Brownfield opportunity rules did not
                        identify a leakage, unloaded-running, pressure,
                        capacity, or utilization action from the supplied
                        audit data.
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {result.opportunities.map((opportunity) => (
                    <div
                      key={opportunity.opportunity_code}
                      className="rounded-xl border border-slate-200 p-5"
                    >
                      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                        <div>
                          <div className="flex flex-wrap gap-2">
                            <Badge
                              variant={priorityVariant(
                                opportunity.priority,
                              )}
                            >
                              {
                                opportunityPriorityLabels[
                                  opportunity.priority
                                ]
                              }{" "}
                              Priority
                            </Badge>

                            <Badge variant="outline">
                              {
                                opportunityCategoryLabels[
                                  opportunity.category
                                ]
                              }
                            </Badge>

                            <Badge variant="outline">
                              {opportunity.opportunity_code}
                            </Badge>
                          </div>

                          <h4 className="mt-3 text-base font-semibold text-slate-950">
                            {opportunity.title}
                          </h4>

                          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
                            {opportunity.rationale}
                          </p>
                        </div>
                      </div>

                      <div className="mt-5 grid gap-3 sm:grid-cols-3">
                        <div className="rounded-lg bg-slate-50 p-3">
                          <p className="text-xs text-slate-500">
                            Power Saving
                          </p>

                          <p className="mt-1 font-semibold text-slate-900">
                            {formatDecimal(
                              opportunity.estimated_power_saving_kw,
                            )}{" "}
                            kW
                          </p>
                        </div>

                        <div className="rounded-lg bg-slate-50 p-3">
                          <p className="text-xs text-slate-500">
                            Annual Energy Saving
                          </p>

                          <p className="mt-1 font-semibold text-slate-900">
                            {formatDecimal(
                              opportunity.estimated_annual_energy_saving_kwh,
                              0,
                            )}{" "}
                            kWh/year
                          </p>
                        </div>

                        <div className="rounded-lg bg-slate-50 p-3">
                          <p className="text-xs text-slate-500">
                            Annual Cost Saving
                          </p>

                          <p className="mt-1 font-semibold text-slate-900">
                            {formatDecimal(
                              opportunity.estimated_annual_cost_saving,
                              2,
                            )}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>

            <div className="rounded-lg border border-dashed border-slate-300 p-4">
              <p className="text-sm font-medium text-slate-800">
                Engineering interpretation boundary
              </p>

              <p className="mt-1 text-xs leading-5 text-slate-500">
                Opportunity values are engineering estimates generated from
                the current measured audit basis and rule-based models. They
                should be validated against plant operating requirements,
                measurements, implementation scope, and detailed engineering
                before investment decisions.
              </p>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
