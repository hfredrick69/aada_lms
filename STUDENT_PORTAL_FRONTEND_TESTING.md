# Student Portal Frontend Testing Guide

## Overview

This guide covers frontend testing for the AADA Student Portal (React + Vite + TypeScript).

## Test Framework

- **Vitest** - Fast unit test runner
- **React Testing Library** - Component testing utilities
- **TypeScript** - Type-safe testing

## Running Tests

### Run All Tests
```bash
cd frontend/aada_web
npm test
```

### Run Tests in Watch Mode
```bash
npm run test:watch
```

### Run Tests with Coverage
```bash
npm run test:coverage
```

## Test Structure

### Test Files Location
`frontend/aada_web/src/__tests__/`

### Test Files
- `DashboardPage.test.tsx` - Dashboard tests
- `Modules.test.tsx` - Module browsing and navigation
- `Payments.test.tsx` - Payment history and status
- `Externships.test.tsx` - Externship tracking
- `Documents.test.tsx` - Document access
- `AppLayout.test.tsx` - Layout and navigation tests

## Writing Tests

### Component Test Template
```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import YourComponent from '../features/your-feature/YourComponent';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } }
});

describe('YourComponent', () => {
  it('renders correctly', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <YourComponent />
        </BrowserRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });
});
```

### Testing with React Query
```typescript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      cacheTime: 0
    }
  }
});

// Wrap component in QueryClientProvider
render(
  <QueryClientProvider client={queryClient}>
    <YourComponent />
  </QueryClientProvider>
);
```

### Mocking API Responses
```typescript
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.get('/api/modules', (req, res, ctx) => {
    return res(ctx.json([
      { id: 1, title: 'Module 1' }
    ]));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## Test Categories

### 1. Page Component Tests
Test student-facing pages render correctly and handle interactions.

### 2. Authentication Tests
Test login flow and session management.

### 3. Module Navigation Tests
Test module browsing, filtering, and content access.

### 4. Progress Tracking Tests
Test that progress indicators display correctly.

### 5. Dark Mode Tests
Test theme switching and persistence.

## Best Practices

1. **Type Safety** - Leverage TypeScript for test type checking
2. **Accessibility Testing** - Test with screen readers in mind
3. **Responsive Testing** - Test mobile and desktop views
4. **Loading States** - Test loading and error states
5. **User Flows** - Test complete user journeys

## Debugging Tests

### Debug in VS Code
Add breakpoint and run:
```bash
npm test -- --inspect-brk
```

### View Test UI
```bash
npm run test:ui
```

## Performance Testing

Test component render performance:
```typescript
import { renderHook, waitFor } from '@testing-library/react';

it('loads data efficiently', async () => {
  const start = performance.now();

  const { result } = renderHook(() => useYourHook());

  await waitFor(() => {
    expect(result.current.data).toBeDefined();
  });

  const duration = performance.now() - start;
  expect(duration).toBeLessThan(1000); // < 1 second
});
```

---

Generated: 2025-11-03
