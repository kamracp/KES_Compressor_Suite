import type {
  PropsWithChildren,
} from "react";

import {
  AlertTriangle,
  FolderSearch,
  LoaderCircle,
  RefreshCw,
  ShieldX,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { Link } from "react-router";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import { ApiError } from "../../services/apiClient";
import { useProjectContext } from "./useProjectContext";

type ProjectContextStateProps = {
  badge: string;
  description: string;
  icon: LucideIcon;
  loading?: boolean;
  onRetry?: () => void;
  retrying?: boolean;
  title: string;
};

type ProjectErrorContent = {
  badge: string;
  description: string;
  icon: LucideIcon;
  title: string;
};

function getProjectErrorContent(
  error: unknown,
): ProjectErrorContent {
  if (
    error instanceof ApiError &&
    error.status === 403
  ) {
    return {
      badge: "Access Denied",
      description:
        "Your account does not have permission to access this project.",
      icon: ShieldX,
      title: "Project Access Denied",
    };
  }

  if (
    error instanceof ApiError &&
    error.status === 404
  ) {
    return {
      badge: "Not Found",
      description:
        "The requested project does not exist or is no longer available.",
      icon: FolderSearch,
      title: "Project Not Found",
    };
  }

  return {
    badge: "Project Error",
    description:
      "The project workspace could not be loaded. Retry the request or return to the project list.",
    icon: AlertTriangle,
    title: "Unable to Load Project",
  };
}

function ProjectContextState({
  badge,
  description,
  icon: Icon,
  loading = false,
  onRetry,
  retrying = false,
  title,
}: ProjectContextStateProps) {
  return (
    <main className="flex min-h-[50vh] items-center justify-center">
      <Card
        className="w-full max-w-2xl"
        role={loading ? "status" : "alert"}
        aria-live="polite"
      >
        <CardHeader>
          <div className="mb-3 flex items-center gap-3">
            <div className="flex size-11 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
              <Icon
                className={
                  loading
                    ? "size-5 animate-spin"
                    : "size-5"
                }
                aria-hidden="true"
              />
            </div>

            <Badge variant="outline">
              {badge}
            </Badge>
          </div>

          <CardTitle className="text-2xl">
            {title}
          </CardTitle>

          <CardDescription className="max-w-xl leading-6">
            {description}
          </CardDescription>
        </CardHeader>

        {!loading && (
          <CardContent className="flex flex-wrap gap-3">
            {onRetry && (
              <Button
                type="button"
                onClick={onRetry}
                disabled={retrying}
              >
                <RefreshCw
                  className={
                    retrying
                      ? "size-4 animate-spin"
                      : "size-4"
                  }
                  aria-hidden="true"
                />
                {retrying
                  ? "Retrying..."
                  : "Retry Project"}
              </Button>
            )}

            <Button
              asChild
              variant="outline"
            >
              <Link to="/projects">
                Return to Projects
              </Link>
            </Button>
          </CardContent>
        )}
      </Card>
    </main>
  );
}

export function ProjectContextRoute({
  children,
}: PropsWithChildren) {
  const {
    hasValidProjectId,
    project,
    projectQuery,
  } = useProjectContext();

  if (!hasValidProjectId) {
    return (
      <ProjectContextState
        badge="Invalid Project"
        description="The project address must contain a valid positive numeric project ID."
        icon={FolderSearch}
        title="Invalid Project Address"
      />
    );
  }

  if (projectQuery.isPending) {
    return (
      <ProjectContextState
        badge="Project Workspace"
        description="Retrieving the authenticated project context."
        icon={LoaderCircle}
        loading
        title="Loading Project Workspace"
      />
    );
  }

  if (projectQuery.isError) {
    const errorContent = getProjectErrorContent(
      projectQuery.error,
    );

    return (
      <ProjectContextState
        {...errorContent}
        onRetry={() => {
          void projectQuery.refetch();
        }}
        retrying={projectQuery.isFetching}
      />
    );
  }

  if (!project) {
    return (
      <ProjectContextState
        badge="Project Unavailable"
        description="The project response did not include an accessible project record."
        icon={AlertTriangle}
        title="Project Unavailable"
      />
    );
  }

  return children;
}