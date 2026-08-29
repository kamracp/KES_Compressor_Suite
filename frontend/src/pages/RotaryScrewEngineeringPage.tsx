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
  Gauge,
  Play,
  RotateCcw,
  Ruler,
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
import { executeRotaryScrewCalculation } from "../features/projects/rotaryScrewService";
import type {
  EngineeringNumber,
  RotaryScrewControlType,
  RotaryScrewExecutionResponse,
  RotaryScrewOilType,
  RotaryScrewStageCount,
} from "../features/projects/rotaryScrewTypes";
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
  maximumFractionDigits = 3,
): string {
  const numericValue = Number(value);

  if (!Number.isFinite(numericValue)) {
    return String(value);
  }

  return numericValue.toLocaleString("en-IN", {
    maximumFractionDigits,
  });
}

function formatOilType(oilType: RotaryScrewOilType): string {
  return oilType === "OIL_INJECTED" ? "Oil-Injected" : "Oil-Free";
}

function formatControlType(controlType: RotaryScrewControlType): string {
  return controlType === "FIXED_SPEED_LOAD_UNLOAD"
    ? "Fixed Speed (Load/Unload)"
    : "Variable Speed Drive";
}

function formatStageCount(stageCount: RotaryScrewStageCount): string {
  return stageCount === "SINGLE_STAGE" ? "Single Stage" : "Two Stage";
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

    return `The rotary screw calculation service returned HTTP ${error.status}.`;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "The rotary screw compressor calculation could not be completed.";
}

