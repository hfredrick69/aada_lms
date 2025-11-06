import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '../pages/Dashboard';
import { AuthProvider } from '../context/AuthContext';

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

vi.mock('../api/students.js', () => ({
  listStudents: vi.fn(async () => [
    { id: '1', first_name: 'John', last_name: 'Doe' },
    { id: '2', first_name: 'Jane', last_name: 'Smith' }
  ])
}));

vi.mock('../api/courses.js', () => ({
  listPrograms: vi.fn(async () => [
    { id: '1', code: 'MA-101', name: 'Medical Assisting' }
  ])
}));

vi.mock('../api/payments.js', () => ({
  listInvoices: vi.fn(async () => [
    { id: '1', status: 'open' },
    { id: '2', status: 'paid' }
  ])
}));

vi.mock('../api/externships.js', () => ({
  listExternships: vi.fn(async () => [
    { id: '1', status: 'active' }
  ])
}));

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders dashboard header', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Dashboard />
        </AuthProvider>
      </BrowserRouter>
    );

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText(/Monitor enrollment/i)).toBeInTheDocument();
  });

  it('displays metric cards after loading', async () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Dashboard />
        </AuthProvider>
      </BrowserRouter>
    );

    expect(screen.getByText('Loading metrics...')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Active Students')).toBeInTheDocument();
      expect(screen.getByText('Programs & Modules')).toBeInTheDocument();
      expect(screen.getByText('Open Invoices')).toBeInTheDocument();
      expect(screen.getByText('Externship Placements')).toBeInTheDocument();
    });
  });
});
