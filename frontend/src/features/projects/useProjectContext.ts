import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router";

import { useAuth } from "../auth/AuthProvider";
import { getProject } from "./projectService";

export function useProjectContext() {
  const { projectId } = useParams();
  const { accessToken } = useAuth();

  const numericProjectId = Number(projectId);
  const hasValidProjectId =
    Number.isInteger(numericProjectId) &&
    numericProjectId > 0;

  const projectQuery = useQuery({
    queryKey: ["projects", numericProjectId],
    queryFn: () => {
      if (!accessToken) {
        throw new Error(
          "Authenticated access token is required.",
        );
      }

      if (!hasValidProjectId) {
        throw new Error("Valid project ID is required.");
      }

      return getProject(
        accessToken,
        numericProjectId,
      );
    },
    enabled:
      Boolean(accessToken) &&
      hasValidProjectId,
  });

  return {
    projectId: numericProjectId,
    hasValidProjectId,
    project: projectQuery.data,
    projectQuery,
  };
}
