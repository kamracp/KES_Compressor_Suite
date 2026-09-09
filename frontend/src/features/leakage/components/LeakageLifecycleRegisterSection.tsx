import {
  RefreshCw,
  Tags,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import type {
  CompressedAirLeakLifecycleStatus,
  CompressedAirLeakListResponse,
} from "../leakageLifecycleTypes";

type LeakageLifecycleRegisterSectionProps = {
  register: CompressedAirLeakListResponse | undefined;
  isPending: boolean;
  isFetching: boolean;
  errorMessage?: string | null;
  onRefresh: () => void;
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

function formatTimestamp(value: string): string {
  const timestamp = new Date(value);

  if (Number.isNaN(timestamp.getTime())) {
    return value;
  }

  return timestamp.toLocaleString();
}

export function LeakageLifecycleRegisterSection({
  register,
  isPending,
  isFetching,
  errorMessage,
  onRefresh,
}: LeakageLifecycleRegisterSectionProps) {
  const summaryItems = [
    {
      label: "Total",
      value: register?.total_leaks ?? 0,
    },
    {
      label: "Tagged",
      value: register?.tagged_leaks ?? 0,
    },
    {
      label: "Assigned",
      value: register?.assigned_leaks ?? 0,
    },
    {
      label: "Closed",
      value: register?.closed_leaks ?? 0,
    },
  ];

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex items-start gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
              <Tags className="size-5" />
            </div>

            <div>
              <CardTitle>
                Persistent Leakage Lifecycle
              </CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Track each project leakage point from tagging
                through assignment and verified closure, while
                preserving its auditable lifecycle record.
              </CardDescription>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            disabled={isPending || isFetching}
            onClick={onRefresh}
          >
            <RefreshCw
              className={
                isFetching
                  ? "size-4 animate-spin"
                  : "size-4"
              }
            />
            {isFetching ? "Refreshing..." : "Refresh"}
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-5">
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {summaryItems.map((item) => (
            <div
              key={item.label}
              className="rounded-xl border border-slate-200 bg-slate-50 p-4"
            >
              <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                {item.label}
              </p>

              <p className="mt-2 text-2xl font-bold text-slate-950">
                {item.value}
              </p>
            </div>
          ))}
        </div>

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
            Loading persistent leakage register...
          </div>
        )}

        {!isPending &&
          !errorMessage &&
          register?.items.length === 0 && (
            <div className="rounded-xl border border-dashed border-slate-300 p-6 text-center">
              <p className="text-sm font-medium text-slate-800">
                No persistent leakage records yet.
              </p>

              <p className="mt-1 text-xs leading-5 text-slate-500">
                Tag a calculated or surveyed leakage point to
                begin its assignment and closure lifecycle.
              </p>
            </div>
          )}

        {!isPending &&
          !errorMessage &&
          register &&
          register.items.length > 0 && (
            <div className="rounded-xl border border-slate-200">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Leak Code</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Assigned To</TableHead>
                    <TableHead>Tagged At</TableHead>
                    <TableHead>Updated At</TableHead>
                  </TableRow>
                </TableHeader>

                <TableBody>
                  {register.items.map((leak) => (
                    <TableRow key={leak.id}>
                      <TableCell className="font-medium text-slate-950">
                        {leak.leak_code}
                      </TableCell>

                      <TableCell>
                        {leak.location}
                      </TableCell>

                      <TableCell>
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
                      </TableCell>

                      <TableCell>
                        {leak.assigned_to ?? "Unassigned"}
                      </TableCell>

                      <TableCell>
                        {formatTimestamp(leak.tagged_at)}
                      </TableCell>

                      <TableCell>
                        {formatTimestamp(leak.updated_at)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
      </CardContent>
    </Card>
  );
}
