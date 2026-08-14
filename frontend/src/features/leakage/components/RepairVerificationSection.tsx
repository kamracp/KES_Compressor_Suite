import {
  CheckCircle2,
  Wrench,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
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
  LeakRegisterItemInput,
  LeakRepairStatus,
} from "../leakageTypes";

type RepairVerificationSectionProps = {
  leaks: LeakRegisterItemInput[];
  onChange: (leaks: LeakRegisterItemInput[]) => void;
};

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

export function RepairVerificationSection({
  leaks,
  onChange,
}: RepairVerificationSectionProps) {
  function updateLeak(
    index: number,
    changes: Partial<LeakRegisterItemInput>,
  ): void {
    onChange(
      leaks.map((leak, leakIndex) =>
        leakIndex === index
          ? {
              ...leak,
              ...changes,
            }
          : leak,
      ),
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <Wrench className="size-5" />
          </div>

          <div>
            <CardTitle>
              Repair Verification
            </CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Record measured leakage after repair so the analysis
              can compare baseline and verified post-repair flow
              and quantify actual leakage reduction.
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-5">
        {leaks.map((leak, index) => {
          const hasVerification =
            leak.verified_post_repair_flow_nm3_per_hr !==
              null &&
            leak.verified_post_repair_flow_nm3_per_hr !==
              undefined &&
            leak.verified_post_repair_flow_nm3_per_hr.trim() !== "";

          return (
            <section
              key={`${leak.leak_code}-verification-${index}`}
              className="rounded-xl border border-slate-200 p-5"
            >
              <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="font-semibold text-slate-950">
                      {leak.leak_code || `Leak ${index + 1}`}
                    </h3>

                    <Badge variant={statusVariant(leak.repair_status)}>
                      {leak.repair_status}
                    </Badge>

                    {hasVerification && (
                      <Badge variant="secondary">
                        <CheckCircle2 className="size-3" />
                        Measurement Entered
                      </Badge>
                    )}
                  </div>

                  <p className="mt-1 text-sm text-slate-500">
                    {leak.location || "Location not entered"}
                  </p>
                </div>

                <div className="text-left md:text-right">
                  <p className="text-xs font-medium text-slate-500">
                    Baseline Leakage
                  </p>

                  <p className="mt-1 text-lg font-semibold text-slate-950">
                    {leak.baseline_leakage_flow_nm3_per_hr || "—"}
                  </p>

                  <p className="text-xs text-slate-500">
                    Nm³/h
                  </p>
                </div>
              </div>

              <div className="mt-5 grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor={`verified-flow-${index}`}>
                    Verified Post-Repair Flow
                  </Label>

                  <Input
                    id={`verified-flow-${index}`}
                    type="number"
                    min="0"
                    step="any"
                    value={
                      leak.verified_post_repair_flow_nm3_per_hr ??
                      ""
                    }
                    placeholder="Example: 20"
                    onChange={(event) =>
                      updateLeak(index, {
                        verified_post_repair_flow_nm3_per_hr:
                          event.target.value || null,
                      })
                    }
                  />

                  <p className="text-xs leading-5 text-slate-500">
                    Nm³/h measured after corrective action.
                  </p>
                </div>

                <div className="rounded-lg border border-dashed border-slate-300 p-4">
                  <p className="text-sm font-medium text-slate-800">
                    Verification basis
                  </p>

                  <p className="mt-1 text-xs leading-5 text-slate-500">
                    Use a comparable operating pressure and
                    measurement method where practical. The backend
                    calculates verified flow reduction as baseline
                    leakage minus post-repair leakage.
                  </p>
                </div>
              </div>
            </section>
          );
        })}

        <div className="rounded-lg border border-dashed border-slate-300 p-4">
          <p className="text-sm font-medium text-slate-800">
            Expected versus verified saving
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            Expected repair fraction is the planning assumption.
            Post-repair leakage is the verification measurement.
            Keeping these separate preserves traceability between
            forecast savings and measured repair performance.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
