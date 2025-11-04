import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { AuthUser } from '@/api/generated/models';

interface AuthState {
  accessToken: string | null;
  user: AuthUser | null;
  isAuthenticated: boolean;
  setToken: (token: string | null) => void;
  setUser: (user: AuthUser | null) => void;
  clearSession: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      user: null,
      isAuthenticated: false,

      setToken: (token) =>
        set({
          accessToken: token,
          isAuthenticated: !!token,
        }),

      setUser: (user) => set({ user }),

      clearSession: () =>
        set({
          accessToken: null,
          user: null,
          isAuthenticated: false,
        }),
    }),
    {
      name: 'aada-auth',
      storage: createJSONStorage(() => localStorage),
    }
  )
);
