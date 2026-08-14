import { apiRequest } from "../../services/apiClient";
import type { CalculationCase } from "./calculationCaseTypes";

export function listCalculationCases(
  accessToken: string,
): Promise<CalculationCase[]> {
  return apiRequest<CalculationCase[]>(
    "/calculation-cases",
    {
      accessToken,
    },
  );
}

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
