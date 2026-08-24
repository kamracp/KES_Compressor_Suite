import {
  useState,
  type ComponentProps,
  type FormEvent,
} from "react";

import { useMutation } from "@tanstack/react-query";
import {
  AlertTriangle,
  Calculator,
  CheckCircle2,
  Database,
  Gauge,
  History,
  Play,
  Settings2,
  Snowflake,
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
import {
  executeCompressionCalculation,
} from "../features/projects/compressionService";
import type {
  CompressionExecutionResponse,
} from "../features/projects/compressionTypes";

type EngineeringInputProps = Omit<
  ComponentProps<typeof Input>,
  "id"
> & {
  id: string;
  label: string;
  unit?: string;
};

type ValidationCheckResult = {
  code: string;
  description: string;
  status: string;
  actualValue: unknown;
  limitDescription: string;
};

type ResultMetric = {
  label: string;
  value: unknown;
  unit?: string;
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
        <Label htmlFor={id}>
          {label}
        </Label>

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

function formatResultValue(value: unknown): string {
  if (typeof value === "number") {
    return value.toLocaleString("en-IN", {
      maximumFractionDigits: 3,
    });
  }

  if (
    typeof value === "string" &&
    value.trim() !== "" &&
    Number.isFinite(Number(value))
  ) {
    return Number(value).toLocaleString("en-IN", {
      maximumFractionDigits: 3,
    });
  }

  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }

  return String(value);
}

function isResultObject(
  value: unknown,
): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function normalizeStatus(value: unknown): string {
  return typeof value === "string"
    ? value.toUpperCase()
    : "UNKNOWN";
}

function readValidationChecks(
  value: unknown,
): ValidationCheckResult[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value.flatMap((item) => {
    if (!isResultObject(item)) {
      return [];
    }

    return [{
      code:
        typeof item.code === "string"
          ? item.code
          : "UNSPECIFIED_CHECK",
      description:
        typeof item.description === "string"
          ? item.description
          : "No validation description was provided.",
      status: normalizeStatus(item.status),
      actualValue: item.actual_value,
      limitDescription:
        typeof item.limit_description === "string"
          ? item.limit_description
          : "No limit was provided.",
    }];
  });
}

export function CompressionEngineeringPage() {
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

  const [numberOfStages, setNumberOfStages] = useState("2");
  const [specificHeatCp, setSpecificHeatCp] = useState("1.005");
  const [isentropicEfficiency, setIsentropicEfficiency] =
    useState("0.80");
  const [mechanicalEfficiency, setMechanicalEfficiency] =
    useState("0.95");

  const [intercoolerOutletTemperature, setIntercoolerOutletTemperature] =
    useState("310");

  const [coolingWaterInletTemperature, setCoolingWaterInletTemperature] =
    useState("300");
  const [coolingWaterOutletTemperature, setCoolingWaterOutletTemperature] =
    useState("310");

  const [selectedDriverPower, setSelectedDriverPower] = useState("500");
  const [driverServiceFactor, setDriverServiceFactor] = useState("0.10");
  const [motorEfficiency, setMotorEfficiency] = useState("0.95");

  const [persistResult, setPersistResult] = useState(false);
  const [calculationCode, setCalculationCode] = useState("");
  const [title, setTitle] = useState("Compression Engineering Calculation");
  const [engineeringNotes, setEngineeringNotes] = useState("");

  const [result, setResult] =
    useState<CompressionExecutionResponse | null>(null);

  if (!accessToken) {
    throw new Error("Authenticated access token is required.");
  }

  if (!hasValidProjectId) {
    throw new Error("Valid project ID is required.");
  }

  const calculationMutation = useMutation({
    mutationFn: () =>
      executeCompressionCalculation(
        accessToken,
        {
          calculation: {
            gas: {
              suction_pressure_bar: Number(suctionPressure),
              discharge_pressure_bar: Number(dischargePressure),
              suction_temperature_k: Number(suctionTemperature),
              mass_flow_kg_per_s: Number(massFlow),
              actual_flow_m3_per_s: Number(actualFlow),
              molecular_weight_kg_per_kmol: Number(molecularWeight),
              suction_z_factor: Number(suctionZ),
              discharge_z_factor: Number(dischargeZ),
              isentropic_exponent: Number(isentropicExponent),
            },

            number_of_stages: Number(numberOfStages),

            specific_heat_cp_kj_per_kg_k: Number(specificHeatCp),
            isentropic_efficiency: Number(isentropicEfficiency),
            mechanical_efficiency: Number(mechanicalEfficiency),

            intercooler_outlet_temperature_k:
              Number(intercoolerOutletTemperature),

            cooling_water_inlet_temperature_k:
              Number(coolingWaterInletTemperature),

            cooling_water_outlet_temperature_k:
              Number(coolingWaterOutletTemperature),

            selected_driver_power_kw:
              Number(selectedDriverPower),

            driver_service_factor:
              Number(driverServiceFactor),

            motor_efficiency:
              motorEfficiency
                ? Number(motorEfficiency)
                : null,
          },

          execution: {
            persist_result: persistResult,

            project_id:
              persistResult
                ? projectId
                : null,

            calculation_code:
              persistResult
                ? calculationCode
                : null,

            title:
              persistResult
                ? title
                : null,

            engineering_notes:
              persistResult && engineeringNotes
                ? engineeringNotes
                : null,
          },
        },
      ),

    onSuccess: (response) => {
      setResult(response);
    },
  });

  function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ): void {
    event.preventDefault();

    setResult(null);
    calculationMutation.mutate();
  }

  const engineeringResult = result?.result ?? null;
  const driverResult = isResultObject(engineeringResult?.driver)
    ? engineeringResult.driver
    : null;
  const temperatureResult = isResultObject(engineeringResult?.temperature)
    ? engineeringResult.temperature
    : null;
  const stagingResult = isResultObject(engineeringResult?.staging)
    ? engineeringResult.staging
    : null;
  const overallStatus = normalizeStatus(engineeringResult?.overall_status);
  const validationChecks = readValidationChecks(
    engineeringResult?.validation_checks,
  );
  const resultMetrics: ResultMetric[] = result
    ? [
        {
          label: "Shaft Power",
          value: driverResult?.shaft_power_kw,
          unit: "kW",
        },
        {
          label: "Required Driver",
          value: driverResult?.required_driver_power_kw,
          unit: "kW",
        },
        {
          label: "Selected Driver",
          value: driverResult?.selected_driver_power_kw,
          unit: "kW",
        },
        {
          label: "Driver Margin",
          value: driverResult?.driver_margin_kw,
          unit: "kW",
        },
        {
          label: "Discharge Temperature",
          value: temperatureResult?.actual_discharge_temperature_k,
          unit: "K",
        },
        {
          label: "Stage Compression Ratio",
          value: stagingResult?.stage_compression_ratio,
        },
      ].filter((metric) => metric.value !== undefined)
    : [];
  const resultPresentation = overallStatus === "PASS"
    ? {
        cardClass: "border-emerald-200 bg-emerald-50/30",
        iconClass: "text-emerald-600",
        badgeClass: "border-emerald-300 bg-emerald-100 text-emerald-900",
        title: "Compression Engineering Result",
        description:
          "Calculation completed and all configured engineering checks passed.",
      }
    : overallStatus === "WARN"
      ? {
          cardClass: "border-amber-300 bg-amber-50/40",
          iconClass: "text-amber-700",
          badgeClass: "border-amber-300 bg-amber-100 text-amber-950",
          title: "Engineering Review Recommended",
          description:
            "Calculation completed with one or more engineering warnings requiring review.",
        }
      : overallStatus === "FAIL"
        ? {
            cardClass: "border-red-300 bg-red-50/40",
            iconClass: "text-red-700",
            badgeClass: "border-red-300 bg-red-100 text-red-950",
            title: "Engineering Review Required",
            description:
              "Calculation completed, but one or more engineering checks failed. Resolve the failed checks before equipment selection or approval.",
          }
        : {
            cardClass: "border-slate-300 bg-slate-50/40",
            iconClass: "text-slate-600",
            badgeClass: "border-slate-300 bg-slate-100 text-slate-900",
            title: "Compression Engineering Result",
            description:
              "Calculation completed. Review the engineering result and validation checks.",
          };
  const ResultStatusIcon = overallStatus === "PASS"
    ? CheckCircle2
    : AlertTriangle;

  return (
    <main className="space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <Badge variant="outline">
              Advanced Compression Engineering
            </Badge>

            <h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">
              Compression Engineering
            </h1>

            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">
              Calculate multi-stage compressor thermodynamic performance,
              intercooling duty, cooling-water requirements, and driver
              adequacy using a project-scoped engineering workflow.
            </p>

            <div className="mt-4 flex flex-wrap gap-2">
              <Badge variant="secondary">
                {project
                  ? `${project.project_code} · ${project.project_name}`
                  : projectQuery.isPending
                    ? "Loading project..."
                    : `Project ${projectId}`}
              </Badge>

              {project && (
                <Badge variant="outline">
                  {project.status}
                </Badge>
              )}

              <Badge variant="outline">
                Vendor Neutral
              </Badge>

              <Badge variant="outline">
                Calculation Persistence
              </Badge>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button
              asChild
              variant="outline"
            >
              <Link to={`/projects/${projectId}/compressor`}>
                <Settings2 className="size-4" />
                Advanced Engineering
              </Link>
            </Button>

            <Button
              asChild
              variant="outline"
            >
              <Link to={`/projects/${projectId}/calculations`}>
                <History className="size-4" />
                Calculation History
              </Link>
            </Button>

            <Button
              type="submit"
              form="compression-engineering-form"
              disabled={calculationMutation.isPending}
            >
              <Play className="size-4" />
              {calculationMutation.isPending
                ? "Calculating..."
                : "Run Calculation"}
            </Button>
          </div>
        </div>
      </section>

      <Card>
        <CardHeader>
          <div className="flex items-start gap-3">
            <Calculator className="mt-0.5 size-5 text-slate-500" />

            <div>
              <CardTitle>
                Guided Calculation Workflow
              </CardTitle>

              <CardDescription className="mt-1 leading-6">
                Complete the gas basis, compression design, cooling system,
                driver selection, and optional project-persistence record.
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="flex flex-wrap gap-2">
          {[
            "01 Gas Basis",
            "02 Compression Design",
            "03 Intercooling",
            "04 Driver Selection",
            "05 Project Record",
            "06 Engineering Result",
          ].map((stage) => (
            <Badge
              key={stage}
              variant="outline"
            >
              {stage}
            </Badge>
          ))}
        </CardContent>
      </Card>

      <form
        id="compression-engineering-form"
        className="space-y-6"
        onSubmit={handleSubmit}
      >
        <Card>
          <fieldset>
            <legend className="sr-only">
              Gas Operating Conditions
            </legend>

            <CardHeader>
              <div className="flex items-start gap-3">
                <Wind className="mt-0.5 size-5 text-slate-500" />

                <div>
                  <CardTitle>
                    Gas Operating Conditions
                  </CardTitle>

                  <CardDescription className="mt-1 leading-6">
                    Define the suction state, delivery pressure, gas flow,
                    molecular properties, and real-gas correction factors.
                  </CardDescription>
                </div>
              </div>
            </CardHeader>

            <CardContent className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
              <EngineeringInput
                id="suction-pressure"
                label="Suction Pressure"
                unit="bar abs"
                type="number"
                step="any"
                min="0.01"
                required
                value={suctionPressure}
                onChange={(event) =>
                  setSuctionPressure(event.target.value)
                }
              />

              <EngineeringInput
                id="discharge-pressure"
                label="Discharge Pressure"
                unit="bar abs"
                type="number"
                step="any"
                min="0.01"
                required
                value={dischargePressure}
                onChange={(event) =>
                  setDischargePressure(event.target.value)
                }
              />

              <EngineeringInput
                id="suction-temperature"
                label="Suction Temperature"
                unit="K"
                type="number"
                step="any"
                min="0.01"
                required
                value={suctionTemperature}
                onChange={(event) =>
                  setSuctionTemperature(event.target.value)
                }
              />

              <EngineeringInput
                id="mass-flow"
                label="Mass Flow"
                unit="kg/s"
                type="number"
                step="any"
                min="0.0001"
                required
                value={massFlow}
                onChange={(event) =>
                  setMassFlow(event.target.value)
                }
              />

              <EngineeringInput
                id="actual-flow"
                label="Actual Flow"
                unit="m³/s"
                type="number"
                step="any"
                min="0.0001"
                required
                value={actualFlow}
                onChange={(event) =>
                  setActualFlow(event.target.value)
                }
              />

              <EngineeringInput
                id="molecular-weight"
                label="Molecular Weight"
                unit="kg/kmol"
                type="number"
                step="any"
                min="0.01"
                required
                value={molecularWeight}
                onChange={(event) =>
                  setMolecularWeight(event.target.value)
                }
              />

              <EngineeringInput
                id="suction-z"
                label="Suction Z-Factor"
                type="number"
                step="any"
                min="0.01"
                required
                value={suctionZ}
                onChange={(event) =>
                  setSuctionZ(event.target.value)
                }
              />

              <EngineeringInput
                id="discharge-z"
                label="Discharge Z-Factor"
                type="number"
                step="any"
                min="0.01"
                required
                value={dischargeZ}
                onChange={(event) =>
                  setDischargeZ(event.target.value)
                }
              />

              <EngineeringInput
                id="isentropic-exponent"
                label="Isentropic Exponent"
                unit="k"
                type="number"
                step="any"
                min="1.0001"
                required
                value={isentropicExponent}
                onChange={(event) =>
                  setIsentropicExponent(event.target.value)
                }
              />
            </CardContent>
          </fieldset>
        </Card>

        <div className="grid gap-6 xl:grid-cols-2">
          <Card>
            <fieldset>
              <legend className="sr-only">
                Compression Design
              </legend>

              <CardHeader>
                <div className="flex items-start gap-3">
                  <Gauge className="mt-0.5 size-5 text-slate-500" />

                  <div>
                    <CardTitle>
                      Compression Design
                    </CardTitle>

                    <CardDescription className="mt-1 leading-6">
                      Set stage count, heat capacity, and compressor
                      efficiency assumptions.
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="grid gap-5 sm:grid-cols-2">
                <EngineeringInput
                  id="stages"
                  label="Number of Stages"
                  type="number"
                  min="1"
                  step="1"
                  required
                  value={numberOfStages}
                  onChange={(event) =>
                    setNumberOfStages(event.target.value)
                  }
                />

                <EngineeringInput
                  id="cp"
                  label="Specific Heat Cp"
                  unit="kJ/kg-K"
                  type="number"
                  min="0.01"
                  step="any"
                  required
                  value={specificHeatCp}
                  onChange={(event) =>
                    setSpecificHeatCp(event.target.value)
                  }
                />

                <EngineeringInput
                  id="isentropic-efficiency"
                  label="Isentropic Efficiency"
                  type="number"
                  min="0.01"
                  max="1"
                  step="any"
                  required
                  value={isentropicEfficiency}
                  onChange={(event) =>
                    setIsentropicEfficiency(event.target.value)
                  }
                />

                <EngineeringInput
                  id="mechanical-efficiency"
                  label="Mechanical Efficiency"
                  type="number"
                  min="0.01"
                  max="1"
                  step="any"
                  required
                  value={mechanicalEfficiency}
                  onChange={(event) =>
                    setMechanicalEfficiency(event.target.value)
                  }
                />
              </CardContent>
            </fieldset>
          </Card>

          <Card>
            <fieldset>
              <legend className="sr-only">
                Intercooling / Cooling Water
              </legend>

              <CardHeader>
                <div className="flex items-start gap-3">
                  <Snowflake className="mt-0.5 size-5 text-slate-500" />

                  <div>
                    <CardTitle>
                      Intercooling / Cooling Water
                    </CardTitle>

                    <CardDescription className="mt-1 leading-6">
                      Define interstage cooling and cooling-water temperature
                      limits used by the heat-rejection calculation.
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="grid gap-5 sm:grid-cols-2">
                <EngineeringInput
                  id="intercooler-outlet"
                  label="Intercooler Outlet"
                  unit="K"
                  type="number"
                  min="0.01"
                  step="any"
                  required
                  value={intercoolerOutletTemperature}
                  onChange={(event) =>
                    setIntercoolerOutletTemperature(event.target.value)
                  }
                />

                <EngineeringInput
                  id="cw-inlet"
                  label="Cooling Water Inlet"
                  unit="K"
                  type="number"
                  min="0.01"
                  step="any"
                  required
                  value={coolingWaterInletTemperature}
                  onChange={(event) =>
                    setCoolingWaterInletTemperature(event.target.value)
                  }
                />

                <EngineeringInput
                  id="cw-outlet"
                  label="Cooling Water Outlet"
                  unit="K"
                  type="number"
                  min="0.01"
                  step="any"
                  required
                  value={coolingWaterOutletTemperature}
                  onChange={(event) =>
                    setCoolingWaterOutletTemperature(event.target.value)
                  }
                />
              </CardContent>
            </fieldset>
          </Card>
        </div>

        <Card>
          <fieldset>
            <legend className="sr-only">
              Driver Selection
            </legend>

            <CardHeader>
              <div className="flex items-start gap-3">
                <Settings2 className="mt-0.5 size-5 text-slate-500" />

                <div>
                  <CardTitle>
                    Driver Selection
                  </CardTitle>

                  <CardDescription className="mt-1 leading-6">
                    Evaluate installed driver power, service margin, and motor
                    conversion efficiency against calculated shaft demand.
                  </CardDescription>
                </div>
              </div>
            </CardHeader>

            <CardContent className="grid gap-5 md:grid-cols-3">
              <EngineeringInput
                id="driver-power"
                label="Selected Driver Power"
                unit="kW"
                type="number"
                min="0.01"
                step="any"
                required
                value={selectedDriverPower}
                onChange={(event) =>
                  setSelectedDriverPower(event.target.value)
                }
              />

              <div className="space-y-2">
                <EngineeringInput
                  id="service-factor"
                  label="Driver Service Margin"
                  unit="fraction"
                  type="number"
                  min="0"
                  step="any"
                  required
                  value={driverServiceFactor}
                  onChange={(event) =>
                    setDriverServiceFactor(event.target.value)
                  }
                />

                <p className="text-xs leading-5 text-slate-500">
                  Enter 0.10 for a 10% power reserve. Required driver power
                  equals shaft power multiplied by one plus this margin.
                </p>
              </div>

              <EngineeringInput
                id="motor-efficiency"
                label="Motor Efficiency"
                type="number"
                min="0.01"
                max="1"
                step="any"
                value={motorEfficiency}
                onChange={(event) =>
                  setMotorEfficiency(event.target.value)
                }
              />
            </CardContent>
          </fieldset>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-start gap-3">
              <Database className="mt-0.5 size-5 text-slate-500" />

              <div>
                <CardTitle>
                  Project Calculation Record
                </CardTitle>

                <CardDescription className="mt-1 leading-6">
                  Optionally persist this calculation under the authenticated
                  project for revision history and engineering review.
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-5">
            <label className="flex cursor-pointer items-start gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4">
              <input
                type="checkbox"
                className="mt-0.5 size-4 rounded border-slate-300"
                checked={persistResult}
                onChange={(event) =>
                  setPersistResult(event.target.checked)
                }
              />

              <span>
                <span className="block text-sm font-semibold text-slate-900">
                  Save result to project
                </span>

                <span className="mt-1 block text-sm leading-6 text-slate-600">
                  Store the calculation code, title, engineering notes,
                  request inputs, and calculated result under this project.
                </span>
              </span>
            </label>

            {persistResult && (
              <fieldset className="grid gap-5 border-t border-slate-200 pt-5 md:grid-cols-2">
                <legend className="sr-only">
                  Persistence Details
                </legend>

                <EngineeringInput
                  id="calculation-code"
                  label="Calculation Code"
                  required
                  value={calculationCode}
                  onChange={(event) =>
                    setCalculationCode(event.target.value)
                  }
                />

                <EngineeringInput
                  id="calculation-title"
                  label="Calculation Title"
                  required
                  value={title}
                  onChange={(event) =>
                    setTitle(event.target.value)
                  }
                />

                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="engineering-notes">
                    Engineering Notes
                  </Label>

                  <textarea
                    id="engineering-notes"
                    className="min-h-28 w-full rounded-md border border-slate-200 bg-transparent px-3 py-2 text-sm shadow-xs outline-none transition focus-visible:border-slate-400 focus-visible:ring-3 focus-visible:ring-slate-200"
                    value={engineeringNotes}
                    onChange={(event) =>
                      setEngineeringNotes(event.target.value)
                    }
                  />
                </div>
              </fieldset>
            )}
          </CardContent>
        </Card>

        <div className="flex justify-end">
          <Button
            type="submit"
            size="lg"
            disabled={calculationMutation.isPending}
          >
            <Play className="size-4" />
            {calculationMutation.isPending
              ? "Calculating..."
              : "Run Compression Calculation"}
          </Button>
        </div>
      </form>

      {calculationMutation.isError && (
        <Card className="border-red-200 bg-red-50">
          <CardHeader>
            <div className="flex items-start gap-3">
              <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-700" />

              <div>
                <CardTitle className="text-red-950">
                  Calculation Error
                </CardTitle>

                <CardDescription className="mt-1 text-red-800">
                  Compression calculation could not be completed. Review the
                  engineering inputs and try again.
                </CardDescription>
              </div>
            </div>
          </CardHeader>
        </Card>
      )}

      {result && (
        <Card className={resultPresentation.cardClass}>
          <CardHeader>
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div className="flex items-start gap-3">
                <ResultStatusIcon
                  className={`mt-0.5 size-5 shrink-0 ${resultPresentation.iconClass}`}
                />

                <div>
                  <CardTitle>
                    {resultPresentation.title}
                  </CardTitle>

                  <CardDescription className="mt-1 leading-6">
                    {resultPresentation.description}
                  </CardDescription>
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                <Badge
                  variant="outline"
                  className={resultPresentation.badgeClass}
                >
                  {overallStatus}
                </Badge>

                {result.calculation_case_id !== null && (
                  <Badge variant="secondary">
                    Saved Case {result.calculation_case_id}
                  </Badge>
                )}
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-5">
            {resultMetrics.length > 0 && (
              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                {resultMetrics.map((metric) => (
                  <div
                    key={metric.label}
                    className="rounded-xl border border-slate-200 bg-white p-4"
                  >
                    <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                      {metric.label}
                    </p>

                    <p className="mt-2 break-words text-lg font-semibold text-slate-950">
                      {formatResultValue(metric.value)}
                      {metric.unit && (
                        <span className="ml-1 text-sm font-medium text-slate-500">
                          {metric.unit}
                        </span>
                      )}
                    </p>
                  </div>
                ))}
              </div>
            )}

            {validationChecks.length > 0 && (
              <section aria-labelledby="validation-checks-heading">
                <div className="mb-3 flex items-center justify-between gap-3">
                  <h2
                    id="validation-checks-heading"
                    className="text-sm font-semibold text-slate-950"
                  >
                    Engineering Validation Checks
                  </h2>

                  <span className="text-xs text-slate-500">
                    {validationChecks.filter((check) => check.status === "PASS").length}
                    {" of "}
                    {validationChecks.length} passed
                  </span>
                </div>

                <div className="space-y-3">
                  {validationChecks.map((check) => {
                    const checkClass = check.status === "PASS"
                      ? "border-emerald-200 bg-emerald-50"
                      : check.status === "WARN"
                        ? "border-amber-300 bg-amber-50"
                        : "border-red-300 bg-red-50";
                    const checkBadgeClass = check.status === "PASS"
                      ? "border-emerald-300 bg-emerald-100 text-emerald-900"
                      : check.status === "WARN"
                        ? "border-amber-300 bg-amber-100 text-amber-950"
                        : "border-red-300 bg-red-100 text-red-950";

                    return (
                      <article
                        key={check.code}
                        className={`rounded-xl border p-4 ${checkClass}`}
                      >
                        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                          <div>
                            <p className="text-sm font-semibold text-slate-950">
                              {check.code.replaceAll("_", " ")}
                            </p>

                            <p className="mt-1 text-sm leading-6 text-slate-700">
                              {check.description}
                            </p>
                          </div>

                          <Badge
                            variant="outline"
                            className={checkBadgeClass}
                          >
                            {check.status}
                          </Badge>
                        </div>

                        <dl className="mt-3 grid gap-2 text-xs text-slate-600 sm:grid-cols-2">
                          <div>
                            <dt className="font-medium text-slate-500">
                              Actual
                            </dt>
                            <dd className="mt-1 font-semibold text-slate-800">
                              {formatResultValue(check.actualValue)}
                            </dd>
                          </div>

                          <div>
                            <dt className="font-medium text-slate-500">
                              Acceptance Limit
                            </dt>
                            <dd className="mt-1 font-semibold text-slate-800">
                              {check.limitDescription}
                            </dd>
                          </div>
                        </dl>
                      </article>
                    );
                  })}
                </div>
              </section>
            )}

            <details className="rounded-xl border border-slate-200 bg-white">
              <summary className="cursor-pointer px-4 py-3 text-sm font-semibold text-slate-800">
                View complete engineering result payload
              </summary>

              <pre className="max-h-[36rem] overflow-auto border-t border-slate-200 bg-slate-950 p-4 text-xs leading-6 text-slate-100">
                {JSON.stringify(result.result, null, 2)}
              </pre>
            </details>
          </CardContent>
        </Card>
      )}
    </main>
  );
}
