import { test, expect } from '@playwright/test';

/**
 * Lead-Based Document Signing E2E Tests
 *
 * Tests the complete workflow of sending documents to leads for signature
 * without requiring authentication.
 */

const ADMIN_EMAIL = 'admin@aada.edu';
const ADMIN_PASSWORD = 'AdminPass!23';
const API_BASE_URL = 'http://localhost:8000';
const STUDENT_PORTAL_URL = 'http://localhost:5174';

// Helper to login
async function loginAdmin(request: any) {
  const response = await request.post(`${API_BASE_URL}/api/auth/login`, {
    data: { email: ADMIN_EMAIL, password: ADMIN_PASSWORD }
  });
  expect(response.ok()).toBeTruthy();
  return response;
}

// Helper to get lead source
async function getOrCreateLeadSource(request: any): Promise<string> {
  const response = await request.get(`${API_BASE_URL}/api/crm/leads/sources`);
  if (response.ok()) {
    const sources = await response.json();
    if (sources.length > 0) {
      return sources[0].id;
    }
  }

  // Create one if none exist
  const createResp = await request.post(`${API_BASE_URL}/api/crm/leads/sources`, {
    data: {
      name: 'E2E Test Source',
      description: 'Test source for E2E testing'
    }
  });
  if (createResp.ok()) {
    const source = await createResp.json();
    return source.id;
  }

  return '';
}

