import {
  useMemo,
  useState,
  type ComponentProps,
  type Dispatch,
  type FormEvent,
  type SetStateAction,
} from "react";

import { useMutation } from "@tanstack/react-query";
import {
  AlertTriangle,
  Atom,
  Calculator,
  CheckCircle2,
  Gauge,
  Play,
  RotateCcw,
  Thermometer,
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
import { calculateGasProperties } from "../features/projects/gasService";
import type { GasPropertiesResponse } from "../features/projects/gasTypes";
import { useProjectContext } from "../features/projects/useProjectContext";
import { ApiError } from "../services/apiClient";

const MOLE_FRACTION_TOLERANCE = 0.000001;

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
  unit?: string;
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

function formatResultValue(
  value: string,
  maximumFractionDigits = 4,
): string {
  const numericValue = Number(value);

  if (!Number.isFinite(numericValue)) {
    return value;
  }

  return numericValue.toLocaleString("en-IN", {
    maximumFractionDigits,
  });
}

function ResultMetric({
  label,
  value,
  unit,
  description,
}: ResultMetricProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </dt>

      <dd className="mt-2 break-words text-xl font-semibold text-slate-950">
        {formatResultValue(value)}
        {unit && (
          <span className="ml-1 text-sm font-medium text-slate-500">
            {unit}
          </span>
        )}
      </dd>

      {description && (
        <p className="mt-2 text-xs leading-5 text-slate-600">
          {description}
        </p>
      )}
    </div>
  );
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

    return `The calculation service returned HTTP ${error.status}.`;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "The gas-property calculation could not be completed.";
}

