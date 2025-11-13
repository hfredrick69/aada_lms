import { test, expect, Page } from '@playwright/test';

/**
 * Progress Tracking E2E Tests
 *
 * Tests the engagement tracking system including:
 * - Progress API endpoints
 * - ModuleProgressTracker component
 * - Database persistence
 * - Resume functionality
 */

const STUDENT_EMAIL = 'alice.student@aada.edu';
const STUDENT_PASSWORD = 'AlicePass!23';
const API_ORIGIN = process.env.PLAYWRIGHT_API_ORIGIN ?? 'http://localhost:8000';
const API_BASE_URL = process.env.PLAYWRIGHT_API_BASE_URL ?? `${API_ORIGIN}/api`;
const STUDENT_PORTAL_URL = process.env.STUDENT_PORTAL_URL ?? `http://${process.env.E2E_HOST ?? 'localhost'}:5174`;

const shouldRunProgressSpecs = process.env.RUN_PROGRESS_SPECS === 'true';
const progressDescribe = shouldRunProgressSpecs ? test.describe : test.describe.skip;

// Test data (alice.student@aada.edu from seed data)
const TEST_USER_ID = '73d0b1c8-756d-4bb8-a90c-c599963f7e60';
const TEST_ENROLLMENT_ID = '5c368e87-afe6-48bb-bb9f-b580de9f1eb5';
const TEST_MODULE_ID = 'e8c7950f-9419-4a4b-ab1e-96d6b92275ba';

async function openFirstModule(page: Page) {
  const moduleLink = page.locator('a[href^="/modules/"]').first();
  await expect(moduleLink).toBeVisible({ timeout: 5000 });
  await moduleLink.click();
  await page.waitForLoadState('networkidle');
}

// Helper to login via API
async function loginUser(request: any, email: string, password: string) {
  const response = await request.post(`${API_BASE_URL}/auth/login`, {
    data: { email, password }
  });
  expect(response.ok()).toBeTruthy();
  const body = await response.json();
  expect(body?.access_token).toBeTruthy();
  return body.access_token as string;
}

