import { NavLink, useParams } from "react-router";

export function CompressorEngineeringPage() {
  const { projectId } = useParams();

  return (
    <main>
      <h1>Compressor Engineering</h1>

      <p>
        Project ID: {projectId}
      </p>

      <nav>
        <ul>
          <li>
            <NavLink to={`/projects/${projectId}/compressor/gas`}>
              Gas Properties
            </NavLink>
          </li>

          <li>
            <NavLink to={`/projects/${projectId}/compressor/compression`}>
              Compression
            </NavLink>
          </li>

          <li>
            <NavLink to={`/projects/${projectId}/compressor/reciprocating`}>
              Reciprocating
            </NavLink>
          </li>

          <li>
            <NavLink to={`/projects/${projectId}/compressor/centrifugal`}>
              Centrifugal
            </NavLink>
          </li>

          <li>
            <NavLink to={`/projects/${projectId}/compressor/selection`}>
              Compressor Selection
            </NavLink>
          </li>
        </ul>
      </nav>

      <section>
        <h2>Engineering Workbench</h2>

        <p>
          Select a compressor engineering calculation module.
        </p>
      </section>
    </main>
  );
}
