import { apiRequest } from "../../services/apiClient";
import type {
  Project,
  ProjectCreateRequest,
} from "../../types/project";

export function listProjects(
  accessToken: string,
): Promise<Project[]> {
  return apiRequest<Project[]>(
    "/projects",
    {
      accessToken,
    },
  );
}

export function getProject(
  accessToken: string,
  projectId: number,
): Promise<Project> {
  return apiRequest<Project>(
    `/projects/${projectId}`,
    {
      accessToken,
    },
  );
}

export function createProject(
  accessToken: string,
  payload: ProjectCreateRequest,
): Promise<Project> {
  return apiRequest<Project>(
    "/projects",
    {
      method: "POST",
      accessToken,
      body: JSON.stringify(payload),
    },
  );
}
