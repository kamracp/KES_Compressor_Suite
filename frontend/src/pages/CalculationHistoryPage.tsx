import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router";

import { useAuth } from "../features/auth/AuthProvider";
import { useProjectContext } from "../features/projects/useProjectContext";
import {
  listProjectCalculationCases,
} from "../features/projects/calculationCaseService";

export function CalculationHistoryPage() {
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

  if (!hasValidProjectId) {
    throw new Error("Valid project ID is required.");
  }

  const calculationCasesQuery = useQuery({
    queryKey: [
      "projects",
      projectId,
      "calculation-cases",
    ],
    queryFn: () =>
      listProjectCalculationCases(
        accessToken,
        projectId,
      ),
  });

  return (
    <main>
      <h1>Calculation History</h1>

      <p>
        {project
          ? `${project.project_code} · ${project.project_name} · ${project.status}`
          : projectQuery.isPending
            ? "Loading project..."
            : `Project ${projectId}`}
      </p>

      <p>
        Review saved compressor engineering calculations
        and reopen their stored inputs and results.
      </p>

      {calculationCasesQuery.isPending && (
        <p>Loading calculation history...</p>
      )}

      {calculationCasesQuery.isError && (
        <p>
          Calculation history could not be loaded.
        </p>
      )}

      {calculationCasesQuery.data?.length === 0 && (
        <p>
          No saved calculations are available for this project.
        </p>
      )}

      {calculationCasesQuery.data &&
        calculationCasesQuery.data.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>Code</th>
                <th>Type</th>
                <th>Title</th>
                <th>Revision</th>
                <th>Status</th>
                <th>Created</th>
                <th>Completed</th>
                <th>Open</th>
              </tr>
            </thead>

            <tbody>
              {calculationCasesQuery.data.map(
                (calculationCase) => (
                  <tr key={calculationCase.id}>
                    <td>
                      {calculationCase.calculation_code}
                    </td>

                    <td>
                      {calculationCase.calculation_type}
                    </td>

                    <td>
                      {calculationCase.title}
                    </td>

                    <td>
                      {calculationCase.revision}
                    </td>

                    <td>
                      {calculationCase.status}
                    </td>

                    <td>
                      {new Date(
                        calculationCase.created_at,
                      ).toLocaleString()}
                    </td>

                    <td>
                      {calculationCase.completed_at
                        ? new Date(
                            calculationCase.completed_at,
                          ).toLocaleString()
                        : "-"}
                    </td>

                    <td>
                      <Link
                        to={
                          `/projects/${projectId}` +
                          `/calculations/${calculationCase.id}`
                        }
                      >
                        Open
                      </Link>
                    </td>
                  </tr>
                ),
              )}
            </tbody>
          </table>
        )}
    </main>
  );
}
