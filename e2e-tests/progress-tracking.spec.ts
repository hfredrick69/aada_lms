import { test, expect } from '@playwright/test';

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
const API_BASE_URL = 'http://localhost:8000';
const STUDENT_PORTAL_URL = 'http://localhost:5174';

// Test data
const TEST_USER_ID = '4c89b4db-9989-4886-acef-39540ecec854';
const TEST_ENROLLMENT_ID = '6a284f0b-f5a1-4068-9f6a-76b7f7551507';
const TEST_MODULE_ID = '2e7e1cf1-764d-4afb-a821-dfee913a8d40';

// Helper to login via API
async function loginUser(request: any, email: string, password: string) {
  const response = await request.post(`${API_BASE_URL}/api/auth/login`, {
    data: { email, password }
  });
  expect(response.ok()).toBeTruthy();
  return response;
}

test.describe('Progress Tracking API - /api/progress', () => {

  test('should save progress with engagement data', async ({ request }) => {
    // Login
    await loginUser(request, STUDENT_EMAIL, STUDENT_PASSWORD);

    // Save progress
    const progressData = {
      enrollment_id: TEST_ENROLLMENT_ID,
      module_id: TEST_MODULE_ID,
      last_scroll_position: 2500,
      active_time_seconds: 120,
      sections_viewed: ['intro', 'chapter1', 'chapter2', 'conclusion']
    };

    const response = await request.post(`${API_BASE_URL}/api/progress/`, {
      data: progressData
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
    await loginUser(request, STUDENT_EMAIL, STUDENT_PASSWORD);

    // First save some progress
    await request.post(`${API_BASE_URL}/api/progress/`, {
      data: {
        enrollment_id: TEST_ENROLLMENT_ID,
        module_id: TEST_MODULE_ID,
        last_scroll_position: 1800,
        active_time_seconds: 90,
        sections_viewed: ['intro', 'chapter1']
      }
    });

    // Retrieve progress
    const response = await request.get(
      `${API_BASE_URL}/api/progress/${TEST_USER_ID}/module/${TEST_MODULE_ID}`
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
    await loginUser(request, STUDENT_EMAIL, STUDENT_PASSWORD);

    // Save initial progress
    await request.post(`${API_BASE_URL}/api/progress/`, {
      data: {
        enrollment_id: TEST_ENROLLMENT_ID,
        module_id: TEST_MODULE_ID,
        last_scroll_position: 1000,
        active_time_seconds: 30,
        sections_viewed: ['intro']
      }
    });

    // Update progress
    const updateResponse = await request.post(`${API_BASE_URL}/api/progress/`, {
      data: {
        enrollment_id: TEST_ENROLLMENT_ID,
        module_id: TEST_MODULE_ID,
        last_scroll_position: 3000,
        active_time_seconds: 150,
        sections_viewed: ['intro', 'chapter1', 'chapter2']
      }
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
    await loginUser(request, STUDENT_EMAIL, STUDENT_PASSWORD);

    // Get overall progress
    const response = await request.get(
      `${API_BASE_URL}/api/progress/${TEST_USER_ID}`
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
      `${API_BASE_URL}/api/progress/${TEST_USER_ID}/module/${TEST_MODULE_ID}`
    );

    // Should be unauthorized
    expect(response.status()).toBe(401);
  });
});

test.describe('ModuleProgressTracker Component', () => {

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
    await page.click('text=Module 1');

    // Wait for module content to load
    await page.waitForLoadState('networkidle');

    // Scroll down the page
    await page.evaluate(() => window.scrollTo(0, 1500));
    await page.waitForTimeout(2000); // Wait for tracker to register scroll

    // Check console for progress tracker logs (optional)
    const consoleLogs: string[] = [];
    page.on('console', msg => {
      if (msg.text().includes('ModuleProgressTracker') || msg.text().includes('Progress saved')) {
        consoleLogs.push(msg.text());
      }
    });

    // Wait for auto-save (30 seconds + buffer)
    await page.waitForTimeout(35000);

    // Verify progress was saved via API
    const apiContext = await page.context().request;
    const progressResponse = await apiContext.get(
      `${API_BASE_URL}/api/progress/${TEST_USER_ID}/module/${TEST_MODULE_ID}`
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
    const loginResponse = await apiContext.post(`${API_BASE_URL}/api/auth/login`, {
      data: { email: STUDENT_EMAIL, password: STUDENT_PASSWORD }
    });
    expect(loginResponse.ok()).toBeTruthy();

    // Save progress with specific scroll position
    await apiContext.post(`${API_BASE_URL}/api/progress/`, {
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
    await page.click('text=Module 1');

    // Wait for scroll restoration
    await page.waitForTimeout(2000);

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
    await page.click('text=Module 1');
    await page.waitForLoadState('networkidle');

    // Simulate user activity
    await page.mouse.move(100, 100);
    await page.waitForTimeout(3000);
    await page.mouse.move(200, 200);
    await page.waitForTimeout(3000);

    // Wait for auto-save
    await page.waitForTimeout(35000);

    // Verify active time was tracked
    const apiContext = await page.context().request;
    const progressResponse = await apiContext.get(
      `${API_BASE_URL}/api/progress/${TEST_USER_ID}/module/${TEST_MODULE_ID}`
    );

    const progress = await progressResponse.json();
    expect(progress.active_time_seconds).toBeGreaterThan(5); // At least 6 seconds
  });
});

test.describe('Progress Integration Tests', () => {

  test('should persist progress across page reloads', async ({ page }) => {
    // Login
    await page.goto(STUDENT_PORTAL_URL);
    await page.fill('input[type="email"]', STUDENT_EMAIL);
    await page.fill('input[type="password"]', STUDENT_PASSWORD);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');

    // Navigate to module
    await page.click('text=Modules');
    await page.click('text=Module 1');
    await page.waitForLoadState('networkidle');

    // Scroll and wait for save
    await page.evaluate(() => window.scrollTo(0, 1200));
    await page.waitForTimeout(35000); // Wait for auto-save

    // Get current scroll position via API
    const apiContext = await page.context().request;
    const progressBefore = await apiContext.get(
      `${API_BASE_URL}/api/progress/${TEST_USER_ID}/module/${TEST_MODULE_ID}`
    );
    const beforeData = await progressBefore.json();

    // Reload page
    await page.reload();
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Verify scroll was restored
    const scrollY = await page.evaluate(() => window.scrollY);
    expect(Math.abs(scrollY - beforeData.last_scroll_position)).toBeLessThan(100);

    // Verify progress is still available
    const progressAfter = await apiContext.get(
      `${API_BASE_URL}/api/progress/${TEST_USER_ID}/module/${TEST_MODULE_ID}`
    );
    const afterData = await progressAfter.json();

    expect(afterData.last_scroll_position).toBe(beforeData.last_scroll_position);
    expect(afterData.active_time_seconds).toBeGreaterThanOrEqual(beforeData.active_time_seconds);
  });
});
