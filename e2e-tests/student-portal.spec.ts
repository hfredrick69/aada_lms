import { test, expect } from '@playwright/test';

/**
 * Student Portal E2E Tests
 *
 * Validates Phase 4 authentication and core student functionality
 */

const STUDENT_EMAIL = 'alice.student@aada.edu';
const STUDENT_PASSWORD = 'AlicePass!23';
const STUDENT_PORTAL_URL = 'http://localhost:5174';

test.describe('Student Portal - Authentication', () => {
  test('should load login page', async ({ page }) => {
    await page.goto(STUDENT_PORTAL_URL + '/login');

    // Verify login page elements
    await expect(page.locator('h1, h4').filter({ hasText: 'Welcome Back' })).toBeVisible();
    await expect(page.getByLabel('Email', { exact: false })).toBeVisible();
    await expect(page.getByLabel('Password', { exact: false })).toBeVisible();
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
  });

  test('should login with valid credentials', async ({ page }) => {
    await page.goto(STUDENT_PORTAL_URL + '/login');

    // Fill login form
    await page.getByLabel('Email', { exact: false }).fill(STUDENT_EMAIL);
    await page.getByLabel('Password', { exact: false }).fill(STUDENT_PASSWORD);

    // Submit form
    await page.getByRole('button', { name: /sign in/i }).click();

    // Wait for navigation to dashboard
    await page.waitForURL('**/dashboard', { timeout: 10000 });

    // Verify we're on the dashboard
    expect(page.url()).toContain('/dashboard');

    // Verify cookies are set (Phase 4 httpOnly cookies)
    const cookies = await page.context().cookies();
    const hasAccessToken = cookies.some(c => c.name === 'access_token');
    const hasRefreshToken = cookies.some(c => c.name === 'refresh_token');

    expect(hasAccessToken).toBeTruthy();
    expect(hasRefreshToken).toBeTruthy();
  });

  test('should reject invalid credentials', async ({ page }) => {
    await page.goto(STUDENT_PORTAL_URL + '/login');

    // Fill with wrong password
    await page.getByLabel('Email', { exact: false }).fill(STUDENT_EMAIL);
    await page.getByLabel('Password', { exact: false }).fill('WrongPassword!23');

    // Submit form
    await page.getByRole('button', { name: /sign in/i }).click();

    // Wait for potential error
    await page.waitForTimeout(2000);

    // Should still be on login page (not redirected to dashboard)
    expect(page.url()).toContain('/login');
  });
});

