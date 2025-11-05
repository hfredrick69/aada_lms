import { defineConfig, devices } from '@playwright/test';

/**
 * E2E Test Configuration for AADA LMS
 *
 * Tests both student and admin portals for Phase 4 authentication compliance
 */
export default defineConfig({
  testDir: './e2e-tests',
  fullyParallel: false, // Run tests serially to avoid race conditions
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1, // Single worker to ensure test isolation
  reporter: 'html',

  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Assume servers are already running
  // Backend: http://localhost:8000
  // Student Portal: http://localhost:5173
  // Admin Portal: http://localhost:5174
});
