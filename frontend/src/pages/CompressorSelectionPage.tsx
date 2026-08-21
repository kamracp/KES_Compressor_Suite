import {
  useState,
  type FormEvent,
} from "react";

import { useMutation } from "@tanstack/react-query";

import { useAuth } from "../features/auth/AuthProvider";
import { useProjectContext } from "../features/projects/useProjectContext";
import {
  executeCompressorSelection,
} from "../features/projects/selectionService";
import type {
  CompressorSelectionExecutionResponse,
} from "../features/projects/selectionTypes";

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

  if (!accessToken) {
    throw new Error("Authenticated access token is required.");
  }

  if (!hasValidProjectId) {
    throw new Error("Valid project ID is required.");
  }

  const selectionMutation = useMutation({
    mutationFn: () =>
      executeCompressorSelection(
        accessToken,
        {
          calculation: {
            required_flow_m3_per_hr: Number(requiredFlow),
            suction_pressure_bar: Number(suctionPressure),
            discharge_pressure_bar: Number(dischargePressure),
            required_turndown_fraction: Number(turndown),
            continuous_operation: continuousOperation,
            gas_molecular_weight: Number(molecularWeight),
            estimated_operating_hours_per_year:
              Number(operatingHours),
          },
          execution: {
            persist_result: persistResult,
            project_id:
              persistResult
                ? projectId
                : null,
            calculation_code:
              persistResult ? calculationCode : null,
            title:
              persistResult ? title : null,
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
    selectionMutation.mutate();
  }

  return (
    <main>
      <h1>Compressor Type Selection</h1>

      <p>
        {project
          ? `${project.project_code} · ${project.project_name} · ${project.status}`
          : projectQuery.isPending
            ? "Loading project..."
            : `Project ${projectId}`}
      </p>

      <p>
        Compare reciprocating and centrifugal compressor suitability.
      </p>

      <form onSubmit={handleSubmit}>
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
          <label htmlFor="suction-pressure">
            Suction Pressure (bar)
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
            Discharge Pressure (bar)
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
          <label htmlFor="turndown">
            Required Turndown Fraction
          </label>
          <input
            id="turndown"
            type="number"
            min="0.01"
            max="1"
            step="any"
            required
            value={turndown}
            onChange={(event) =>
              setTurndown(event.target.value)
            }
          />
        </div>

        <div>
          <label htmlFor="molecular-weight">
            Gas Molecular Weight
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
          <label htmlFor="operating-hours">
            Annual Operating Hours
          </label>
          <input
            id="operating-hours"
            type="number"
            min="0"
            step="any"
            required
            value={operatingHours}
            onChange={(event) =>
              setOperatingHours(event.target.value)
            }
          />
        </div>

        <div>
          <label>
            <input
              type="checkbox"
              checked={continuousOperation}
              onChange={(event) =>
                setContinuousOperation(event.target.checked)
              }
            />
            Continuous Operation
          </label>
        </div>

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
          disabled={selectionMutation.isPending}
        >
          {selectionMutation.isPending
            ? "Calculating..."
            : "Run Selection"}
        </button>
      </form>

      {selectionMutation.isError && (
        <section>
          <h2>Calculation Error</h2>
          <p>
            Compressor selection could not be completed.
          </p>
        </section>
      )}

      {result && (
        <section>
          <h2>Selection Result</h2>

          <p>
            Recommended Type:
            {" "}
            <strong>{result.result.recommended_type}</strong>
          </p>

          <p>
            Reciprocating Score:
            {" "}
            {result.result.reciprocating.overall_score}
          </p>

          <p>
            Centrifugal Score:
            {" "}
            {result.result.centrifugal.overall_score}
          </p>

          <p>
            Score Difference:
            {" "}
            {result.result.score_difference}
          </p>

          <p>
            {result.result.recommendation_summary}
          </p>

          <h3>Reciprocating Rationale</h3>
          <ul>
            {result.result.reciprocating.rationale.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>

          <h3>Centrifugal Rationale</h3>
          <ul>
            {result.result.centrifugal.rationale.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>

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
