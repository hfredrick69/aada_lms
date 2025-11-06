import { test, expect } from '@playwright/test';

test('Debug Leads page', async ({ page }) => {
  // Login as admin
  await page.goto('http://localhost:5173/login');
  await page.fill('input[name="email"]', 'admin@aada.edu');
  await page.fill('input[name="password"]', 'AdminPass!23');
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard');

  // Navigate to Leads page
  await page.goto('http://localhost:5173/leads');
  await page.waitForLoadState('networkidle');

  // Take screenshot
  await page.screenshot({ path: 'leads-page-debug.png', fullPage: true });

  // Print page content
  const content = await page.content();
  console.log('Page HTML:', content.substring(0, 1000));

  // Check for errors in console
  page.on('console', msg => console.log('BROWSER:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));

  // Wait a bit
  await page.waitForTimeout(5000);

  // Take another screenshot
  await page.screenshot({ path: 'leads-page-after-wait.png', fullPage: true });
});
