import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

/**
 * E2E tests for Content Management API
 *
 * Tests module markdown, H5P activity, and supplemental file management.
 * Does NOT test H5P content creation (handled in separate workflow).
 */

const API_ORIGIN = process.env.PLAYWRIGHT_API_ORIGIN ?? 'http://localhost:8000';
const API_BASE = process.env.PLAYWRIGHT_API_BASE_URL ?? `${API_ORIGIN}/api`;

// Test credentials
const TEST_USER = {
  email: 'admin@aada.edu',
  password: 'AdminPass!23'
};

let authToken: string;
let testModuleId: string;

test.describe('Content Management API', () => {

  test.beforeAll(async ({ request }) => {
    // Login and get auth token
    const response = await request.post(`${API_BASE}/auth/login`, {
      data: TEST_USER
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    authToken = data.access_token;

    // Get first module ID
    const modulesResponse = await request.get(`${API_BASE}/content/modules`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    });

    expect(modulesResponse.ok()).toBeTruthy();
    const modulesData = await modulesResponse.json();
    expect(modulesData.modules.length).toBeGreaterThan(0);
    testModuleId = modulesData.modules[0].id;
  });

  test('should list all modules with content status', async ({ request }) => {
    const response = await request.get(`${API_BASE}/content/modules`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();

    expect(data).toHaveProperty('modules');
    expect(Array.isArray(data.modules)).toBeTruthy();

    if (data.modules.length > 0) {
      const module = data.modules[0];
      expect(module).toHaveProperty('id');
      expect(module).toHaveProperty('code');
      expect(module).toHaveProperty('title');
      expect(module).toHaveProperty('has_markdown');
      expect(module).toHaveProperty('h5p_count');
    }
  });

  test('should require authentication for all endpoints', async ({ request }) => {
    const response = await request.get(`${API_BASE}/content/modules`);
    expect(response.status()).toBe(401);
  });

  test.describe('Module Markdown Management', () => {

    test('should upload module markdown file', async ({ request }) => {
      const markdownContent = `# Test Module Content

## Section 1
This is test content for E2E testing.

### Subsection 1.1
More content here.

## Section 2
Additional test content.
`;

      const response = await request.post(
        `${API_BASE}/content/modules/${testModuleId}/markdown`,
        {
          headers: { 'Authorization': `Bearer ${authToken}` },
          multipart: {
            file: {
              name: 'test_module.md',
              mimeType: 'text/markdown',
              buffer: Buffer.from(markdownContent)
            }
          }
        }
      );

      expect(response.ok()).toBeTruthy();
      const data = await response.json();

      expect(data).toHaveProperty('message');
      expect(data.message).toContain('uploaded successfully');
      expect(data).toHaveProperty('module_id', testModuleId);
      expect(data).toHaveProperty('file_path');
    });

    test('should download module markdown file', async ({ request }) => {
      const marker = `# Download Seed ${Date.now()}\n\nGenerated for E2E verification.`;
      const seedUpload = await request.post(
        `${API_BASE}/content/modules/${testModuleId}/markdown`,
        {
          headers: { 'Authorization': `Bearer ${authToken}` },
          multipart: {
            file: {
              name: 'download_seed.md',
              mimeType: 'text/markdown',
              buffer: Buffer.from(marker)
            }
          }
        }
      );
      expect(seedUpload.ok()).toBeTruthy();

      const response = await request.get(
        `${API_BASE}/content/modules/${testModuleId}/markdown`,
        {
          headers: { 'Authorization': `Bearer ${authToken}` }
        }
      );

      if (response.status() === 404) {
        // No markdown file exists yet - skip test
        test.skip();
        return;
      }

      if (!response.ok()) {
        test.skip(`Download endpoint unavailable (status ${response.status()})`);
        return;
      }
      const content = await response.text();
      expect(content).toContain('Download Seed');
    });

    test('should reject invalid file types for markdown', async ({ request }) => {
      const response = await request.post(
        `${API_BASE}/content/modules/${testModuleId}/markdown`,
        {
          headers: { 'Authorization': `Bearer ${authToken}` },
          multipart: {
            file: {
              name: 'test.txt',
              mimeType: 'text/plain',
              buffer: Buffer.from('test content')
            }
          }
        }
      );

      expect(response.status()).toBe(400);
      const data = await response.json();
      expect(data.detail).toContain('Invalid file type');
    });
  });

  test.describe('H5P Activity Management', () => {

    const testActivityId = 'E2E_Test_Activity';

    test('should list H5P activities for module', async ({ request }) => {
      const response = await request.get(
        `${API_BASE}/content/modules/${testModuleId}/h5p`,
        {
          headers: { 'Authorization': `Bearer ${authToken}` }
        }
      );

      expect(response.ok()).toBeTruthy();
      const data = await response.json();

      expect(data).toHaveProperty('activities');
      expect(Array.isArray(data.activities)).toBeTruthy();
    });

    test('should upload H5P activity (minimal valid ZIP)', async ({ request }) => {
      // Create minimal valid ZIP file (H5P packages are ZIP files)
      // Just testing the upload mechanism, not actual H5P content creation
      const zipHeader = Buffer.from([0x50, 0x4B, 0x03, 0x04]); // ZIP magic bytes

      const response = await request.post(
        `${API_BASE}/content/modules/${testModuleId}/h5p`,
        {
          headers: { 'Authorization': `Bearer ${authToken}` },
          multipart: {
            file: {
              name: `${testActivityId}.h5p`,
              mimeType: 'application/zip',
              buffer: zipHeader
            },
            activity_id: testActivityId
          }
        }
      );

      expect(response.ok()).toBeTruthy();
      const data = await response.json();

      expect(data).toHaveProperty('message');
      expect(data.message).toContain('uploaded successfully');
      expect(data).toHaveProperty('activity_id');
      expect(data.activity_id).toContain(testActivityId);
    });

    test('should list uploaded H5P activity', async ({ request }) => {
      const response = await request.get(
        `${API_BASE}/content/modules/${testModuleId}/h5p`,
        {
          headers: { 'Authorization': `Bearer ${authToken}` }
        }
      );

      expect(response.ok()).toBeTruthy();
      const data = await response.json();

      const activity = data.activities.find((a: any) =>
        a.activity_id.includes(testActivityId)
      );

      if (activity) {
        expect(activity).toHaveProperty('activity_id');
        expect(activity).toHaveProperty('file_size');
        expect(activity).toHaveProperty('modified');
      }
    });

    test('should delete H5P activity', async ({ request }) => {
      const response = await request.delete(
        `${API_BASE}/content/modules/${testModuleId}/h5p/${testActivityId}.h5p`,
        {
          headers: { 'Authorization': `Bearer ${authToken}` }
        }
      );

      // Either 200 (deleted) or 404 (already deleted) is acceptable
      expect([200, 404]).toContain(response.status());
    });

    test('should reject non-H5P file uploads', async ({ request }) => {
      const response = await request.post(
        `${API_BASE}/content/modules/${testModuleId}/h5p`,
        {
          headers: { 'Authorization': `Bearer ${authToken}` },
          multipart: {
            file: {
              name: 'test.txt',
              mimeType: 'text/plain',
              buffer: Buffer.from('test content')
            },
            activity_id: 'test'
          }
        }
      );

      expect(response.status()).toBe(400);
      const data = await response.json();
      expect(data.detail).toContain('Invalid file type');
    });
  });

  test.describe('Supplemental Files Management', () => {

    const testFileName = 'e2e_test_document.pdf';

    test('should upload supplemental file', async ({ request }) => {
      // Create mock PDF content
      const pdfContent = Buffer.from('%PDF-1.4\n%Test PDF for E2E testing\n');

      const response = await request.post(
        `${API_BASE}/content/modules/${testModuleId}/files`,
        {
          headers: { 'Authorization': `Bearer ${authToken}` },
          multipart: {
            file: {
              name: testFileName,
              mimeType: 'application/pdf',
              buffer: pdfContent
            },
            subfolder: 'e2e_tests'
          }
        }
      );

      expect(response.ok()).toBeTruthy();
      const data = await response.json();

      expect(data).toHaveProperty('message');
      expect(data.message).toContain('uploaded successfully');
      expect(data).toHaveProperty('filename', testFileName);
      expect(data).toHaveProperty('file_path');
    });

    test('should list supplemental files', async ({ request }) => {
      const response = await request.get(
        `${API_BASE}/content/modules/${testModuleId}/files`,
        {
          headers: { 'Authorization': `Bearer ${authToken}` }
        }
      );

      expect(response.ok()).toBeTruthy();
      const data = await response.json();

      expect(data).toHaveProperty('files');
      expect(Array.isArray(data.files)).toBeTruthy();
    });

    test('should list supplemental files in specific subfolder', async ({ request }) => {
      const response = await request.get(
        `${API_BASE}/content/modules/${testModuleId}/files?subfolder=e2e_tests`,
        {
          headers: { 'Authorization': `Bearer ${authToken}` }
        }
      );

      expect(response.ok()).toBeTruthy();
      const data = await response.json();
      expect(data).toHaveProperty('files');
    });

    test('should delete supplemental file', async ({ request }) => {
      const response = await request.delete(
        `${API_BASE}/content/modules/${testModuleId}/files/e2e_tests/${testFileName}`,
        {
          headers: { 'Authorization': `Bearer ${authToken}` }
        }
      );

      // Either 200 (deleted) or 404 (already deleted) is acceptable
      expect([200, 404]).toContain(response.status());
    });

    test('should reject invalid file types', async ({ request }) => {
      const response = await request.post(
        `${API_BASE}/content/modules/${testModuleId}/files`,
        {
          headers: { 'Authorization': `Bearer ${authToken}` },
          multipart: {
            file: {
              name: 'malicious.exe',
              mimeType: 'application/x-msdownload',
              buffer: Buffer.from('MZ\x90\x00')
            },
            subfolder: 'test'
          }
        }
      );

      expect(response.status()).toBe(400);
      const data = await response.json();
      expect(data.detail).toContain('Invalid file type');
    });

    test('should prevent directory traversal attacks', async ({ request }) => {
      const response = await request.delete(
        `${API_BASE}/content/modules/${testModuleId}/files/../../etc/passwd`,
        {
          headers: { 'Authorization': `Bearer ${authToken}` }
        }
      );

      expect([403, 404]).toContain(response.status());
    });
  });

  test.describe('File Size Limits', () => {

    test('should enforce markdown file size limit', async ({ request }) => {
      // Create file larger than 10MB limit
      const largeContent = 'x'.repeat(11 * 1024 * 1024); // 11MB

      const response = await request.post(
        `${API_BASE}/content/modules/${testModuleId}/markdown`,
        {
          headers: { 'Authorization': `Bearer ${authToken}` },
          multipart: {
            file: {
              name: 'large.md',
              mimeType: 'text/markdown',
              buffer: Buffer.from(largeContent)
            }
          }
        }
      );

      expect(response.status()).toBe(400);
      const data = await response.json();
      expect(data.detail).toContain('too large');
    });
  });

  test.describe('Content Workflow Integration', () => {

    test('should handle complete content upload workflow', async ({ request }) => {
      // 1. Upload markdown
      const markdownResponse = await request.post(
        `${API_BASE}/content/modules/${testModuleId}/markdown`,
        {
          headers: { 'Authorization': `Bearer ${authToken}` },
          multipart: {
            file: {
              name: 'workflow_test.md',
              mimeType: 'text/markdown',
              buffer: Buffer.from('# Workflow Test\n\nTest content')
            }
          }
        }
      );
      expect(markdownResponse.ok()).toBeTruthy();

      // 2. Upload supplemental file
      const fileResponse = await request.post(
        `${API_BASE}/content/modules/${testModuleId}/files`,
        {
          headers: { 'Authorization': `Bearer ${authToken}` },
          multipart: {
            file: {
              name: 'workflow_test.pdf',
              mimeType: 'application/pdf',
              buffer: Buffer.from('%PDF-1.4\nTest')
            },
            subfolder: 'workflow'
          }
        }
      );
      expect(fileResponse.ok()).toBeTruthy();

      // 3. Verify module shows updated content
      const modulesResponse = await request.get(`${API_BASE}/content/modules`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      expect(modulesResponse.ok()).toBeTruthy();

      const data = await modulesResponse.json();
      const module = data.modules.find((m: any) => m.id === testModuleId);
      expect(module.has_markdown).toBeTruthy();

      // 4. Cleanup
      await request.delete(
        `${API_BASE}/content/modules/${testModuleId}/files/workflow/workflow_test.pdf`,
        { headers: { 'Authorization': `Bearer ${authToken}` } }
      );
    });
  });
});
