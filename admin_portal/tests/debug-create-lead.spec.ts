import { test, expect } from '@playwright/test';

test('Debug create lead', async ({ page }) => {
  // Capture console messages and errors
  const messages = [];
  const errors = [];

  page.on('console', msg => messages.push(`CONSOLE: ${msg.type()}: ${msg.text()}`));
  page.on('pageerror', error => errors.push(`PAGE ERROR: ${error.message}`));

  // Login as admin
  await page.goto('http://localhost:5173/login');
  await page.fill('input[name="email"]', 'admin@aada.edu');
  await page.fill('input[name="password"]', 'AdminPass!23');
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard');

  // Navigate to Leads page
  await page.click('nav a[href="/leads"]');
  await page.waitForURL('**/leads');
  await page.waitForSelector('h2:has-text("Lead Management")');

  // Wait a bit for sources to load
  await page.waitForTimeout(2000);

  // Check what lead sources are available
  const sourceOptions = await page.locator('select[name="lead_source_id"]').first().locator('option').all();
  console.log(`Found ${sourceOptions.length} source options`);

  // Fill out the form
  await page.fill('input[name="first_name"]', 'Debug');
  await page.fill('input[name="last_name"]', 'Test');
  await page.fill('input[name="email"]', `debug.${Date.now()}@example.com`);
  await page.fill('input[name="phone"]', '555-1234');

  // Select lead source
  const sourceSelect = page.locator('select[name="lead_source_id"]').first();
  await sourceSelect.selectOption({ index: 1 });
  const selectedValue = await sourceSelect.inputValue();
  console.log('Selected source ID:', selectedValue);

  // Take screenshot before submit
  await page.screenshot({ path: 'before-submit.png' });

  // Submit
  await page.click('button[type="submit"]');

  // Wait a bit
  await page.waitForTimeout(3000);

  // Take screenshot after submit
  await page.screenshot({ path: 'after-submit.png' });

  // Check if table has any rows
  const tableRows = await page.locator('table tbody tr').count();
  console.log(`Table has ${tableRows} rows`);

  // Check for errors
  const errorDiv = await page.locator('.bg-red-50').textContent().catch(() => null);
  if (errorDiv) {
    console.log('Error message on page:', errorDiv);
  }

  // Print all messages and errors
  console.log('\n=== Console Messages ===');
  messages.forEach(m => console.log(m));
  console.log('\n=== Page Errors ===');
  errors.forEach(e => console.log(e));

  // Check page content
  const pageText = await page.locator('body').textContent();
  console.log('\nPage contains "Debug Test":', pageText.includes('Debug Test'));
  console.log('Page contains "No leads found":', pageText.includes('No leads found'));
});
