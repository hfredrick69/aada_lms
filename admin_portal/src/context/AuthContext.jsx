import { createContext, useCallback, useContext, useMemo, useState } from "react";
import { me, login as loginRequest } from "../api/auth.js";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const reset = useCallback(() => {
    setUser(null);
    setError(null);
  }, []);

  const login = useCallback(async (credentials) => {
    setLoading(true);
    setError(null);
    try {
      // Phase 4: Tokens stored in httpOnly cookies by backend
      await loginRequest(credentials);
      // Fetch user profile (cookies sent automatically via withCredentials)
      const profile = await me();
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
      user,
      loading,
      error,
      login,
      logout,
      hasRole,
      setError
    }),
    [user, loading, error, login, logout, hasRole, setError]
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
