import { useQuery } from "@tanstack/react-query";

import { useAuth } from "../features/auth/AuthProvider";
import { getHealth } from "../services/healthService";

export function DashboardPage() {
  const {
    currentUser,
    logout,
  } = useAuth();

  const healthQuery = useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
  });

  return (
    <main>
      <h1>KES Compressor Engineering Suite</h1>

      <p>
        Enterprise compressor and compressed-air engineering platform.
      </p>

      <section>
        <h2>User</h2>

        <p>
          Name: {currentUser?.full_name}
        </p>

        <p>
          Email: {currentUser?.email}
        </p>

        <p>
          Organization ID: {currentUser?.organization_id}
        </p>

        <button
          type="button"
          onClick={logout}
        >
          Sign out
        </button>
      </section>

      <section>
        <h2>Backend Status</h2>

        {healthQuery.isPending && (
          <p>Checking backend connection...</p>
        )}

        {healthQuery.isError && (
          <p>Backend connection failed.</p>
        )}

        {healthQuery.data && (
          <>
            <p>
              Status: {healthQuery.data.status}
            </p>

            <p>
              Service: {healthQuery.data.service}
            </p>
          </>
        )}
      </section>
    </main>
  );
}
