import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router";

import { useAuth } from "../features/auth/AuthProvider";
import {
  listProjectCalculationCases,
} from "../features/projects/calculationCaseService";

export function CalculationHistoryPage() {
  const { projectId } = useParams();
  const { accessToken } = useAuth();

  if (!accessToken) {
    throw new Error("Authenticated access token is required.");
  }

  if (!projectId) {
    throw new Error("Project ID is required.");
  }

  const numericProjectId = Number(projectId);

  const calculationCasesQuery = useQuery({
    queryKey: [
      "projects",
      numericProjectId,
      "calculation-cases",
    ],
    queryFn: () =>
      listProjectCalculationCases(
        accessToken,
        numericProjectId,
      ),
  });

  return (
    <main>
      <h1>Calculation History</h1>

      <p>
        Project ID: {numericProjectId}
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
                          `/projects/${numericProjectId}` +
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