test.describe('Lead Document Signing Workflow', () => {
  let leadId: string;
  let documentId: string;
  let signingToken: string;

  test('complete lead signing workflow', async ({ request, page }) => {
    // Step 1: Login as admin
    await loginAdmin(request);

    // Step 2: Get or create lead source
    const leadSourceId = await getOrCreateLeadSource(request);
    expect(leadSourceId).toBeTruthy();

    // Step 3: Create a new lead
    const timestamp = Date.now();
    const newLead = {
      first_name: 'Jane',
      last_name: 'Prospect',
      email: `jane.prospect.${timestamp}@test.com`,
      phone: '555-0123',
      lead_source_id: leadSourceId,
      notes: 'E2E test lead for document signing'
    };

    const leadResponse = await request.post(`${API_BASE_URL}/api/crm/leads`, {
      data: newLead
    });
    expect(leadResponse.status()).toBe(201);

    const created = await leadResponse.json();
    expect(created.email).toBe(newLead.email);
    leadId = created.id;

    // Step 4: Get existing template (assuming one exists)
    const templatesResp = await request.get(`${API_BASE_URL}/api/documents/templates`);
    if (!templatesResp.ok()) {
      console.log('No templates available, skipping document sending test');
      return;
    }

    const templates = await templatesResp.json();
    if (templates.length === 0) {
      console.log('No templates available, skipping document sending test');
      return;
    }

    const templateId = templates[0].id;

    // Step 5: Send document to lead
    const sendDocResp = await request.post(`${API_BASE_URL}/api/documents/send`, {
      data: {
        template_id: templateId,
        lead_id: leadId
      }
    });
    expect(sendDocResp.status()).toBe(200);

    const document = await sendDocResp.json();
    expect(document.lead_id).toBe(leadId);
    expect(document.signing_token).toBeTruthy();
    expect(document.status).toBe('pending');

    documentId = document.id;
    signingToken = document.signing_token;

    // Step 6: Access public signing page (no auth)
    const publicDocResp = await request.get(`${API_BASE_URL}/api/public/sign/${signingToken}`);
    expect(publicDocResp.status()).toBe(200);

    const publicDoc = await publicDocResp.json();
    expect(publicDoc.signer_name).toContain('Jane');
    expect(publicDoc.signer_email).toBe(newLead.email);

    // Step 7: Submit signature via public API
    const fakeSignature = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==';

    const signResp = await request.post(`${API_BASE_URL}/api/public/sign/${signingToken}`, {
      data: {
        signature_data: fakeSignature,
        typed_name: 'Jane Prospect'
      }
    });
    expect(signResp.status()).toBe(200);

    const signResult = await signResp.json();
    expect(signResult.success).toBe(true);

    // Step 8: Verify document status changed
    const verifyResp = await request.get(`${API_BASE_URL}/api/documents/${documentId}`);
    expect(verifyResp.status()).toBe(200);

    const verifiedDoc = await verifyResp.json();
    expect(['student_signed', 'completed']).toContain(verifiedDoc.status);
    expect(verifiedDoc.student_signed_at).toBeTruthy();
  });

  test('should reject invalid signing token', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/api/public/sign/invalid-token-abc123`);
    expect(response.status()).toBe(404);
  });

  test('should not allow signing twice with same token', async ({ request }) => {
    await loginAdmin(request);

    // Create lead and document
    const leadSourceId = await getOrCreateLeadSource(request);
    const timestamp = Date.now();

    const leadResp = await request.post(`${API_BASE_URL}/api/crm/leads`, {
      data: {
        first_name: 'Test',
        last_name: 'DoubleSign',
        email: `double.${timestamp}@test.com`,
        lead_source_id: leadSourceId
      }
    });

    if (!leadResp.ok()) return;
    const lead = await leadResp.json();

    // Get template
    const templatesResp = await request.get(`${API_BASE_URL}/api/documents/templates`);
    if (!templatesResp.ok()) return;
    const templates = await templatesResp.json();
    if (templates.length === 0) return;

    // Send document
    const docResp = await request.post(`${API_BASE_URL}/api/documents/send`, {
      data: {
        template_id: templates[0].id,
        lead_id: lead.id
      }
    });

    if (!docResp.ok()) return;
    const doc = await docResp.json();

    // Sign once
    const sig = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==';
    const firstSign = await request.post(`${API_BASE_URL}/api/public/sign/${doc.signing_token}`, {
      data: {
        signature_data: sig,
        typed_name: 'Test DoubleSign'
      }
    });
    expect(firstSign.status()).toBe(200);

    // Try to sign again
    const secondSign = await request.post(`${API_BASE_URL}/api/public/sign/${doc.signing_token}`, {
      data: {
        signature_data: sig,
        typed_name: 'Test DoubleSign'
      }
    });
    expect(secondSign.status()).toBe(400);
  });

  test('should enforce rate limiting on public endpoints', async ({ request }) => {
    const testToken = 'rate-limit-test-token';

    // Make multiple rapid requests
    const requests = [];
    for (let i = 0; i < 15; i++) {
      requests.push(request.get(`${API_BASE_URL}/api/public/sign/${testToken}`));
    }

    const responses = await Promise.all(requests);

    // At least one should be rate limited (429)
    const rateLimited = responses.some(r => r.status() === 429);
    expect(rateLimited).toBe(true);
  });

  test('should have audit trail for signed document', async ({ request }) => {
    if (!documentId) {
      test.skip();
    }

    await loginAdmin(request);

    const response = await request.get(`${API_BASE_URL}/api/documents/${documentId}/audit-trail`);
    expect(response.status()).toBe(200);

    const audit = await response.json();
    expect(audit.logs).toBeTruthy();
    expect(Array.isArray(audit.logs)).toBe(true);

    if (audit.logs.length > 0) {
      const eventTypes = audit.logs.map((log: any) => log.event_type);
      expect(eventTypes).toContain('document_sent');
    }
  });

  test('should validate signature data format', async ({ request }) => {
    await loginAdmin(request);

    const leadSourceId = await getOrCreateLeadSource(request);
    const timestamp = Date.now();

    // Create test lead
    const leadResp = await request.post(`${API_BASE_URL}/api/crm/leads`, {
      data: {
        first_name: 'Validation',
        last_name: 'Test',
        email: `validation.${timestamp}@test.com`,
        lead_source_id: leadSourceId
      }
    });

    if (!leadResp.ok()) return;
    const lead = await leadResp.json();

    // Get template
    const templatesResp = await request.get(`${API_BASE_URL}/api/documents/templates`);
    if (!templatesResp.ok()) return;
    const templates = await templatesResp.json();
    if (templates.length === 0) return;

    // Send document
    const docResp = await request.post(`${API_BASE_URL}/api/documents/send`, {
      data: {
        template_id: templates[0].id,
        lead_id: lead.id
      }
    });

    if (!docResp.ok()) return;
    const doc = await docResp.json();

    // Try with empty signature
    const emptySignResp = await request.post(`${API_BASE_URL}/api/public/sign/${doc.signing_token}`, {
      data: {
        signature_data: '',
        typed_name: 'Validation Test'
      }
    });
    expect(emptySignResp.status()).toBe(400);

    // Try with empty name
    const emptyNameResp = await request.post(`${API_BASE_URL}/api/public/sign/${doc.signing_token}`, {
      data: {
        signature_data: 'validBase64Data',
        typed_name: ''
      }
    });
    expect(emptyNameResp.status()).toBe(400);
  });
});
