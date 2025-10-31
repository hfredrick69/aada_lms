import { createContext, useCallback, useContext, useMemo, useState } from "react";
import { me, login as loginRequest } from "../api/auth.js";
import { setAuthToken } from "../api/axiosClient.js";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const reset = useCallback(() => {
    setToken(null);
    setUser(null);
    setError(null);
    setAuthToken(null);
  }, []);

  const login = useCallback(async (credentials) => {
    setLoading(true);
    setError(null);
    try {
      const { access_token } = await loginRequest(credentials);
      setToken(access_token);
      setAuthToken(access_token);
      const profile = await me(access_token);
      const normalizedRoles = Array.isArray(profile?.roles)
        ? profile.roles
        : profile?.role
        ? [profile.role]
        : [];
      const normalizedProfile = {
        ...profile,
        roles: normalizedRoles
      };
      setUser(normalizedProfile);
      return normalizedProfile;
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "Unable to sign in");
      reset();
      throw err;
    } finally {
      setLoading(false);
    }
  }, [reset]);

  const logout = useCallback(() => {
    reset();
  }, [reset]);

  const hasRole = useCallback(
    (roles) => {
      if (!user?.roles?.length) return false;
      const list = Array.isArray(roles) ? roles : [roles];
      return user.roles.some((role) => list.includes(role));
    },
    [user]
  );

  const value = useMemo(
    () => ({
      token,
      user,
      loading,
      error,
      login,
      logout,
      hasRole,
      setError
    }),
    [token, user, loading, error, login, logout, hasRole, setError]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