progressDescribe('Progress Tracking API - /api/progress', () => {

  test('should save progress with engagement data', async ({ request }) => {
    // Login
    const token = await loginUser(request, STUDENT_EMAIL, STUDENT_PASSWORD);
    const headers = { Authorization: `Bearer ${token}` };

    // Save progress
    const progressData = {
      enrollment_id: TEST_ENROLLMENT_ID,
      module_id: TEST_MODULE_ID,
      last_scroll_position: 2500,
      active_time_seconds: 120,
      sections_viewed: ['intro', 'chapter1', 'chapter2', 'conclusion']
    };

    const response = await request.post(`${API_BASE_URL}/progress/`, {
      data: progressData,
      headers,
    });

    expect(response.status()).toBe(201);
    const saved = await response.json();

    // Verify response structure
    expect(saved).toHaveProperty('id');
    expect(saved.enrollment_id).toBe(TEST_ENROLLMENT_ID);
    expect(saved.module_id).toBe(TEST_MODULE_ID);
    expect(saved.last_scroll_position).toBe(2500);
    expect(saved.active_time_seconds).toBe(120);
    expect(saved.sections_viewed).toEqual(['intro', 'chapter1', 'chapter2', 'conclusion']);
    expect(saved).toHaveProperty('last_accessed_at');
  });

  test('should retrieve saved progress for a module', async ({ request }) => {
    // Login
    const token = await loginUser(request, STUDENT_EMAIL, STUDENT_PASSWORD);
    const headers = { Authorization: `Bearer ${token}` };

    // First save some progress
    await request.post(`${API_BASE_URL}/progress/`, {
      data: {
        enrollment_id: TEST_ENROLLMENT_ID,
        module_id: TEST_MODULE_ID,
        last_scroll_position: 1800,
        active_time_seconds: 90,
        sections_viewed: ['intro', 'chapter1']
      },
      headers,
    });

    // Retrieve progress
    const response = await request.get(
      `${API_BASE_URL}/progress/${TEST_USER_ID}/module/${TEST_MODULE_ID}`,
      { headers }
    );

    expect(response.ok()).toBeTruthy();
    const progress = await response.json();

    expect(progress.module_id).toBe(TEST_MODULE_ID);
    expect(progress.last_scroll_position).toBe(1800);
    expect(progress.active_time_seconds).toBe(90);
    expect(progress.sections_viewed).toContain('intro');
    expect(progress.sections_viewed).toContain('chapter1');
  });

  test('should update existing progress', async ({ request }) => {
    // Login
    const token = await loginUser(request, STUDENT_EMAIL, STUDENT_PASSWORD);
    const headers = { Authorization: `Bearer ${token}` };

    // Save initial progress
    await request.post(`${API_BASE_URL}/progress/`, {
      data: {
        enrollment_id: TEST_ENROLLMENT_ID,
        module_id: TEST_MODULE_ID,
        last_scroll_position: 1000,
        active_time_seconds: 30,
        sections_viewed: ['intro']
      },
      headers,
    });

    // Update progress
    const updateResponse = await request.post(`${API_BASE_URL}/progress/`, {
      data: {
        enrollment_id: TEST_ENROLLMENT_ID,
        module_id: TEST_MODULE_ID,
        last_scroll_position: 3000,
        active_time_seconds: 150,
        sections_viewed: ['intro', 'chapter1', 'chapter2']
      },
      headers,
    });

    expect(updateResponse.ok()).toBeTruthy();
    const updated = await updateResponse.json();

    // Verify updated values
    expect(updated.last_scroll_position).toBe(3000);
    expect(updated.active_time_seconds).toBe(150);
    expect(updated.sections_viewed).toHaveLength(3);
  });

  test('should retrieve overall user progress', async ({ request }) => {
    // Login
    const token = await loginUser(request, STUDENT_EMAIL, STUDENT_PASSWORD);
    const headers = { Authorization: `Bearer ${token}` };

    // Get overall progress
    const response = await request.get(
      `${API_BASE_URL}/progress/${TEST_USER_ID}`,
      { headers }
    );

    expect(response.ok()).toBeTruthy();
    const overallProgress = await response.json();

    // Verify structure
    expect(overallProgress).toHaveProperty('user_id');
    expect(overallProgress).toHaveProperty('enrollment_id');
    expect(overallProgress).toHaveProperty('total_modules');
    expect(overallProgress).toHaveProperty('completed_modules');
    expect(overallProgress).toHaveProperty('completion_percentage');
    expect(overallProgress).toHaveProperty('modules');
    expect(Array.isArray(overallProgress.modules)).toBeTruthy();
  });

  test('should prevent unauthorized access', async ({ request }) => {
    // Try to access progress without logging in
    const response = await request.get(
      `${API_BASE_URL}/progress/${TEST_USER_ID}/module/${TEST_MODULE_ID}`
    );

    // Should be unauthorized
    expect(response.status()).toBe(401);
  });
});

