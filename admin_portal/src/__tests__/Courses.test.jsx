import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Courses from '../pages/Courses';
import { AuthContext } from '../context/AuthContext';
import axiosClient from '../utils/axiosClient';

vi.mock('../utils/axiosClient');

const mockAuthContext = {
  user: { id: '123', roles: ['Admin'] },
  isAuthenticated: true,
  hasRole: vi.fn(() => true)
};

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
        <AuthContext.Provider value={mockAuthContext}>
          <Courses />
        </AuthContext.Provider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('MA-101')).toBeInTheDocument();
      expect(screen.getByText('MA-201')).toBeInTheDocument();
    });
  });
});
