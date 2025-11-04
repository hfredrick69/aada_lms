import type { ReactNode } from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import LoginPage from './LoginPage';
import { useAuthStore } from '@/stores/auth-store';

const mutateMock = vi.fn();
const optionsSpy = vi.fn();

vi.mock('@/api/hooks', () => ({
  useLoginMutation: (options?: unknown) => {
    optionsSpy(options);
    return {
      mutate: mutateMock,
      isPending: false,
      error: null,
    };
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return ({ children }: { children: ReactNode }) => (
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </MemoryRouter>
  );
};

describe('LoginPage', () => {
  beforeEach(() => {
    mutateMock.mockReset();
    optionsSpy.mockReset();
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
    });
  });

  it('renders login form fields', () => {
    const wrapper = createWrapper();
    render(<LoginPage />, { wrapper });

    expect(screen.getByRole('heading', { name: /welcome back/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toHaveAttribute('type', 'password');
  });

  it('submits provided credentials to the login mutation', () => {
    const wrapper = createWrapper();
    render(<LoginPage />, { wrapper });

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'student@aada.edu' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'secure-pass' },
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    expect(mutateMock).toHaveBeenCalledTimes(1);
    expect(mutateMock).toHaveBeenCalledWith({
      data: { email: 'student@aada.edu', password: 'secure-pass' },
    });
    expect(optionsSpy).toHaveBeenCalled();
  });
});
