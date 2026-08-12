import {
  useState,
  type FormEvent,
} from "react";

import { Link } from "react-router";

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import { useAuth } from "../features/auth/AuthProvider";
import {
  createProject,
  listProjects,
} from "../features/projects/projectService";

export function ProjectsPage() {
  const queryClient = useQueryClient();

  const {
    accessToken,
  } = useAuth();

  const [projectCode, setProjectCode] = useState("");
  const [projectName, setProjectName] = useState("");
  const [clientName, setClientName] = useState("");

  if (!accessToken) {
    throw new Error("Authenticated access token is required.");
  }

  const projectsQuery = useQuery({
    queryKey: ["projects"],
    queryFn: () => listProjects(accessToken),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      createProject(
        accessToken,
        {
          project_code: projectCode,
          project_name: projectName,
          client_name: clientName || null,
          status: "DRAFT",
        },
      ),
    onSuccess: async () => {
      setProjectCode("");
      setProjectName("");
      setClientName("");

      await queryClient.invalidateQueries({
        queryKey: ["projects"],
      });
    },
  });

  function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ): void {
    event.preventDefault();
    createMutation.mutate();
  }

  return (
    <main>
      <h1>Projects</h1>

      <p>
        Manage compressor engineering projects for your organization.
      </p>

      <section>
        <h2>New Project</h2>

        <form onSubmit={handleSubmit}>
          <div>
            <label htmlFor="project-code">
              Project Code
            </label>

            <input
              id="project-code"
              required
              value={projectCode}
              onChange={(event) =>
                setProjectCode(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="project-name">
              Project Name
            </label>

            <input
              id="project-name"
              required
              value={projectName}
              onChange={(event) =>
                setProjectName(event.target.value)
              }
            />
          </div>

          <div>
            <label htmlFor="client-name">
              Client Name
            </label>

            <input
              id="client-name"
              value={clientName}
              onChange={(event) =>
                setClientName(event.target.value)
              }
            />
          </div>

          <button
            type="submit"
            disabled={createMutation.isPending}
          >
            {createMutation.isPending
              ? "Creating..."
              : "Create Project"}
          </button>

          {createMutation.isError && (
            <p>Project creation failed.</p>
          )}
        </form>
      </section>

      <section>
        <h2>Project List</h2>

        {projectsQuery.isPending && (
          <p>Loading projects...</p>
        )}

        {projectsQuery.isError && (
          <p>Unable to load projects.</p>
        )}

        {projectsQuery.data?.length === 0 && (
          <p>No projects found.</p>
        )}

        {projectsQuery.data && projectsQuery.data.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>Code</th>
                <th>Project</th>
                <th>Client</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {projectsQuery.data.map((project) => (
                <tr key={project.id}>
                  <td>{project.project_code}</td>
                  <td>
                    <Link to={`/projects/${project.id}`}>
                      {project.project_name}
                    </Link>
                  </td>
                  <td>{project.client_name ?? "-"}</td>
                  <td>{project.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </main>
  );
}
