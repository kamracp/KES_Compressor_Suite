import type { PropsWithChildren } from "react";

import { NavLink } from "react-router";

import { useAuth } from "../features/auth/AuthProvider";

export function AppLayout({
  children,
}: PropsWithChildren) {
  const {
    currentUser,
    logout,
  } = useAuth();

  return (
    <div>
      <aside>
        <h2>KES Compressor Suite</h2>

        <nav>
          <ul>
            <li>
              <NavLink to="/">
                Dashboard
              </NavLink>
            </li>

            <li>
              <NavLink to="/projects">
                Projects
              </NavLink>
            </li>

            <li>
              <NavLink to="/assessments">
                Assessments
              </NavLink>
            </li>

            <li>
              <NavLink to="/reports">
                Reports
              </NavLink>
            </li>
          </ul>
        </nav>

        <section>
          <p>
            {currentUser?.full_name}
          </p>

          <p>
            Org: {currentUser?.organization_id}
          </p>

          <button
            type="button"
            onClick={logout}
          >
            Sign out
          </button>
        </section>
      </aside>

      <section>
        {children}
      </section>
    </div>
  );
}
