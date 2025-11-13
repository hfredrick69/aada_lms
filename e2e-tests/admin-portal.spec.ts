import { test, expect } from '@playwright/test';
import {
  apiLogin,
  ensureEnrollmentTemplate,
  ensureStudentExists,
  drawSignature,
  listUserDocuments,
  waitForDocumentStatus,
} from './helpers';

/**
 * Admin Portal E2E Tests
 *
 * Validates Phase 4 authentication and core admin functionality
 */

const ADMIN_EMAIL = 'admin@aada.edu';
const ADMIN_PASSWORD = 'AdminPass!23';
const E2E_HOST = process.env.E2E_HOST ?? 'localhost';
const ADMIN_PORTAL_URL = process.env.ADMIN_PORTAL_URL ?? `http://${E2E_HOST}:5173`;
const STUDENT_PORTAL_URL = process.env.STUDENT_PORTAL_URL ?? `http://${E2E_HOST}:5174`;

test.describe('Admin Portal - Authentication', () => {
  test('should load login page', async ({ page }) => {
    await page.goto(ADMIN_PORTAL_URL + '/login');

    // Verify login page elements
    await expect(page.getByRole('heading', { name: /admin portal/i })).toBeVisible();
    await expect(page.getByText('Students Are Our Top Priority!!!')).toBeVisible();
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

    await expect(page).toHaveURL(/login/, { timeout: 5000 });
  });

  test('should reject invalid credentials', async ({ page }) => {
    await page.goto(ADMIN_PORTAL_URL + '/login');

    // Fill with wrong password
    await page.getByLabel('Email', { exact: false }).fill(ADMIN_EMAIL);
    await page.getByLabel('Password', { exact: false }).fill('WrongPassword!23');

    // Submit form
    await page.getByRole('button', { name: /sign in/i }).click();

    // Wait for potential error
    await page.waitForLoadState('networkidle');

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
    await page.waitForLoadState('networkidle');

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
    await page.waitForLoadState('networkidle');

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
    await page.waitForLoadState('networkidle');

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
    await page.waitForLoadState('networkidle');

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
    await page.waitForLoadState('networkidle');

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
    await page.waitForLoadState('networkidle');

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
    await page.waitForLoadState('networkidle');

    // Should not show error message
    await expect(page.locator('text=/something went wrong|unable to load/i')).not.toBeVisible();

    // Log errors if found
    if (apiErrors.length > 0) console.error('Settings API Errors:', apiErrors);
    if (errors.length > 0) console.error('Settings Console Errors:', errors);

    // Should not have API errors
    expect(apiErrors.length).toBe(0);
  });
});

