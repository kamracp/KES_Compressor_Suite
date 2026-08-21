import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router";

import { useAuth } from "../features/auth/AuthProvider";
import { useProjectContext } from "../features/projects/useProjectContext";
import { getCalculationCase } from "../features/projects/calculationCaseService";

export function CalculationDetailPage() {
  const { calculationCaseId } = useParams();
  const { accessToken } = useAuth();
  const {
    projectId,
    hasValidProjectId,
    project,
    projectQuery,
  } = useProjectContext();

  if (!accessToken) {
    throw new Error("Authenticated access token is required.");
  }

  const numericCalculationCaseId = Number(calculationCaseId);

  if (
    !hasValidProjectId ||
    !Number.isInteger(numericCalculationCaseId) ||
    numericCalculationCaseId <= 0
  ) {
    throw new Error(
      "Valid project ID and calculation case ID are required.",
    );
  }

  const calculationQuery = useQuery({
    queryKey: [
      "projects",
      projectId,
      "calculation-case",
      numericCalculationCaseId,
    ],
    queryFn: () =>
      getCalculationCase(
        accessToken,
        numericCalculationCaseId,
      ),
  });

  if (calculationQuery.isPending) {
    return <p>Loading calculation...</p>;
  }

  if (calculationQuery.isError) {
    return <p>Unable to load calculation.</p>;
  }

  const calculation = calculationQuery.data;

  if (calculation.project_id !== projectId) {
    return (
      <main>
        <h1>Calculation Project Mismatch</h1>
        <p>
          This calculation does not belong to the requested project.
        </p>
        <p>
          <Link to={`/projects/${projectId}/calculations`}>
            Return to Calculation History
          </Link>
        </p>
      </main>
    );
  }

  return (
    <main>
      <p>
        <Link to={`/projects/${projectId}/calculations`}>
          Back to Calculation History
        </Link>
      </p>

      <h1>{calculation.title}</h1>

      <p>
        {project
          ? `${project.project_code} · ${project.project_name} · ${project.status}`
          : projectQuery.isPending
            ? "Loading project..."
            : `Project ${projectId}`}
      </p>

      <dl>
        <dt>Calculation Code</dt>
        <dd>{calculation.calculation_code}</dd>

        <dt>Type</dt>
        <dd>{calculation.calculation_type}</dd>

        <dt>Status</dt>
        <dd>{calculation.status}</dd>

        <dt>Revision</dt>
        <dd>{calculation.revision}</dd>

        <dt>Created</dt>
        <dd>
          {new Date(calculation.created_at).toLocaleString()}
        </dd>

        <dt>Completed</dt>
        <dd>
          {calculation.completed_at
            ? new Date(calculation.completed_at).toLocaleString()
            : "-"}
        </dd>
      </dl>

      <section>
        <h2>Engineering Notes</h2>

        <p>
          {calculation.engineering_notes ?? "No engineering notes."}
        </p>
      </section>

      <section>
        <h2>Input Data</h2>

        <pre>
          {JSON.stringify(calculation.input_data, null, 2)}
        </pre>
      </section>

      <section>
        <h2>Result Data</h2>

        {calculation.result_data ? (
          <pre>
            {JSON.stringify(calculation.result_data, null, 2)}
          </pre>
        ) : (
          <p>No result data available.</p>
        )}
      </section>
    </main>
  );
}
