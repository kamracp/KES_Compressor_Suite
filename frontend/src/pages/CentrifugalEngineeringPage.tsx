import {
  useState,
  type FormEvent,
} from "react";

import { useMutation } from "@tanstack/react-query";
import { useParams } from "react-router";

import { useAuth } from "../features/auth/AuthProvider";
import {
  executeCentrifugalCalculation,
} from "../features/projects/centrifugalService";
import type {
  CentrifugalExecutionResponse,
} from "../features/projects/centrifugalTypes";

export function CentrifugalEngineeringPage() {
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

  if (!accessToken) {
    throw new Error("Authenticated access token is required.");
  }

  const calculationMutation = useMutation({
    mutationFn: () =>
      executeCentrifugalCalculation(
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

            polytropic_efficiency: Number(polytropicEfficiency),

            number_of_impeller_stages: Number(impellerStages),
            head_coefficient: Number(headCoefficient),
            rotational_speed_rpm: Number(rotationalSpeed),

            mechanical_loss_fraction: Number(mechanicalLossFraction),
            driver_margin_fraction: Number(driverMarginFraction),

            selected_driver_power_kw: Number(selectedDriverPower),

            motor_efficiency:
              motorEfficiency
                ? Number(motorEfficiency)
                : null,

            surge_flow_fraction: Number(surgeFlowFraction),
            anti_surge_margin_fraction:
              Number(antiSurgeMarginFraction),
            stonewall_flow_fraction:
              Number(stonewallFlowFraction),
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
      <h1>Centrifugal Compressor Engineering</h1>

      <p>Project ID: {projectId}</p>

      <p>
        Evaluate centrifugal compressor head, power,
        operating range, surge margin, and driver sizing.
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
              min="0.01"
              step="any"
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
              min="0.01"
              step="any"
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
              min="0.01"
              step="any"
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
              min="0.0001"
              step="any"
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
              min="0.0001"
              step="any"
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
              min="0.01"
              step="any"
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
              min="0.01"
              step="any"
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
              min="0.01"
              step="any"
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
              min="1.0001"
              step="any"
              required
              value={isentropicExponent}
              onChange={(event) =>
                setIsentropicExponent(event.target.value)
              }
            />
          </div>
        </fieldset>

        <fieldset>
          <legend>Compressor Design</legend>

          <div>
            <label htmlFor="polytropic-efficiency">
              Polytropic Efficiency
            </label>
            <input
              id="polytropic-efficiency"
              type="number"
              min="0.01"
              max="1"
              step="any"
              required
              value={polytropicEfficiency}
              onChange={(event) =>
                setPolytropicEfficiency(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="impeller-stages">
              Number of Impeller Stages
            </label>
            <input
              id="impeller-stages"
              type="number"
              min="1"
              step="1"
              required
              value={impellerStages}
              onChange={(event) =>
                setImpellerStages(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="head-coefficient">
              Head Coefficient
            </label>
            <input
              id="head-coefficient"
              type="number"
              min="0.01"
              step="any"
              required
              value={headCoefficient}
              onChange={(event) =>
                setHeadCoefficient(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="speed-rpm">
              Rotational Speed (rpm)
            </label>
            <input
              id="speed-rpm"
              type="number"
              min="1"
              step="any"
              required
              value={rotationalSpeed}
              onChange={(event) =>
                setRotationalSpeed(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="mechanical-loss">
              Mechanical Loss Fraction
            </label>
            <input
              id="mechanical-loss"
              type="number"
              min="0"
              step="any"
              required
              value={mechanicalLossFraction}
              onChange={(event) =>
                setMechanicalLossFraction(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="driver-margin">
              Driver Margin Fraction
            </label>
            <input
              id="driver-margin"
              type="number"
              min="0"
              step="any"
              required
              value={driverMarginFraction}
              onChange={(event) =>
                setDriverMarginFraction(event.target.value)
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

        <fieldset>
          <legend>Operating Envelope</legend>

          <div>
            <label htmlFor="surge-flow">
              Surge Flow Fraction
            </label>
            <input
              id="surge-flow"
              type="number"
              min="0.01"
              max="0.999"
              step="any"
              required
              value={surgeFlowFraction}
              onChange={(event) =>
                setSurgeFlowFraction(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="anti-surge-margin">
              Anti-Surge Margin Fraction
            </label>
            <input
              id="anti-surge-margin"
              type="number"
              min="0"
              step="any"
              required
              value={antiSurgeMarginFraction}
              onChange={(event) =>
                setAntiSurgeMarginFraction(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="stonewall-flow">
              Stonewall Flow Fraction
            </label>
            <input
              id="stonewall-flow"
              type="number"
              min="1.0001"
              step="any"
              required
              value={stonewallFlowFraction}
              onChange={(event) =>
                setStonewallFlowFraction(event.target.value)
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
            : "Run Centrifugal Calculation"}
        </button>
      </form>

      {calculationMutation.isError && (
        <section>
          <h2>Calculation Error</h2>
          <p>
            Centrifugal compressor calculation could not be completed.
          </p>
        </section>
      )}

      {result && (
        <section>
          <h2>Centrifugal Result</h2>

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
