import {
  useState,
  type ComponentProps,
  type Dispatch,
  type FormEvent,
  type SetStateAction,
} from "react";

import { useMutation } from "@tanstack/react-query";
import {
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  Gauge,
  Play,
  RotateCcw,
  Save,
  Scale,
  Settings2,
  Wind,
} from "lucide-react";
import { Link } from "react-router";

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

import { useAuth } from "../features/auth/AuthProvider";
import { useProjectContext } from "../features/projects/useProjectContext";
import { executeCompressorSelection } from "../features/projects/selectionService";
import type {
  CompressorOptionAssessment,
  CompressorSelectionExecutionResponse,
  CompressorType,
  SelectionRating,
} from "../features/projects/selectionTypes";
import { ApiError } from "../services/apiClient";

type EngineeringInputProps = Omit<
  ComponentProps<typeof Input>,
  "id"
> & {
  id: string;
  label: string;
  unit?: string;
};

type ResultMetricProps = {
  label: string;
  value: string;
  description?: string;
};

type TechnologyAssessmentProps = {
  title: string;
  assessment: CompressorOptionAssessment;
  recommended: boolean;
};

const RATING_STYLES: Record<SelectionRating, string> = {
  EXCELLENT: "border-emerald-300 bg-emerald-100 text-emerald-900",
  GOOD: "border-blue-300 bg-blue-100 text-blue-900",
  ACCEPTABLE: "border-amber-300 bg-amber-100 text-amber-900",
  POOR: "border-red-300 bg-red-100 text-red-900",
};

function EngineeringInput({
  id,
  label,
  unit,
  ...inputProps
}: EngineeringInputProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-3">
        <Label htmlFor={id}>{label}</Label>

        {unit && (
          <span className="text-xs font-medium text-slate-500">
            {unit}
          </span>
        )}
      </div>

      <Input
        id={id}
        {...inputProps}
      />
    </div>
  );
}

function formatNumericValue(
  value: string,
  maximumFractionDigits = 2,
): string {
  const numericValue = Number(value);

  if (!Number.isFinite(numericValue)) {
    return value;
  }

  return numericValue.toLocaleString("en-IN", {
    maximumFractionDigits,
  });
}

function formatCompressorType(compressorType: CompressorType): string {
  return compressorType === "RECIPROCATING"
    ? "Reciprocating"
    : "Centrifugal";
}

function ResultMetric({
  label,
  value,
  description,
}: ResultMetricProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </dt>

      <dd className="mt-2 break-words text-xl font-semibold text-slate-950">
        {value}
      </dd>

      {description && (
        <p className="mt-2 text-xs leading-5 text-slate-600">
          {description}
        </p>
      )}
    </div>
  );
}

function RatingBadge({ rating }: { rating: SelectionRating }) {
  return (
    <Badge
      variant="outline"
      className={RATING_STYLES[rating]}
    >
      {rating}
    </Badge>
  );
}

function AssessmentRating({
  label,
  rating,
}: {
  label: string;
  rating: SelectionRating;
}) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-lg border border-slate-200 bg-white px-3 py-2">
      <dt className="text-sm text-slate-600">{label}</dt>
      <dd>
        <RatingBadge rating={rating} />
      </dd>
    </div>
  );
}

