import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Payments from '../pages/Payments';
import { AuthContext } from '../context/AuthContext';
import axiosClient from '../utils/axiosClient';

vi.mock('../utils/axiosClient');

const mockAuthContext = {
  user: { id: '123', roles: ['Admin', 'Finance'] },
  isAuthenticated: true,
  hasRole: vi.fn(() => true)
};

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
        <AuthContext.Provider value={mockAuthContext}>
          <Payments />
        </AuthContext.Provider>
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
        <AuthContext.Provider value={mockAuthContext}>
          <Payments />
        </AuthContext.Provider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/8,500/)).toBeInTheDocument();
    });
  });
});
