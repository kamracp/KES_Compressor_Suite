import { NavLink, useParams } from "react-router";

export function ProjectWorkspacePage() {
  const { projectId } = useParams();

  return (
    <main>
      <h1>Project Engineering Workspace</h1>

      <p>
        Project ID: {projectId}
      </p>

      <nav>
        <ul>
          <li>
            <NavLink to={`/projects/${projectId}`}>
              Overview
            </NavLink>
          </li>

          <li>
            <NavLink to={`/projects/${projectId}/compressor`}>
              Compressor Engineering
            </NavLink>
          </li>

          <li>
            <NavLink to={`/projects/${projectId}/compressed-air`}>
              Compressed Air System
            </NavLink>
          </li>

          <li>
            <NavLink to={`/projects/${projectId}/calculations`}>
              Calculation History
            </NavLink>
          </li>

          <li>
            <NavLink to={`/projects/${projectId}/assessments`}>
              Assessments
            </NavLink>
          </li>

          <li>
            <NavLink to={`/projects/${projectId}/reports`}>
              Reports
            </NavLink>
          </li>
        </ul>
      </nav>

      <section>
        <h2>Overview</h2>

        <p>
          Engineering calculations, assessments, reports, and project history
          will be managed from this workspace.
        </p>
      </section>
    </main>
  );
}
