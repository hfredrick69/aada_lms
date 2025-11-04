# Admin Portal Frontend Testing Guide

## Overview

This guide covers frontend testing for the AADA Admin Portal (React + Vite).

## Test Framework

- **Vitest** - Fast unit test runner
- **React Testing Library** - Component testing utilities
- **Vitest UI** - Interactive test runner

## Running Tests

### Run All Tests
```bash
cd admin_portal
npm test
```

### Run Tests in Watch Mode
```bash
npm run test:watch
```

### Run Tests with UI
```bash
npm run test:ui
```

### Run Tests with Coverage
```bash
npm run test:coverage
```

## Test Structure

### Test Files Location
`admin_portal/src/__tests__/`

### Test Files
- `Dashboard.test.jsx` - Dashboard page tests
- `Students.test.jsx` - Student management tests
- `Courses.test.jsx` - Course management tests
- `Payments.test.jsx` - Payment management tests
- `Externships.test.jsx` - Externship management tests
- `Reports.test.jsx` - Reports page tests
- `Settings.test.jsx` - Settings page tests
- `AuthContext.test.jsx` - Authentication context tests
- `RoleGate.test.jsx` - Role-based access control tests

## Writing Tests

### Component Test Template
```jsx
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import YourComponent from '../pages/YourComponent';
import { AuthContext } from '../context/AuthContext';

const mockAuthContext = {
  user: { id: '123', roles: ['Admin'] },
  isAuthenticated: true,
  hasRole: vi.fn(() => true)
};

describe('YourComponent', () => {
  it('renders correctly', () => {
    render(
      <BrowserRouter>
        <AuthContext.Provider value={mockAuthContext}>
          <YourComponent />
        </AuthContext.Provider>
      </BrowserRouter>
    );

    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });
});
```

### Testing User Interactions
```jsx
import { fireEvent, waitFor } from '@testing-library/react';

it('handles button click', async () => {
  render(<YourComponent />);

  const button = screen.getByRole('button', { name: /submit/i });
  fireEvent.click(button);

  await waitFor(() => {
    expect(screen.getByText('Success')).toBeInTheDocument();
  });
});
```

### Mocking API Calls
```jsx
import axiosClient from '../utils/axiosClient';
vi.mock('../utils/axiosClient');

beforeEach(() => {
  axiosClient.get.mockResolvedValue({
    data: [{ id: 1, name: 'Test' }]
  });
});
```

## Test Categories

### 1. Page Component Tests
Test that pages render correctly with proper data and handle user interactions.

### 2. Authentication Tests
Test login/logout flows and role-based access control.

### 3. API Integration Tests
Test that components correctly fetch and display data from the backend.

### 4. Form Tests
Test form validation, submission, and error handling.

### 5. Navigation Tests
Test routing and navigation between pages.

## Best Practices

1. **Test User Behavior** - Test what users see and do, not implementation details
2. **Use Semantic Queries** - Prefer `getByRole`, `getByLabelText` over `getByTestId`
3. **Wait for Async Updates** - Use `waitFor` for async state changes
4. **Mock External Dependencies** - Mock API calls, timers, etc.
5. **Keep Tests Focused** - One assertion per test when possible
6. **Clean Up** - Clear mocks between tests with `beforeEach`

## Debugging Tests

### View Test Output
```bash
npm test -- --reporter=verbose
```

### Run Single Test File
```bash
npm test Dashboard.test.jsx
```

### Debug in Browser
```bash
npm run test:ui
```

## CI/CD Integration

Tests run automatically:
- On pre-commit hooks (via QA agent)
- In CI/CD pipeline (GitHub Actions if configured)
- Before production deployments

---

Generated: 2025-11-03
