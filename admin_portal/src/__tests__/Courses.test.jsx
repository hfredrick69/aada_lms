import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Courses from '../pages/Courses';
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
    roles: ['admin']
  }))
}));

describe('Courses Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    axiosClient.get.mockResolvedValue({
      data: [
        { id: '1', code: 'MA-101', name: 'Introduction to Medical Assisting', total_clock_hours: 40 },
        { id: '2', code: 'MA-201', name: 'Clinical Procedures', total_clock_hours: 60 }
      ]
    });
  });

  it('renders course list', async () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Courses />
        </AuthProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('MA-101')).toBeInTheDocument();
      expect(screen.getByText('MA-201')).toBeInTheDocument();
    });
  });
});
