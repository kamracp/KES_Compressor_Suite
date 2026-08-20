import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type PropsWithChildren,
} from "react";

import {
  clearAccessToken,
  getAccessToken,
  setAccessToken,
} from "./authStorage";
import {
  getCurrentUser,
  login as loginRequest,
} from "./authService";
import type {
  CurrentUserResponse,
  LoginRequest,
} from "../../types/auth";
import { AUTH_UNAUTHORIZED_EVENT } from "../../services/apiClient";

type AuthContextValue = {
  accessToken: string | null;
  currentUser: CurrentUserResponse | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (payload: LoginRequest) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({
  children,
}: PropsWithChildren) {
  const [accessToken, setTokenState] = useState<string | null>(
    getAccessToken(),
  );
  const [currentUser, setCurrentUser] =
    useState<CurrentUserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    function handleUnauthorized(): void {
      clearAccessToken();
      setTokenState(null);
      setCurrentUser(null);
    }

    window.addEventListener(
      AUTH_UNAUTHORIZED_EVENT,
      handleUnauthorized,
    );

    return () => {
      window.removeEventListener(
        AUTH_UNAUTHORIZED_EVENT,
        handleUnauthorized,
      );
    };
  }, []);

  useEffect(() => {
    async function restoreSession(): Promise<void> {
      if (!accessToken) {
        setIsLoading(false);
        return;
      }

      try {
        const user = await getCurrentUser(accessToken);
        setCurrentUser(user);
      } catch {
        clearAccessToken();
        setTokenState(null);
        setCurrentUser(null);
      } finally {
        setIsLoading(false);
      }
    }

    void restoreSession();
  }, [accessToken]);

  async function login(payload: LoginRequest): Promise<void> {
    const token = await loginRequest(payload);

    setAccessToken(token.access_token);
    setTokenState(token.access_token);

    const user = await getCurrentUser(token.access_token);
    setCurrentUser(user);
  }

  function logout(): void {
    clearAccessToken();
    setTokenState(null);
    setCurrentUser(null);
  }

  const value = useMemo<AuthContextValue>(
    () => ({
      accessToken,
      currentUser,
      isAuthenticated: Boolean(accessToken && currentUser),
      isLoading,
      login,
      logout,
    }),
    [accessToken, currentUser, isLoading],
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within AuthProvider.");
  }

  return context;
}
