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
  CheckCircle2,
  Cylinder,
  Gauge,
  Play,
  RotateCcw,
  Save,
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
import { executeReciprocatingCalculation } from "../features/projects/reciprocatingService";
import type {
  CylinderAction,
  EngineeringNumber,
  ReciprocatingExecutionResponse,
} from "../features/projects/reciprocatingTypes";
import { useProjectContext } from "../features/projects/useProjectContext";
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

function formatEngineeringNumber(
  value: EngineeringNumber,
  maximumFractionDigits = 2,
): string {
  const numericValue = Number(value);

  if (!Number.isFinite(numericValue)) {
    return String(value);
  }

  return numericValue.toLocaleString("en-IN", {
    maximumFractionDigits,
  });
}

function formatPercentage(
  value: EngineeringNumber,
  maximumFractionDigits = 1,
): string {
  const numericValue = Number(value);

  if (!Number.isFinite(numericValue)) {
    return String(value);
  }

  return `${(numericValue * 100).toLocaleString("en-IN", {
    maximumFractionDigits,
  })}%`;
}

function formatCylinderAction(action: CylinderAction): string {
  return action === "DOUBLE_ACTING"
    ? "Double Acting"
    : "Single Acting";
}

function getCalculationErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (
      typeof error.details === "object" &&
      error.details !== null &&
      "detail" in error.details &&
      typeof error.details.detail === "string"
    ) {
      return error.details.detail;
    }

    return `The reciprocating calculation service returned HTTP ${error.status}.`;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "The reciprocating compressor calculation could not be completed.";
}