test.describe('Admin Portal - Agreements', () => {
  test('can send and counter-sign enrollment agreements', async ({ page, request, browser }) => {
    test.setTimeout(120000);
    const adminToken = await apiLogin(request, ADMIN_EMAIL, ADMIN_PASSWORD);
    const template = await ensureEnrollmentTemplate(request, adminToken);
    const student = await ensureStudentExists(request, adminToken, {
      email: 'alice.student@aada.edu',
      password: 'AlicePass!23',
      first_name: 'Alice',
      last_name: 'Student',
    });

    await page.goto(ADMIN_PORTAL_URL + '/login');
    await page.getByLabel('Email', { exact: false }).fill(ADMIN_EMAIL);
    await page.getByLabel('Password', { exact: false }).fill(ADMIN_PASSWORD);
    await page.getByRole('button', { name: /sign in/i }).click();
    await page.waitForURL('**/dashboard', { timeout: 10000 });

    await page.click('text=Agreements');
    await expect(page.getByRole('heading', { name: /Enrollment Agreements/i })).toBeVisible();

    await page.selectOption('[data-testid="agreement-student-select"]', student.id);
    const advisorNotes = `Automated test agreement ${Date.now()}`;
    await page.fill('textarea', advisorNotes);
    await page.getByRole('button', { name: 'Send Agreement' }).click();
    await expect(page.getByText('Enrollment agreement sent successfully.')).toBeVisible({ timeout: 5000 });

    // Locate the newly created document via API so we can simulate the student signature
    const documentsResponse = await listUserDocuments(request, adminToken, student.id);
    const seededDoc = documentsResponse.documents?.find((doc: any) => doc.form_data?.advisor_notes === advisorNotes);
    if (!seededDoc) {
      throw new Error('Unable to find sent enrollment agreement');
    }

    // Complete the public signing flow through the student portal UI so the admin session remains untouched
    const studentContext = await browser.newContext();
    const publicPage = await studentContext.newPage();
    await publicPage.goto(`${STUDENT_PORTAL_URL}/sign/${seededDoc.signing_token}`);
    await publicPage.getByRole('heading', { name: /enrollment agreement/i }).waitFor({ timeout: 10000 });
    await publicPage.getByRole('button', { name: /next step/i }).click();
    await publicPage.getByLabel('Phone number').fill('(404) 555-7890');
    await publicPage.getByLabel('Preferred start date').fill('2025-01-01');
    await publicPage.getByLabel('Emergency contact').fill('Automation Buddy 555-1111');
    await publicPage.getByLabel('Housing needs').selectOption('interested');
    await publicPage.getByLabel('Questions or accessibility requests').fill('Playwright automated submission');
    await publicPage.getByRole('button', { name: /next step/i }).click();
    await publicPage.getByLabel('Full name').fill(`${student.first_name} ${student.last_name}`);
    await drawSignature(publicPage, 'canvas');
    await publicPage.getByRole('button', { name: /submit signature/i }).click();
    await expect(publicPage.getByText(/document signed successfully/i)).toBeVisible({ timeout: 10000 });
    await publicPage.close();
    await studentContext.close();

    await waitForDocumentStatus(request, adminToken, student.id, seededDoc.id, 'student_signed', {
      timeoutMs: 60000,
      pollIntervalMs: 2000,
    });

    // Reload to ensure the admin grid reflects the latest status
    const agreementsTab = page.getByRole('link', { name: /^Agreements$/i });
    await agreementsTab.click();
    await page.waitForLoadState('networkidle');
    await page.waitForLoadState('networkidle');

    // Switch to the "Awaiting AADA signature" filter so the new record remains visible
    await expect(page.getByRole('heading', { name: /enrollment agreements/i })).toBeVisible({ timeout: 15000 });
    const statusCombo = page.getByRole('combobox', { name: /status/i });
    await expect(statusCombo).toBeVisible({ timeout: 10000 });
    await statusCombo.click();
    await page.getByRole('option', { name: /Awaiting AADA signature/i }).click();

    // Wait for the newly created row to appear with the unique advisor notes
    const row = page.locator('tbody tr', { hasText: advisorNotes }).first();
    await row.waitFor({ timeout: 20000 });
    await expect(row).toBeVisible({ timeout: 5000 });
    await expect(row.getByText(/awaiting counter-sign/i)).toBeVisible({ timeout: 20000 });

    await row.getByRole('button', { name: 'Counter-sign' }).click();
    await page.getByLabel('Authorized signer name').fill('Registrar QA');
    await drawSignature(page, '.signature-canvas');
    await page.getByRole('button', { name: /save signature/i }).click();
    await page.getByRole('button', { name: 'Submit signature' }).click();

    await waitForDocumentStatus(request, adminToken, student.id, seededDoc.id, ['completed'], {
      timeoutMs: 60000,
      pollIntervalMs: 2000,
    });

    const filterSelect = page.getByRole('combobox', { name: /status/i });
    await filterSelect.click();
    await page.getByRole('option', { name: /all statuses/i }).click();

    const completedRow = page.locator('tbody tr', { hasText: advisorNotes }).first();
    await expect(completedRow.getByText('Completed')).toBeVisible({ timeout: 10000 });
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
    await page.waitForLoadState('networkidle');

    // Navigate to different page to test session
    await page.click('text=Courses');
    await page.waitForLoadState('networkidle');

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
    await page.waitForLoadState('networkidle');
    expect(page.url()).toContain('/settings');

    // Should not show access denied
    await expect(page.locator('text=/access denied|unauthorized/i')).not.toBeVisible();
  });
});