progressDescribe('ModuleProgressTracker Component', () => {

  test('should track scroll position and save progress', async ({ page, request }) => {
    // Login via UI
    await page.goto(STUDENT_PORTAL_URL);
    await page.fill('input[type="email"]', STUDENT_EMAIL);
    await page.fill('input[type="password"]', STUDENT_PASSWORD);
    await page.click('button[type="submit"]');

    // Wait for dashboard
    await page.waitForURL('**/dashboard');

    // Navigate to Modules
    await page.click('text=Modules');
    await page.waitForURL('**/modules');

    // Click on first module
    await openFirstModule(page);


    // Scroll down the page
    await page.evaluate(() => window.scrollTo(0, 1500));
    await page.waitForTimeout(500); // Wait for tracker to register scroll

    // Check console for progress tracker logs (optional)
    const consoleLogs: string[] = [];
    page.on('console', msg => {
      if (msg.text().includes('ModuleProgressTracker') || msg.text().includes('Progress saved')) {
        consoleLogs.push(msg.text());
      }
    });

    // Wait for a single auto-save cycle
    await page.waitForTimeout(5000);

    // Verify progress was saved via API
    const apiContext = await page.context().request;
    const progressResponse = await apiContext.get(
      `${API_BASE_URL}/progress/${TEST_USER_ID}/module/${TEST_MODULE_ID}`
    );

    expect(progressResponse.ok()).toBeTruthy();
    const progress = await progressResponse.json();

    // Verify scroll position was saved
    expect(progress.last_scroll_position).toBeGreaterThan(0);
    expect(progress.active_time_seconds).toBeGreaterThan(0);
  });

  test('should resume from last scroll position', async ({ page }) => {
    // First, save some progress via API
    const context = await page.context();
    const apiContext = context.request;

    // Login
    const loginResponse = await apiContext.post(`${API_BASE_URL}/auth/login`, {
      data: { email: STUDENT_EMAIL, password: STUDENT_PASSWORD }
    });
    expect(loginResponse.ok()).toBeTruthy();

    // Save progress with specific scroll position
    await apiContext.post(`${API_BASE_URL}/progress/`, {
      data: {
        enrollment_id: TEST_ENROLLMENT_ID,
        module_id: TEST_MODULE_ID,
        last_scroll_position: 2000,
        active_time_seconds: 60,
        sections_viewed: ['intro']
      }
    });

    // Now login via UI
    await page.goto(STUDENT_PORTAL_URL);
    await page.fill('input[type="email"]', STUDENT_EMAIL);
    await page.fill('input[type="password"]', STUDENT_PASSWORD);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');

    // Navigate to module
    await page.click('text=Modules');
    await openFirstModule(page);

    // Wait for scroll restoration
    await page.waitForTimeout(500);

    // Verify page scrolled to saved position
    const scrollY = await page.evaluate(() => window.scrollY);
    expect(scrollY).toBeGreaterThan(1500); // Should be close to 2000
    expect(scrollY).toBeLessThan(2500);
  });

  test('should track active time accurately', async ({ page }) => {
    // Login
    await page.goto(STUDENT_PORTAL_URL);
    await page.fill('input[type="email"]', STUDENT_EMAIL);
    await page.fill('input[type="password"]', STUDENT_PASSWORD);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');

    // Navigate to module
    await page.click('text=Modules');
    await openFirstModule(page);
    await page.waitForLoadState('networkidle');

    // Simulate user activity
    await page.mouse.move(100, 100);
    await page.waitForTimeout(800);
    await page.mouse.move(200, 200);
    await page.waitForTimeout(800);

    // Wait for a single auto-save cycle
    await page.waitForTimeout(5000);

    // Verify active time was tracked
    const apiContext = await page.context().request;
    const progressResponse = await apiContext.get(
      `${API_BASE_URL}/progress/${TEST_USER_ID}/module/${TEST_MODULE_ID}`
    );

    const progress = await progressResponse.json();
    expect(progress.active_time_seconds).toBeGreaterThan(5); // At least 6 seconds
  });
});

progressDescribe('Progress Integration Tests', () => {

  test('should persist progress across page reloads', async ({ page }) => {
    // Login
    await page.goto(STUDENT_PORTAL_URL);
    await page.fill('input[type="email"]', STUDENT_EMAIL);
    await page.fill('input[type="password"]', STUDENT_PASSWORD);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');

    // Navigate to module
    await page.click('text=Modules');
    await openFirstModule(page);
    await page.waitForLoadState('networkidle');

    // Scroll and wait for save
    await page.evaluate(() => window.scrollTo(0, 1200));
    await page.waitForTimeout(5000); // Single auto-save cycle

    // Get current scroll position via API
    const apiContext = await page.context().request;
    const progressBefore = await apiContext.get(
      `${API_BASE_URL}/progress/${TEST_USER_ID}/module/${TEST_MODULE_ID}`
    );
    const beforeData = await progressBefore.json();

    // Reload page
    await page.reload();
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // Verify scroll was restored
    const scrollY = await page.evaluate(() => window.scrollY);
    expect(Math.abs(scrollY - beforeData.last_scroll_position)).toBeLessThan(100);

    // Verify progress is still available
    const progressAfter = await apiContext.get(
      `${API_BASE_URL}/progress/${TEST_USER_ID}/module/${TEST_MODULE_ID}`
    );
    const afterData = await progressAfter.json();

    expect(afterData.last_scroll_position).toBe(beforeData.last_scroll_position);
    expect(afterData.active_time_seconds).toBeGreaterThanOrEqual(beforeData.active_time_seconds);
  });
});
