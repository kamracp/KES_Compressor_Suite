import {
  AlertTriangle,
  CheckCircle2,
  CircleDashed,
  Gauge,
  TrendingDown,
  Wrench,
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import type {
  CompressedAirLeakageManagementResponse,
  LeakPriority,
  LeakRepairStatus,
} from "../leakageTypes";

type LeakageEngineeringReviewSectionProps = {
  result: CompressedAirLeakageManagementResponse | null;
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

  return (numericValue * 100).toLocaleString("en-IN", {
    maximumFractionDigits,
  });
}

function formatYears(
  value: string | null,
): string {
  if (value === null) {
    return "Not evaluated";
  }

  return formatDecimal(value, 3);
}

function enumLabel(value: string): string {
  return value
    .split("_")
    .map(
      (part) =>
        part.charAt(0).toUpperCase() +
        part.slice(1).toLowerCase(),
    )
    .join(" ");
}

function priorityVariant(
  priority: LeakPriority,
): "destructive" | "secondary" | "outline" {
  if (
    priority === "CRITICAL" ||
    priority === "HIGH"
  ) {
    return "destructive";
  }

  if (priority === "MEDIUM") {
    return "secondary";
  }

  return "outline";
}

function statusVariant(
  status: LeakRepairStatus,
): "default" | "secondary" | "outline" {
  if (status === "VERIFIED") {
    return "default";
  }

  if (status === "REPAIRED") {
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

export function LeakageEngineeringReviewSection({
  result,
  isPending,
  errorMessage,
}: LeakageEngineeringReviewSectionProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <Gauge className="size-5" />
          </div>

          <div>
            <CardTitle>
              Leakage Engineering Review
            </CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Review registered leakage, equivalent compressor
              power loss, annual energy and cost impact,
              recoverable savings, repair priorities, simple
              payback, and post-repair verification.
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
                  Leakage analysis failed
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
            <CircleDashed className="mx-auto size-8 text-slate-400" />

            <p className="mt-3 font-semibold text-slate-900">
              Leakage analysis not yet calculated
            </p>

            <p className="mx-auto mt-1 max-w-2xl text-sm leading-6 text-slate-500">
              Complete the leakage register and energy basis,
              then run the engineering analysis to review losses,
              savings, priorities, and repair verification.
            </p>
          </div>
        )}

        {!isPending && !errorMessage && result && (
          <>
            <section>
              <div className="mb-4 flex items-center gap-2">
                <Zap className="size-5 text-slate-600" />

                <h3 className="font-semibold text-slate-950">
                  Leakage Baseline
                </h3>
              </div>

              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <Metric
                  label="Registered Leakage"
                  value={formatDecimal(
                    result.total_registered_leakage_flow_nm3_per_hr,
                  )}
                  unit="Nm³/h"
                />

                <Metric
                  label="Leakage / Average Demand"
                  value={`${formatPercent(
                    result.leakage_fraction_of_average_system_demand,
                  )}%`}
                />

                <Metric
                  label="Equivalent Wasted Power"
                  value={formatDecimal(
                    result.total_wasted_power_kw,
                  )}
                  unit="kW"
                />

                <Metric
                  label="Registered Leak Count"
                  value={result.leak_count.toLocaleString("en-IN")}
                  unit="leak points"
                />
              </div>
            </section>

            <section>
              <div className="mb-4 flex items-center gap-2">
                <TrendingDown className="size-5 text-slate-600" />

                <h3 className="font-semibold text-slate-950">
                  Annual Energy & Cost Impact
                </h3>
              </div>

              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <Metric
                  label="Annual Wasted Energy"
                  value={formatDecimal(
                    result.total_annual_wasted_energy_kwh,
                  )}
                  unit="kWh/year"
                />

                <Metric
                  label="Annual Wasted Cost"
                  value={formatDecimal(
                    result.total_annual_wasted_energy_cost,
                  )}
                  unit="currency/year"
                />

                <Metric
                  label="Recoverable Energy"
                  value={formatDecimal(
                    result.total_annual_energy_saving_kwh,
                  )}
                  unit="kWh/year"
                />

                <Metric
                  label="Recoverable Cost"
                  value={formatDecimal(
                    result.total_annual_cost_saving,
                  )}
                  unit="currency/year"
                />
              </div>
            </section>

            <section>
              <div className="mb-4 flex items-center gap-2">
                <Wrench className="size-5 text-slate-600" />

                <h3 className="font-semibold text-slate-950">
                  Repair Opportunity
                </h3>
              </div>

              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <Metric
                  label="Recoverable Leakage"
                  value={formatDecimal(
                    result.total_recoverable_leakage_flow_nm3_per_hr,
                  )}
                  unit="Nm³/h"
                />

                <Metric
                  label="Recoverable Power"
                  value={formatDecimal(
                    result.total_recoverable_power_kw,
                  )}
                  unit="kW"
                />

                <Metric
                  label="Residual Leakage"
                  value={formatDecimal(
                    result.total_residual_leakage_flow_nm3_per_hr,
                  )}
                  unit="Nm³/h"
                />

                <Metric
                  label="Verified Flow Reduction"
                  value={formatDecimal(
                    result.verified_flow_reduction_nm3_per_hr,
                  )}
                  unit={`${result.verified_leak_count} verified leak(s)`}
                />
              </div>
            </section>

            <section>
              <div className="mb-4 flex items-center gap-2">
                <CheckCircle2 className="size-5 text-slate-600" />

                <div>
                  <h3 className="font-semibold text-slate-950">
                    Leak Priority & Repair Register
                  </h3>

                  <p className="mt-1 text-xs leading-5 text-slate-500">
                    Priority is an internal engineering ranking
                    based on each leak&apos;s share of total
                    registered leakage.
                  </p>
                </div>
              </div>

              <div className="overflow-hidden rounded-xl border border-slate-200">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Leak</TableHead>
                      <TableHead>Priority</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">
                        Leakage
                      </TableHead>
                      <TableHead className="text-right">
                        Share
                      </TableHead>
                      <TableHead className="text-right">
                        Wasted Power
                      </TableHead>
                      <TableHead className="text-right">
                        Annual Saving
                      </TableHead>
                      <TableHead className="text-right">
                        Payback
                      </TableHead>
                      <TableHead className="text-right">
                        Verified Reduction
                      </TableHead>
                    </TableRow>
                  </TableHeader>

                  <TableBody>
                    {result.items.map((item) => (
                      <TableRow key={item.leak_code}>
                        <TableCell>
                          <div>
                            <p className="font-medium text-slate-950">
                              {item.leak_code}
                            </p>

                            <p className="mt-1 text-xs text-slate-500">
                              {item.location}
                            </p>

                            <p className="mt-1 text-xs text-slate-400">
                              {enumLabel(
                                item.source_category,
                              )}
                            </p>
                          </div>
                        </TableCell>

                        <TableCell>
                          <Badge
                            variant={priorityVariant(
                              item.priority,
                            )}
                          >
                            {enumLabel(item.priority)}
                          </Badge>
                        </TableCell>

                        <TableCell>
                          <Badge
                            variant={statusVariant(
                              item.repair_status,
                            )}
                          >
                            {enumLabel(item.repair_status)}
                          </Badge>
                        </TableCell>

                        <TableCell className="text-right font-medium">
                          {formatDecimal(
                            item.baseline_leakage_flow_nm3_per_hr,
                          )}
                          <span className="ml-1 text-xs font-normal text-slate-500">
                            Nm³/h
                          </span>
                        </TableCell>

                        <TableCell className="text-right">
                          {formatPercent(
                            item.fraction_of_total_registered_leakage,
                          )}
                          %
                        </TableCell>

                        <TableCell className="text-right">
                          {formatDecimal(
                            item.energy.wasted_power_kw,
                          )}
                          <span className="ml-1 text-xs text-slate-500">
                            kW
                          </span>
                        </TableCell>

                        <TableCell className="text-right">
                          {formatDecimal(
                            item.energy.annual_cost_saving,
                          )}
                        </TableCell>

                        <TableCell className="text-right">
                          {formatYears(
                            item.simple_payback_years,
                          )}
                          {item.simple_payback_years !== null && (
                            <span className="ml-1 text-xs text-slate-500">
                              yr
                            </span>
                          )}
                        </TableCell>

                        <TableCell className="text-right">
                          {formatDecimal(
                            item.verified_flow_reduction_nm3_per_hr,
                          )}

                          {item.verified_flow_reduction_nm3_per_hr !==
                            null && (
                            <span className="ml-1 text-xs text-slate-500">
                              Nm³/h
                            </span>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </section>

            <div className="rounded-lg border border-dashed border-slate-300 p-4">
              <p className="text-sm font-medium text-slate-800">
                Engineering interpretation
              </p>

              <p className="mt-1 text-xs leading-5 text-slate-500">
                Energy and cost savings are engineering estimates
                derived from registered leakage flow, entered
                specific power, annual operating hours, electricity
                tariff, and expected repair fraction. Verified
                post-repair flow is reported separately so measured
                repair performance is not confused with forecast
                savings.
              </p>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
