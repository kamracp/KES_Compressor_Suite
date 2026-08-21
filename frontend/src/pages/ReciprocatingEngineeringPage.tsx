import {
  useState,
  type FormEvent,
} from "react";

import { useMutation } from "@tanstack/react-query";

import { useAuth } from "../features/auth/AuthProvider";
import { useProjectContext } from "../features/projects/useProjectContext";
import {
  executeReciprocatingCalculation,
} from "../features/projects/reciprocatingService";
import type {
  ReciprocatingExecutionResponse,
} from "../features/projects/reciprocatingTypes";

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

  if (!accessToken) {
    throw new Error("Authenticated access token is required.");
  }

  if (!hasValidProjectId) {
    throw new Error("Valid project ID is required.");
  }

  const calculationMutation = useMutation({
    mutationFn: () =>
      executeReciprocatingCalculation(
        accessToken,
        {
          calculation: {
            required_flow_m3_per_hr: Number(requiredFlow),

            bore_mm: Number(bore),
            stroke_mm: Number(stroke),
            rod_diameter_mm: Number(rodDiameter),
            speed_rpm: Number(speedRpm),
            clearance_fraction: Number(clearanceFraction),

            stage_compression_ratio: Number(stageCompressionRatio),

            suction_z_factor: Number(suctionZ),
            discharge_z_factor: Number(dischargeZ),
            isentropic_exponent: Number(isentropicExponent),

            suction_pressure_bar: Number(suctionPressure),
            discharge_pressure_bar: Number(dischargePressure),

            allowable_rod_load_kn: Number(allowableRodLoad),
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

  return (
    <main>
      <h1>Reciprocating Compressor Engineering</h1>

      <p>
        {project
          ? `${project.project_code} · ${project.project_name} · ${project.status}`
          : projectQuery.isPending
            ? "Loading project..."
            : `Project ${projectId}`}
      </p>

      <p>
        Evaluate reciprocating compressor displacement, capacity,
        volumetric efficiency, and rod-load suitability.
      </p>

      <form onSubmit={handleSubmit}>
        <fieldset>
          <legend>Capacity and Cylinder Geometry</legend>

          <div>
            <label htmlFor="required-flow">
              Required Flow (m³/hr)
            </label>
            <input
              id="required-flow"
              type="number"
              min="0.01"
              step="any"
              required
              value={requiredFlow}
              onChange={(event) =>
                setRequiredFlow(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="bore">
              Bore (mm)
            </label>
            <input
              id="bore"
              type="number"
              min="0.01"
              step="any"
              required
              value={bore}
              onChange={(event) =>
                setBore(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="stroke">
              Stroke (mm)
            </label>
            <input
              id="stroke"
              type="number"
              min="0.01"
              step="any"
              required
              value={stroke}
              onChange={(event) =>
                setStroke(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="rod-diameter">
              Rod Diameter (mm)
            </label>
            <input
              id="rod-diameter"
              type="number"
              min="0"
              step="any"
              required
              value={rodDiameter}
              onChange={(event) =>
                setRodDiameter(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="speed">
              Speed (rpm)
            </label>
            <input
              id="speed"
              type="number"
              min="0.01"
              step="any"
              required
              value={speedRpm}
              onChange={(event) =>
                setSpeedRpm(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="clearance">
              Clearance Fraction
            </label>
            <input
              id="clearance"
              type="number"
              min="0"
              max="0.999"
              step="any"
              required
              value={clearanceFraction}
              onChange={(event) =>
                setClearanceFraction(event.target.value)
              }
            />
          </div>
        </fieldset>

        <fieldset>
          <legend>Compression Conditions</legend>

          <div>
            <label htmlFor="stage-ratio">
              Stage Compression Ratio
            </label>
            <input
              id="stage-ratio"
              type="number"
              min="1.0001"
              step="any"
              required
              value={stageCompressionRatio}
              onChange={(event) =>
                setStageCompressionRatio(event.target.value)
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
            <label htmlFor="rod-load">
              Allowable Rod Load (kN)
            </label>
            <input
              id="rod-load"
              type="number"
              min="0.01"
              step="any"
              required
              value={allowableRodLoad}
              onChange={(event) =>
                setAllowableRodLoad(event.target.value)
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
            : "Run Reciprocating Calculation"}
        </button>
      </form>

      {calculationMutation.isError && (
        <section>
          <h2>Calculation Error</h2>
          <p>
            Reciprocating compressor calculation could not be completed.
          </p>
        </section>
      )}

      {result && (
        <section>
          <h2>Reciprocating Result</h2>

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