export function ReciprocatingEngineeringPage() {
  const { accessToken } = useAuth();
  const {
    projectId,
    hasValidProjectId,
    project,
    projectQuery,
  } = useProjectContext();

  const [requiredFlow, setRequiredFlow] = useState("1000");
  const [bore, setBore] = useState("250");
  const [stroke, setStroke] = useState("200");
  const [rodDiameter, setRodDiameter] = useState("60");
  const [speedRpm, setSpeedRpm] = useState("600");
  const [clearanceFraction, setClearanceFraction] = useState("0.05");

  const [stageCompressionRatio, setStageCompressionRatio] =
    useState("3.0");
  const [suctionZ, setSuctionZ] = useState("1.0");
  const [dischargeZ, setDischargeZ] = useState("1.0");
  const [isentropicExponent, setIsentropicExponent] = useState("1.4");

  const [suctionPressure, setSuctionPressure] = useState("1.013");
  const [dischargePressure, setDischargePressure] = useState("8.0");
  const [allowableRodLoad, setAllowableRodLoad] = useState("150");

  const [persistResult, setPersistResult] = useState(false);
  const [calculationCode, setCalculationCode] = useState("");
  const [title, setTitle] =
    useState("Reciprocating Compressor Calculation");
  const [engineeringNotes, setEngineeringNotes] = useState("");

  const [result, setResult] =
    useState<ReciprocatingExecutionResponse | null>(null);

  const requiredFlowValue = Number(requiredFlow);
  const boreValue = Number(bore);
  const strokeValue = Number(stroke);
  const rodDiameterValue = Number(rodDiameter);
  const speedRpmValue = Number(speedRpm);
  const clearanceFractionValue = Number(clearanceFraction);
  const stageCompressionRatioValue = Number(stageCompressionRatio);
  const suctionZValue = Number(suctionZ);
  const dischargeZValue = Number(dischargeZ);
  const isentropicExponentValue = Number(isentropicExponent);
  const suctionPressureValue = Number(suctionPressure);
  const dischargePressureValue = Number(dischargePressure);
  const allowableRodLoadValue = Number(allowableRodLoad);

  const flowIsValid =
    Number.isFinite(requiredFlowValue) && requiredFlowValue > 0;
  const geometryIsValid =
    Number.isFinite(boreValue) &&
    boreValue > 0 &&
    Number.isFinite(strokeValue) &&
    strokeValue > 0 &&
    rodDiameter.trim().length > 0 &&
    Number.isFinite(rodDiameterValue) &&
    rodDiameterValue >= 0 &&
    rodDiameterValue < boreValue &&
    Number.isFinite(speedRpmValue) &&
    speedRpmValue > 0 &&
    clearanceFraction.trim().length > 0 &&
    Number.isFinite(clearanceFractionValue) &&
    clearanceFractionValue >= 0 &&
    clearanceFractionValue < 1;
  const thermodynamicBasisIsValid =
    Number.isFinite(stageCompressionRatioValue) &&
    stageCompressionRatioValue > 1 &&
    Number.isFinite(suctionZValue) &&
    suctionZValue > 0 &&
    Number.isFinite(dischargeZValue) &&
    dischargeZValue > 0 &&
    Number.isFinite(isentropicExponentValue) &&
    isentropicExponentValue > 1;
  const pressureBasisIsValid =
    Number.isFinite(suctionPressureValue) &&
    suctionPressureValue > 0 &&
    Number.isFinite(dischargePressureValue) &&
    dischargePressureValue > suctionPressureValue;
  const rodLoadBasisIsValid =
    Number.isFinite(allowableRodLoadValue) && allowableRodLoadValue > 0;
  const persistenceIsValid =
    !persistResult ||
    (calculationCode.trim().length > 0 && title.trim().length > 0);

  const overallPressureRatio = pressureBasisIsValid
    ? dischargePressureValue / suctionPressureValue
    : null;
  const rodToBoreRatio = geometryIsValid
    ? rodDiameterValue / boreValue
    : null;
  const theoreticalDisplacement = geometryIsValid
    ? (() => {
        const boreM = boreValue / 1000;
        const rodDiameterM = rodDiameterValue / 1000;
        const strokeM = strokeValue / 1000;
        const pistonAreaM2 = Math.PI * boreM ** 2 / 4;
        const rodAreaM2 = Math.PI * rodDiameterM ** 2 / 4;
        const displacementPerRevolutionM3 =
          (2 * pistonAreaM2 - rodAreaM2) * strokeM;

        return displacementPerRevolutionM3 * speedRpmValue * 60;
      })()
    : null;

  const calculationMutation = useMutation({
    mutationFn: () => {
      if (!accessToken) {
        throw new Error("Authenticated access token is required.");
      }

      return executeReciprocatingCalculation(
        accessToken,
        {
          calculation: {
            required_flow_m3_per_hr: requiredFlowValue,
            bore_mm: boreValue,
            stroke_mm: strokeValue,
            rod_diameter_mm: rodDiameterValue,
            speed_rpm: speedRpmValue,
            clearance_fraction: clearanceFractionValue,
            stage_compression_ratio: stageCompressionRatioValue,
            suction_z_factor: suctionZValue,
            discharge_z_factor: dischargeZValue,
            isentropic_exponent: isentropicExponentValue,
            suction_pressure_bar: suctionPressureValue,
            discharge_pressure_bar: dischargePressureValue,
            allowable_rod_load_kn: allowableRodLoadValue,
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
    geometryIsValid &&
    thermodynamicBasisIsValid &&
    pressureBasisIsValid &&
    rodLoadBasisIsValid &&
    persistenceIsValid &&
    !calculationMutation.isPending;

  function clearPreviousResult(): void {
    setResult(null);
    calculationMutation.reset();
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
    setRequiredFlow("1000");
    setBore("250");
    setStroke("200");
    setRodDiameter("60");
    setSpeedRpm("600");
    setClearanceFraction("0.05");
    setStageCompressionRatio("3.0");
    setSuctionZ("1.0");
    setDischargeZ("1.0");
    setIsentropicExponent("1.4");
    setSuctionPressure("1.013");
    setDischargePressure("8.0");
    setAllowableRodLoad("150");
    setPersistResult(false);
    setCalculationCode("");
    setTitle("Reciprocating Compressor Calculation");
    setEngineeringNotes("");
    clearPreviousResult();
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();

    if (!canSubmit) {
      return;
    }

    setResult(null);
    calculationMutation.mutate();
  }

  return (
    <main className="mx-auto w-full max-w-7xl space-y-6 pb-12">
      <Card className="bg-white">
        <CardHeader>
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="space-y-3">
              <Badge variant="outline">
                Reciprocating Compressor Engineering
              </Badge>

              <div>
                <h1 className="text-3xl font-bold tracking-tight text-slate-950">
                  Reciprocating Compressor Engineering
                </h1>

                <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
                  Evaluate double-acting cylinder displacement, volumetric
                  efficiency, installed capacity, cylinder count, and rod-load
                  suitability against one traceable engineering basis.
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
                <Badge variant="outline">Cylinder Sizing</Badge>
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
                disabled={calculationMutation.isPending}
              >
                <RotateCcw className="size-4" />
                Reset
              </Button>

              <Button
                type="submit"
                form="reciprocating-engineering-form"
                disabled={!canSubmit}
              >
                <Play className="size-4" />
                {calculationMutation.isPending
                  ? "Calculating..."
                  : "Run Calculation"}
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-start gap-3">
            <Settings2 className="mt-0.5 size-5 shrink-0 text-slate-500" />

            <div>
              <CardTitle>Guided Reciprocating Design Workflow</CardTitle>

              <CardDescription className="mt-1 leading-6">
                Establish the capacity duty and cylinder geometry, confirm the
                gas and pressure basis, assess rod loading, and optionally
                retain the completed case in the active project.
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          <div className="grid gap-3 md:grid-cols-3">
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                1 · Capacity and Geometry
              </p>
              <p className="mt-2 text-sm leading-6 text-slate-700">
                Define flow, bore, stroke, rod diameter, speed, and clearance.
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                2 · Compression Basis
              </p>
              <p className="mt-2 text-sm leading-6 text-slate-700">
                Enter stage ratio, gas factors, absolute pressures, and rod-load
                limit.
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                3 · Engineering Review
              </p>
              <p className="mt-2 text-sm leading-6 text-slate-700">
                Review cylinder count, capacity margin, efficiency, and rod-load
                adequacy.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <form
        id="reciprocating-engineering-form"
        className="space-y-6"
        onSubmit={handleSubmit}
      >
        <Card>
          <CardHeader>
            <div className="flex items-start gap-3">
              <Cylinder className="mt-0.5 size-5 shrink-0 text-slate-500" />

              <div>
                <CardTitle>Capacity Duty and Cylinder Geometry</CardTitle>

                <CardDescription className="mt-1 leading-6">
                  Define the required delivered flow and the double-acting
                  cylinder geometry used for theoretical displacement and
                  cylinder-count sizing.
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-5">
            <fieldset className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
              <legend className="sr-only">
                Capacity duty and cylinder geometry
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
                id="bore"
                label="Cylinder Bore"
                unit="mm"
                type="number"
                min="0.01"
                step="any"
                inputMode="decimal"
                required
                value={bore}
                onChange={(event) =>
                  updateInput(setBore, event.target.value)
                }
              />

              <EngineeringInput
                id="stroke"
                label="Piston Stroke"
                unit="mm"
                type="number"
                min="0.01"
                step="any"
                inputMode="decimal"
                required
                value={stroke}
                onChange={(event) =>
                  updateInput(setStroke, event.target.value)
                }
              />

              <EngineeringInput
                id="rod-diameter"
                label="Piston Rod Diameter"
                unit="mm"
                type="number"
                min="0"
                step="any"
                inputMode="decimal"
                required
                value={rodDiameter}
                onChange={(event) =>
                  updateInput(setRodDiameter, event.target.value)
                }
              />

              <EngineeringInput
                id="speed"
                label="Compressor Speed"
                unit="rpm"
                type="number"
                min="0.01"
                step="any"
                inputMode="decimal"
                required
                value={speedRpm}
                onChange={(event) =>
                  updateInput(setSpeedRpm, event.target.value)
                }
              />

              <EngineeringInput
                id="clearance"
                label="Clearance Fraction"
                unit="fraction"
                type="number"
                min="0"
                max="0.999"
                step="any"
                inputMode="decimal"
                required
                value={clearanceFraction}
                onChange={(event) =>
                  updateInput(setClearanceFraction, event.target.value)
                }
              />
            </fieldset>

            <div
              role={geometryIsValid ? "status" : "alert"}
              className={`rounded-xl border p-4 ${
                geometryIsValid
                  ? "border-emerald-200 bg-emerald-50"
                  : "border-red-300 bg-red-50"
              }`}
            >
              <div className="flex items-start gap-3">
                {geometryIsValid ? (
                  <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-emerald-700" />
                ) : (
                  <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-700" />
                )}

                <div>
                  <p className="text-sm font-semibold text-slate-950">
                    Cylinder Geometry Check
                  </p>

                  <p className="mt-1 text-sm leading-6 text-slate-700">
                    {geometryIsValid
                      ? "The bore, stroke, rod diameter, speed, and clearance define a valid double-acting cylinder basis."
                      : "Enter positive bore, stroke, and speed values; keep rod diameter below bore and clearance from zero to less than one."}
                  </p>
                </div>
              </div>
            </div>

            <dl className="grid gap-3 sm:grid-cols-3">
              <ResultMetric
                label="Required Flow"
                value={
                  flowIsValid
                    ? `${requiredFlowValue.toLocaleString("en-IN")} m³/hr`
                    : "Invalid"
                }
              />

              <ResultMetric
                label="Rod-to-Bore Ratio"
                value={
                  rodToBoreRatio === null
                    ? "Invalid"
                    : formatPercentage(rodToBoreRatio)
                }
                description="Geometric ratio for the entered piston rod and bore"
              />

              <ResultMetric
                label="Theoretical Displacement"
                value={
                  theoreticalDisplacement === null
                    ? "Invalid"
                    : `${theoreticalDisplacement.toLocaleString("en-IN", {
                        maximumFractionDigits: 2,
                      })} m³/hr`
                }
                description="Live double-acting preview before volumetric-efficiency correction"
              />
            </dl>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-start gap-3">
              <Gauge className="mt-0.5 size-5 shrink-0 text-slate-500" />

              <div>
                <CardTitle>Compression and Rod-load Basis</CardTitle>

                <CardDescription className="mt-1 leading-6">
                  Establish the per-stage compression basis, gas
                  compressibility values, absolute pressure differential, and
                  allowable piston-rod load.
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-5">
            <fieldset className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
              <legend className="sr-only">
                Compression thermodynamic basis
              </legend>

              <EngineeringInput
                id="stage-ratio"
                label="Stage Compression Ratio"
                unit="ratio"
                type="number"
                min="1.0001"
                step="any"
                inputMode="decimal"
                required
                value={stageCompressionRatio}
                onChange={(event) =>
                  updateInput(setStageCompressionRatio, event.target.value)
                }
              />

              <EngineeringInput
                id="suction-z"
                label="Suction Z-Factor"
                type="number"
                min="0.01"
                step="any"
                inputMode="decimal"
                required
                value={suctionZ}
                onChange={(event) =>
                  updateInput(setSuctionZ, event.target.value)
                }
              />

              <EngineeringInput
                id="discharge-z"
                label="Discharge Z-Factor"
                type="number"
                min="0.01"
                step="any"
                inputMode="decimal"
                required
                value={dischargeZ}
                onChange={(event) =>
                  updateInput(setDischargeZ, event.target.value)
                }
              />

              <EngineeringInput
                id="isentropic-exponent"
                label="Isentropic Exponent"
                unit="k"
                type="number"
                min="1.0001"
                step="any"
                inputMode="decimal"
                required
                value={isentropicExponent}
                onChange={(event) =>
                  updateInput(setIsentropicExponent, event.target.value)
                }
              />

              <EngineeringInput
                id="suction-pressure"
                label="Suction Pressure"
                unit="bar(a)"
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
                unit="bar(a)"
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

              <EngineeringInput
                id="rod-load"
                label="Allowable Rod Load"
                unit="kN"
                type="number"
                min="0.01"
                step="any"
                inputMode="decimal"
                required
                value={allowableRodLoad}
                onChange={(event) =>
                  updateInput(setAllowableRodLoad, event.target.value)
                }
              />
            </fieldset>

            <div
              role={
                pressureBasisIsValid &&
                thermodynamicBasisIsValid &&
                rodLoadBasisIsValid
                  ? "status"
                  : "alert"
              }
              className={`rounded-xl border p-4 ${
                pressureBasisIsValid &&
                thermodynamicBasisIsValid &&
                rodLoadBasisIsValid
                  ? "border-emerald-200 bg-emerald-50"
                  : "border-red-300 bg-red-50"
              }`}
            >
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-start gap-3">
                  {pressureBasisIsValid &&
                  thermodynamicBasisIsValid &&
                  rodLoadBasisIsValid ? (
                    <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-emerald-700" />
                  ) : (
                    <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-700" />
                  )}

                  <div>
                    <p className="text-sm font-semibold text-slate-950">
                      Compression Basis Check
                    </p>

                    <p className="mt-1 text-sm leading-6 text-slate-700">
                      {pressureBasisIsValid &&
                      thermodynamicBasisIsValid &&
                      rodLoadBasisIsValid
                        ? "The pressure relationship, gas factors, stage ratio, exponent, and allowable rod load are ready for calculation."
                        : "Use absolute pressures with discharge above suction, stage ratio and exponent above one, positive Z-factors, and a positive allowable rod load."}
                    </p>
                  </div>
                </div>

                <div className="text-left sm:text-right">
                  <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                    Overall Pressure Ratio
                  </p>

                  <p className="mt-1 font-mono text-lg font-semibold text-slate-950">
                    {overallPressureRatio === null
                      ? "Invalid"
                      : overallPressureRatio.toFixed(3)}
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm leading-6 text-slate-600">
                Enter suction and discharge pressure as absolute values. The
                stage compression ratio is used by the volumetric-efficiency
                model and may differ from the overall pressure ratio for a
                multistage arrangement.
              </p>
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
                The engineering result will be returned for review without
                creating a persistent calculation case.
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
            {calculationMutation.isPending
              ? "Calculating Reciprocating Case..."
              : "Calculate Reciprocating Case"}
          </Button>
        </div>
      </form>

      {calculationMutation.isError && (
        <Card className="border-red-300 bg-red-50">
          <CardHeader>
            <div className="flex items-start gap-3">
              <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-700" />

              <div>
                <CardTitle className="text-red-950">
                  Reciprocating Calculation Error
                </CardTitle>

                <CardDescription className="mt-1 leading-6 text-red-800">
                  {getCalculationErrorMessage(calculationMutation.error)}
                </CardDescription>

                <p className="mt-2 text-sm leading-6 text-red-800">
                  Confirm the capacity duty, cylinder geometry, thermodynamic
                  basis, pressure relationship, rod-load limit, and project
                  record details before trying again.
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
                  <CardTitle>
                    Reciprocating Engineering Complete
                  </CardTitle>

                  <CardDescription className="mt-1 leading-6">
                    Review displacement, volumetric efficiency, cylinder
                    sizing, installed capacity margin, and piston-rod loading
                    for the submitted design basis.
                  </CardDescription>
                </div>
              </div>

              <Badge
                variant="outline"
                className={
                  result.result.cylinder_sizing.capacity_is_adequate &&
                  result.result.rod_load.rod_load_is_adequate
                    ? "border-emerald-300 bg-emerald-100 text-emerald-900"
                    : "border-amber-300 bg-amber-100 text-amber-900"
                }
              >
                {result.result.cylinder_sizing.capacity_is_adequate &&
                result.result.rod_load.rod_load_is_adequate
                  ? "DESIGN ADEQUATE"
                  : "ENGINEERING REVIEW"}
              </Badge>
            </div>
          </CardHeader>

          <CardContent className="space-y-6">
            <dl className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <ResultMetric
                label="Required Cylinders"
                value={result.result.cylinder_sizing.required_cylinders.toLocaleString(
                  "en-IN",
                )}
                description="Whole-cylinder count selected by the sizing engine"
              />

              <ResultMetric
                label="Installed Capacity"
                value={`${formatEngineeringNumber(
                  result.result.cylinder_sizing.installed_capacity_m3_per_hr,
                )} m³/hr`}
              />

              <ResultMetric
                label="Capacity Margin"
                value={formatPercentage(
                  result.result.cylinder_sizing.capacity_margin_fraction,
                )}
                description={`${formatEngineeringNumber(
                  result.result.cylinder_sizing.capacity_margin_m3_per_hr,
                )} m³/hr above the required duty`}
              />

              <ResultMetric
                label="Maximum Rod Load"
                value={`${formatEngineeringNumber(
                  result.result.rod_load.maximum_absolute_load_kn,
                )} kN`}
                description={`${formatEngineeringNumber(
                  result.result.rod_load.allowable_rod_load_kn,
                )} kN allowable`}
              />
            </dl>

            <section aria-labelledby="cylinder-performance-heading">
              <div className="mb-3 flex items-center gap-2">
                <Cylinder className="size-4 text-slate-500" />
                <h2
                  id="cylinder-performance-heading"
                  className="text-sm font-semibold text-slate-950"
                >
                  Cylinder Performance
                </h2>
              </div>

              <dl className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                <ResultMetric
                  label="Cylinder Action"
                  value={formatCylinderAction(
                    result.result.capacity.geometry.action,
                  )}
                />

                <ResultMetric
                  label="Total Displacement"
                  value={`${formatEngineeringNumber(
                    result.result.capacity.displacement
                      .total_displacement_m3_per_hr,
                  )} m³/hr`}
                  description={`${formatEngineeringNumber(
                    result.result.capacity.displacement
                      .total_displacement_m3_per_min,
                  )} m³/min`}
                />

                <ResultMetric
                  label="Volumetric Efficiency"
                  value={formatPercentage(
                    result.result.capacity.volumetric_efficiency
                      .volumetric_efficiency,
                  )}
                />

                <ResultMetric
                  label="Delivered Flow per Cylinder"
                  value={`${formatEngineeringNumber(
                    result.result.cylinder_sizing
                      .delivered_flow_per_cylinder_m3_per_hr,
                  )} m³/hr`}
                />
              </dl>
            </section>

            <section aria-labelledby="displacement-detail-heading">
              <h2
                id="displacement-detail-heading"
                className="mb-3 text-sm font-semibold text-slate-950"
              >
                Geometry and Displacement Detail
              </h2>

              <dl className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                <ResultMetric
                  label="Piston Area"
                  value={`${formatEngineeringNumber(
                    result.result.capacity.displacement.piston_area_m2,
                    6,
                  )} m²`}
                />

                <ResultMetric
                  label="Rod Area"
                  value={`${formatEngineeringNumber(
                    result.result.capacity.displacement.rod_area_m2,
                    6,
                  )} m²`}
                />

                <ResultMetric
                  label="Head-end Displacement"
                  value={`${formatEngineeringNumber(
                    result.result.capacity.displacement
                      .head_end_displacement_m3_per_min,
                    4,
                  )} m³/min`}
                />

                <ResultMetric
                  label="Crank-end Displacement"
                  value={`${formatEngineeringNumber(
                    result.result.capacity.displacement
                      .crank_end_displacement_m3_per_min,
                    4,
                  )} m³/min`}
                />
              </dl>
            </section>

            <section aria-labelledby="adequacy-review-heading">
              <h2
                id="adequacy-review-heading"
                className="mb-3 text-sm font-semibold text-slate-950"
              >
                Engineering Adequacy Review
              </h2>

              <div className="grid gap-4 lg:grid-cols-2">
                <div
                  className={`rounded-xl border p-5 ${
                    result.result.cylinder_sizing.capacity_is_adequate
                      ? "border-emerald-200 bg-emerald-50"
                      : "border-red-300 bg-red-50"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {result.result.cylinder_sizing.capacity_is_adequate ? (
                      <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-emerald-700" />
                    ) : (
                      <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-700" />
                    )}

                    <div>
                      <h3 className="text-sm font-semibold text-slate-950">
                        Capacity Assessment
                      </h3>
                      <p className="mt-2 text-sm leading-6 text-slate-700">
                        {result.result.cylinder_sizing.capacity_is_adequate
                          ? "Installed cylinder capacity meets or exceeds the submitted required flow."
                          : "Installed cylinder capacity does not meet the submitted required flow and requires design revision."}
                      </p>
                    </div>
                  </div>
                </div>

                <div
                  className={`rounded-xl border p-5 ${
                    result.result.rod_load.rod_load_is_adequate
                      ? "border-emerald-200 bg-emerald-50"
                      : "border-red-300 bg-red-50"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {result.result.rod_load.rod_load_is_adequate ? (
                      <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-emerald-700" />
                    ) : (
                      <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-700" />
                    )}

                    <div>
                      <h3 className="text-sm font-semibold text-slate-950">
                        Rod-load Assessment
                      </h3>
                      <p className="mt-2 text-sm leading-6 text-slate-700">
                        {result.result.rod_load.rod_load_is_adequate
                          ? "The maximum absolute piston-rod load remains within the entered allowable limit."
                          : "The calculated piston-rod load exceeds the allowable limit and requires engineering review."}
                      </p>

                      <dl className="mt-3 grid gap-2 text-sm sm:grid-cols-2">
                        <div>
                          <dt className="text-slate-500">Compression Load</dt>
                          <dd className="mt-1 font-semibold text-slate-950">
                            {formatEngineeringNumber(
                              result.result.rod_load.compression_load_kn,
                            )}{" "}
                            kN
                          </dd>
                        </div>
                        <div>
                          <dt className="text-slate-500">Tension Load</dt>
                          <dd className="mt-1 font-semibold text-slate-950">
                            {formatEngineeringNumber(
                              result.result.rod_load.tension_load_kn,
                            )}{" "}
                            kN
                          </dd>
                        </div>
                      </dl>
                    </div>
                  </div>
                </div>
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
                View complete reciprocating calculation payload
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
