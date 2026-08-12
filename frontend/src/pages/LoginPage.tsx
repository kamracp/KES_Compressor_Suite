import {
  useState,
  type FormEvent,
} from "react";

import { Navigate, useNavigate } from "react-router";

import { useAuth } from "../features/auth/AuthProvider";

export function LoginPage() {
  const navigate = useNavigate();

  const {
    isAuthenticated,
    login,
  } = useAuth();

  const [organizationId, setOrganizationId] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(
    null,
  );

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ): Promise<void> {
    event.preventDefault();

    const parsedOrganizationId = Number(organizationId);

    if (!Number.isInteger(parsedOrganizationId)) {
      setErrorMessage("Organization ID must be a valid integer.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      await login({
        organization_id: parsedOrganizationId,
        email,
        password,
      });

      navigate("/", {
        replace: true,
      });
    } catch {
      setErrorMessage(
        "Login failed. Check organization ID, email, and password.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main>
      <h1>KES Compressor Engineering Suite</h1>

      <h2>Sign in</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="organization-id">
            Organization ID
          </label>

          <input
            id="organization-id"
            type="number"
            min="1"
            required
            value={organizationId}
            onChange={(event) =>
              setOrganizationId(event.target.value)
            }
          />
        </div>

        <div>
          <label htmlFor="email">
            Email
          </label>

          <input
            id="email"
            type="email"
            required
            value={email}
            onChange={(event) =>
              setEmail(event.target.value)
            }
          />
        </div>

        <div>
          <label htmlFor="password">
            Password
          </label>

          <input
            id="password"
            type="password"
            required
            value={password}
            onChange={(event) =>
              setPassword(event.target.value)
            }
          />
        </div>

        {errorMessage && (
          <p>{errorMessage}</p>
        )}

        <button
          type="submit"
          disabled={isSubmitting}
        >
          {isSubmitting ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </main>
  );
}
