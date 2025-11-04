import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

export type ThemeMode = 'light' | 'dark';

interface ThemeState {
  mode: ThemeMode;
  toggle: () => void;
  setMode: (mode: ThemeMode) => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      mode: 'light',
      toggle: () => {
        const next = get().mode === 'light' ? 'dark' : 'light';
        set({ mode: next });
      },
      setMode: (mode) => set({ mode }),
    }),
    {
      name: 'aada-theme',
      storage: typeof window === 'undefined'
        ? undefined
        : createJSONStorage(() => window.localStorage),
      partialize: ({ mode }) => ({ mode }),
    },
  ),
);
