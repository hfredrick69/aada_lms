import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Students from '../pages/Students';
import { AuthContext } from '../context/AuthContext';
import axiosClient from '../utils/axiosClient';

vi.mock('../utils/axiosClient');

const mockAuthContext = {
  user: { id: '123', roles: ['Admin'] },
  isAuthenticated: true,
  loading: false,
  hasRole: vi.fn(() => true)
};

describe('Students Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    axiosClient.get.mockResolvedValue({
      data: [
        { id: '1', first_name: 'John', last_name: 'Doe', email: 'john@aada.edu', status: 'active' },
        { id: '2', first_name: 'Jane', last_name: 'Smith', email: 'jane@aada.edu', status: 'active' }
      ]
    });
  });

  it('renders students list', async () => {
    render(
      <BrowserRouter>
        <AuthContext.Provider value={mockAuthContext}>
          <Students />
        </AuthContext.Provider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });
  });

  it('displays loading state', () => {
    axiosClient.get.mockImplementation(() => new Promise(() => {}));

    render(
      <BrowserRouter>
        <AuthContext.Provider value={mockAuthContext}>
          <Students />
        </AuthContext.Provider>
      </BrowserRouter>
    );

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });
});
