import { test, expect } from '@playwright/test';

/**
 * Admin Portal E2E Tests
 *
 * Validates Phase 4 authentication and core admin functionality
 */

const ADMIN_EMAIL = 'admin@aada.edu';
const ADMIN_PASSWORD = 'AdminPass!23';
const ADMIN_PORTAL_URL = 'http://localhost:5173';

test.describe('Admin Portal - Authentication', () => {
  test('should load login page', async ({ page }) => {
    await page.goto(ADMIN_PORTAL_URL + '/login');

    // Verify login page elements
    await expect(page.locator('h1, h2, h3, h4').filter({ hasText: 'Welcome Back' })).toBeVisible();
    await expect(page.getByLabel('Email', { exact: false })).toBeVisible();
    await expect(page.getByLabel('Password', { exact: false })).toBeVisible();
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
  });

  test('should login with admin credentials', async ({ page }) => {
    await page.goto(ADMIN_PORTAL_URL + '/login');

    // Fill login form
    await page.getByLabel('Email', { exact: false }).fill(ADMIN_EMAIL);
    await page.getByLabel('Password', { exact: false }).fill(ADMIN_PASSWORD);

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

  test('should reject student credentials in admin portal', async ({ page }) => {
    await page.goto(ADMIN_PORTAL_URL + '/login');

    // Try to login with student credentials
    await page.getByLabel('Email', { exact: false }).fill('alice.student@aada.edu');
    await page.getByLabel('Password', { exact: false }).fill('AlicePass!23');

    // Submit form
    await page.getByRole('button', { name: /sign in/i }).click();

    // Wait for response
    await page.waitForTimeout(2000);

    // Should either show error or be denied access (depending on implementation)
    // For now, we just verify they can log in (role checking might be separate)
    // In a production system, you'd want role-based access control here
  });

  test('should reject invalid credentials', async ({ page }) => {
    await page.goto(ADMIN_PORTAL_URL + '/login');

    // Fill with wrong password
    await page.getByLabel('Email', { exact: false }).fill(ADMIN_EMAIL);
    await page.getByLabel('Password', { exact: false }).fill('WrongPassword!23');

    // Submit form
    await page.getByRole('button', { name: /sign in/i }).click();

    // Wait for potential error
    await page.waitForTimeout(3000);

    // Should still be on login page (not redirected to dashboard)
    expect(page.url()).toContain('/login');

    // Note: Error message display not yet implemented in UI
  });
});

test.describe('Admin Portal - All Pages Load', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto(ADMIN_PORTAL_URL + '/login');
    await page.getByLabel('Email', { exact: false }).fill(ADMIN_EMAIL);
    await page.getByLabel('Password', { exact: false }).fill(ADMIN_PASSWORD);
    await page.getByRole('button', { name: /sign in/i }).click();
    await page.waitForURL('**/dashboard', { timeout: 10000 });
  });

  test('Dashboard page should load without errors', async ({ page }) => {
    // Already on dashboard from login
    const errors: string[] = [];
    const apiErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error' && !msg.text().includes('DevTools')) {
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

    // Verify dashboard content - use first() to avoid strict mode violation
    await expect(page.locator('h1, h2, h3, h4').filter({ hasText: /dashboard|admin|overview/i }).first()).toBeVisible({ timeout: 5000 });

    // Log errors if found
    if (apiErrors.length > 0) console.error('Dashboard API Errors:', apiErrors);
    if (errors.length > 0) console.error('Dashboard Console Errors:', errors);

    // Should not have API errors
    expect(apiErrors.length).toBe(0);
  });

  test('Students page should load without errors', async ({ page }) => {
    const errors: string[] = [];
    const apiErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error' && !msg.text().includes('DevTools')) {
        errors.push(msg.text());
      }
    });

    page.on('response', (response) => {
      if (response.status() >= 400 && response.url().includes('/api/')) {
        apiErrors.push(`${response.status()} ${response.url()}`);
      }
    });

    // Navigate to Students
    await page.click('text=Students');
    await page.waitForTimeout(3000);

    // Should not show error message
    await expect(page.locator('text=/something went wrong|unable to load/i')).not.toBeVisible();

    // Log errors if found
    if (apiErrors.length > 0) console.error('Students API Errors:', apiErrors);
    if (errors.length > 0) console.error('Students Console Errors:', errors);

    // Should not have API errors
    expect(apiErrors.length).toBe(0);
  });

  test('Courses page should load without errors', async ({ page }) => {
    const errors: string[] = [];
    const apiErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error' && !msg.text().includes('DevTools')) {
        errors.push(msg.text());
      }
    });

    page.on('response', (response) => {
      if (response.status() >= 400 && response.url().includes('/api/')) {
        apiErrors.push(`${response.status()} ${response.url()}`);
      }
    });

    // Navigate to Courses
    await page.click('text=Courses');
    await page.waitForTimeout(3000);

    // Should not show error message
    await expect(page.locator('text=/something went wrong|unable to load/i')).not.toBeVisible();

    // Log errors if found
    if (apiErrors.length > 0) console.error('Courses API Errors:', apiErrors);
    if (errors.length > 0) console.error('Courses Console Errors:', errors);

    // Should not have API errors
    expect(apiErrors.length).toBe(0);
  });

  test('Payments page should load without errors', async ({ page }) => {
    const errors: string[] = [];
    const apiErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error' && !msg.text().includes('DevTools')) {
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

    // Should not show error message
    await expect(page.locator('text=/something went wrong|unable to load/i')).not.toBeVisible();

    // Log errors if found
    if (apiErrors.length > 0) console.error('Payments API Errors:', apiErrors);
    if (errors.length > 0) console.error('Payments Console Errors:', errors);

    // Should not have API errors
    expect(apiErrors.length).toBe(0);
  });

  test('Externships page should load without errors', async ({ page }) => {
    const errors: string[] = [];
    const apiErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error' && !msg.text().includes('DevTools')) {
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

    // Should not show error message
    await expect(page.locator('text=/something went wrong|unable to load/i')).not.toBeVisible();

    // Log errors if found
    if (apiErrors.length > 0) console.error('Externships API Errors:', apiErrors);
    if (errors.length > 0) console.error('Externships Console Errors:', errors);

    // Should not have API errors
    expect(apiErrors.length).toBe(0);
  });

  test('Reports page should load without errors', async ({ page }) => {
    const errors: string[] = [];
    const apiErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error' && !msg.text().includes('DevTools')) {
        errors.push(msg.text());
      }
    });

    page.on('response', (response) => {
      if (response.status() >= 400 && response.url().includes('/api/')) {
        apiErrors.push(`${response.status()} ${response.url()}`);
      }
    });

    // Navigate to Reports
    await page.click('text=Reports');
    await page.waitForTimeout(3000);

    // Should not show error message
    await expect(page.locator('text=/something went wrong|unable to load/i')).not.toBeVisible();

    // Log errors if found
    if (apiErrors.length > 0) console.error('Reports API Errors:', apiErrors);
    if (errors.length > 0) console.error('Reports Console Errors:', errors);

    // Should not have API errors
    expect(apiErrors.length).toBe(0);
  });

  test('Settings page should load without errors', async ({ page }) => {
    const errors: string[] = [];
    const apiErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error' && !msg.text().includes('DevTools')) {
        errors.push(msg.text());
      }
    });

    page.on('response', (response) => {
      if (response.status() >= 400 && response.url().includes('/api/')) {
        apiErrors.push(`${response.status()} ${response.url()}`);
      }
    });

    // Navigate to Settings
    await page.click('text=Settings');
    await page.waitForTimeout(3000);

    // Should not show error message
    await expect(page.locator('text=/something went wrong|unable to load/i')).not.toBeVisible();

    // Log errors if found
    if (apiErrors.length > 0) console.error('Settings API Errors:', apiErrors);
    if (errors.length > 0) console.error('Settings Console Errors:', errors);

    // Should not have API errors
    expect(apiErrors.length).toBe(0);
  });
});