function TechnologyAssessment({
  title,
  assessment,
  recommended,
}: TechnologyAssessmentProps) {
  return (
    <Card
      className={
        recommended
          ? "border-emerald-300 bg-emerald-50/40"
          : "bg-white"
      }
    >
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div>
            <CardTitle>{title}</CardTitle>
            <CardDescription className="mt-1">
              Overall score {formatNumericValue(assessment.overall_score)}
            </CardDescription>
          </div>

          {recommended && (
            <Badge className="bg-emerald-700 text-white hover:bg-emerald-700">
              RECOMMENDED
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-5">
        <dl className="grid gap-2">
          <AssessmentRating
            label="Capacity Fit"
            rating={assessment.capacity_rating}
          />
          <AssessmentRating
            label="Pressure Ratio Fit"
            rating={assessment.pressure_ratio_rating}
          />
          <AssessmentRating
            label="Turndown Fit"
            rating={assessment.turndown_rating}
          />
          <AssessmentRating
            label="Efficiency Fit"
            rating={assessment.efficiency_rating}
          />
          <AssessmentRating
            label="Maintenance Fit"
            rating={assessment.maintenance_rating}
          />
        </dl>

        <div>
          <h3 className="text-sm font-semibold text-slate-950">
            Engineering Rationale
          </h3>

          <ul className="mt-3 space-y-2">
            {assessment.rationale.map((item) => (
              <li
                key={item}
                className="flex gap-2 text-sm leading-6 text-slate-700"
              >
                <CheckCircle2 className="mt-1 size-4 shrink-0 text-slate-400" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}

function getSelectionErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (
      typeof error.details === "object" &&
      error.details !== null &&
      "detail" in error.details &&
      typeof error.details.detail === "string"
    ) {
      return error.details.detail;
    }

    return `The selection service returned HTTP ${error.status}.`;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "The compressor technology selection could not be completed.";
}

export function CompressorSelectionPage() {
  const { accessToken } = useAuth();
  const {
    projectId,
    hasValidProjectId,
    project,
    projectQuery,
  } = useProjectContext();

  const [requiredFlow, setRequiredFlow] = useState("3000");
  const [suctionPressure, setSuctionPressure] = useState("1.0");
  const [dischargePressure, setDischargePressure] = useState("8.0");
  const [turndown, setTurndown] = useState("0.30");
  const [continuousOperation, setContinuousOperation] = useState(true);
  const [molecularWeight, setMolecularWeight] = useState("28.97");
  const [operatingHours, setOperatingHours] = useState("8000");

  const [persistResult, setPersistResult] = useState(false);
  const [calculationCode, setCalculationCode] = useState("");
  const [title, setTitle] = useState("Compressor Type Selection");
  const [engineeringNotes, setEngineeringNotes] = useState("");

  const [result, setResult] =
    useState<CompressorSelectionExecutionResponse | null>(null);

  const requiredFlowValue = Number(requiredFlow);
  const suctionPressureValue = Number(suctionPressure);
  const dischargePressureValue = Number(dischargePressure);
  const turndownValue = Number(turndown);
  const molecularWeightValue = Number(molecularWeight);
  const operatingHoursValue = Number(operatingHours);

  const flowIsValid =
    Number.isFinite(requiredFlowValue) && requiredFlowValue > 0;
  const pressureBasisIsValid =
    Number.isFinite(suctionPressureValue) &&
    suctionPressureValue > 0 &&
    Number.isFinite(dischargePressureValue) &&
    dischargePressureValue > suctionPressureValue;
  const turndownIsValid =
    Number.isFinite(turndownValue) &&
    turndownValue > 0 &&
    turndownValue <= 1;
  const molecularWeightIsValid =
    Number.isFinite(molecularWeightValue) && molecularWeightValue > 0;
  const operatingHoursAreValid =
    operatingHours.trim().length > 0 &&
    Number.isFinite(operatingHoursValue) &&
    operatingHoursValue >= 0;
  const persistenceIsValid =
    !persistResult ||
    (calculationCode.trim().length > 0 && title.trim().length > 0);

  const pressureRatio = pressureBasisIsValid
    ? dischargePressureValue / suctionPressureValue
    : null;

  const selectionMutation = useMutation({
    mutationFn: () => {
      if (!accessToken) {
        throw new Error("Authenticated access token is required.");
      }

      return executeCompressorSelection(
        accessToken,
        {
          calculation: {
            required_flow_m3_per_hr: requiredFlowValue,
            suction_pressure_bar: suctionPressureValue,
            discharge_pressure_bar: dischargePressureValue,
            required_turndown_fraction: turndownValue,
            continuous_operation: continuousOperation,
            gas_molecular_weight: molecularWeightValue,
            estimated_operating_hours_per_year: operatingHoursValue,
          },
          execution: {
            persist_result: persistResult,
            project_id: persistResult ? projectId : null,
            calculation_code: persistResult
              ? calculationCode.trim()
              : null,
            title: persistResult ? title.trim() : null,
            engineering_notes:
              persistResult && engineeringNotes.trim()
                ? engineeringNotes.trim()
                : null,
          },
        },
      );
    },
    onSuccess: (response) => {
      setResult(response);
    },
  });

  if (!accessToken) {
    throw new Error("Authenticated access token is required.");
  }

  if (!hasValidProjectId) {
    throw new Error("Valid project ID is required.");
  }

  const canSubmit =
    flowIsValid &&
    pressureBasisIsValid &&
    turndownIsValid &&
    molecularWeightIsValid &&
    operatingHoursAreValid &&
    persistenceIsValid &&
    !selectionMutation.isPending;

  function clearPreviousResult(): void {
    setResult(null);
    selectionMutation.reset();
  }

  function updateInput(
    setter: Dispatch<SetStateAction<string>>,
    value: string,
  ): void {
    setter(value);
    clearPreviousResult();
  }

  function updateBoolean(
    setter: Dispatch<SetStateAction<boolean>>,
    value: boolean,
  ): void {
    setter(value);
    clearPreviousResult();
  }

  function handleReset(): void {
    setRequiredFlow("3000");
    setSuctionPressure("1.0");
    setDischargePressure("8.0");
    setTurndown("0.30");
    setContinuousOperation(true);
    setMolecularWeight("28.97");
    setOperatingHours("8000");
    setPersistResult(false);
    setCalculationCode("");
    setTitle("Compressor Type Selection");
    setEngineeringNotes("");
    clearPreviousResult();
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();

    if (!canSubmit) {
      return;
    }

    setResult(null);
    selectionMutation.mutate();
  }

  return (
    <main className="mx-auto w-full max-w-7xl space-y-6 pb-12">
      <Card className="bg-white">
        <CardHeader>
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="space-y-3">
              <Badge variant="outline">
                Compressor Selection Engineering
              </Badge>

              <div>
                <h1 className="text-3xl font-bold tracking-tight text-slate-950">
                  Compressor Technology Selection
                </h1>

                <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
                  Compare reciprocating and centrifugal compressor suitability
                  using flow, pressure ratio, turndown, operating profile, gas
                  molecular weight, efficiency, and maintainability criteria.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-2 text-xs">
                <span className="font-semibold text-slate-900">
                  {project
                    ? `${project.project_code} · ${project.project_name}`
                    : projectQuery.isPending
                      ? "Loading project..."
                      : `Project ${projectId}`}
                </span>

                {project && (
                  <Badge variant="outline">{project.status}</Badge>
                )}

                <Badge variant="outline">Vendor Neutral</Badge>
                <Badge variant="outline">Decision Support</Badge>
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              <Button
                asChild
                variant="outline"
              >
                <Link to={`/projects/${projectId}/compressor`}>
                  <Wind className="size-4" />
                  Advanced Engineering
                </Link>
              </Button>

              <Button
                type="button"
                variant="outline"
                onClick={handleReset}
                disabled={selectionMutation.isPending}
              >
                <RotateCcw className="size-4" />
                Reset
              </Button>

              <Button
                type="submit"
                form="compressor-selection-form"
                disabled={!canSubmit}
              >
                <Play className="size-4" />
                {selectionMutation.isPending
                  ? "Evaluating..."
                  : "Run Selection"}
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-start gap-3">
            <Scale className="mt-0.5 size-5 shrink-0 text-slate-500" />

            <div>
              <CardTitle>Guided Technology Selection Workflow</CardTitle>

              <CardDescription className="mt-1 leading-6">
                Establish the design duty and operating profile, evaluate each
                technology against the same engineering basis, and retain the
                recommendation in the project record when required.
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="flex flex-wrap gap-2">
          <Badge variant="outline">01 Design Duty</Badge>
          <Badge variant="outline">02 Pressure Basis</Badge>
          <Badge variant="outline">03 Operating Profile</Badge>
          <Badge variant="outline">04 Technology Scoring</Badge>
          <Badge variant="outline">05 Recommendation</Badge>
        </CardContent>
      </Card>

      <form
        id="compressor-selection-form"
        className="space-y-6"
        onSubmit={handleSubmit}
      >
        <Card>
          <CardHeader>
            <div className="flex items-start gap-3">
              <Gauge className="mt-0.5 size-5 shrink-0 text-slate-500" />

              <div>
                <CardTitle>Design Duty and Pressure Basis</CardTitle>

                <CardDescription className="mt-1 leading-6">
                  Define the required capacity and suction-to-discharge pressure
                  basis used for the technology suitability assessment.
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-5">
            <fieldset className="grid gap-5 md:grid-cols-3">
              <legend className="sr-only">
                Compressor design duty and pressure basis
              </legend>

              <EngineeringInput
                id="required-flow"
                label="Required Flow"
                unit="m³/hr"
                type="number"
                min="0.01"
                step="any"
                inputMode="decimal"
                required
                value={requiredFlow}
                onChange={(event) =>
                  updateInput(setRequiredFlow, event.target.value)
                }
              />

              <EngineeringInput
                id="suction-pressure"
                label="Suction Pressure"
                unit="bar"
                type="number"
                min="0.01"
                step="any"
                inputMode="decimal"
                required
                value={suctionPressure}
                onChange={(event) =>
                  updateInput(setSuctionPressure, event.target.value)
                }
              />

              <EngineeringInput
                id="discharge-pressure"
                label="Discharge Pressure"
                unit="bar"
                type="number"
                min="0.01"
                step="any"
                inputMode="decimal"
                required
                value={dischargePressure}
                onChange={(event) =>
                  updateInput(setDischargePressure, event.target.value)
                }
              />
            </fieldset>

            <div
              role={pressureBasisIsValid ? "status" : "alert"}
              className={`rounded-xl border p-4 ${
                pressureBasisIsValid
                  ? "border-emerald-200 bg-emerald-50"
                  : "border-red-300 bg-red-50"
              }`}
            >
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-start gap-3">
                  {pressureBasisIsValid ? (
                    <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-emerald-700" />
                  ) : (
                    <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-700" />
                  )}

                  <div>
                    <p className="text-sm font-semibold text-slate-950">
                      Pressure Basis Check
                    </p>

                    <p className="mt-1 text-sm leading-6 text-slate-700">
                      {pressureBasisIsValid
                        ? "The discharge pressure exceeds the suction pressure and the ratio is ready for assessment."
                        : "Enter positive pressures with discharge pressure greater than suction pressure."}
                    </p>
                  </div>
                </div>

                <div className="text-left sm:text-right">
                  <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                    Pressure Ratio
                  </p>

                  <p className="mt-1 font-mono text-lg font-semibold text-slate-950">
                    {pressureRatio === null
                      ? "Invalid"
                      : pressureRatio.toFixed(3)}
                  </p>
                </div>
              </div>
            </div>

            <p className="text-xs leading-5 text-slate-500">
              Use one consistent pressure basis for both entries. The API
              contract is preserved exactly; no hidden pressure conversion is
              applied by this workspace.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-start gap-3">
              <Settings2 className="mt-0.5 size-5 shrink-0 text-slate-500" />

              <div>
                <CardTitle>Operating Profile and Gas Basis</CardTitle>

                <CardDescription className="mt-1 leading-6">
                  Record the required turndown, annual utilization, gas
                  molecular weight, and continuity expectation used in the
                  technology comparison.
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-5">
            <fieldset className="grid gap-5 md:grid-cols-3">
              <legend className="sr-only">
                Compressor operating profile and gas basis
              </legend>

              <EngineeringInput
                id="turndown"
                label="Required Turndown"
                unit="fraction"
                type="number"
                min="0.01"
                max="1"
                step="any"
                inputMode="decimal"
                required
                value={turndown}
                onChange={(event) =>
                  updateInput(setTurndown, event.target.value)
                }
              />

              <EngineeringInput
                id="molecular-weight"
                label="Gas Molecular Weight"
                unit="kg/kmol"
                type="number"
                min="0.01"
                step="any"
                inputMode="decimal"
                required
                value={molecularWeight}
                onChange={(event) =>
                  updateInput(setMolecularWeight, event.target.value)
                }
              />

              <EngineeringInput
                id="operating-hours"
                label="Annual Operating Hours"
                unit="hr/year"
                type="number"
                min="0"
                step="any"
                inputMode="decimal"
                required
                value={operatingHours}
                onChange={(event) =>
                  updateInput(setOperatingHours, event.target.value)
                }
              />
            </fieldset>

            <label className="flex cursor-pointer items-start gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4">
              <input
                type="checkbox"
                className="mt-1 size-4 rounded border-slate-300"
                checked={continuousOperation}
                onChange={(event) =>
                  updateBoolean(
                    setContinuousOperation,
                    event.target.checked,
                  )
                }
              />

              <span>
                <span className="block text-sm font-semibold text-slate-950">
                  Continuous Operation Required
                </span>
                <span className="mt-1 block text-sm leading-6 text-slate-600">
                  Include continuous-duty suitability and maintainability in
                  the technology recommendation.
                </span>
              </span>
            </label>

            <div className="grid gap-3 sm:grid-cols-3">
              <div className="rounded-xl border border-slate-200 bg-white p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  Design Flow
                </p>
                <p className="mt-2 text-lg font-semibold text-slate-950">
                  {flowIsValid
                    ? requiredFlowValue.toLocaleString("en-IN")
                    : "Invalid"}
                  {flowIsValid && (
                    <span className="ml-1 text-sm text-slate-500">
                      m³/hr
                    </span>
                  )}
                </p>
              </div>

              <div className="rounded-xl border border-slate-200 bg-white p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  Turndown Requirement
                </p>
                <p className="mt-2 text-lg font-semibold text-slate-950">
                  {turndownIsValid
                    ? `${(turndownValue * 100).toFixed(1)}%`
                    : "Invalid"}
                </p>
              </div>

              <div className="rounded-xl border border-slate-200 bg-white p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  Duty Profile
                </p>
                <p className="mt-2 text-lg font-semibold text-slate-950">
                  {continuousOperation ? "Continuous" : "Intermittent"}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-start gap-3">
              <Save className="mt-0.5 size-5 shrink-0 text-slate-500" />

              <div>
                <CardTitle>Project Record</CardTitle>

                <CardDescription className="mt-1 leading-6">
                  Run an advisory calculation only, or retain the result as an
                  auditable calculation case inside the active project.
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-5">
            <label className="flex cursor-pointer items-start gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4">
              <input
                type="checkbox"
                className="mt-1 size-4 rounded border-slate-300"
                checked={persistResult}
                onChange={(event) =>
                  updateBoolean(setPersistResult, event.target.checked)
                }
              />

              <span>
                <span className="block text-sm font-semibold text-slate-950">
                  Save Result to Project
                </span>
                <span className="mt-1 block text-sm leading-6 text-slate-600">
                  Create a calculation case linked to the active authenticated
                  project and retain its engineering notes.
                </span>
              </span>
            </label>

            {persistResult ? (
              <fieldset className="grid gap-5 md:grid-cols-2">
                <legend className="sr-only">
                  Calculation persistence details
                </legend>

                <EngineeringInput
                  id="calculation-code"
                  label="Calculation Code"
                  autoComplete="off"
                  required
                  value={calculationCode}
                  onChange={(event) =>
                    updateInput(setCalculationCode, event.target.value)
                  }
                />

                <EngineeringInput
                  id="calculation-title"
                  label="Calculation Title"
                  autoComplete="off"
                  required
                  value={title}
                  onChange={(event) =>
                    updateInput(setTitle, event.target.value)
                  }
                />

                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="engineering-notes">
                    Engineering Notes
                  </Label>
                  <textarea
                    id="engineering-notes"
                    className="min-h-28 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm shadow-sm outline-none transition focus-visible:border-slate-400 focus-visible:ring-2 focus-visible:ring-slate-200"
                    value={engineeringNotes}
                    onChange={(event) =>
                      updateInput(setEngineeringNotes, event.target.value)
                    }
                  />
                </div>
              </fieldset>
            ) : (
              <div className="rounded-xl border border-slate-200 bg-white p-4 text-sm leading-6 text-slate-600">
                The recommendation will be returned for review without creating
                a persistent calculation case.
              </div>
            )}
          </CardContent>
        </Card>

        <div className="flex justify-end">
          <Button
            type="submit"
            size="lg"
            disabled={!canSubmit}
          >
            <Play className="size-4" />
            {selectionMutation.isPending
              ? "Evaluating Technologies..."
              : "Evaluate Compressor Technologies"}
          </Button>
        </div>
      </form>

      {selectionMutation.isError && (
        <Card className="border-red-300 bg-red-50">
          <CardHeader>
            <div className="flex items-start gap-3">
              <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-700" />

              <div>
                <CardTitle className="text-red-950">
                  Compressor Selection Error
                </CardTitle>

                <CardDescription className="mt-1 leading-6 text-red-800">
                  {getSelectionErrorMessage(selectionMutation.error)}
                </CardDescription>

                <p className="mt-2 text-sm leading-6 text-red-800">
                  Confirm the capacity, pressure relationship, turndown, gas
                  basis, and project-record details before trying again.
                </p>
              </div>
            </div>
          </CardHeader>
        </Card>
      )}

      {result && (
        <Card className="border-emerald-200 bg-emerald-50/40">
          <CardHeader>
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-emerald-700" />

                <div>
                  <CardTitle>Technology Selection Complete</CardTitle>

                  <CardDescription className="mt-1 leading-6">
                    Review the comparative ratings, deterministic rationale,
                    and recommended compressor technology for the entered duty.
                  </CardDescription>
                </div>
              </div>

              <Badge className="bg-emerald-700 text-white hover:bg-emerald-700">
                {formatCompressorType(result.result.recommended_type)}
              </Badge>
            </div>
          </CardHeader>

          <CardContent className="space-y-6">
            <dl className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <ResultMetric
                label="Recommended Technology"
                value={formatCompressorType(result.result.recommended_type)}
                description="Highest-ranked option for the submitted engineering basis"
              />

              <ResultMetric
                label="Reciprocating Score"
                value={formatNumericValue(
                  result.result.reciprocating.overall_score,
                )}
              />

              <ResultMetric
                label="Centrifugal Score"
                value={formatNumericValue(
                  result.result.centrifugal.overall_score,
                )}
              />

              <ResultMetric
                label="Score Difference"
                value={formatNumericValue(result.result.score_difference)}
                description="Decision separation reported by the engine"
              />
            </dl>

            <div className="rounded-xl border border-emerald-200 bg-white p-5">
              <div className="flex items-start gap-3">
                <BarChart3 className="mt-0.5 size-5 shrink-0 text-emerald-700" />

                <div>
                  <h2 className="text-sm font-semibold text-slate-950">
                    Recommendation Summary
                  </h2>
                  <p className="mt-2 text-sm leading-6 text-slate-700">
                    {result.result.recommendation_summary}
                  </p>
                </div>
              </div>
            </div>

            <section aria-labelledby="technology-comparison-heading">
              <h2
                id="technology-comparison-heading"
                className="mb-3 text-sm font-semibold text-slate-950"
              >
                Technology Assessment Matrix
              </h2>

              <div className="grid gap-4 lg:grid-cols-2">
                <TechnologyAssessment
                  title="Reciprocating Compressor"
                  assessment={result.result.reciprocating}
                  recommended={
                    result.result.recommended_type === "RECIPROCATING"
                  }
                />

                <TechnologyAssessment
                  title="Centrifugal Compressor"
                  assessment={result.result.centrifugal}
                  recommended={
                    result.result.recommended_type === "CENTRIFUGAL"
                  }
                />
              </div>
            </section>

            {result.calculation_case_id !== null && (
              <div className="flex flex-col gap-4 rounded-xl border border-blue-200 bg-blue-50 p-5 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm font-semibold text-blue-950">
                    Calculation Case Saved
                  </p>
                  <p className="mt-1 text-sm leading-6 text-blue-800">
                    Case ID {result.calculation_case_id} is linked to the active
                    project and available in Calculation History.
                  </p>
                </div>

                <Button
                  asChild
                  variant="outline"
                  className="border-blue-300 bg-white"
                >
                  <Link
                    to={`/projects/${projectId}/calculations/${result.calculation_case_id}`}
                  >
                    <Save className="size-4" />
                    Open Saved Case
                  </Link>
                </Button>
              </div>
            )}

            <details className="rounded-xl border border-slate-200 bg-white">
              <summary className="cursor-pointer px-4 py-3 text-sm font-semibold text-slate-800">
                View complete technology-selection result payload
              </summary>

              <pre className="max-h-[32rem] overflow-auto border-t border-slate-200 bg-slate-950 p-4 text-xs leading-6 text-slate-100">
                {JSON.stringify(result, null, 2)}
              </pre>
            </details>
          </CardContent>
        </Card>
      )}
    </main>
  );
}
