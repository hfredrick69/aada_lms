import { create } from 'zustand';
import type { AuthUser } from '@/api/generated/models';

interface AuthState {
  user: AuthUser | null;
  isAuthenticated: boolean;
  setUser: (user: AuthUser | null) => void;
  setAuthenticated: (authenticated: boolean) => void;
  clearSession: () => void;
}

export const useAuthStore = create<AuthState>()((set) => ({
  user: null,
  isAuthenticated: false,

  setUser: (user) =>
    set({
      user,
      isAuthenticated: !!user,
    }),

  setAuthenticated: (authenticated) =>
    set({ isAuthenticated: authenticated }),

  clearSession: () =>
    set({
      user: null,
      isAuthenticated: false,
    }),
}));