export function RotaryScrewEngineeringPage() {
  const { accessToken } = useAuth();
  const {
    projectId,
    hasValidProjectId,
    project,
    projectQuery,
  } = useProjectContext();

  const [inletPressure, setInletPressure] = useState("1.013");
  const [inletTemperature, setInletTemperature] = useState("300");
  const [dischargePressure, setDischargePressure] = useState("7.0");
  const [rotationalSpeed, setRotationalSpeed] = useState("3000");
  const [oilType, setOilType] =
    useState<RotaryScrewOilType>("OIL_INJECTED");
  const [controlType, setControlType] = useState<RotaryScrewControlType>(
    "FIXED_SPEED_LOAD_UNLOAD",
  );
  const [stageCount, setStageCount] =
    useState<RotaryScrewStageCount>("SINGLE_STAGE");

  const [ratedFad, setRatedFad] = useState("10");
  const [packageInputPower, setPackageInputPower] = useState("60");

  const [includeGeometry, setIncludeGeometry] = useState(false);
  const [maleRotorDiameter, setMaleRotorDiameter] = useState("200");
  const [rotorLength, setRotorLength] = useState("300");
  const [areaUtilisationCoefficient, setAreaUtilisationCoefficient] =
    useState("0.5");

  const [includeStandardAirCorrection, setIncludeStandardAirCorrection] =
    useState(false);
  const [referencePressure, setReferencePressure] = useState("1.013");
  const [referenceTemperature, setReferenceTemperature] = useState("293.15");

  const [persistResult, setPersistResult] = useState(false);
  const [calculationCode, setCalculationCode] = useState("");
  const [title, setTitle] = useState("Rotary Screw Compressor Calculation");
  const [engineeringNotes, setEngineeringNotes] = useState("");

  const [result, setResult] =
    useState<RotaryScrewExecutionResponse | null>(null);

  const inletPressureValue = Number(inletPressure);
  const inletTemperatureValue = Number(inletTemperature);
  const dischargePressureValue = Number(dischargePressure);
  const rotationalSpeedValue = Number(rotationalSpeed);
  const ratedFadValue = Number(ratedFad);
  const packageInputPowerValue = Number(packageInputPower);
  const maleRotorDiameterValue = Number(maleRotorDiameter);
  const rotorLengthValue = Number(rotorLength);
  const areaUtilisationCoefficientValue = Number(
    areaUtilisationCoefficient,
  );
  const referencePressureValue = Number(referencePressure);
  const referenceTemperatureValue = Number(referenceTemperature);

  const operatingBasisIsValid =
    Number.isFinite(inletPressureValue) &&
    inletPressureValue > 0 &&
    Number.isFinite(inletTemperatureValue) &&
    inletTemperatureValue > 0 &&
    Number.isFinite(dischargePressureValue) &&
    dischargePressureValue > 0 &&
    Number.isFinite(rotationalSpeedValue) &&
    rotationalSpeedValue > 0;

  const performanceBasisIsValid =
    Number.isFinite(ratedFadValue) &&
    ratedFadValue > 0 &&
    Number.isFinite(packageInputPowerValue) &&
    packageInputPowerValue > 0;

  const geometryBasisIsValid =
    !includeGeometry ||
    (Number.isFinite(maleRotorDiameterValue) &&
      maleRotorDiameterValue > 0 &&
      Number.isFinite(rotorLengthValue) &&
      rotorLengthValue > 0 &&
      Number.isFinite(areaUtilisationCoefficientValue) &&
      areaUtilisationCoefficientValue > 0);

  const standardAirBasisIsValid =
    !includeStandardAirCorrection ||
    (Number.isFinite(referencePressureValue) &&
      referencePressureValue > 0 &&
      Number.isFinite(referenceTemperatureValue) &&
      referenceTemperatureValue > 0);

  const persistenceIsValid =
    !persistResult ||
    (calculationCode.trim().length > 0 && title.trim().length > 0);

  const specificPowerPreview =
    performanceBasisIsValid
      ? packageInputPowerValue / ratedFadValue
      : null;

  const canSubmit =
    operatingBasisIsValid &&
    performanceBasisIsValid &&
    geometryBasisIsValid &&
    standardAirBasisIsValid &&
    persistenceIsValid;

  const calculationMutation = useMutation({
    mutationFn: () => {
      if (!accessToken) {
        throw new Error("Authenticated access token is required.");
      }

      return executeRotaryScrewCalculation(accessToken, {
        calculation: {
          inlet_pressure_bar_a: inletPressureValue,
          inlet_temperature_k: inletTemperatureValue,
          discharge_pressure_bar_g: dischargePressureValue,
          rotational_speed_rpm: rotationalSpeedValue,
          oil_type: oilType,
          control_type: controlType,
          stage_count: stageCount,
          rated_fad_m3_per_min: ratedFadValue,
          package_input_power_kw: packageInputPowerValue,
          rotor_geometry: includeGeometry
            ? {
                male_rotor_diameter_mm: maleRotorDiameterValue,
                rotor_length_mm: rotorLengthValue,
                area_utilisation_coefficient:
                  areaUtilisationCoefficientValue,
              }
            : null,
          standard_reference_pressure_bar_a: includeStandardAirCorrection
            ? referencePressureValue
            : null,
          standard_reference_temperature_k: includeStandardAirCorrection
            ? referenceTemperatureValue
            : null,
        },
        execution: {
          persist_result: persistResult,
          project_id: persistResult ? projectId : null,
          calculation_code: persistResult ? calculationCode.trim() : null,
          title: persistResult ? title.trim() : null,
          engineering_notes:
            persistResult && engineeringNotes.trim()
              ? engineeringNotes.trim()
              : null,
        },
      });
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
    setInletPressure("1.013");
    setInletTemperature("300");
    setDischargePressure("7.0");
    setRotationalSpeed("3000");
    setOilType("OIL_INJECTED");
    setControlType("FIXED_SPEED_LOAD_UNLOAD");
    setStageCount("SINGLE_STAGE");
    setRatedFad("10");
    setPackageInputPower("60");
    setIncludeGeometry(false);
    setMaleRotorDiameter("200");
    setRotorLength("300");
    setAreaUtilisationCoefficient("0.5");
    setIncludeStandardAirCorrection(false);
    setReferencePressure("1.013");
    setReferenceTemperature("293.15");
    setPersistResult(false);
    setCalculationCode("");
    setTitle("Rotary Screw Compressor Calculation");
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
                Rotary Screw Compressor Engineering
              </Badge>

              <div>
                <h1 className="text-3xl font-bold tracking-tight text-slate-950">
                  Rotary Screw Compressor Engineering
                </h1>

                <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
                  Verify manufacturer CAGI-tested performance data, optionally
                  estimate theoretical rotor displacement from geometry, and
                  optionally apply an ISO 1217 standard-air correction for
                  site conditions.
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
                <Badge variant="outline">ISO 1217</Badge>
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
                form="rotary-screw-engineering-form"
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
              <CardTitle>Why Rotary Screw Is Scoped Differently</CardTitle>

              <CardDescription className="mt-1 leading-6">
                A screw compressor's free air delivery and power depend on
                the manufacturer's proprietary rotor profile, not a universal
                formula -- unlike reciprocating or centrifugal machines. This
                workspace therefore verifies real manufacturer datasheet
                data rather than predicting it.
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          <div className="grid gap-3 md:grid-cols-3">
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                1 · Manufacturer Data
              </p>
              <p className="mt-2 text-sm leading-6 text-slate-700">
                Enter the rated FAD and package input power from an actual
                CAGI-tested datasheet -- always calculated.
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                2 · Rotor Geometry (Optional)
              </p>
              <p className="mt-2 text-sm leading-6 text-slate-700">
                Supply male rotor diameter, length, and area-utilisation
                coefficient for a theoretical displacement estimate.
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                3 · Standard-Air Correction (Optional)
              </p>
              <p className="mt-2 text-sm leading-6 text-slate-700">
                Supply reference test conditions to correct rated FAD to
                actual site inlet conditions.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <form
        id="rotary-screw-engineering-form"
        className="space-y-6"
        onSubmit={handleSubmit}
      >
        <Card>
          <CardHeader>
            <div className="flex items-start gap-3">
              <Wind className="mt-0.5 size-5 shrink-0 text-slate-500" />

              <div>
                <CardTitle>Site Operating Point</CardTitle>

                <CardDescription className="mt-1 leading-6">
                  Enter the compressor's inlet conditions, target discharge
                  pressure, rotational speed, and machine configuration.
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-5">
            <fieldset className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
              <legend className="sr-only">Site operating point</legend>

              <EngineeringInput
                id="inlet-pressure"
                label="Inlet Pressure"
                unit="bar(a)"
                type="number"
                min="0.01"
                step="any"
                inputMode="decimal"
                required
                value={inletPressure}
                onChange={(event) =>
                  updateInput(setInletPressure, event.target.value)
                }
              />

              <EngineeringInput
                id="inlet-temperature"
                label="Inlet Temperature"
                unit="K"
                type="number"
                min="0.01"
                step="any"
                inputMode="decimal"
                required
                value={inletTemperature}
                onChange={(event) =>
                  updateInput(setInletTemperature, event.target.value)
                }
              />

              <EngineeringInput
                id="discharge-pressure"
                label="Discharge Pressure"
                unit="bar(g)"
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
                id="rotational-speed"
                label="Rotational Speed"
                unit="rpm"
                type="number"
                min="1"
                step="any"
                inputMode="decimal"
                required
                value={rotationalSpeed}
                onChange={(event) =>
                  updateInput(setRotationalSpeed, event.target.value)
                }
              />
            </fieldset>

            <fieldset className="grid gap-5 md:grid-cols-3">
              <legend className="sr-only">Machine configuration</legend>

              <div className="space-y-2">
                <Label htmlFor="oil-type">Lubrication Type</Label>
                <select
                  id="oil-type"
                  className="h-9 w-full rounded-md border border-slate-200 bg-white px-3 text-sm shadow-sm outline-none transition focus-visible:border-slate-400 focus-visible:ring-2 focus-visible:ring-slate-200"
                  value={oilType}
                  onChange={(event) => {
                    setOilType(event.target.value as RotaryScrewOilType);
                    clearPreviousResult();
                  }}
                >
                  <option value="OIL_INJECTED">Oil-Injected</option>
                  <option value="OIL_FREE">Oil-Free</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="control-type">Capacity Control</Label>
                <select
                  id="control-type"
                  className="h-9 w-full rounded-md border border-slate-200 bg-white px-3 text-sm shadow-sm outline-none transition focus-visible:border-slate-400 focus-visible:ring-2 focus-visible:ring-slate-200"
                  value={controlType}
                  onChange={(event) => {
                    setControlType(
                      event.target.value as RotaryScrewControlType,
                    );
                    clearPreviousResult();
                  }}
                >
                  <option value="FIXED_SPEED_LOAD_UNLOAD">
                    Fixed Speed (Load/Unload)
                  </option>
                  <option value="VARIABLE_SPEED_DRIVE">
                    Variable Speed Drive
                  </option>
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="stage-count">Compression Stages</Label>
                <select
                  id="stage-count"
                  className="h-9 w-full rounded-md border border-slate-200 bg-white px-3 text-sm shadow-sm outline-none transition focus-visible:border-slate-400 focus-visible:ring-2 focus-visible:ring-slate-200"
                  value={stageCount}
                  onChange={(event) => {
                    setStageCount(
                      event.target.value as RotaryScrewStageCount,
                    );
                    clearPreviousResult();
                  }}
                >
                  <option value="SINGLE_STAGE">Single Stage</option>
                  <option value="TWO_STAGE">Two Stage</option>
                </select>
              </div>
            </fieldset>

            <div
              role={operatingBasisIsValid ? "status" : "alert"}
              className={`rounded-xl border p-4 ${
                operatingBasisIsValid
                  ? "border-emerald-200 bg-emerald-50"
                  : "border-red-300 bg-red-50"
              }`}
            >
              <div className="flex items-start gap-3">
                {operatingBasisIsValid ? (
                  <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-emerald-700" />
                ) : (
                  <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-700" />
                )}

                <div>
                  <p className="text-sm font-semibold text-slate-950">
                    Operating-point Check
                  </p>

                  <p className="mt-1 text-sm leading-6 text-slate-700">
                    {operatingBasisIsValid
                      ? "Inlet pressure, inlet temperature, discharge pressure, and rotational speed are ready for calculation."
                      : "Use positive inlet pressure, inlet temperature, discharge pressure, and rotational speed."}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-start gap-3">
              <Gauge className="mt-0.5 size-5 shrink-0 text-slate-500" />

              <div>
                <CardTitle>Manufacturer Performance Data</CardTitle>

                <CardDescription className="mt-1 leading-6">
                  Enter the rated free air delivery and package input power
                  exactly as published on an actual CAGI-tested manufacturer
                  datasheet. This is verified and benchmarked, not invented.
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-5">
            <fieldset className="grid gap-5 md:grid-cols-2">
              <legend className="sr-only">
                Manufacturer performance data
              </legend>

              <EngineeringInput
                id="rated-fad"
                label="Rated Free Air Delivery"
                unit="m³/min"
                type="number"
                min="0.0001"
                step="any"
                inputMode="decimal"
                required
                value={ratedFad}
                onChange={(event) =>
                  updateInput(setRatedFad, event.target.value)
                }
              />

              <EngineeringInput
                id="package-input-power"
                label="Package Input Power"
                unit="kW"
                type="number"
                min="0.01"
                step="any"
                inputMode="decimal"
                required
                value={packageInputPower}
                onChange={(event) =>
                  updateInput(setPackageInputPower, event.target.value)
                }
              />
            </fieldset>

            <div
              role={performanceBasisIsValid ? "status" : "alert"}
              className={`rounded-xl border p-4 ${
                performanceBasisIsValid
                  ? "border-emerald-200 bg-emerald-50"
                  : "border-red-300 bg-red-50"
              }`}
            >
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-start gap-3">
                  {performanceBasisIsValid ? (
                    <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-emerald-700" />
                  ) : (
                    <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-700" />
                  )}

                  <div>
                    <p className="text-sm font-semibold text-slate-950">
                      Performance-data Check
                    </p>

                    <p className="mt-1 text-sm leading-6 text-slate-700">
                      {performanceBasisIsValid
                        ? "Rated FAD and package input power are ready for specific-power calculation."
                        : "Use a positive rated FAD and a positive package input power."}
                    </p>
                  </div>
                </div>

                <div className="text-left sm:text-right">
                  <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                    Specific Power Preview
                  </p>
                  <p className="mt-1 font-mono text-lg font-semibold text-slate-950">
                    {specificPowerPreview === null
                      ? "Invalid"
                      : `${specificPowerPreview.toFixed(3)} kW/m³/min`}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-start gap-3">
              <Ruler className="mt-0.5 size-5 shrink-0 text-slate-500" />

              <div>
                <CardTitle>Rotor Geometry (Optional)</CardTitle>

                <CardDescription className="mt-1 leading-6">
                  Supply male-rotor geometry for a theoretical (ideal)
                  displacement estimate. The area-utilisation coefficient is
                  profile-specific -- use a manufacturer value or a
                  documented textbook range, never an assumed default.
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-5">
            <label className="flex cursor-pointer items-start gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4">
              <input
                type="checkbox"
                className="mt-1 size-4 rounded border-slate-300"
                checked={includeGeometry}
                onChange={(event) =>
                  updateBoolean(setIncludeGeometry, event.target.checked)
                }
              />

              <span>
                <span className="block text-sm font-semibold text-slate-950">
                  Include Theoretical Displacement Estimate
                </span>
                <span className="mt-1 block text-sm leading-6 text-slate-600">
                  Calculate ideal rotor displacement from geometry, alongside
                  the manufacturer performance verification.
                </span>
              </span>
            </label>

            {includeGeometry && (
              <fieldset className="grid gap-5 md:grid-cols-3">
                <legend className="sr-only">Male rotor geometry</legend>

                <EngineeringInput
                  id="male-rotor-diameter"
                  label="Male Rotor Diameter"
                  unit="mm"
                  type="number"
                  min="0.01"
                  step="any"
                  inputMode="decimal"
                  required={includeGeometry}
                  value={maleRotorDiameter}
                  onChange={(event) =>
                    updateInput(setMaleRotorDiameter, event.target.value)
                  }
                />

                <EngineeringInput
                  id="rotor-length"
                  label="Rotor Length"
                  unit="mm"
                  type="number"
                  min="0.01"
                  step="any"
                  inputMode="decimal"
                  required={includeGeometry}
                  value={rotorLength}
                  onChange={(event) =>
                    updateInput(setRotorLength, event.target.value)
                  }
                />

                <EngineeringInput
                  id="area-utilisation-coefficient"
                  label="Area Utilisation Coefficient"
                  unit="C-theta"
                  type="number"
                  min="0.01"
                  step="any"
                  inputMode="decimal"
                  required={includeGeometry}
                  value={areaUtilisationCoefficient}
                  onChange={(event) =>
                    updateInput(
                      setAreaUtilisationCoefficient,
                      event.target.value,
                    )
                  }
                />
              </fieldset>
            )}

            {includeGeometry && !geometryBasisIsValid && (
              <div
                role="alert"
                className="rounded-xl border border-red-300 bg-red-50 p-4"
              >
                <div className="flex items-start gap-3">
                  <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-700" />

                  <p className="text-sm leading-6 text-slate-700">
                    Use a positive male rotor diameter, rotor length, and
                    area-utilisation coefficient.
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-start gap-3">
              <Gauge className="mt-0.5 size-5 shrink-0 text-slate-500" />

              <div>
                <CardTitle>ISO 1217 Standard-Air Correction (Optional)</CardTitle>

                <CardDescription className="mt-1 leading-6">
                  Supply the reference test conditions the rated FAD was
                  established at, to correct it to the site inlet
                  conditions entered above.
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-5">
            <label className="flex cursor-pointer items-start gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4">
              <input
                type="checkbox"
                className="mt-1 size-4 rounded border-slate-300"
                checked={includeStandardAirCorrection}
                onChange={(event) =>
                  updateBoolean(
                    setIncludeStandardAirCorrection,
                    event.target.checked,
                  )
                }
              />

              <span>
                <span className="block text-sm font-semibold text-slate-950">
                  Include Standard-Air Correction
                </span>
                <span className="mt-1 block text-sm leading-6 text-slate-600">
                  Correct rated FAD to site inlet conditions using the ideal
                  gas law density ratio.
                </span>
              </span>
            </label>

            {includeStandardAirCorrection && (
              <fieldset className="grid gap-5 md:grid-cols-2">
                <legend className="sr-only">Reference test conditions</legend>

                <EngineeringInput
                  id="reference-pressure"
                  label="Reference Pressure"
                  unit="bar(a)"
                  type="number"
                  min="0.01"
                  step="any"
                  inputMode="decimal"
                  required={includeStandardAirCorrection}
                  value={referencePressure}
                  onChange={(event) =>
                    updateInput(setReferencePressure, event.target.value)
                  }
                />

                <EngineeringInput
                  id="reference-temperature"
                  label="Reference Temperature"
                  unit="K"
                  type="number"
                  min="0.01"
                  step="any"
                  inputMode="decimal"
                  required={includeStandardAirCorrection}
                  value={referenceTemperature}
                  onChange={(event) =>
                    updateInput(setReferenceTemperature, event.target.value)
                  }
                />
              </fieldset>
            )}

            {includeStandardAirCorrection && !standardAirBasisIsValid && (
              <div
                role="alert"
                className="rounded-xl border border-red-300 bg-red-50 p-4"
              >
                <div className="flex items-start gap-3">
                  <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-700" />

                  <p className="text-sm leading-6 text-slate-700">
                    Use a positive reference pressure and reference
                    temperature.
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-start gap-3">
              <Save className="mt-0.5 size-5 shrink-0 text-slate-500" />

              <div>
                <CardTitle>Project Record</CardTitle>

                <CardDescription className="mt-1 leading-6">
                  Run an advisory calculation only, or retain the result as
                  an auditable calculation case inside the active project.
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
                  Create a calculation case linked to the active
                  authenticated project and retain its engineering notes.
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
              ? "Calculating Rotary Screw Case..."
              : "Calculate Rotary Screw Case"}
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
                  Rotary Screw Calculation Error
                </CardTitle>

                <CardDescription className="mt-1 leading-6 text-red-800">
                  {getCalculationErrorMessage(calculationMutation.error)}
                </CardDescription>

                <p className="mt-2 text-sm leading-6 text-red-800">
                  Confirm the operating point, manufacturer performance data,
                  optional geometry and standard-air inputs, and project
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
                    Rotary Screw Engineering Complete
                  </CardTitle>

                  <CardDescription className="mt-1 leading-6">
                    Review verified performance, optional theoretical
                    displacement, and optional standard-air correction for
                    the submitted design basis.
                  </CardDescription>
                </div>
              </div>

              <Badge
                variant="outline"
                className="border-emerald-300 bg-emerald-100 text-emerald-900"
              >
                CALCULATED
              </Badge>
            </div>
          </CardHeader>

          <CardContent className="space-y-6">
            <section aria-labelledby="operating-point-review-heading">
              <div className="mb-3 flex items-center gap-2">
                <Wind className="size-4 text-slate-500" />
                <h2
                  id="operating-point-review-heading"
                  className="text-sm font-semibold text-slate-950"
                >
                  Operating Point Review
                </h2>
              </div>

              <dl className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                <ResultMetric
                  label="Inlet Pressure"
                  value={`${formatEngineeringNumber(
                    result.result.operating_point.inlet_pressure_bar_a,
                  )} bar(a)`}
                />

                <ResultMetric
                  label="Inlet Temperature"
                  value={`${formatEngineeringNumber(
                    result.result.operating_point.inlet_temperature_k,
                  )} K`}
                />

                <ResultMetric
                  label="Discharge Pressure"
                  value={`${formatEngineeringNumber(
                    result.result.operating_point.discharge_pressure_bar_g,
                  )} bar(g)`}
                />

                <ResultMetric
                  label="Rotational Speed"
                  value={`${formatEngineeringNumber(
                    result.result.operating_point.rotational_speed_rpm,
                    0,
                  )} rpm`}
                />

                <ResultMetric
                  label="Lubrication"
                  value={formatOilType(
                    result.result.operating_point.oil_type,
                  )}
                />

                <ResultMetric
                  label="Capacity Control"
                  value={formatControlType(
                    result.result.operating_point.control_type,
                  )}
                />

                <ResultMetric
                  label="Stage Count"
                  value={formatStageCount(
                    result.result.operating_point.stage_count,
                  )}
                />
              </dl>
            </section>

            <section aria-labelledby="performance-review-heading">
              <div className="mb-3 flex items-center gap-2">
                <Gauge className="size-4 text-slate-500" />
                <h2
                  id="performance-review-heading"
                  className="text-sm font-semibold text-slate-950"
                >
                  Manufacturer Performance Review
                </h2>
              </div>

              <dl className="grid gap-3 sm:grid-cols-3">
                <ResultMetric
                  label="Rated FAD"
                  value={`${formatEngineeringNumber(
                    result.result.performance.rated_fad_m3_per_min,
                  )} m³/min`}
                />

                <ResultMetric
                  label="Package Input Power"
                  value={`${formatEngineeringNumber(
                    result.result.performance.package_input_power_kw,
                  )} kW`}
                />

                <ResultMetric
                  label="Specific Power"
                  value={`${formatEngineeringNumber(
                    result.result.performance.specific_power_kw_per_m3_min,
                  )} kW/m³/min`}
                  description="Package input power divided by rated FAD"
                />
              </dl>
            </section>

            {result.result.displacement && (
              <section aria-labelledby="displacement-review-heading">
                <div className="mb-3 flex items-center gap-2">
                  <Ruler className="size-4 text-slate-500" />
                  <h2
                    id="displacement-review-heading"
                    className="text-sm font-semibold text-slate-950"
                  >
                    Theoretical Displacement Review
                  </h2>
                </div>

                <dl className="grid gap-3 sm:grid-cols-1">
                  <ResultMetric
                    label="Theoretical Displacement"
                    value={`${formatEngineeringNumber(
                      result.result.displacement
                        .theoretical_displacement_m3_per_min,
                    )} m³/min`}
                    description="Ideal rotor swept volume, before volumetric-efficiency losses"
                  />
                </dl>
              </section>
            )}

            {result.result.standard_air_correction && (
              <section aria-labelledby="standard-air-review-heading">
                <div className="mb-3 flex items-center gap-2">
                  <Gauge className="size-4 text-slate-500" />
                  <h2
                    id="standard-air-review-heading"
                    className="text-sm font-semibold text-slate-950"
                  >
                    Standard-Air Correction Review
                  </h2>
                </div>

                <dl className="grid gap-3 sm:grid-cols-3">
                  <ResultMetric
                    label="Reference Pressure"
                    value={`${formatEngineeringNumber(
                      result.result.standard_air_correction
                        .reference_pressure_bar_a,
                    )} bar(a)`}
                  />

                  <ResultMetric
                    label="Reference Temperature"
                    value={`${formatEngineeringNumber(
                      result.result.standard_air_correction
                        .reference_temperature_k,
                    )} K`}
                  />

                  <ResultMetric
                    label="Corrected FAD"
                    value={`${formatEngineeringNumber(
                      result.result.standard_air_correction
                        .corrected_fad_m3_per_min,
                    )} m³/min`}
                    description="Rated FAD corrected to site inlet conditions"
                  />
                </dl>
              </section>
            )}

            {result.calculation_case_id !== null && (
              <div className="flex flex-col gap-4 rounded-xl border border-blue-200 bg-blue-50 p-5 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm font-semibold text-blue-950">
                    Calculation Case Saved
                  </p>
                  <p className="mt-1 text-sm leading-6 text-blue-800">
                    Case ID {result.calculation_case_id} is linked to the
                    active project and available in Calculation History.
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
                View complete rotary screw calculation payload
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