export function GasPropertiesPage() {
  const { accessToken } = useAuth();
  const {
    projectId,
    hasValidProjectId,
    project,
    projectQuery,
  } = useProjectContext();

  const [methane, setMethane] = useState("0.90");
  const [ethane, setEthane] = useState("0.05");
  const [nitrogen, setNitrogen] = useState("0.03");
  const [carbonDioxide, setCarbonDioxide] = useState("0.02");
  const [pressureBar, setPressureBar] = useState("10");
  const [temperatureK, setTemperatureK] = useState("300");
  const [result, setResult] =
    useState<GasPropertiesResponse | null>(null);

  const moleFractionValues = useMemo(
    () => [
      Number(methane),
      Number(ethane),
      Number(nitrogen),
      Number(carbonDioxide),
    ],
    [methane, ethane, nitrogen, carbonDioxide],
  );

  const moleFractionTotal = useMemo(
    () => moleFractionValues.reduce((total, value) => total + value, 0),
    [moleFractionValues],
  );

  const moleFractionsAreValid = moleFractionValues.every(
    (value) => Number.isFinite(value) && value >= 0 && value <= 1,
  );
  const totalIsValid =
    moleFractionsAreValid &&
    Math.abs(moleFractionTotal - 1) <= MOLE_FRACTION_TOLERANCE;
  const pressureIsValid =
    Number.isFinite(Number(pressureBar)) && Number(pressureBar) > 0;
  const temperatureIsValid =
    Number.isFinite(Number(temperatureK)) && Number(temperatureK) > 0;

  const calculationMutation = useMutation({
    mutationFn: () => {
      if (!accessToken) {
        throw new Error("Authenticated access token is required.");
      }

      return calculateGasProperties(
        accessToken,
        {
          components: [
            {
              component: "methane",
              mole_fraction: Number(methane),
            },
            {
              component: "ethane",
              mole_fraction: Number(ethane),
            },
            {
              component: "nitrogen",
              mole_fraction: Number(nitrogen),
            },
            {
              component: "carbon_dioxide",
              mole_fraction: Number(carbonDioxide),
            },
          ],
          pressure_bar: Number(pressureBar),
          temperature_k: Number(temperatureK),
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
    totalIsValid &&
    pressureIsValid &&
    temperatureIsValid &&
    !calculationMutation.isPending;

  function updateInput(
    setter: Dispatch<SetStateAction<string>>,
    value: string,
  ): void {
    setter(value);
    setResult(null);
    calculationMutation.reset();
  }

  function handleReset(): void {
    setMethane("0.90");
    setEthane("0.05");
    setNitrogen("0.03");
    setCarbonDioxide("0.02");
    setPressureBar("10");
    setTemperatureK("300");
    setResult(null);
    calculationMutation.reset();
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
                Advanced Gas Engineering
              </Badge>

              <div>
                <h1 className="text-3xl font-bold tracking-tight text-slate-950">
                  Gas Properties Calculation
                </h1>

                <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
                  Calculate mixture molecular properties, Kay&apos;s-rule
                  pseudo-critical conditions, Papay Z-factor, and real-gas
                  density at the specified compressor operating state.
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
                  <Badge variant="outline">
                    {project.status}
                  </Badge>
                )}

                <Badge variant="outline">
                  Vendor Neutral
                </Badge>

                <Badge variant="outline">
                  Calculation Only
                </Badge>
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
                form="gas-properties-form"
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
            <Calculator className="mt-0.5 size-5 shrink-0 text-slate-500" />

            <div>
              <CardTitle>
                Guided Gas Property Workflow
              </CardTitle>

              <CardDescription className="mt-1 leading-6">
                Establish the composition basis, confirm the absolute
                operating state, and review the calculated real-gas property
                set before using it in downstream compressor calculations.
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="flex flex-wrap gap-2">
          <Badge variant="outline">01 Composition Basis</Badge>
          <Badge variant="outline">02 Mixture Balance</Badge>
          <Badge variant="outline">03 Operating State</Badge>
          <Badge variant="outline">04 Pseudo-critical Basis</Badge>
          <Badge variant="outline">05 Real-gas Result</Badge>
        </CardContent>
      </Card>

      <form
        id="gas-properties-form"
        className="space-y-6"
        onSubmit={handleSubmit}
      >
        <Card>
          <CardHeader>
            <div className="flex items-start gap-3">
              <Atom className="mt-0.5 size-5 shrink-0 text-slate-500" />

              <div>
                <CardTitle>
                  Gas Composition Basis
                </CardTitle>

                <CardDescription className="mt-1 leading-6">
                  Enter component mole fractions on a 0-to-1 basis. The
                  mixture must total 1.000000 before calculation.
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-5">
            <fieldset className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
              <legend className="sr-only">
                Gas component mole fractions
              </legend>

              <EngineeringInput
                id="methane"
                label="Methane (CH₄)"
                unit="mole fraction"
                type="number"
                min="0"
                max="1"
                step="any"
                inputMode="decimal"
                required
                value={methane}
                onChange={(event) =>
                  updateInput(setMethane, event.target.value)
                }
              />

              <EngineeringInput
                id="ethane"
                label="Ethane (C₂H₆)"
                unit="mole fraction"
                type="number"
                min="0"
                max="1"
                step="any"
                inputMode="decimal"
                required
                value={ethane}
                onChange={(event) =>
                  updateInput(setEthane, event.target.value)
                }
              />

              <EngineeringInput
                id="nitrogen"
                label="Nitrogen (N₂)"
                unit="mole fraction"
                type="number"
                min="0"
                max="1"
                step="any"
                inputMode="decimal"
                required
                value={nitrogen}
                onChange={(event) =>
                  updateInput(setNitrogen, event.target.value)
                }
              />

              <EngineeringInput
                id="carbon-dioxide"
                label="Carbon Dioxide (CO₂)"
                unit="mole fraction"
                type="number"
                min="0"
                max="1"
                step="any"
                inputMode="decimal"
                required
                value={carbonDioxide}
                onChange={(event) =>
                  updateInput(setCarbonDioxide, event.target.value)
                }
              />
            </fieldset>

            <div
              role={totalIsValid ? "status" : "alert"}
              className={`rounded-xl border p-4 ${
                totalIsValid
                  ? "border-emerald-200 bg-emerald-50"
                  : "border-red-300 bg-red-50"
              }`}
            >
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-start gap-3">
                  {totalIsValid ? (
                    <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-emerald-700" />
                  ) : (
                    <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-700" />
                  )}

                  <div>
                    <p className="text-sm font-semibold text-slate-950">
                      Mixture Balance
                    </p>

                    <p className="mt-1 text-sm leading-6 text-slate-700">
                      {totalIsValid
                        ? "Composition is balanced and ready for calculation."
                        : "Adjust the component fractions until the total equals 1.000000."}
                    </p>
                  </div>
                </div>

                <div className="text-left sm:text-right">
                  <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                    Mole Fraction Total
                  </p>

                  <p className="mt-1 font-mono text-lg font-semibold text-slate-950">
                    {Number.isFinite(moleFractionTotal)
                      ? moleFractionTotal.toFixed(6)
                      : "Invalid"}
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
                <CardTitle>
                  Operating State
                </CardTitle>

                <CardDescription className="mt-1 leading-6">
                  Define the absolute pressure and thermodynamic temperature
                  used for reduced-property, compressibility, and density
                  calculations.
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent className="grid gap-5 md:grid-cols-2">
            <EngineeringInput
              id="pressure"
              label="Absolute Pressure"
              unit="bar(a)"
              type="number"
              min="0.01"
              step="any"
              inputMode="decimal"
              required
              value={pressureBar}
              onChange={(event) =>
                updateInput(setPressureBar, event.target.value)
              }
            />

            <EngineeringInput
              id="temperature"
              label="Absolute Temperature"
              unit="K"
              type="number"
              min="0.01"
              step="any"
              inputMode="decimal"
              required
              value={temperatureK}
              onChange={(event) =>
                updateInput(setTemperatureK, event.target.value)
              }
            />

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 md:col-span-2">
              <div className="flex items-start gap-3">
                <Thermometer className="mt-0.5 size-5 shrink-0 text-slate-500" />

                <p className="text-sm leading-6 text-slate-600">
                  Pressure must be entered as absolute pressure, not gauge
                  pressure. Temperature must be entered in kelvin. These two
                  values define the exact state at which Z-factor and density
                  are reported.
                </p>
              </div>
            </div>
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
              ? "Calculating Gas Properties..."
              : "Calculate Gas Properties"}
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
                  Gas Property Calculation Error
                </CardTitle>

                <CardDescription className="mt-1 leading-6 text-red-800">
                  {getCalculationErrorMessage(calculationMutation.error)}
                </CardDescription>

                <p className="mt-2 text-sm leading-6 text-red-800">
                  Confirm the composition balance, absolute operating state,
                  and supported component basis before trying again.
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
                    Gas Property Calculation Complete
                  </CardTitle>

                  <CardDescription className="mt-1 leading-6">
                    Review the calculated mixture, pseudo-critical, reduced,
                    and real-gas properties for the specified operating state.
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
            <section aria-labelledby="mixture-results-heading">
              <h2
                id="mixture-results-heading"
                className="mb-3 text-sm font-semibold text-slate-950"
              >
                Mixture and Real-gas Properties
              </h2>

              <dl className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                <ResultMetric
                  label="Molecular Weight"
                  value={result.molecular_weight_kg_per_kmol}
                  unit="kg/kmol"
                />

                <ResultMetric
                  label="Specific Gravity"
                  value={result.specific_gravity_air_1}
                  description="Relative to dry air = 1.0"
                />

                <ResultMetric
                  label="Compressibility Factor"
                  value={result.z_factor}
                  description="Z = 1.0 is the ideal-gas reference"
                />

                <ResultMetric
                  label="Real-gas Density"
                  value={result.density_kg_per_m3}
                  unit="kg/m³"
                />
              </dl>
            </section>

            <section aria-labelledby="critical-results-heading">
              <h2
                id="critical-results-heading"
                className="mb-3 text-sm font-semibold text-slate-950"
              >
                Pseudo-critical and Reduced Properties
              </h2>

              <dl className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                <ResultMetric
                  label="Pseudo-critical Temperature"
                  value={result.pseudocritical_temperature_k}
                  unit="K"
                />

                <ResultMetric
                  label="Pseudo-critical Pressure"
                  value={result.pseudocritical_pressure_bar}
                  unit="bar(a)"
                />

                <ResultMetric
                  label="Reduced Temperature"
                  value={result.reduced_temperature}
                />

                <ResultMetric
                  label="Reduced Pressure"
                  value={result.reduced_pressure}
                />
              </dl>
            </section>

            <div className="rounded-xl border border-slate-200 bg-white p-4">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Z-factor Correlation
              </p>

              <p className="mt-2 text-base font-semibold text-slate-950">
                {result.z_factor_correlation}
              </p>

              <p className="mt-2 text-sm leading-6 text-slate-600">
                This is the correlation selected by the calculation engine for
                the reported reduced state and compressibility factor.
              </p>
            </div>

            <details className="rounded-xl border border-slate-200 bg-white">
              <summary className="cursor-pointer px-4 py-3 text-sm font-semibold text-slate-800">
                View complete gas property result payload
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