test.describe('Student Portal - All Pages Load', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto(STUDENT_PORTAL_URL + '/login');
    await page.getByLabel('Email', { exact: false }).fill(STUDENT_EMAIL);
    await page.getByLabel('Password', { exact: false }).fill(STUDENT_PASSWORD);
    await page.getByRole('button', { name: /sign in/i }).click();
    await page.waitForURL('**/dashboard', { timeout: 10000 });
  });

  test('Dashboard page should load without errors', async ({ page }) => {
    // Set up error listeners immediately (already on dashboard from login)
    const errors: string[] = [];
    const apiErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error' && !msg.text().includes('DevTools') && !msg.text().includes('React Router')) {
        errors.push(msg.text());
      }
    });

    page.on('response', (response) => {
      if (response.status() >= 400 && response.url().includes('/api/')) {
        apiErrors.push(`${response.status()} ${response.url()}`);
      }
    });

    // Wait for content to load
    await page.waitForTimeout(3000);

    // Verify dashboard content - use specific heading instead of filter
    await expect(page.getByRole('heading', { level: 4 })).toBeVisible({ timeout: 5000 });

    // Log errors if found
    if (apiErrors.length > 0) {
      console.error('Dashboard API Errors:', apiErrors);
    }
    if (errors.length > 0) {
      console.error('Dashboard Console Errors:', errors);
    }

    // Should not have errors
    expect(apiErrors.length).toBe(0);
    expect(errors.length).toBe(0);
  });

  test('Modules page should load without errors', async ({ page }) => {
    // Set up error listeners BEFORE navigation
    const errors: string[] = [];
    const apiErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error' && !msg.text().includes('DevTools') && !msg.text().includes('React Router')) {
        errors.push(msg.text());
      }
    });

    page.on('response', (response) => {
      if (response.status() >= 400 && response.url().includes('/api/')) {
        apiErrors.push(`${response.status()} ${response.url()}`);
      }
    });

    // Navigate to Modules
    await page.click('text=Modules');
    await page.waitForTimeout(3000);

    // Verify actual modules content exists - use first() to avoid strict mode violation
    await expect(page.getByRole('heading', { name: /Program Modules/i })).toBeVisible({ timeout: 5000 });

    // Log errors if found
    if (apiErrors.length > 0) {
      console.error('Modules API Errors:', apiErrors);
    }
    if (errors.length > 0) {
      console.error('Modules Console Errors:', errors);
    }

    // Should not have errors
    expect(apiErrors.length).toBe(0);
    expect(errors.length).toBe(0);
  });

  test('Payments page should load without errors', async ({ page }) => {
    // Set up error listeners BEFORE navigation
    const errors: string[] = [];
    const apiErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error' && !msg.text().includes('DevTools') && !msg.text().includes('React Router')) {
        errors.push(msg.text());
      }
    });

    page.on('response', (response) => {
      if (response.status() >= 400 && response.url().includes('/api/')) {
        apiErrors.push(`${response.status()} ${response.url()}`);
      }
    });

    // Navigate to Payments
    await page.click('text=Payments');
    await page.waitForTimeout(3000);

    // Verify actual content exists
    await expect(page.getByRole('heading', { name: /Payments & Tuition/i })).toBeVisible();
    await expect(page.getByText(/Withdrawals in progress/i)).toBeVisible();
    await expect(page.getByText(/Refunds issued/i)).toBeVisible();

    // Should not show "Something went wrong"
    await expect(page.locator('text=/something went wrong/i')).not.toBeVisible();

    // Log errors if found
    if (apiErrors.length > 0) {
      console.error('Payments API Errors:', apiErrors);
    }
    if (errors.length > 0) {
      console.error('Payments Console Errors:', errors);
    }

    // Should not have errors
    expect(apiErrors.length).toBe(0);
    expect(errors.length).toBe(0);
  });

  test('Externships page should load without errors', async ({ page }) => {
    // Set up error listeners BEFORE navigation
    const errors: string[] = [];
    const apiErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error' && !msg.text().includes('DevTools') && !msg.text().includes('React Router')) {
        errors.push(msg.text());
      }
    });

    page.on('response', (response) => {
      if (response.status() >= 400 && response.url().includes('/api/')) {
        apiErrors.push(`${response.status()} ${response.url()}`);
      }
    });

    // Navigate to Externships
    await page.click('text=Externships');
    await page.waitForTimeout(3000);

    // Verify actual content exists
    await expect(page.getByRole('heading', { name: /Externship Tracker/i })).toBeVisible();
    await expect(page.getByText(/Progress summary/i)).toBeVisible();
    await expect(page.getByText(/Total hours completed/i)).toBeVisible();

    // Should not show "Something went wrong"
    await expect(page.locator('text=/something went wrong/i')).not.toBeVisible();

    // Log errors if found
    if (apiErrors.length > 0) {
      console.error('Externships API Errors:', apiErrors);
    }
    if (errors.length > 0) {
      console.error('Externships Console Errors:', errors);
    }

    // Should not have errors
    expect(apiErrors.length).toBe(0);
    expect(errors.length).toBe(0);
  });

  test('Documents page should load without errors', async ({ page }) => {
    // Set up error listeners BEFORE navigation
    const errors: string[] = [];
    const apiErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error' && !msg.text().includes('DevTools') && !msg.text().includes('React Router')) {
        errors.push(msg.text());
      }
    });

    page.on('response', (response) => {
      if (response.status() >= 400 && response.url().includes('/api/')) {
        apiErrors.push(`${response.status()} ${response.url()}`);
      }
    });

    // Navigate to Documents
    await page.click('text=Documents');
    await page.waitForTimeout(3000);

    // Verify actual content exists
    await expect(page.getByRole('heading', { name: /Documents & Uploads/i })).toBeVisible();
    await expect(page.getByText(/Upload credential/i)).toBeVisible();
    await expect(page.getByText(/Credential archive/i)).toBeVisible();

    // Should NOT show error message
    await expect(page.locator('text=/something went wrong|unable to load/i')).not.toBeVisible();

    // Log any errors found
    if (apiErrors.length > 0) {
      console.error('Documents API Errors:', apiErrors);
    }
    if (errors.length > 0) {
      console.error('Documents Console Errors:', errors);
    }

    // Should not have errors
    expect(apiErrors.length).toBe(0);
    expect(errors.length).toBe(0);
  });
});

// TODO: Add module content tests when module viewing UI is stabilized
// test.describe('Student Portal - Module Content', () => {
//   - Test viewing module lessons
//   - Test H5P content loading
//   - Test CSP compliance
// });

test.describe('Student Portal - Protected Routes', () => {
  test('should redirect to login when not authenticated', async ({ page }) => {
    // Try to access dashboard without logging in
    await page.goto(STUDENT_PORTAL_URL + '/dashboard');

    // Should redirect to login
    await page.waitForURL('**/login', { timeout: 5000 });
    expect(page.url()).toContain('/login');
  });

  test('should persist session after navigation', async ({ page }) => {
    // Login first
    await page.goto(STUDENT_PORTAL_URL + '/login');
    await page.getByLabel('Email', { exact: false }).fill(STUDENT_EMAIL);
    await page.getByLabel('Password', { exact: false }).fill(STUDENT_PASSWORD);
    await page.getByRole('button', { name: /sign in/i }).click();
    await page.waitForURL('**/dashboard', { timeout: 10000 });

    // Navigate to another page
    await page.click('text=Modules');
    await page.waitForTimeout(2000);

    // Navigate back - should still be authenticated
    await page.goto(STUDENT_PORTAL_URL + '/dashboard');
    await page.waitForTimeout(1000);

    // Should still be authenticated
    expect(page.url()).toContain('/dashboard');
  });
});
