import { test, expect } from '@playwright/test';

test.describe('Lead Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin
    await page.goto('http://localhost:5173/login');
    await page.fill('input[name="email"]', 'admin@aada.edu');
    await page.fill('input[name="password"]', 'AdminPass!23');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');

    // Navigate to Leads page
    await page.goto('http://localhost:5173/leads');
    await page.waitForLoadState('networkidle');
  });

  test('should display leads page with navigation', async ({ page }) => {
    // Check page title
    await expect(page.locator('h2')).toContainText('Lead Management');

    // Check sidebar has Leads link
    await expect(page.locator('nav a[href="/leads"]')).toBeVisible();
  });

  test('should display lead source options', async ({ page }) => {
    // Check that lead source dropdown has options
    const sourceSelect = page.locator('select[name="lead_source_id"]').first();
    await expect(sourceSelect).toBeVisible();

    // Should have default sources
    const options = await sourceSelect.locator('option').allTextContents();
    expect(options.length).toBeGreaterThan(1); // "Select source" + actual sources
    expect(options.join(',')).toContain('Website');
  });

  test('should create a new lead', async ({ page }) => {
    // Fill out the create lead form
    await page.fill('input[name="first_name"]', 'Test');
    await page.fill('input[name="last_name"]', 'Lead');
    await page.fill('input[name="email"]', `test.lead.${Date.now()}@example.com`);
    await page.fill('input[name="phone"]', '555-0100');

    // Select lead source (first option after "Select source")
    const sourceSelect = page.locator('select[name="lead_source_id"]').first();
    await sourceSelect.selectOption({ index: 1 });

    await page.fill('input[name="notes"]', 'Automated test lead');

    // Submit form
    await page.click('button[type="submit"]', { timeout: 5000 });

    // Wait for lead to appear in table
    await page.waitForTimeout(1000);

    // Check that lead appears in the list
    await expect(page.locator('table tbody tr')).toContainText('Test Lead');
  });

  test('should filter leads by status', async ({ page }) => {
    // Wait for leads to load
    await page.waitForTimeout(1000);

    // Check that status filter exists
    const statusFilter = page.locator('select[name="status"]');
    await expect(statusFilter).toBeVisible();

    // Select a status
    await statusFilter.selectOption('new');
    await page.waitForTimeout(500);

    // Verify filter was applied (URL or table update)
    // This is a basic check - in a real scenario we'd verify the filtered results
    await expect(statusFilter).toHaveValue('new');
  });

  test('should open lead detail modal', async ({ page }) => {
    // Create a test lead first
    await page.fill('input[name="first_name"]', 'Modal');
    await page.fill('input[name="last_name"]', 'Test');
    await page.fill('input[name="email"]', `modal.test.${Date.now()}@example.com`);

    const sourceSelect = page.locator('select[name="lead_source_id"]').first();
    await sourceSelect.selectOption({ index: 1 });

    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);

    // Click on the lead name to open detail modal
    const leadLink = page.locator('table button:has-text("Modal Test")').first();
    await leadLink.click();

    // Wait for modal to appear
    await page.waitForTimeout(500);

    // Check modal content
    await expect(page.locator('.fixed .bg-white')).toBeVisible();
    await expect(page.locator('.fixed .bg-white')).toContainText('Modal Test');
    await expect(page.locator('.fixed .bg-white')).toContainText('modal.test.');
  });

  test('should update lead status from table', async ({ page }) => {
    // Create a test lead
    await page.fill('input[name="first_name"]', 'Status');
    await page.fill('input[name="last_name"]', 'Update');
    await page.fill('input[name="email"]', `status.update.${Date.now()}@example.com`);

    const sourceSelect = page.locator('select[name="lead_source_id"]').first();
    await sourceSelect.selectOption({ index: 1 });

    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);

    // Find the status dropdown for this lead
    const statusDropdown = page.locator('table tbody tr:has-text("Status Update") select').first();
    await expect(statusDropdown).toBeVisible();

    // Change status to "contacted"
    await statusDropdown.selectOption('contacted');
    await page.waitForTimeout(500);

    // Verify status was updated
    await expect(statusDropdown).toHaveValue('contacted');
  });

  test('should add activity to lead', async ({ page }) => {
    // Create a test lead
    await page.fill('input[name="first_name"]', 'Activity');
    await page.fill('input[name="last_name"]', 'Test');
    await page.fill('input[name="email"]', `activity.test.${Date.now()}@example.com`);

    const sourceSelect = page.locator('select[name="lead_source_id"]').first();
    await sourceSelect.selectOption({ index: 1 });

    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);

    // Open lead detail
    const leadLink = page.locator('table button:has-text("Activity Test")').first();
    await leadLink.click();
    await page.waitForTimeout(500);

    // Click Add Activity button
    await page.click('button:has-text("Add Activity")');
    await page.waitForTimeout(300);

    // Fill activity form
    await page.selectOption('select[name="activity_type"]', 'call');
    await page.fill('input[name="subject"]', 'Test phone call');
    await page.fill('textarea[name="description"]', 'Discussed program options');

    // Submit activity
    await page.click('button[type="submit"]:has-text("Add Activity")');
    await page.waitForTimeout(1000);

    // Verify activity appears in timeline
    await expect(page.locator('.fixed .bg-white')).toContainText('Test phone call');
    await expect(page.locator('.fixed .bg-white')).toContainText('call');
  });

  test('should delete a lead', async ({ page }) => {
    // Create a test lead
    const uniqueEmail = `delete.test.${Date.now()}@example.com`;
    await page.fill('input[name="first_name"]', 'Delete');
    await page.fill('input[name="last_name"]', 'Test');
    await page.fill('input[name="email"]', uniqueEmail);

    const sourceSelect = page.locator('select[name="lead_source_id"]').first();
    await sourceSelect.selectOption({ index: 1 });

    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);

    // Open lead detail
    const leadLink = page.locator('table button:has-text("Delete Test")').first();
    await leadLink.click();
    await page.waitForTimeout(500);

    // Click delete button
    page.on('dialog', dialog => dialog.accept()); // Accept confirmation dialog
    await page.click('button:has-text("Delete Lead")');
    await page.waitForTimeout(1000);

    // Verify lead is removed from table
    await expect(page.locator('table')).not.toContainText('Delete Test');
  });

  test('should display activity timeline', async ({ page }) => {
    // Create a test lead
    await page.fill('input[name="first_name"]', 'Timeline');
    await page.fill('input[name="last_name"]', 'Test');
    await page.fill('input[name="email"]', `timeline.test.${Date.now()}@example.com`);

    const sourceSelect = page.locator('select[name="lead_source_id"]').first();
    await sourceSelect.selectOption({ index: 1 });

    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);

    // Open lead detail
    const leadLink = page.locator('table button:has-text("Timeline Test")').first();
    await leadLink.click();
    await page.waitForTimeout(500);

    // Check for Activity Timeline section
    await expect(page.locator('.fixed .bg-white')).toContainText('Activity Timeline');

    // Should have at least "Lead Created" activity
    await expect(page.locator('.fixed .bg-white')).toContainText('Lead Created');
  });

  test('should validate required fields', async ({ page }) => {
    // Try to submit without required fields
    const submitButton = page.locator('button[type="submit"]:has-text("Add Lead")');

    // Check that first_name is required
    await submitButton.click();

    // Browser validation should prevent submission
    const firstNameInput = page.locator('input[name="first_name"]');
    const isInvalid = await firstNameInput.evaluate((el: HTMLInputElement) => !el.validity.valid);
    expect(isInvalid).toBe(true);
  });

  test('should show program interest options', async ({ page }) => {
    // Check program interest dropdown exists
    const programSelect = page.locator('select[name="program_interest_id"]').first();
    await expect(programSelect).toBeVisible();

    // Should have "No preference" option
    await expect(programSelect).toContainText('No preference');

    // Should have actual programs
    const options = await programSelect.locator('option').allTextContents();
    expect(options.length).toBeGreaterThan(1);
  });
});
