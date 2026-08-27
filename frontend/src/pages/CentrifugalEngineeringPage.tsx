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
  ChartColumn,
  CheckCircle2,
  Gauge,
  Play,
  RotateCcw,
  Save,
  Settings2,
  Wind,
  Zap,
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
import { executeCentrifugalCalculation } from "../features/projects/centrifugalService";
import type {
  CentrifugalDriverType,
  CentrifugalExecutionResponse,
  EngineeringNumber,
} from "../features/projects/centrifugalTypes";
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

function formatDriverType(driverType: CentrifugalDriverType): string {
  if (driverType === "ELECTRIC_MOTOR") {
    return "Electric Motor";
  }

  if (driverType === "GAS_TURBINE") {
    return "Gas Turbine";
  }

  return "Steam Turbine";
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

    return `The centrifugal calculation service returned HTTP ${error.status}.`;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "The centrifugal compressor calculation could not be completed.";
}

export function CentrifugalEngineeringPage() {
  const { accessToken } = useAuth();
  const {
    projectId,
    hasValidProjectId,
    project,
    projectQuery,
  } = useProjectContext();

  const [suctionPressure, setSuctionPressure] = useState("1.013");
  const [dischargePressure, setDischargePressure] = useState("8.0");
  const [suctionTemperature, setSuctionTemperature] = useState("300");
  const [massFlow, setMassFlow] = useState("1.0");
  const [actualFlow, setActualFlow] = useState("1.0");
  const [molecularWeight, setMolecularWeight] = useState("28.97");
  const [suctionZ, setSuctionZ] = useState("1.0");
  const [dischargeZ, setDischargeZ] = useState("1.0");
  const [isentropicExponent, setIsentropicExponent] = useState("1.4");

  const [polytropicEfficiency, setPolytropicEfficiency] =
    useState("0.82");
  const [impellerStages, setImpellerStages] = useState("4");
  const [headCoefficient, setHeadCoefficient] = useState("0.65");
  const [rotationalSpeed, setRotationalSpeed] = useState("12000");

  const [mechanicalLossFraction, setMechanicalLossFraction] =
    useState("0.03");
  const [driverMarginFraction, setDriverMarginFraction] =
    useState("0.10");
  const [selectedDriverPower, setSelectedDriverPower] =
    useState("500");
  const [motorEfficiency, setMotorEfficiency] = useState("0.95");

  const [surgeFlowFraction, setSurgeFlowFraction] = useState("0.70");
  const [antiSurgeMarginFraction, setAntiSurgeMarginFraction] =
    useState("0.10");
  const [stonewallFlowFraction, setStonewallFlowFraction] =
    useState("1.25");

  const [persistResult, setPersistResult] = useState(false);
  const [calculationCode, setCalculationCode] = useState("");
  const [title, setTitle] =
    useState("Centrifugal Compressor Calculation");
  const [engineeringNotes, setEngineeringNotes] = useState("");

  const [result, setResult] =
    useState<CentrifugalExecutionResponse | null>(null);

  const suctionPressureValue = Number(suctionPressure);
  const dischargePressureValue = Number(dischargePressure);
  const suctionTemperatureValue = Number(suctionTemperature);
  const massFlowValue = Number(massFlow);
  const actualFlowValue = Number(actualFlow);
  const molecularWeightValue = Number(molecularWeight);
  const suctionZValue = Number(suctionZ);
  const dischargeZValue = Number(dischargeZ);
  const isentropicExponentValue = Number(isentropicExponent);
  const polytropicEfficiencyValue = Number(polytropicEfficiency);
  const impellerStagesValue = Number(impellerStages);
  const headCoefficientValue = Number(headCoefficient);
  const rotationalSpeedValue = Number(rotationalSpeed);
  const mechanicalLossFractionValue = Number(mechanicalLossFraction);
  const driverMarginFractionValue = Number(driverMarginFraction);
  const selectedDriverPowerValue = Number(selectedDriverPower);
  const motorEfficiencyValue = motorEfficiency.trim()
    ? Number(motorEfficiency)
    : null;
  const surgeFlowFractionValue = Number(surgeFlowFraction);
  const antiSurgeMarginFractionValue = Number(antiSurgeMarginFraction);
  const stonewallFlowFractionValue = Number(stonewallFlowFraction);

  const pressureBasisIsValid =
    Number.isFinite(suctionPressureValue) &&
    suctionPressureValue > 0 &&
    Number.isFinite(dischargePressureValue) &&
    dischargePressureValue > suctionPressureValue;
  const gasBasisIsValid =
    Number.isFinite(suctionTemperatureValue) &&
    suctionTemperatureValue > 0 &&
    Number.isFinite(massFlowValue) &&
    massFlowValue > 0 &&
    Number.isFinite(actualFlowValue) &&
    actualFlowValue > 0 &&
    Number.isFinite(molecularWeightValue) &&
    molecularWeightValue > 0 &&
    Number.isFinite(suctionZValue) &&
    suctionZValue > 0 &&
    Number.isFinite(dischargeZValue) &&
    dischargeZValue > 0 &&
    Number.isFinite(isentropicExponentValue) &&
    isentropicExponentValue > 1;
  const aerodynamicBasisIsValid =
    Number.isFinite(polytropicEfficiencyValue) &&
    polytropicEfficiencyValue > 0 &&
    polytropicEfficiencyValue <= 1 &&
    Number.isInteger(impellerStagesValue) &&
    impellerStagesValue >= 1 &&
    Number.isFinite(headCoefficientValue) &&
    headCoefficientValue > 0 &&
    Number.isFinite(rotationalSpeedValue) &&
    rotationalSpeedValue > 0;
  const driverBasisIsValid =
    Number.isFinite(mechanicalLossFractionValue) &&
    mechanicalLossFractionValue >= 0 &&
    Number.isFinite(driverMarginFractionValue) &&
    driverMarginFractionValue >= 0 &&
    Number.isFinite(selectedDriverPowerValue) &&
    selectedDriverPowerValue > 0 &&
    (motorEfficiencyValue === null ||
      (Number.isFinite(motorEfficiencyValue) &&
        motorEfficiencyValue > 0 &&
        motorEfficiencyValue <= 1));
  const envelopeInputsAreValid =
    Number.isFinite(surgeFlowFractionValue) &&
    surgeFlowFractionValue > 0 &&
    surgeFlowFractionValue < 1 &&
    Number.isFinite(antiSurgeMarginFractionValue) &&
    antiSurgeMarginFractionValue >= 0 &&
    Number.isFinite(stonewallFlowFractionValue) &&
    stonewallFlowFractionValue > 1;
  const antiSurgeSetpointFraction = envelopeInputsAreValid
    ? surgeFlowFractionValue * (1 + antiSurgeMarginFractionValue)
    : null;
  const antiSurgeSetpointIsBelowDesign =
    antiSurgeSetpointFraction !== null &&
    antiSurgeSetpointFraction < 1;
  const persistenceIsValid =
    !persistResult ||
    (calculationCode.trim().length > 0 && title.trim().length > 0);

  const overallPressureRatio = pressureBasisIsValid
    ? dischargePressureValue / suctionPressureValue
    : null;
  const actualFlowM3PerHr =
    Number.isFinite(actualFlowValue) && actualFlowValue > 0
      ? actualFlowValue * 3600
      : null;
  const inletSpecificVolume =
    Number.isFinite(actualFlowValue) &&
    actualFlowValue > 0 &&
    Number.isFinite(massFlowValue) &&
    massFlowValue > 0
      ? actualFlowValue / massFlowValue
      : null;
  const operatingSpanFraction = envelopeInputsAreValid
    ? stonewallFlowFractionValue - surgeFlowFractionValue
    : null;

  const calculationMutation = useMutation({
    mutationFn: () => {
      if (!accessToken) {
        throw new Error("Authenticated access token is required.");
      }

      return executeCentrifugalCalculation(
        accessToken,
        {
          calculation: {
            gas: {
              suction_pressure_bar: suctionPressureValue,
              discharge_pressure_bar: dischargePressureValue,
              suction_temperature_k: suctionTemperatureValue,
              mass_flow_kg_per_s: massFlowValue,
              actual_flow_m3_per_s: actualFlowValue,
              molecular_weight_kg_per_kmol: molecularWeightValue,
              suction_z_factor: suctionZValue,
              discharge_z_factor: dischargeZValue,
              isentropic_exponent: isentropicExponentValue,
            },
            polytropic_efficiency: polytropicEfficiencyValue,
            number_of_impeller_stages: impellerStagesValue,
            head_coefficient: headCoefficientValue,
            rotational_speed_rpm: rotationalSpeedValue,
            mechanical_loss_fraction: mechanicalLossFractionValue,
            driver_margin_fraction: driverMarginFractionValue,
            selected_driver_power_kw: selectedDriverPowerValue,
            motor_efficiency: motorEfficiencyValue,
            surge_flow_fraction: surgeFlowFractionValue,
            anti_surge_margin_fraction: antiSurgeMarginFractionValue,
            stonewall_flow_fraction: stonewallFlowFractionValue,
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
    pressureBasisIsValid &&
    gasBasisIsValid &&
    aerodynamicBasisIsValid &&
    driverBasisIsValid &&
    envelopeInputsAreValid &&
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
    setSuctionPressure("1.013");
    setDischargePressure("8.0");
    setSuctionTemperature("300");
    setMassFlow("1.0");
    setActualFlow("1.0");
    setMolecularWeight("28.97");
    setSuctionZ("1.0");
    setDischargeZ("1.0");
    setIsentropicExponent("1.4");
    setPolytropicEfficiency("0.82");
    setImpellerStages("4");
    setHeadCoefficient("0.65");
    setRotationalSpeed("12000");
    setMechanicalLossFraction("0.03");
    setDriverMarginFraction("0.10");
    setSelectedDriverPower("500");
    setMotorEfficiency("0.95");
    setSurgeFlowFraction("0.70");
    setAntiSurgeMarginFraction("0.10");
    setStonewallFlowFraction("1.25");
    setPersistResult(false);
    setCalculationCode("");
    setTitle("Centrifugal Compressor Calculation");
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
                Centrifugal Compressor Engineering
              </Badge>

              <div>
                <h1 className="text-3xl font-bold tracking-tight text-slate-950">
                  Centrifugal Compressor Engineering
                </h1>

                <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
                  Establish the gas operating point, calculate polytropic head
                  and impeller geometry, verify driver capacity, and review the
                  surge-to-stonewall operating envelope against one traceable
                  design basis.
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
                <Badge variant="outline">Performance Map</Badge>
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
                form="centrifugal-engineering-form"
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
              <CardTitle>Guided Centrifugal Design Workflow</CardTitle>

              <CardDescription className="mt-1 leading-6">
                Define the operating point, establish the aerodynamic and
                driver basis, assess the operating envelope, and optionally
                retain the completed case in the active project.
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          <div className="grid gap-3 md:grid-cols-3">
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                1 · Operating Point
              </p>
              <p className="mt-2 text-sm leading-6 text-slate-700">
                Set absolute pressures, temperature, flow, molecular weight,
                compressibility, and isentropic exponent.
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                2 · Machine Basis
              </p>
              <p className="mt-2 text-sm leading-6 text-slate-700">
                Define polytropic efficiency, impeller stages, head
                coefficient, speed, losses, and driver margin.
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                3 · Engineering Review
              </p>
              <p className="mt-2 text-sm leading-6 text-slate-700">
                Review head, impeller sizing, power adequacy, surge protection,
                stonewall limit, and scaled speed points.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <form
        id="centrifugal-engineering-form"
        className="space-y-6"
        onSubmit={handleSubmit}
      >
        <Card>
          <CardHeader>
            <div className="flex items-start gap-3">
              <Wind className="mt-0.5 size-5 shrink-0 text-slate-500" />

              <div>
                <CardTitle>Gas Operating Point</CardTitle>

                <CardDescription className="mt-1 leading-6">
                  Enter the absolute suction and discharge conditions together
                  with actual inlet flow and the gas-property basis used for
                  the polytropic head calculation.
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-5">
            <fieldset className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
              <legend className="sr-only">
                Gas operating point
              </legend>

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
                id="suction-temperature"
                label="Suction Temperature"
                unit="K"
                type="number"
                min="0.01"
                step="any"
                inputMode="decimal"
                required
                value={suctionTemperature}
                onChange={(event) =>
                  updateInput(setSuctionTemperature, event.target.value)
                }
              />

              <EngineeringInput
                id="mass-flow"
                label="Mass Flow"
                unit="kg/s"
                type="number"
                min="0.0001"
                step="any"
                inputMode="decimal"
                required
                value={massFlow}
                onChange={(event) =>
                  updateInput(setMassFlow, event.target.value)
                }
              />

              <EngineeringInput
                id="actual-flow"
                label="Actual Inlet Flow"
                unit="m³/s"
                type="number"
                min="0.0001"
                step="any"
                inputMode="decimal"
                required
                value={actualFlow}
                onChange={(event) =>
                  updateInput(setActualFlow, event.target.value)
                }
              />

              <EngineeringInput
                id="molecular-weight"
                label="Molecular Weight"
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
            </fieldset>

            <div
              role={pressureBasisIsValid && gasBasisIsValid ? "status" : "alert"}
              className={`rounded-xl border p-4 ${
                pressureBasisIsValid && gasBasisIsValid
                  ? "border-emerald-200 bg-emerald-50"
                  : "border-red-300 bg-red-50"
              }`}
            >
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-start gap-3">
                  {pressureBasisIsValid && gasBasisIsValid ? (
                    <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-emerald-700" />
                  ) : (
                    <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-700" />
                  )}

                  <div>
                    <p className="text-sm font-semibold text-slate-950">
                      Operating-point Check
                    </p>

                    <p className="mt-1 text-sm leading-6 text-slate-700">
                      {pressureBasisIsValid && gasBasisIsValid
                        ? "The absolute pressure relationship, flow quantities, temperature, molecular weight, Z-factors, and isentropic exponent are ready for calculation."
                        : "Use positive absolute conditions, keep discharge pressure above suction pressure, and enter an isentropic exponent greater than one."}
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

            <dl className="grid gap-3 sm:grid-cols-3">
              <ResultMetric
                label="Actual Inlet Flow"
                value={
                  actualFlowM3PerHr === null
                    ? "Invalid"
                    : `${actualFlowM3PerHr.toLocaleString("en-IN", {
                        maximumFractionDigits: 2,
                      })} m³/hr`
                }
              />

              <ResultMetric
                label="Inlet Specific Volume"
                value={
                  inletSpecificVolume === null
                    ? "Invalid"
                    : `${inletSpecificVolume.toLocaleString("en-IN", {
                        maximumFractionDigits: 4,
                      })} m³/kg`
                }
                description="Live ratio of actual inlet flow to submitted mass flow"
              />

              <ResultMetric
                label="Average Z Preview"
                value={
                  Number.isFinite(suctionZValue) &&
                  Number.isFinite(dischargeZValue) &&
                  suctionZValue > 0 &&
                  dischargeZValue > 0
                    ? ((suctionZValue + dischargeZValue) / 2).toFixed(3)
                    : "Invalid"
                }
              />
            </dl>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-start gap-3">
              <Gauge className="mt-0.5 size-5 shrink-0 text-slate-500" />

              <div>
                <CardTitle>Aerodynamic and Impeller Basis</CardTitle>

                <CardDescription className="mt-1 leading-6">
                  Establish the polytropic-efficiency assumption and the
                  impeller stage, loading, and speed basis used to estimate
                  head per stage, tip speed, and impeller diameter.
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-5">
            <fieldset className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
              <legend className="sr-only">
                Aerodynamic and impeller basis
              </legend>

              <EngineeringInput
                id="polytropic-efficiency"
                label="Polytropic Efficiency"
                unit="fraction"
                type="number"
                min="0.01"
                max="1"
                step="any"
                inputMode="decimal"
                required
                value={polytropicEfficiency}
                onChange={(event) =>
                  updateInput(setPolytropicEfficiency, event.target.value)
                }
              />

              <EngineeringInput
                id="impeller-stages"
                label="Impeller Stages"
                unit="count"
                type="number"
                min="1"
                step="1"
                inputMode="numeric"
                required
                value={impellerStages}
                onChange={(event) =>
                  updateInput(setImpellerStages, event.target.value)
                }
              />

              <EngineeringInput
                id="head-coefficient"
                label="Head Coefficient"
                unit="dimensionless"
                type="number"
                min="0.01"
                step="any"
                inputMode="decimal"
                required
                value={headCoefficient}
                onChange={(event) =>
                  updateInput(setHeadCoefficient, event.target.value)
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

            <div
              role={aerodynamicBasisIsValid ? "status" : "alert"}
              className={`rounded-xl border p-4 ${
                aerodynamicBasisIsValid
                  ? "border-emerald-200 bg-emerald-50"
                  : "border-red-300 bg-red-50"
              }`}
            >
              <div className="flex items-start gap-3">
                {aerodynamicBasisIsValid ? (
                  <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-emerald-700" />
                ) : (
                  <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-700" />
                )}

                <div>
                  <p className="text-sm font-semibold text-slate-950">
                    Aerodynamic Basis Check
                  </p>
                  <p className="mt-1 text-sm leading-6 text-slate-700">
                    {aerodynamicBasisIsValid
                      ? "Efficiency, whole-stage count, head coefficient, and rotational speed define a valid calculation basis."
                      : "Use an efficiency above zero and not above one, a whole stage count of at least one, and positive head coefficient and speed values."}
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm leading-6 text-slate-600">
                The calculation uses the entered overall pressure ratio and gas
                properties to determine polytropic head, then divides that head
                across the selected impeller stages before estimating tip speed
                and diameter.
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-start gap-3">
              <Zap className="mt-0.5 size-5 shrink-0 text-slate-500" />

              <div>
                <CardTitle>Driver and Operating Envelope</CardTitle>

                <CardDescription className="mt-1 leading-6">
                  Define mechanical losses, installed driver capacity, motor
                  efficiency, and the surge-control and stonewall fractions
                  used for operating-range review.
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-6">
            <fieldset className="space-y-5">
              <legend className="text-sm font-semibold text-slate-950">
                Driver Basis
              </legend>

              <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
                <EngineeringInput
                  id="mechanical-loss"
                  label="Mechanical Loss"
                  unit="fraction"
                  type="number"
                  min="0"
                  step="any"
                  inputMode="decimal"
                  required
                  value={mechanicalLossFraction}
                  onChange={(event) =>
                    updateInput(setMechanicalLossFraction, event.target.value)
                  }
                />

                <EngineeringInput
                  id="driver-margin"
                  label="Required Driver Margin"
                  unit="fraction"
                  type="number"
                  min="0"
                  step="any"
                  inputMode="decimal"
                  required
                  value={driverMarginFraction}
                  onChange={(event) =>
                    updateInput(setDriverMarginFraction, event.target.value)
                  }
                />

                <EngineeringInput
                  id="selected-driver-power"
                  label="Selected Driver Power"
                  unit="kW"
                  type="number"
                  min="0.01"
                  step="any"
                  inputMode="decimal"
                  required
                  value={selectedDriverPower}
                  onChange={(event) =>
                    updateInput(setSelectedDriverPower, event.target.value)
                  }
                />

                <EngineeringInput
                  id="motor-efficiency"
                  label="Motor Efficiency"
                  unit="fraction · optional"
                  type="number"
                  min="0.01"
                  max="1"
                  step="any"
                  inputMode="decimal"
                  value={motorEfficiency}
                  onChange={(event) =>
                    updateInput(setMotorEfficiency, event.target.value)
                  }
                />
              </div>
            </fieldset>

            <fieldset className="space-y-5">
              <legend className="text-sm font-semibold text-slate-950">
                Operating Envelope
              </legend>

              <div className="grid gap-5 md:grid-cols-3">
                <EngineeringInput
                  id="surge-flow-fraction"
                  label="Surge Flow Fraction"
                  unit="fraction of design flow"
                  type="number"
                  min="0.01"
                  max="0.999"
                  step="any"
                  inputMode="decimal"
                  required
                  value={surgeFlowFraction}
                  onChange={(event) =>
                    updateInput(setSurgeFlowFraction, event.target.value)
                  }
                />

                <EngineeringInput
                  id="anti-surge-margin-fraction"
                  label="Anti-Surge Margin"
                  unit="fraction above surge"
                  type="number"
                  min="0"
                  step="any"
                  inputMode="decimal"
                  required
                  value={antiSurgeMarginFraction}
                  onChange={(event) =>
                    updateInput(
                      setAntiSurgeMarginFraction,
                      event.target.value,
                    )
                  }
                />

                <EngineeringInput
                  id="stonewall-flow-fraction"
                  label="Stonewall Flow Fraction"
                  unit="fraction of design flow"
                  type="number"
                  min="1.0001"
                  step="any"
                  inputMode="decimal"
                  required
                  value={stonewallFlowFraction}
                  onChange={(event) =>
                    updateInput(setStonewallFlowFraction, event.target.value)
                  }
                />
              </div>
            </fieldset>

            <div className="grid gap-4 lg:grid-cols-2">
              <div
                role={driverBasisIsValid ? "status" : "alert"}
                className={`rounded-xl border p-4 ${
                  driverBasisIsValid
                    ? "border-emerald-200 bg-emerald-50"
                    : "border-red-300 bg-red-50"
                }`}
              >
                <div className="flex items-start gap-3">
                  {driverBasisIsValid ? (
                    <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-emerald-700" />
                  ) : (
                    <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-700" />
                  )}

                  <div>
                    <p className="text-sm font-semibold text-slate-950">
                      Driver-input Check
                    </p>
                    <p className="mt-1 text-sm leading-6 text-slate-700">
                      {driverBasisIsValid
                        ? "Loss, required margin, selected power, and optional motor efficiency are ready for driver sizing."
                        : "Use non-negative loss and margin fractions, positive selected power, and motor efficiency above zero and not above one when entered."}
                    </p>
                  </div>
                </div>
              </div>

              <div
                role={envelopeInputsAreValid ? "status" : "alert"}
                className={`rounded-xl border p-4 ${
                  envelopeInputsAreValid
                    ? antiSurgeSetpointIsBelowDesign
                      ? "border-emerald-200 bg-emerald-50"
                      : "border-amber-300 bg-amber-50"
                    : "border-red-300 bg-red-50"
                }`}
              >
                <div className="flex items-start gap-3">
                  {envelopeInputsAreValid &&
                  antiSurgeSetpointIsBelowDesign ? (
                    <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-emerald-700" />
                  ) : (
                    <AlertTriangle
                      className={`mt-0.5 size-5 shrink-0 ${
                        envelopeInputsAreValid
                          ? "text-amber-700"
                          : "text-red-700"
                      }`}
                    />
                  )}

                  <div>
                    <p className="text-sm font-semibold text-slate-950">
                      Envelope-input Check
                    </p>
                    <p className="mt-1 text-sm leading-6 text-slate-700">
                      {!envelopeInputsAreValid
                        ? "Keep surge flow between zero and design flow, use a non-negative anti-surge margin, and keep stonewall flow above design flow."
                        : antiSurgeSetpointIsBelowDesign
                          ? "The anti-surge setpoint remains below design flow and the stonewall limit remains above design flow."
                          : "Inputs are calculable, but the anti-surge setpoint reaches or exceeds design flow and requires control-strategy review."}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <dl className="grid gap-3 sm:grid-cols-3">
              <ResultMetric
                label="Selected Driver"
                value={
                  driverBasisIsValid
                    ? `${selectedDriverPowerValue.toLocaleString("en-IN")} kW`
                    : "Invalid"
                }
              />

              <ResultMetric
                label="Anti-Surge Setpoint Preview"
                value={
                  antiSurgeSetpointFraction === null
                    ? "Invalid"
                    : formatPercentage(antiSurgeSetpointFraction)
                }
                description="Fraction of submitted design flow"
              />

              <ResultMetric
                label="Envelope Span Preview"
                value={
                  operatingSpanFraction === null
                    ? "Invalid"
                    : formatPercentage(operatingSpanFraction)
                }
                description="Stonewall flow fraction minus surge flow fraction"
              />
            </dl>
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
              ? "Calculating Centrifugal Case..."
              : "Calculate Centrifugal Case"}
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
                  Centrifugal Calculation Error
                </CardTitle>

                <CardDescription className="mt-1 leading-6 text-red-800">
                  {getCalculationErrorMessage(calculationMutation.error)}
                </CardDescription>

                <p className="mt-2 text-sm leading-6 text-red-800">
                  Confirm the gas operating point, aerodynamic basis, driver
                  inputs, operating-envelope fractions, and project record
                  details before trying again.
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
                    Centrifugal Engineering Complete
                  </CardTitle>

                  <CardDescription className="mt-1 leading-6">
                    Review polytropic head, impeller geometry, driver capacity,
                    surge-control limits, and performance-map speed points for
                    the submitted design basis.
                  </CardDescription>
                </div>
              </div>

              <Badge
                variant="outline"
                className={
                  result.result.power.driver_is_adequate &&
                  result.result.surge.design_point_is_within_envelope
                    ? "border-emerald-300 bg-emerald-100 text-emerald-900"
                    : "border-amber-300 bg-amber-100 text-amber-900"
                }
              >
                {result.result.power.driver_is_adequate &&
                result.result.surge.design_point_is_within_envelope
                  ? "DESIGN ADEQUATE"
                  : "ENGINEERING REVIEW"}
              </Badge>
            </div>
          </CardHeader>

          <CardContent className="space-y-6">
            <dl className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <ResultMetric
                label="Polytropic Head"
                value={`${formatEngineeringNumber(
                  result.result.head.polytropic_head_kj_per_kg,
                )} kJ/kg`}
              />

              <ResultMetric
                label="Required Driver Power"
                value={`${formatEngineeringNumber(
                  result.result.power.required_driver_power_kw,
                )} kW`}
              />

              <ResultMetric
                label="Driver Margin"
                value={`${formatEngineeringNumber(
                  result.result.power.driver_margin_kw,
                )} kW`}
                description={
                  result.result.power.driver_is_adequate
                    ? "Selected driver meets the calculated requirement"
                    : "Negative margin requires driver re-selection"
                }
              />

              <ResultMetric
                label="Impeller Diameter"
                value={`${formatEngineeringNumber(
                  result.result.impeller.impeller_diameter_m,
                  4,
                )} m`}
              />
            </dl>

            <section aria-labelledby="head-review-heading">
              <div className="mb-3 flex items-center gap-2">
                <Gauge className="size-4 text-slate-500" />
                <h2
                  id="head-review-heading"
                  className="text-sm font-semibold text-slate-950"
                >
                  Thermodynamic Head Review
                </h2>
              </div>

              <dl className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                <ResultMetric
                  label="Overall Compression Ratio"
                  value={formatEngineeringNumber(
                    result.result.head.overall_compression_ratio,
                    4,
                  )}
                />

                <ResultMetric
                  label="Average Z-Factor"
                  value={formatEngineeringNumber(
                    result.result.head.average_z_factor,
                    4,
                  )}
                />

                <ResultMetric
                  label="Polytropic Exponent"
                  value={formatEngineeringNumber(
                    result.result.head.polytropic_exponent,
                    4,
                  )}
                />

                <ResultMetric
                  label="Polytropic Head"
                  value={`${formatEngineeringNumber(
                    result.result.head.polytropic_head_kj_per_kg,
                    3,
                  )} kJ/kg`}
                />
              </dl>
            </section>

            <section aria-labelledby="impeller-review-heading">
              <div className="mb-3 flex items-center gap-2">
                <Settings2 className="size-4 text-slate-500" />
                <h2
                  id="impeller-review-heading"
                  className="text-sm font-semibold text-slate-950"
                >
                  Impeller Sizing Review
                </h2>
              </div>

              <dl className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                <ResultMetric
                  label="Impeller Stages"
                  value={result.result.impeller.number_of_impeller_stages.toLocaleString(
                    "en-IN",
                  )}
                />

                <ResultMetric
                  label="Head per Stage"
                  value={`${formatEngineeringNumber(
                    result.result.impeller.head_per_stage_kj_per_kg,
                    3,
                  )} kJ/kg`}
                />

                <ResultMetric
                  label="Head Coefficient"
                  value={formatEngineeringNumber(
                    result.result.impeller.head_coefficient,
                    4,
                  )}
                />

                <ResultMetric
                  label="Impeller Tip Speed"
                  value={`${formatEngineeringNumber(
                    result.result.impeller.impeller_tip_speed_m_per_s,
                    2,
                  )} m/s`}
                />

                <ResultMetric
                  label="Rotational Speed"
                  value={`${formatEngineeringNumber(
                    result.result.impeller.rotational_speed_rpm,
                    0,
                  )} rpm`}
                />

                <ResultMetric
                  label="Estimated Diameter"
                  value={`${formatEngineeringNumber(
                    result.result.impeller.impeller_diameter_m,
                    4,
                  )} m`}
                />
              </dl>
            </section>

            <section aria-labelledby="driver-review-heading">
              <div className="mb-3 flex items-center gap-2">
                <Zap className="size-4 text-slate-500" />
                <h2
                  id="driver-review-heading"
                  className="text-sm font-semibold text-slate-950"
                >
                  Power and Driver Review
                </h2>
              </div>

              <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
                <dl className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                  <ResultMetric
                    label="Gas Power"
                    value={`${formatEngineeringNumber(
                      result.result.power.gas_power_kw,
                    )} kW`}
                  />

                  <ResultMetric
                    label="Shaft Power"
                    value={`${formatEngineeringNumber(
                      result.result.power.shaft_power_kw,
                    )} kW`}
                  />

                  <ResultMetric
                    label="Required Driver"
                    value={`${formatEngineeringNumber(
                      result.result.power.required_driver_power_kw,
                    )} kW`}
                  />

                  <ResultMetric
                    label="Selected Driver"
                    value={`${formatEngineeringNumber(
                      result.result.power.selected_driver_power_kw,
                    )} kW`}
                  />

                  <ResultMetric
                    label="Electrical Input"
                    value={
                      result.result.power.electrical_input_power_kw === null
                        ? "Not calculated"
                        : `${formatEngineeringNumber(
                            result.result.power.electrical_input_power_kw,
                          )} kW`
                    }
                  />

                  <ResultMetric
                    label="Driver Type"
                    value={formatDriverType(
                      result.result.power.driver_type,
                    )}
                  />
                </dl>

                <div
                  className={`rounded-xl border p-5 ${
                    result.result.power.driver_is_adequate
                      ? "border-emerald-200 bg-emerald-50"
                      : "border-red-300 bg-red-50"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {result.result.power.driver_is_adequate ? (
                      <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-emerald-700" />
                    ) : (
                      <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-700" />
                    )}

                    <div>
                      <h3 className="text-sm font-semibold text-slate-950">
                        Driver-capacity Assessment
                      </h3>
                      <p className="mt-2 text-sm leading-6 text-slate-700">
                        {result.result.power.driver_is_adequate
                          ? "The selected driver meets or exceeds the calculated power requirement including the submitted margin."
                          : "The selected driver is below the calculated requirement and must be re-sized before design acceptance."}
                      </p>
                      <p className="mt-3 text-sm font-semibold text-slate-950">
                        Margin: {formatEngineeringNumber(
                          result.result.power.driver_margin_kw,
                        )} kW
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            <section aria-labelledby="envelope-review-heading">
              <div className="mb-3 flex items-center gap-2">
                <Wind className="size-4 text-slate-500" />
                <h2
                  id="envelope-review-heading"
                  className="text-sm font-semibold text-slate-950"
                >
                  Surge and Stonewall Review
                </h2>
              </div>

              <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
                <dl className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                  <ResultMetric
                    label="Design Flow"
                    value={`${formatEngineeringNumber(
                      result.result.surge.design_flow_m3_per_hr,
                    )} m³/hr`}
                  />

                  <ResultMetric
                    label="Surge Flow"
                    value={`${formatEngineeringNumber(
                      result.result.surge.surge_flow_m3_per_hr,
                    )} m³/hr`}
                  />

                  <ResultMetric
                    label="Anti-Surge Setpoint"
                    value={`${formatEngineeringNumber(
                      result.result.surge.anti_surge_setpoint_m3_per_hr,
                    )} m³/hr`}
                  />

                  <ResultMetric
                    label="Stonewall Flow"
                    value={`${formatEngineeringNumber(
                      result.result.surge.stonewall_flow_m3_per_hr,
                    )} m³/hr`}
                  />

                  <ResultMetric
                    label="Operating Range"
                    value={`${formatEngineeringNumber(
                      result.result.surge.operating_range_m3_per_hr,
                    )} m³/hr`}
                  />

                  <ResultMetric
                    label="Surge Margin"
                    value={formatPercentage(
                      result.result.surge.surge_margin_fraction,
                    )}
                  />
                </dl>

                <div
                  className={`rounded-xl border p-5 ${
                    result.result.surge.design_point_is_within_envelope
                      ? "border-emerald-200 bg-emerald-50"
                      : "border-red-300 bg-red-50"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {result.result.surge.design_point_is_within_envelope ? (
                      <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-emerald-700" />
                    ) : (
                      <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-700" />
                    )}

                    <div>
                      <h3 className="text-sm font-semibold text-slate-950">
                        Operating-envelope Assessment
                      </h3>
                      <p className="mt-2 text-sm leading-6 text-slate-700">
                        {result.result.surge.design_point_is_within_envelope
                          ? "The submitted design flow lies above the surge limit and below the stonewall limit."
                          : "The submitted design point falls outside the calculated surge-to-stonewall envelope and requires review."}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            <section aria-labelledby="performance-map-heading">
              <div className="mb-3 flex items-center gap-2">
                <ChartColumn className="size-4 text-slate-500" />
                <h2
                  id="performance-map-heading"
                  className="text-sm font-semibold text-slate-950"
                >
                  Scaled Performance-map Points
                </h2>
              </div>

              <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
                <div className="grid gap-3 border-b border-slate-200 bg-slate-50 p-4 sm:grid-cols-3">
                  <div>
                    <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                      Design Speed
                    </p>
                    <p className="mt-1 font-semibold text-slate-950">
                      {formatEngineeringNumber(
                        result.result.performance_map.design_speed_rpm,
                        0,
                      )} rpm
                    </p>
                  </div>
                  <div>
                    <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                      Design Flow
                    </p>
                    <p className="mt-1 font-semibold text-slate-950">
                      {formatEngineeringNumber(
                        result.result.performance_map.design_flow_m3_per_hr,
                      )} m³/hr
                    </p>
                  </div>
                  <div>
                    <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                      Design Head
                    </p>
                    <p className="mt-1 font-semibold text-slate-950">
                      {formatEngineeringNumber(
                        result.result.performance_map.design_head_kj_per_kg,
                        3,
                      )} kJ/kg
                    </p>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full min-w-[42rem] text-left text-sm">
                    <thead className="border-b border-slate-200 bg-white text-xs uppercase tracking-wide text-slate-500">
                      <tr>
                        <th className="px-4 py-3 font-medium">Speed Line</th>
                        <th className="px-4 py-3 font-medium">Speed</th>
                        <th className="px-4 py-3 font-medium">Flow</th>
                        <th className="px-4 py-3 font-medium">Head</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {result.result.performance_map.points.map(
                        (point, index) => (
                          <tr key={`${point.speed_fraction}-${index}`}>
                            <td className="px-4 py-3 font-semibold text-slate-950">
                              {formatPercentage(point.speed_fraction, 0)}
                            </td>
                            <td className="px-4 py-3 text-slate-700">
                              {formatEngineeringNumber(point.speed_rpm, 0)} rpm
                            </td>
                            <td className="px-4 py-3 text-slate-700">
                              {formatEngineeringNumber(point.flow_m3_per_hr)} m³/hr
                            </td>
                            <td className="px-4 py-3 text-slate-700">
                              {formatEngineeringNumber(
                                point.head_kj_per_kg,
                                3,
                              )} kJ/kg
                            </td>
                          </tr>
                        ),
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              <p className="mt-3 text-xs leading-5 text-slate-600">
                Speed-line points are deterministic affinity-law scaling
                outputs for engineering review; they do not replace a validated
                manufacturer compressor map.
              </p>
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
                View complete centrifugal calculation payload
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
