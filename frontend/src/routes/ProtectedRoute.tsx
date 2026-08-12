import type { PropsWithChildren } from "react";

import { Navigate } from "react-router";

import { useAuth } from "../features/auth/AuthProvider";

export function ProtectedRoute({
  children,
}: PropsWithChildren) {
  const {
    isAuthenticated,
    isLoading,
  } = useAuth();

  if (isLoading) {
    return <p>Loading session...</p>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
