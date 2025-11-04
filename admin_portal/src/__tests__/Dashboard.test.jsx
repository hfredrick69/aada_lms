import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '../pages/Dashboard';
import { AuthContext } from '../context/AuthContext';

const mockUser = {
  id: '123',
  email: 'admin@aada.edu',
  first_name: 'Admin',
  last_name: 'User',
  roles: ['Admin']
};

const mockAuthContext = {
  user: mockUser,
  isAuthenticated: true,
  loading: false,
  login: vi.fn(),
  logout: vi.fn(),
  hasRole: vi.fn(() => true)
};

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders dashboard with user greeting', () => {
    render(
      <BrowserRouter>
        <AuthContext.Provider value={mockAuthContext}>
          <Dashboard />
        </AuthContext.Provider>
      </BrowserRouter>
    );

    expect(screen.getByText(/Welcome/i)).toBeInTheDocument();
  });

  it('displays metric cards', async () => {
    render(
      <BrowserRouter>
        <AuthContext.Provider value={mockAuthContext}>
          <Dashboard />
        </AuthContext.Provider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Students/i)).toBeInTheDocument();
    });
  });
});
