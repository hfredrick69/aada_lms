import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Students from '../pages/Students';
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
    roles: ['Admin']
  }))
}));

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
        <AuthProvider>
          <Students />
        </AuthProvider>
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
        <AuthProvider>
          <Students />
        </AuthProvider>
      </BrowserRouter>
    );

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });
});
