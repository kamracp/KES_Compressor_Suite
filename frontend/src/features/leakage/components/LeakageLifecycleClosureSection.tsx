import { useState } from "react";

import {
  AlertTriangle,
  CheckCircle2,
  Wrench,
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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import {
  buildLeakageLifecycleCloseRequest,
  createInitialLeakageLifecycleClosureFormState,
  validateLeakageLifecycleClosureFormState,
  type LeakageLifecycleClosureFormState,
} from "../leakageLifecycleClosure";
import type {
  CompressedAirLeakCloseRequest,
  CompressedAirLeakResponse,
} from "../leakageLifecycleTypes";
import {
  MAX_ASSET_FAD_NM3_PER_HR,
} from "../../reference/inputBounds";

type LeakageLifecycleClosureSectionProps = {
  leak: CompressedAirLeakResponse | undefined;
  isPending: boolean;
  errorMessage?: string | null;
  onClose: (
    payload: CompressedAirLeakCloseRequest,
  ) => void;
};

type AssignedLeakClosureFormProps = {
  leak: CompressedAirLeakResponse;
  isPending: boolean;
  onClose: (
    payload: CompressedAirLeakCloseRequest,
  ) => void;
};

type VerificationMethod = Exclude<
  LeakageLifecycleClosureFormState["verificationMethod"],
  ""
>;

const verificationMethods: Array<{
  value: VerificationMethod;
  label: string;
}> = [
  {
    value: "FLOW_METER",
    label: "Flow meter",
  },
  {
    value: "ULTRASONIC_ESTIMATE",
    label: "Ultrasonic survey",
  },
  {
    value: "DECAY_TEST",
    label: "Pressure-decay test",
  },
  {
    value: "LOAD_UNLOAD_TEST",
    label: "Load/unload test",
  },
  {
    value: "ORIFICE_ESTIMATE",
    label: "Orifice estimate",
  },
  {
    value: "ENGINEERING_ESTIMATE",
    label: "Engineering estimate",
  },
  {
    value: "OTHER",
    label: "Other documented method",
  },
];

type TextareaFieldProps = {
  id: string;
  label: string;
  value: string;
  placeholder: string;
  disabled: boolean;
  onChange: (value: string) => void;
};

function TextareaField({
  id,
  label,
  value,
  placeholder,
  disabled,
  onChange,
}: TextareaFieldProps) {
  return (
    <div>
      <Label htmlFor={id}>{label}</Label>
      <textarea
        id={id}
        className="mt-2 min-h-24 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs outline-none transition-[color,box-shadow] placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-50"
        value={value}
        placeholder={placeholder}
        disabled={disabled}
        onChange={(event) => {
          onChange(event.target.value);
        }}
      />
    </div>
  );
}

function sourceBaselineFlow(
  leak: CompressedAirLeakResponse,
): string | null {
  const value =
    leak.source_snapshot.baseline_leakage_flow_nm3_per_hr;

  if (typeof value === "string") {
    return value;
  }

  if (typeof value === "number") {
    return String(value);
  }

  return null;
}

function formatTimestamp(value: string | null): string {
  if (!value) {
    return "Not recorded";
  }

  const timestamp = new Date(value);

  if (Number.isNaN(timestamp.getTime())) {
    return value;
  }

  return timestamp.toLocaleString();
}

function AssignedLeakClosureForm({
  leak,
  isPending,
  onClose,
}: AssignedLeakClosureFormProps) {
  const [state, setState] =
    useState<LeakageLifecycleClosureFormState>(
      createInitialLeakageLifecycleClosureFormState,
    );
  const [evidenceConfirmed, setEvidenceConfirmed] =
    useState(false);
  const [validationErrors, setValidationErrors] = useState<
    string[]
  >([]);

  const fieldPrefix = `leak-${leak.id}-closure`;
  const validationSummaryId = `${fieldPrefix}-errors`;

  function updateState(
    changes: Partial<LeakageLifecycleClosureFormState>,
  ): void {
    setState((current) => ({
      ...current,
      ...changes,
    }));
    setValidationErrors([]);
  }

  function submitClosure(): void {
    const errors =
      validateLeakageLifecycleClosureFormState(state);

    if (!evidenceConfirmed) {
      errors.push(
        "Confirm that the repair and verification evidence has been reviewed.",
      );
    }

    setValidationErrors(errors);

    if (errors.length > 0) {
      return;
    }

    onClose(buildLeakageLifecycleCloseRequest(state));
  }

  return (
    <section className="rounded-xl border border-slate-200 p-5">
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-lg bg-slate-50 p-3">
          <p className="text-xs font-medium text-slate-500">
            Leak Code
          </p>
          <p className="mt-1 text-sm font-semibold text-slate-950">
            {leak.leak_code}
          </p>
        </div>

        <div className="rounded-lg bg-slate-50 p-3">
          <p className="text-xs font-medium text-slate-500">
            Current Status
          </p>
          <div className="mt-1">
            <Badge variant="secondary">Assigned</Badge>
          </div>
        </div>

        <div className="rounded-lg bg-slate-50 p-3">
          <p className="text-xs font-medium text-slate-500">
            Repair Owner
          </p>
          <p className="mt-1 text-sm font-semibold text-slate-950">
            {leak.assigned_to ?? "Recorded owner"}
          </p>
        </div>

        <div className="rounded-lg bg-slate-50 p-3">
          <p className="text-xs font-medium text-slate-500">
            Tagged Baseline
          </p>
          <p className="mt-1 text-sm font-semibold text-slate-950">
            {sourceBaselineFlow(leak) ?? "Not recorded"}{" "}
            Nm³/h
          </p>
        </div>
      </div>

      {validationErrors.length > 0 && (
        <div
          id={validationSummaryId}
          role="alert"
          className="mt-5 flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900"
        >
          <AlertTriangle className="mt-0.5 size-4 shrink-0" />

          <ul className="list-disc space-y-1 pl-5">
            {validationErrors.map((validationError) => (
              <li key={validationError}>
                {validationError}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <TextareaField
          id={`${fieldPrefix}-repair-action`}
          label="Repair action"
          value={state.repairAction}
          placeholder="Describe the completed repair or replacement"
          disabled={isPending}
          onChange={(repairAction) => {
            updateState({ repairAction });
          }}
        />

        <div>
          <Label htmlFor={`${fieldPrefix}-verification-method`}>
            Verification method
          </Label>
          <select
            id={`${fieldPrefix}-verification-method`}
            className="mt-2 h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-50"
            value={state.verificationMethod}
            disabled={isPending}
            onChange={(event) => {
              updateState({
                verificationMethod: event.target.value as LeakageLifecycleClosureFormState["verificationMethod"],
              });
            }}
          >
            <option value="">Select verification method</option>
            {verificationMethods.map((method) => (
              <option
                key={method.value}
                value={method.value}
              >
                {method.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <Label htmlFor={`${fieldPrefix}-verified-flow`}>
            Verified post-repair flow
          </Label>
          <Input
            id={`${fieldPrefix}-verified-flow`}
            className="mt-2"
            type="number"
            min="0"
            max={MAX_ASSET_FAD_NM3_PER_HR}
            step="any"
            value={state.verifiedPostRepairFlowNm3PerHr}
            placeholder="Example: 0.8"
            disabled={isPending}
            aria-describedby={validationSummaryId}
            onChange={(event) => {
              updateState({
                verifiedPostRepairFlowNm3PerHr:
                  event.target.value,
              });
            }}
          />
          <p className="mt-1 text-xs leading-5 text-slate-500">
            Nm³/h at the documented verification condition.
          </p>
        </div>

        <div>
          <Label htmlFor={`${fieldPrefix}-reference`}>
            Verification reference
          </Label>
          <Input
            id={`${fieldPrefix}-reference`}
            className="mt-2"
            value={state.verificationReference}
            placeholder="Optional survey, work order, or evidence ID"
            disabled={isPending}
            onChange={(event) => {
              updateState({
                verificationReference: event.target.value,
              });
            }}
          />
        </div>

        <TextareaField
          id={`${fieldPrefix}-closure-notes`}
          label="Closure notes"
          value={state.closureNotes}
          placeholder="Optional conclusion recorded on the leak"
          disabled={isPending}
          onChange={(closureNotes) => {
            updateState({ closureNotes });
          }}
        />

        <TextareaField
          id={`${fieldPrefix}-change-notes`}
          label="Status-history note"
          value={state.changeNotes}
          placeholder="Optional reason recorded with the status change"
          disabled={isPending}
          onChange={(changeNotes) => {
            updateState({ changeNotes });
          }}
        />
      </div>

      <div className="mt-5 flex items-start gap-3 rounded-lg border border-slate-200 bg-slate-50 p-4">
        <input
          id={`${fieldPrefix}-confirmation`}
          type="checkbox"
          className="mt-0.5 size-4 rounded border-slate-300"
          checked={evidenceConfirmed}
          disabled={isPending}
          onChange={(event) => {
            setEvidenceConfirmed(event.target.checked);
            setValidationErrors([]);
          }}
        />
        <Label
          htmlFor={`${fieldPrefix}-confirmation`}
          className="leading-5"
        >
          I confirm that the completed repair and verification
          evidence have been reviewed before closing this
          lifecycle.
        </Label>
      </div>

      <div className="mt-5 flex justify-end">
        <Button
          type="button"
          disabled={isPending}
          onClick={submitClosure}
        >
          <CheckCircle2 className="size-4" />
          {isPending
            ? "Closing Lifecycle..."
            : "Close Leakage Lifecycle"}
        </Button>
      </div>
    </section>
  );
}

export function LeakageLifecycleClosureSection({
  leak,
  isPending,
  errorMessage,
  onClose,
}: LeakageLifecycleClosureSectionProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <Wrench className="size-5" />
          </div>

          <div>
            <CardTitle>
              Close Leakage Lifecycle
            </CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Close an assigned leak only after recording the
              completed repair, verification method, measured
              post-repair flow, and supporting audit reference.
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

        {!leak && (
          <div className="rounded-xl border border-dashed border-slate-300 p-6 text-center">
            <p className="text-sm font-medium text-slate-800">
              Select an assigned leakage record to review its
              closure evidence.
            </p>
          </div>
        )}

        {leak?.lifecycle_status === "ASSIGNED" && (
          <AssignedLeakClosureForm
            key={leak.id}
            leak={leak}
            isPending={isPending}
            onClose={onClose}
          />
        )}

        {leak?.lifecycle_status === "TAGGED" && (
          <div className="rounded-xl border border-amber-200 bg-amber-50 p-5">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-semibold text-amber-950">
                {leak.leak_code}
              </span>
              <Badge variant="outline">Tagged</Badge>
            </div>
            <p className="mt-2 text-sm leading-6 text-amber-900">
              Assign this leakage record before recording closure
              evidence. Direct TAGGED to CLOSED transitions are
              not permitted.
            </p>
          </div>
        )}

        {leak?.lifecycle_status === "CLOSED" && (
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-semibold text-slate-950">
                {leak.leak_code}
              </span>
              <Badge variant="default">Closed</Badge>
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              This lifecycle was closed on{" "}
              {formatTimestamp(leak.closed_at)} and cannot be
              closed again.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
