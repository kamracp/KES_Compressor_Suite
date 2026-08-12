import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router";

import { useAuth } from "../features/auth/AuthProvider";
import { getCalculationCase } from "../features/projects/calculationCaseService";

export function CalculationDetailPage() {
  const { projectId, calculationCaseId } = useParams();
  const { accessToken } = useAuth();

  if (!accessToken) {
    throw new Error("Authenticated access token is required.");
  }

  if (!projectId || !calculationCaseId) {
    throw new Error("Project ID and calculation case ID are required.");
  }

  const numericProjectId = Number(projectId);
  const numericCalculationCaseId = Number(calculationCaseId);

  const calculationQuery = useQuery({
    queryKey: [
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

  return (
    <main>
      <p>
        <Link to={`/projects/${numericProjectId}/calculations`}>
          Back to Calculation History
        </Link>
      </p>

      <h1>{calculation.title}</h1>

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
