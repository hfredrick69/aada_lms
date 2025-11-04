import { useEffect, useMemo } from 'react';
import type { ReactNode } from 'react';
import { BrowserRouter } from 'react-router-dom';
import {
  CssBaseline,
  ThemeProvider,
  createTheme,
  responsiveFontSizes,
} from '@mui/material';
import {
  QueryClient,
  QueryClientProvider,
} from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useThemeStore } from '@/stores/theme-store';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 0,
    },
  },
});

const useTheme = () => {
  const mode = useThemeStore((state) => state.mode);

  useEffect(() => {
    if (typeof document === 'undefined') return;
    const root = document.documentElement;
    if (mode === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [mode]);

  return useMemo(() => {
    let theme = createTheme({
      palette: {
        mode,
        primary: {
          main: '#1f9eff',
        },
        secondary: {
          main: '#0666b8',
        },
        background: {
          default: mode === 'dark' ? '#0f172a' : '#f8fafc',
          paper: mode === 'dark' ? '#111827' : '#ffffff',
        },
      },
      typography: {
        fontFamily:
          "'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        h1: { fontWeight: 600 },
        h2: { fontWeight: 600 },
        h3: { fontWeight: 600 },
        h4: { fontWeight: 600 },
      },
      shape: {
        borderRadius: 12,
      },
    });

    theme = responsiveFontSizes(theme);

    return theme;
  }, [mode]);
};

const ThemeBridge = ({ children }: { children: ReactNode }) => {
  const theme = useTheme();

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
};

export const AppProviders = ({ children }: { children: ReactNode }) => (
  <QueryClientProvider client={queryClient}>
    <ThemeBridge>
      <BrowserRouter>{children}</BrowserRouter>
    </ThemeBridge>
    <ReactQueryDevtools initialIsOpen={false} />
  </QueryClientProvider>
);
