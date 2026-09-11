import { useState } from "react";

import {
  AlertTriangle,
  UserCheck,
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

import type {
  CompressedAirLeakAssignRequest,
  CompressedAirLeakResponse,
} from "../leakageLifecycleTypes";

type LeakageLifecycleAssignmentSectionProps = {
  leak: CompressedAirLeakResponse | undefined;
  isPending: boolean;
  errorMessage?: string | null;
  onAssign: (
    payload: CompressedAirLeakAssignRequest,
  ) => void;
};

type TaggedLeakAssignmentFormProps = {
  leak: CompressedAirLeakResponse;
  isPending: boolean;
  onAssign: (
    payload: CompressedAirLeakAssignRequest,
  ) => void;
};

function optionalText(value: string): string | null {
  const trimmed = value.trim();

  return trimmed === "" ? null : trimmed;
}

function TaggedLeakAssignmentForm({
  leak,
  isPending,
  onAssign,
}: TaggedLeakAssignmentFormProps) {
  const [assignedTo, setAssignedTo] = useState("");
  const [changeNotes, setChangeNotes] = useState("");
  const [validationErrors, setValidationErrors] = useState<
    string[]
  >([]);

  const assigneeInputId =
    `leak-${leak.id}-assigned-to`;
  const notesInputId =
    `leak-${leak.id}-assignment-notes`;
  const validationSummaryId =
    `leak-${leak.id}-assignment-errors`;

  function submitAssignment(): void {
    const normalizedAssignee = assignedTo.trim();
    const errors: string[] = [];

    if (!normalizedAssignee) {
      errors.push("Assigned-to person or team is required.");
    } else if (normalizedAssignee.length > 255) {
      errors.push(
        "Assigned-to person or team must be 255 characters or fewer.",
      );
    }

    setValidationErrors(errors);

    if (errors.length > 0) {
      return;
    }

    onAssign({
      assigned_to: normalizedAssignee,
      change_notes: optionalText(changeNotes),
    });
  }

  return (
    <section className="rounded-xl border border-slate-200 p-5">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="font-semibold text-slate-950">
              {leak.leak_code}
            </h3>
            <Badge variant="outline">Tagged</Badge>
          </div>

          <p className="mt-1 text-sm text-slate-600">
            {leak.location}
          </p>
        </div>

        <p className="text-xs leading-5 text-slate-500">
          Next permitted status: Assigned
        </p>
      </div>

      {validationErrors.length > 0 && (
        <div
          id={validationSummaryId}
          role="alert"
          className="mt-4 flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900"
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
        <div>
          <Label htmlFor={assigneeInputId}>
            Assigned to
          </Label>
          <Input
            id={assigneeInputId}
            className="mt-2"
            value={assignedTo}
            maxLength={255}
            aria-invalid={validationErrors.length > 0}
            aria-describedby={
              validationErrors.length > 0
                ? validationSummaryId
                : undefined
            }
            placeholder="Person, team, or maintenance owner"
            disabled={isPending}
            onChange={(event) => {
              setAssignedTo(event.target.value);
              setValidationErrors([]);
            }}
          />
        </div>

        <div>
          <Label htmlFor={notesInputId}>
            Assignment note
          </Label>
          <textarea
            id={notesInputId}
            className="mt-2 min-h-20 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs outline-none transition-[color,box-shadow] placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-50"
            value={changeNotes}
            placeholder="Optional audit note for this transition"
            disabled={isPending}
            onChange={(event) => {
              setChangeNotes(event.target.value);
            }}
          />
        </div>
      </div>

      <div className="mt-5 flex justify-end">
        <Button
          type="button"
          disabled={isPending}
          onClick={submitAssignment}
        >
          <UserCheck className="size-4" />
          {isPending ? "Assigning..." : "Assign Leak"}
        </Button>
      </div>
    </section>
  );
}

export function LeakageLifecycleAssignmentSection({
  leak,
  isPending,
  errorMessage,
  onAssign,
}: LeakageLifecycleAssignmentSectionProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <UserCheck className="size-5" />
          </div>

          <div>
            <CardTitle>
              Assign Leakage Repair
            </CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Give the selected tagged leakage record a clear
              repair owner and preserve an optional transition
              note in its immutable lifecycle history.
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
              Select a tagged leakage record to assign its repair.
            </p>
          </div>
        )}

        {leak?.lifecycle_status === "TAGGED" && (
          <TaggedLeakAssignmentForm
            key={leak.id}
            leak={leak}
            isPending={isPending}
            onAssign={onAssign}
          />
        )}

        {leak && leak.lifecycle_status !== "TAGGED" && (
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-semibold text-slate-950">
                {leak.leak_code}
              </span>
              <Badge
                variant={
                  leak.lifecycle_status === "CLOSED"
                    ? "default"
                    : "secondary"
                }
              >
                {leak.lifecycle_status === "CLOSED"
                  ? "Closed"
                  : "Assigned"}
              </Badge>
            </div>

            <p className="mt-2 text-sm leading-6 text-slate-600">
              {leak.lifecycle_status === "CLOSED"
                ? "This lifecycle is closed and cannot be assigned again."
                : `Repair ownership is already assigned to ${
                    leak.assigned_to ?? "the recorded owner"
                  }.`}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