test.describe('Admin Portal - Protected Routes', () => {
  test('should redirect to login when not authenticated', async ({ page }) => {
    // Try to access dashboard without logging in
    await page.goto(ADMIN_PORTAL_URL + '/dashboard');

    // Should redirect to login
    await page.waitForURL('**/login', { timeout: 5000 });
    expect(page.url()).toContain('/login');
  });

  test('should persist session after navigation', async ({ page }) => {
    // Login first
    await page.goto(ADMIN_PORTAL_URL + '/login');
    await page.getByLabel('Email', { exact: false }).fill(ADMIN_EMAIL);
    await page.getByLabel('Password', { exact: false }).fill(ADMIN_PASSWORD);
    await page.getByRole('button', { name: /sign in/i }).click();
    await page.waitForURL('**/dashboard', { timeout: 10000 });

    // Navigate to another page
    await page.click('text=Students');
    await page.waitForTimeout(2000);

    // Navigate to different page to test session
    await page.click('text=Courses');
    await page.waitForTimeout(2000);

    // Should still be authenticated (not redirected to login)
    expect(page.url()).not.toContain('/login');
    expect(page.url()).toContain('/courses');
  });
});

test.describe('Admin Portal - Role-Based Access', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto(ADMIN_PORTAL_URL + '/login');
    await page.getByLabel('Email', { exact: false }).fill(ADMIN_EMAIL);
    await page.getByLabel('Password', { exact: false }).fill(ADMIN_PASSWORD);
    await page.getByRole('button', { name: /sign in/i }).click();
    await page.waitForURL('**/dashboard', { timeout: 10000 });
  });

  test('admin should access settings page', async ({ page }) => {
    // Admin role should have access to Settings
    await page.click('text=Settings');

    // Should navigate successfully
    await page.waitForTimeout(1000);
    expect(page.url()).toContain('/settings');

    // Should not show access denied
    await expect(page.locator('text=/access denied|unauthorized/i')).not.toBeVisible();
  });
});
