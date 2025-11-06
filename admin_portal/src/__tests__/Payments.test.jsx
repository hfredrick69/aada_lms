import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Payments from '../pages/Payments';
import { AuthProvider } from '../context/AuthContext';
import axiosClient from '../api/axiosClient';

vi.mock('../api/axiosClient');

vi.mock('../api/auth.js', () => ({
  login: vi.fn(async () => ({ access_token: 'test-token' })),
  me: vi.fn(async () => ({
    id: '123',
    email: 'admin@aada.edu',
    first_name: 'Admin',
    last_name: 'User',
    roles: ['admin', 'finance']
  }))
}));

describe('Payments Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    axiosClient.get.mockResolvedValue({
      data: [
        { id: '1', user_id: 'user1', amount_cents: 850000, line_type: 'tuition', created_at: '2025-01-01' },
        { id: '2', user_id: 'user2', amount_cents: 500000, line_type: 'payment', created_at: '2025-01-02' }
      ]
    });
  });

  it('renders payment transactions', async () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Payments />
        </AuthProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/tuition/i)).toBeInTheDocument();
      expect(screen.getByText(/payment/i)).toBeInTheDocument();
    });
  });

  it('formats currency correctly', async () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Payments />
        </AuthProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/8,500/)).toBeInTheDocument();
    });
  });
});
