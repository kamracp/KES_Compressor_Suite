import { apiRequest } from "../../services/apiClient";
import type { CalculationCase } from "./calculationCaseTypes";

export function listProjectCalculationCases(
  accessToken: string,
  projectId: number,
): Promise<CalculationCase[]> {
  return apiRequest<CalculationCase[]>(
    `/calculation-cases/project/${projectId}`,
    {
      accessToken,
    },
  );
}

export function getCalculationCase(
  accessToken: string,
  calculationCaseId: number,
): Promise<CalculationCase> {
  return apiRequest<CalculationCase>(
    `/calculation-cases/${calculationCaseId}`,
    {
      accessToken,
    },
  );
}
