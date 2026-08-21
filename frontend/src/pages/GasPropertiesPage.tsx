import {
  useMemo,
  useState,
  type FormEvent,
} from "react";

import { useMutation } from "@tanstack/react-query";

import { useAuth } from "../features/auth/AuthProvider";
import { useProjectContext } from "../features/projects/useProjectContext";
import { calculateGasProperties } from "../features/projects/gasService";
import type { GasPropertiesResponse } from "../features/projects/gasTypes";

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

  if (!accessToken) {
    throw new Error("Authenticated access token is required.");
  }

  if (!hasValidProjectId) {
    throw new Error("Valid project ID is required.");
  }

  const moleFractionTotal = useMemo(
    () =>
      Number(methane) +
      Number(ethane) +
      Number(nitrogen) +
      Number(carbonDioxide),
    [
      methane,
      ethane,
      nitrogen,
      carbonDioxide,
    ],
  );

  const totalIsValid =
    Math.abs(moleFractionTotal - 1) <= 0.000001;

  const calculationMutation = useMutation({
    mutationFn: () =>
      calculateGasProperties(
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
      ),
    onSuccess: (response) => {
      setResult(response);
    },
  });

  function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ): void {
    event.preventDefault();

    if (!totalIsValid) {
      return;
    }

    setResult(null);
    calculationMutation.mutate();
  }

  return (
    <main>
      <h1>Gas Properties</h1>

      <p>
        {project
          ? `${project.project_code} · ${project.project_name} · ${project.status}`
          : projectQuery.isPending
            ? "Loading project..."
            : `Project ${projectId}`}
      </p>

      <p>
        Calculate compressor gas mixture properties,
        pseudo-critical conditions, Z-factor, and density.
      </p>

      <form onSubmit={handleSubmit}>
        <fieldset>
          <legend>Gas Composition — Mole Fraction</legend>

          <div>
            <label htmlFor="methane">
              Methane
            </label>
            <input
              id="methane"
              type="number"
              min="0"
              max="1"
              step="any"
              required
              value={methane}
              onChange={(event) =>
                setMethane(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="ethane">
              Ethane
            </label>
            <input
              id="ethane"
              type="number"
              min="0"
              max="1"
              step="any"
              required
              value={ethane}
              onChange={(event) =>
                setEthane(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="nitrogen">
              Nitrogen
            </label>
            <input
              id="nitrogen"
              type="number"
              min="0"
              max="1"
              step="any"
              required
              value={nitrogen}
              onChange={(event) =>
                setNitrogen(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="carbon-dioxide">
              Carbon Dioxide
            </label>
            <input
              id="carbon-dioxide"
              type="number"
              min="0"
              max="1"
              step="any"
              required
              value={carbonDioxide}
              onChange={(event) =>
                setCarbonDioxide(event.target.value)
              }
            />
          </div>

          <p>
            Mole Fraction Total: {moleFractionTotal.toFixed(6)}
          </p>

          {!totalIsValid && (
            <p>
              Mole fractions must total exactly 1.0.
            </p>
          )}
        </fieldset>

        <fieldset>
          <legend>Operating Conditions</legend>

          <div>
            <label htmlFor="pressure">
              Absolute Pressure (bar)
            </label>
            <input
              id="pressure"
              type="number"
              min="0.01"
              step="any"
              required
              value={pressureBar}
              onChange={(event) =>
                setPressureBar(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="temperature">
              Absolute Temperature (K)
            </label>
            <input
              id="temperature"
              type="number"
              min="0.01"
              step="any"
              required
              value={temperatureK}
              onChange={(event) =>
                setTemperatureK(event.target.value)
              }
            />
          </div>
        </fieldset>

        <button
          type="submit"
          disabled={
            calculationMutation.isPending ||
            !totalIsValid
          }
        >
          {calculationMutation.isPending
            ? "Calculating..."
            : "Calculate Gas Properties"}
        </button>
      </form>

      {calculationMutation.isError && (
        <section>
          <h2>Calculation Error</h2>
          <p>
            Gas property calculation could not be completed.
          </p>
        </section>
      )}

      {result && (
        <section>
          <h2>Gas Property Results</h2>

          <table>
            <tbody>
              <tr>
                <th>Molecular Weight</th>
                <td>
                  {result.molecular_weight_kg_per_kmol}
                  {" kg/kmol"}
                </td>
              </tr>

              <tr>
                <th>Specific Gravity</th>
                <td>
                  {result.specific_gravity_air_1}
                </td>
              </tr>

              <tr>
                <th>Pseudo-critical Temperature</th>
                <td>
                  {result.pseudocritical_temperature_k}
                  {" K"}
                </td>
              </tr>

              <tr>
                <th>Pseudo-critical Pressure</th>
                <td>
                  {result.pseudocritical_pressure_bar}
                  {" bar"}
                </td>
              </tr>

              <tr>
                <th>Reduced Temperature</th>
                <td>
                  {result.reduced_temperature}
                </td>
              </tr>

              <tr>
                <th>Reduced Pressure</th>
                <td>
                  {result.reduced_pressure}
                </td>
              </tr>

              <tr>
                <th>Z-Factor</th>
                <td>
                  {result.z_factor}
                </td>
              </tr>

              <tr>
                <th>Z Correlation</th>
                <td>
                  {result.z_factor_correlation}
                </td>
              </tr>

              <tr>
                <th>Real Gas Density</th>
                <td>
                  {result.density_kg_per_m3}
                  {" kg/m³"}
                </td>
              </tr>
            </tbody>
          </table>
        </section>
      )}
    </main>
  );
}
