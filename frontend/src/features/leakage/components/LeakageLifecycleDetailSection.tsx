import {
  Activity,
  History,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import type {
  CompressedAirLeakKpiSnapshotResponse,
  CompressedAirLeakLifecycleStatus,
  CompressedAirLeakResponse,
  CompressedAirLeakStatusHistoryResponse,
} from "../leakageLifecycleTypes";

type LeakageLifecycleDetailSectionProps = {
  leak: CompressedAirLeakResponse | undefined;
  history:
    | CompressedAirLeakStatusHistoryResponse[]
    | undefined;
  kpiSnapshots:
    | CompressedAirLeakKpiSnapshotResponse[]
    | undefined;
  isPending: boolean;
  errorMessage?: string | null;
};

const statusLabels: Record<
  CompressedAirLeakLifecycleStatus,
  string
> = {
  TAGGED: "Tagged",
  ASSIGNED: "Assigned",
  CLOSED: "Closed",
};

function statusVariant(
  status: CompressedAirLeakLifecycleStatus,
): "default" | "secondary" | "outline" {
  if (status === "CLOSED") {
    return "default";
  }

  if (status === "ASSIGNED") {
    return "secondary";
  }

  return "outline";
}

function formatTimestamp(
  value: string | null,
): string {
  if (!value) {
    return "Not recorded";
  }

  const timestamp = new Date(value);

  if (Number.isNaN(timestamp.getTime())) {
    return value;
  }

  return timestamp.toLocaleString();
}

export function LeakageLifecycleDetailSection({
  leak,
  history,
  kpiSnapshots,
  isPending,
  errorMessage,
}: LeakageLifecycleDetailSectionProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <Activity className="size-5" />
          </div>

          <div>
            <CardTitle>
              Leakage Lifecycle Detail
            </CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Review the selected leakage record, its
              auditable status history, closure evidence,
              and captured KPI snapshots.
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-5">
        {errorMessage && (
          <div
            role="alert"
            className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800"
          >
            {errorMessage}
          </div>
        )}

        {isPending && (
          <div
            aria-live="polite"
            className="rounded-xl border border-dashed border-slate-300 p-6 text-center text-sm text-slate-600"
          >
            Loading leakage lifecycle detail...
          </div>
        )}

        {!isPending && !errorMessage && !leak && (
          <div className="rounded-xl border border-dashed border-slate-300 p-6 text-center">
            <p className="text-sm font-medium text-slate-800">
              Select a leakage record to review its lifecycle.
            </p>
          </div>
        )}

        {!isPending && !errorMessage && leak && (
          <>
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                  Leak Code
                </p>
                <p className="mt-2 font-semibold text-slate-950">
                  {leak.leak_code}
                </p>
              </div>

              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                  Status
                </p>
                <div className="mt-2">
                  <Badge
                    variant={statusVariant(
                      leak.lifecycle_status,
                    )}
                  >
                    {
                      statusLabels[
                        leak.lifecycle_status
                      ]
                    }
                  </Badge>
                </div>
              </div>

              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                  Location
                </p>
                <p className="mt-2 text-sm text-slate-950">
                  {leak.location}
                </p>
              </div>

              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                  Assigned To
                </p>
                <p className="mt-2 text-sm text-slate-950">
                  {leak.assigned_to ?? "Unassigned"}
                </p>
              </div>
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              <div className="rounded-xl border border-slate-200 p-4">
                <div className="flex items-center gap-2">
                  <History className="size-4 text-slate-500" />
                  <h3 className="font-semibold text-slate-950">
                    Status History
                  </h3>
                </div>

                {history && history.length > 0 ? (
                  <div className="mt-4 space-y-3">
                    {history.map((entry) => (
                      <div
                        key={entry.id}
                        className="rounded-lg bg-slate-50 p-3"
                      >
                        <div className="flex flex-wrap items-center gap-2">
                          <Badge
                            variant={statusVariant(
                              entry.new_status,
                            )}
                          >
                            {
                              statusLabels[
                                entry.new_status
                              ]
                            }
                          </Badge>

                          <span className="text-xs text-slate-500">
                            {formatTimestamp(
                              entry.changed_at,
                            )}
                          </span>
                        </div>

                        {entry.change_notes && (
                          <p className="mt-2 text-sm text-slate-700">
                            {entry.change_notes}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="mt-4 text-sm text-slate-500">
                    No lifecycle history recorded.
                  </p>
                )}
              </div>

              <div className="rounded-xl border border-slate-200 p-4">
                <h3 className="font-semibold text-slate-950">
                  KPI Snapshots
                </h3>

                {kpiSnapshots &&
                kpiSnapshots.length > 0 ? (
                  <div className="mt-4 space-y-3">
                    {kpiSnapshots.map((snapshot) => (
                      <div
                        key={snapshot.id}
                        className="rounded-lg bg-slate-50 p-3"
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <span className="text-sm font-medium text-slate-900">
                            {snapshot.snapshot_code}
                          </span>

                          <Badge
                            variant={statusVariant(
                              snapshot.lifecycle_status,
                            )}
                          >
                            {
                              statusLabels[
                                snapshot.lifecycle_status
                              ]
                            }
                          </Badge>
                        </div>

                        <p className="mt-2 text-xs text-slate-500">
                          {formatTimestamp(
                            snapshot.captured_at,
                          )}
                        </p>

                        <pre className="mt-3 overflow-x-auto whitespace-pre-wrap rounded-lg border border-slate-200 bg-white p-3 text-xs text-slate-700">
                          {JSON.stringify(
                            snapshot.metrics_payload,
                            null,
                            2,
                          )}
                        </pre>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="mt-4 text-sm text-slate-500">
                    No KPI snapshots recorded.
                  </p>
                )}
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <div>
                <p className="text-xs font-medium text-slate-500">
                  Tagged
                </p>
                <p className="mt-1 text-sm text-slate-800">
                  {formatTimestamp(leak.tagged_at)}
                </p>
              </div>

              <div>
                <p className="text-xs font-medium text-slate-500">
                  Assigned
                </p>
                <p className="mt-1 text-sm text-slate-800">
                  {formatTimestamp(leak.assigned_at)}
                </p>
              </div>

              <div>
                <p className="text-xs font-medium text-slate-500">
                  Closed
                </p>
                <p className="mt-1 text-sm text-slate-800">
                  {formatTimestamp(leak.closed_at)}
                </p>
              </div>

              <div>
                <p className="text-xs font-medium text-slate-500">
                  Last Updated
                </p>
                <p className="mt-1 text-sm text-slate-800">
                  {formatTimestamp(leak.updated_at)}
                </p>
              </div>
            </div>

            {leak.closure_notes && (
              <div className="rounded-xl border border-slate-200 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                  Closure Notes
                </p>
                <p className="mt-2 text-sm leading-6 text-slate-700">
                  {leak.closure_notes}
                </p>
              </div>
            )}

            {leak.closure_evidence && (
              <div className="rounded-xl border border-slate-200 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                  Closure Evidence
                </p>
                <pre className="mt-3 overflow-x-auto whitespace-pre-wrap rounded-lg bg-slate-50 p-3 text-xs text-slate-700">
                  {JSON.stringify(
                    leak.closure_evidence,
                    null,
                    2,
                  )}
                </pre>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
