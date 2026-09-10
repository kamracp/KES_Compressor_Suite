import {
  AlertTriangle,
  CheckCircle2,
  Tag,
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
  validateLeakageLifecycleTagging,
} from "../leakageLifecyclePayload";
import type {
  LeakRegisterItemInput,
} from "../leakageTypes";

type LeakageLifecycleTaggingSectionProps = {
  leaks: LeakRegisterItemInput[];
  persistedLeakCodes: readonly string[];
  isPending: boolean;
  pendingLeakCode?: string | null;
  errorMessage?: string | null;
  onTagLeak: (leak: LeakRegisterItemInput) => void;
};

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

function normalizedLeakCode(value: string): string {
  return value.trim();
}

export function LeakageLifecycleTaggingSection({
  leaks,
  persistedLeakCodes,
  isPending,
  pendingLeakCode,
  errorMessage,
  onTagLeak,
}: LeakageLifecycleTaggingSectionProps) {
  const persistedCodes = new Set(
    persistedLeakCodes.map(normalizedLeakCode),
  );
  const normalizedPendingLeakCode = pendingLeakCode
    ? normalizedLeakCode(pendingLeakCode)
    : null;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <Tag className="size-5" />
          </div>

          <div>
            <CardTitle>
              Tag Leakage Records
            </CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Save a valid engineering leak row in the persistent
              lifecycle register. Its survey values are preserved
              as an auditable source snapshot before assignment
              and closure activities begin.
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

        {leaks.length === 0 && (
          <div className="rounded-xl border border-dashed border-slate-300 p-6 text-center">
            <p className="text-sm font-medium text-slate-800">
              No engineering leak rows are available.
            </p>

            <p className="mt-1 text-xs leading-5 text-slate-500">
              Add a leak in the engineering register before
              creating its lifecycle record.
            </p>
          </div>
        )}

        {leaks.map((leak, index) => {
          const leakCode = normalizedLeakCode(
            leak.leak_code,
          );
          const validationErrors =
            validateLeakageLifecycleTagging(leak);
          const isAlreadyTagged =
            leakCode !== "" &&
            persistedCodes.has(leakCode);
          const isThisLeakPending =
            isPending &&
            normalizedPendingLeakCode === leakCode;
          const canTag =
            validationErrors.length === 0 &&
            !isAlreadyTagged &&
            !isPending;

          return (
            <section
              key={`${leak.leak_code}-${index}`}
              className="rounded-xl border border-slate-200 p-5"
            >
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="font-semibold text-slate-950">
                      {leakCode || `Leak ${index + 1}`}
                    </h3>

                    {isAlreadyTagged ? (
                      <Badge variant="default">
                        Already Tagged
                      </Badge>
                    ) : validationErrors.length > 0 ? (
                      <Badge variant="destructive">
                        Needs Input
                      </Badge>
                    ) : (
                      <Badge variant="outline">
                        Ready to Tag
                      </Badge>
                    )}
                  </div>

                  <p className="mt-1 text-sm text-slate-600">
                    {leak.location.trim() ||
                      "Location not entered"}
                  </p>
                </div>

                <Button
                  type="button"
                  disabled={!canTag}
                  onClick={() => onTagLeak(leak)}
                  aria-label={`Tag ${
                    leakCode || `leak ${index + 1}`
                  } in lifecycle`}
                >
                  {isThisLeakPending ? (
                    <>
                      <Tag className="size-4" />
                      Tagging...
                    </>
                  ) : isAlreadyTagged ? (
                    <>
                      <CheckCircle2 className="size-4" />
                      Tagged
                    </>
                  ) : (
                    <>
                      <Tag className="size-4" />
                      Tag in Lifecycle
                    </>
                  )}
                </Button>
              </div>

              <dl className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                <div className="rounded-lg bg-slate-50 p-3">
                  <dt className="text-xs font-medium text-slate-500">
                    Baseline Flow
                  </dt>
                  <dd className="mt-1 text-sm font-semibold text-slate-900">
                    {leak.baseline_leakage_flow_nm3_per_hr.trim() ||
                      "Not entered"}{" "}
                    Nm³/h
                  </dd>
                </div>

                <div className="rounded-lg bg-slate-50 p-3">
                  <dt className="text-xs font-medium text-slate-500">
                    Quantification
                  </dt>
                  <dd className="mt-1 text-sm font-semibold text-slate-900">
                    {enumLabel(leak.quantification_basis)}
                  </dd>
                </div>

                <div className="rounded-lg bg-slate-50 p-3">
                  <dt className="text-xs font-medium text-slate-500">
                    Source Category
                  </dt>
                  <dd className="mt-1 text-sm font-semibold text-slate-900">
                    {enumLabel(leak.source_category)}
                  </dd>
                </div>

                <div className="rounded-lg bg-slate-50 p-3">
                  <dt className="text-xs font-medium text-slate-500">
                    Expected Repair
                  </dt>
                  <dd className="mt-1 text-sm font-semibold text-slate-900">
                    {leak.expected_repair_fraction.trim() ||
                      "Not entered"}
                  </dd>
                </div>
              </dl>

              {validationErrors.length > 0 && (
                <div className="mt-4 flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
                  <AlertTriangle className="mt-0.5 size-4 shrink-0" />

                  <div>
                    <p className="font-medium">
                      Complete this row before tagging:
                    </p>

                    <ul className="mt-2 list-disc space-y-1 pl-5">
                      {validationErrors.map((validationError) => (
                        <li key={validationError}>
                          {validationError}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </section>
          );
        })}

        <p className="text-xs leading-5 text-slate-500">
          Tagging creates the permanent lifecycle starting point.
          The captured source snapshot remains unchanged while
          later status transitions are recorded separately.
        </p>
      </CardContent>
    </Card>
  );
}
