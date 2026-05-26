import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useNavigate } from "react-router-dom";
import { queryClient } from "@/lib/query";
import { apiKeysApi, authApi } from "@/lib/api";
import {
  API_KEY,
  AUTH_EVENT,
  TOKEN_KEY,
  clearSessionStorage,
  getApiKey,
  getToken,
  setApiKey,
  setToken,
} from "@/lib/storage";
import type { AuthResponse, CurrentUser } from "@/types/api";

interface AuthContextValue {
  user: CurrentUser | null;
  token: string | null;
  apiKey: string | null;
  hasApiKey: boolean;
  isAuthenticated: boolean;
  isBootstrapping: boolean;
  login: (payload: { email: string; password: string }) => Promise<void>;
  signup: (payload: {
    email: string;
    password: string;
    full_name: string;
    tenant_id: string;
  }) => Promise<void>;
  logout: () => void;
  validateApiKey: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const MASKED_KEY_PLACEHOLDER = "Use existing key securely stored";

function persistAuth(response: AuthResponse) {
  setToken(response.access_token);

  if (response.api_key && response.api_key !== MASKED_KEY_PLACEHOLDER) {
    setApiKey(response.api_key);
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [token, setTokenState] = useState<string | null>(() => getToken());
  const [apiKey, setApiKeyState] = useState<string | null>(() => getApiKey());
  const [isBootstrapping, setIsBootstrapping] = useState(true);

  const syncFromStorage = useCallback(() => {
    setTokenState(localStorage.getItem(TOKEN_KEY));
    setApiKeyState(localStorage.getItem(API_KEY));
  }, []);

  const logout = useCallback(() => {
    clearSessionStorage();
    queryClient.clear();
    setUser(null);
    syncFromStorage();
    navigate("/login", { replace: true });
  }, [navigate, syncFromStorage]);

  useEffect(() => {
    const handleLogout = () => logout();
    window.addEventListener(AUTH_EVENT, handleLogout);
    return () => window.removeEventListener(AUTH_EVENT, handleLogout);
  }, [logout]);

  useEffect(() => {
    const bootstrap = async () => {
      const currentToken = getToken();
      if (!currentToken) {
        setIsBootstrapping(false);
        return;
      }

      try {
        const currentUser = await authApi.me();
        setUser(currentUser);
        syncFromStorage();
      } catch {
        clearSessionStorage();
        setUser(null);
      } finally {
        setIsBootstrapping(false);
      }
    };

    void bootstrap();
  }, [syncFromStorage]);

  const login = useCallback(
    async (payload: { email: string; password: string }) => {
      const response = await authApi.login(payload);
      persistAuth(response);
      syncFromStorage();
      setUser({
        user_id: response.user_id,
        email: response.email,
        full_name: response.full_name,
        role: response.role,
        tenant_id: response.tenant_id,
        is_active: true,
      });
      navigate("/", { replace: true });
    },
    [navigate, syncFromStorage],
  );

  const signup = useCallback(
    async (payload: {
      email: string;
      password: string;
      full_name: string;
      tenant_id: string;
    }) => {
      const response = await authApi.signup(payload);
      persistAuth(response);
      syncFromStorage();
      setUser({
        user_id: response.user_id,
        email: response.email,
        full_name: response.full_name,
        role: response.role,
        tenant_id: response.tenant_id,
        is_active: true,
      });
      navigate("/", { replace: true });
    },
    [navigate, syncFromStorage],
  );

  const validateApiKey = useCallback(async () => {
    try {
      const result = await apiKeysApi.validate();
      return result.valid;
    } catch {
      return false;
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      apiKey,
      hasApiKey: Boolean(apiKey),
      isAuthenticated: Boolean(token),
      isBootstrapping,
      login,
      signup,
      logout,
      validateApiKey,
    }),
    [apiKey, isBootstrapping, login, logout, signup, token, user, validateApiKey],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }

  return context;
}
