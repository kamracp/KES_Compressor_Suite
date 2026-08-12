import {
  useState,
  type FormEvent,
} from "react";

import { useMutation } from "@tanstack/react-query";
import { useParams } from "react-router";

import { useAuth } from "../features/auth/AuthProvider";
import {
  executeCompressionCalculation,
} from "../features/projects/compressionService";
import type {
  CompressionExecutionResponse,
} from "../features/projects/compressionTypes";

export function CompressionEngineeringPage() {
  const { projectId } = useParams();
  const { accessToken } = useAuth();

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
  const [driverServiceFactor, setDriverServiceFactor] = useState("1.10");
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
              persistResult && projectId
                ? Number(projectId)
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

  return (
    <main>
      <h1>Compression Engineering</h1>

      <p>Project ID: {projectId}</p>

      <p>
        Calculate multi-stage compressor thermodynamic performance,
        intercooling duty, and driver requirements.
      </p>

      <form onSubmit={handleSubmit}>
        <fieldset>
          <legend>Gas Operating Conditions</legend>

          <div>
            <label htmlFor="suction-pressure">
              Suction Pressure (bar abs)
            </label>
            <input
              id="suction-pressure"
              type="number"
              step="any"
              min="0.01"
              required
              value={suctionPressure}
              onChange={(event) =>
                setSuctionPressure(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="discharge-pressure">
              Discharge Pressure (bar abs)
            </label>
            <input
              id="discharge-pressure"
              type="number"
              step="any"
              min="0.01"
              required
              value={dischargePressure}
              onChange={(event) =>
                setDischargePressure(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="suction-temperature">
              Suction Temperature (K)
            </label>
            <input
              id="suction-temperature"
              type="number"
              step="any"
              min="0.01"
              required
              value={suctionTemperature}
              onChange={(event) =>
                setSuctionTemperature(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="mass-flow">
              Mass Flow (kg/s)
            </label>
            <input
              id="mass-flow"
              type="number"
              step="any"
              min="0.0001"
              required
              value={massFlow}
              onChange={(event) =>
                setMassFlow(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="actual-flow">
              Actual Flow (m³/s)
            </label>
            <input
              id="actual-flow"
              type="number"
              step="any"
              min="0.0001"
              required
              value={actualFlow}
              onChange={(event) =>
                setActualFlow(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="molecular-weight">
              Molecular Weight (kg/kmol)
            </label>
            <input
              id="molecular-weight"
              type="number"
              step="any"
              min="0.01"
              required
              value={molecularWeight}
              onChange={(event) =>
                setMolecularWeight(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="suction-z">
              Suction Z-Factor
            </label>
            <input
              id="suction-z"
              type="number"
              step="any"
              min="0.01"
              required
              value={suctionZ}
              onChange={(event) =>
                setSuctionZ(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="discharge-z">
              Discharge Z-Factor
            </label>
            <input
              id="discharge-z"
              type="number"
              step="any"
              min="0.01"
              required
              value={dischargeZ}
              onChange={(event) =>
                setDischargeZ(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="isentropic-exponent">
              Isentropic Exponent (k)
            </label>
            <input
              id="isentropic-exponent"
              type="number"
              step="any"
              min="1.0001"
              required
              value={isentropicExponent}
              onChange={(event) =>
                setIsentropicExponent(event.target.value)
              }
            />
          </div>
        </fieldset>

        <fieldset>
          <legend>Compression Design</legend>

          <div>
            <label htmlFor="stages">
              Number of Stages
            </label>
            <input
              id="stages"
              type="number"
              min="1"
              step="1"
              required
              value={numberOfStages}
              onChange={(event) =>
                setNumberOfStages(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="cp">
              Specific Heat Cp (kJ/kg-K)
            </label>
            <input
              id="cp"
              type="number"
              min="0.01"
              step="any"
              required
              value={specificHeatCp}
              onChange={(event) =>
                setSpecificHeatCp(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="isentropic-efficiency">
              Isentropic Efficiency
            </label>
            <input
              id="isentropic-efficiency"
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
          </div>

          <div>
            <label htmlFor="mechanical-efficiency">
              Mechanical Efficiency
            </label>
            <input
              id="mechanical-efficiency"
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
          </div>
        </fieldset>

        <fieldset>
          <legend>Intercooling / Cooling Water</legend>

          <div>
            <label htmlFor="intercooler-outlet">
              Intercooler Outlet Temperature (K)
            </label>
            <input
              id="intercooler-outlet"
              type="number"
              min="0.01"
              step="any"
              required
              value={intercoolerOutletTemperature}
              onChange={(event) =>
                setIntercoolerOutletTemperature(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="cw-inlet">
              Cooling Water Inlet Temperature (K)
            </label>
            <input
              id="cw-inlet"
              type="number"
              min="0.01"
              step="any"
              required
              value={coolingWaterInletTemperature}
              onChange={(event) =>
                setCoolingWaterInletTemperature(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="cw-outlet">
              Cooling Water Outlet Temperature (K)
            </label>
            <input
              id="cw-outlet"
              type="number"
              min="0.01"
              step="any"
              required
              value={coolingWaterOutletTemperature}
              onChange={(event) =>
                setCoolingWaterOutletTemperature(event.target.value)
              }
            />
          </div>
        </fieldset>

        <fieldset>
          <legend>Driver</legend>

          <div>
            <label htmlFor="driver-power">
              Selected Driver Power (kW)
            </label>
            <input
              id="driver-power"
              type="number"
              min="0.01"
              step="any"
              required
              value={selectedDriverPower}
              onChange={(event) =>
                setSelectedDriverPower(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="service-factor">
              Driver Service Factor
            </label>
            <input
              id="service-factor"
              type="number"
              min="0"
              step="any"
              required
              value={driverServiceFactor}
              onChange={(event) =>
                setDriverServiceFactor(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="motor-efficiency">
              Motor Efficiency
            </label>
            <input
              id="motor-efficiency"
              type="number"
              min="0.01"
              max="1"
              step="any"
              value={motorEfficiency}
              onChange={(event) =>
                setMotorEfficiency(event.target.value)
              }
            />
          </div>
        </fieldset>

        <div>
          <label>
            <input
              type="checkbox"
              checked={persistResult}
              onChange={(event) =>
                setPersistResult(event.target.checked)
              }
            />
            Save Result to Project
          </label>
        </div>

        {persistResult && (
          <fieldset>
            <legend>Persistence Details</legend>

            <div>
              <label htmlFor="calculation-code">
                Calculation Code
              </label>
              <input
                id="calculation-code"
                required
                value={calculationCode}
                onChange={(event) =>
                  setCalculationCode(event.target.value)
                }
              />
            </div>

            <div>
              <label htmlFor="calculation-title">
                Title
              </label>
              <input
                id="calculation-title"
                required
                value={title}
                onChange={(event) =>
                  setTitle(event.target.value)
                }
              />
            </div>

            <div>
              <label htmlFor="engineering-notes">
                Engineering Notes
              </label>
              <textarea
                id="engineering-notes"
                value={engineeringNotes}
                onChange={(event) =>
                  setEngineeringNotes(event.target.value)
                }
              />
            </div>
          </fieldset>
        )}

        <button
          type="submit"
          disabled={calculationMutation.isPending}
        >
          {calculationMutation.isPending
            ? "Calculating..."
            : "Run Compression Calculation"}
        </button>
      </form>

      {calculationMutation.isError && (
        <section>
          <h2>Calculation Error</h2>
          <p>
            Compression calculation could not be completed.
          </p>
        </section>
      )}

      {result && (
        <section>
          <h2>Compression Result</h2>

          <pre>
            {JSON.stringify(result.result, null, 2)}
          </pre>

          {result.calculation_case_id !== null && (
            <p>
              Saved Calculation Case ID:
              {" "}
              {result.calculation_case_id}
            </p>
          )}
        </section>
      )}
    </main>
  );
}
