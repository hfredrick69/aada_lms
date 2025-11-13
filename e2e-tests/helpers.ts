import type { APIRequestContext, Page } from '@playwright/test';
import { Buffer } from 'buffer';

const E2E_HOST = process.env.E2E_HOST ?? 'localhost';
const DEFAULT_API_ORIGIN = process.env.PLAYWRIGHT_API_ORIGIN ?? `http://${E2E_HOST}:8000`;
export const API_BASE_URL = process.env.PLAYWRIGHT_API_BASE_URL ?? `${DEFAULT_API_ORIGIN}/api`;
const PUBLIC_SIGN_BASE = `${API_BASE_URL}/public/sign`;

const SAMPLE_SIGNATURE = Buffer.from('Automated Playwright signature').toString('base64');

const SAMPLE_PDF_BASE64 =
  'JVBERi0xLjMKJZOMi54gUmVwb3J0TGFiIEdlbmVyYXRlZCBQREYgZG9jdW1lbnQgaHR0cDovL3d3dy5yZXBvcnRsYWIuY29tCjEgMCBvYmoKPDwKL0YxIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9CYXNlRm9udCAvSGVsdmV0aWNhIC9FbmNvZGluZyAvV2luQW5zaUVuY29kaW5nIC9OYW1lIC9GMSAvU3VidHlwZSAvVHlwZTEgL1R5cGUgL0ZvbnQKPj4KZW5kb2JqCjMgMCBvYmoKPDwKL0NvbnRlbnRzIDcgMCBSIC9NZWRpYUJveCBbIDAgMCA1OTUuMjc1NiA4NDEuODg5OCBdIC9QYXJlbnQgNiAwIFIgL1Jlc291cmNlcyA8PAovRm9udCAxIDAgUiAvUHJvY1NldCBbIC9QREYgL1RleHQgL0ltYWdlQiAvSW1hZ2VDIC9JbWFnZUkgXQo+PiAvUm90YXRlIDAgL1RyYW5zIDw8Cgo+PiAKICAvVHlwZSAvUGFnZQo+PgplbmRvYmoKNCAwIG9iago8PAovUGFnZU1vZGUgL1VzZU5vbmUgL1BhZ2VzIDYgMCBSIC9UeXBlIC9DYXRhbG9nCj4+CmVuZG9iago1IDAgb2JqCjw8Ci9BdXRob3IgKGFub255bW91cykgL0NyZWF0aW9uRGF0ZSAoRDoyMDI1MTExMjE4MjM1OC0wNScwMCcpIC9DcmVhdG9yIChSZXBvcnRMYWIgUERGIExpYnJhcnkgLSB3d3cucmVwb3J0bGFiLmNvbSkgL0tleXdvcmRzICgpIC9Nb2REYXRlIChEOjIwMjUxMTEyMTgyMzU4LTA1JzAwJykgL1Byb2R1Y2VyIChSZXBvcnRMYWIgUERGIExpYnJhcnkgLSB3d3cucmVwb3J0bGFiLmNvbSkgCiAgL1N1YmplY3QgKHVuc3BlY2lmaWVkKSAvVGl0bGUgKHVudGl0bGVkKSAvVHJhcHBlZCAvRmFsc2UKPj4KZW5kb2JqCjYgMCBvYmoKPDwKL0NvdW50IDEgL0tpZHMgWyAzIDAgUiBdIC9UeXBlIC9QYWdlcwo+PgplbmRvYmoKNyAwIG9iago8PAovRmlsdGVyIFsgL0FTQ0lJODVEZWNvZGUgL0ZsYXRlRGVjb2RlIF0gL0xlbmd0aCAxNjkKPj4Kc3RyZWFtCkdhclcwXWFobjUmOzBeQEtoI01WXExJWzM8MFc3MD82RmhNNT11aVlLX0hpLiYuSFhHQVVUXzljckRwYStUTk5tXEthb1kqXkUxNG4vYV9PKylXRj47T10+O3BWal9HZiYyKEhbOUpRPDlbV19bQHQ/Y2hPXzovOVlNZEJsVjEoI2xJKiY9MWE9YzhcQCMsLVc/PUIrQk5bVSZgPF4vNk4qXGlqNTVsfj5lbmRzdHJlYW0KZW5kb2JqCnhyZWYKMCA4CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDA3MyAwMDAwMCBuIAowMDAwMDAwMTA0IDAwMDAwIG4gCjAwMDAwMDAyMTEgMDAwMDAgbiAKMDAwMDAwMDQxNCAwMDAwMCBuIAowMDAwMDAwNDgyIDAwMDAwIG4gCjAwMDAwMDA3NzggMDAwMDAgbiAKMDAwMDAwMDgzNyAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9JRCAKWzw4NWUzYTgxYjUzNTIyYTc1NjlhNzMwNWYxNjM4M2QxYz48ODVlM2E4MWI1MzUyMmE3NTY5YTczMDVmMTYzODNkMWM+XQolIFJlcG9ydExhYiBnZW5lcmF0ZWQgUERGIGRvY3VtZW50IC0tIGRpZ2VzdCAoaHR0cDovL3d3dy5yZXBvcnRsYWIuY29tKQoKL0luZm8gNSAwIFIKL1Jvb3QgNCAwIFIKL1NpemUgOAo+PgpzdGFydHhyZWYKMTA5NgolJUVPRgo=';

const SAMPLE_PDF_BUFFER = Buffer.from(SAMPLE_PDF_BASE64, 'base64');

export async function apiLogin(request: APIRequestContext, email: string, password: string): Promise<string> {
  const response = await request.post(`${API_BASE_URL}/auth/login`, {
    data: { email, password },
  });
  if (response.status() !== 200) {
    throw new Error(`Login failed with status ${response.status()}`);
  }
  const body = await response.json();
  return body.access_token;
}

export async function ensureEnrollmentTemplate(request: APIRequestContext, token: string) {
  const headers = { Authorization: `Bearer ${token}` };
  const listResponse = await request.get(`${API_BASE_URL}/documents/templates`, { headers });
  const templatePayload = await listResponse.json();
  const templates = Array.isArray(templatePayload) ? templatePayload : [];

  const namedTemplate = templates.find(
    (tpl: any) => typeof tpl?.name === 'string' && tpl.name.includes('Enrollment Agreement'),
  );
  if (namedTemplate?.requires_counter_signature) {
    return namedTemplate;
  }

  const anyCounterTemplate = templates.find((tpl: any) => tpl?.requires_counter_signature);
  if (anyCounterTemplate) {
    return anyCounterTemplate;
  }

  const version = `e2e-${Date.now()}`;
  const createResponse = await request.post(`${API_BASE_URL}/documents/templates`, {
    headers,
    multipart: {
      name: 'Enrollment Agreement',
      version,
      description: 'Automated template',
      requires_counter_signature: 'true',
      file: {
        name: 'agreement.pdf',
        mimeType: 'application/pdf',
        buffer: SAMPLE_PDF_BUFFER,
      },
    },
  });

  if (createResponse.status() !== 200) {
    throw new Error(`Template upload failed: ${createResponse.status()}`);
  }
  return await createResponse.json();
}

export async function getStudentByEmail(request: APIRequestContext, token: string, email: string) {
  const response = await request.get(`${API_BASE_URL}/students`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const body = await response.json();
  const students = Array.isArray(body)
    ? body
    : Array.isArray(body?.students)
      ? body.students
      : [];
  const student = students.find((s: any) => s.email === email);
  if (!student) {
    throw new Error(`Student ${email} not found`);
  }
  return student;
}

export async function ensureStudentExists(
  request: APIRequestContext,
  token: string,
  student: { email: string; password?: string; first_name?: string; last_name?: string },
) {
  try {
    return await getStudentByEmail(request, token, student.email);
  } catch (err) {
    const response = await request.post(`${API_BASE_URL}/students`, {
      headers: { Authorization: `Bearer ${token}` },
      data: {
        email: student.email,
        password: student.password ?? 'StudentPass!23',
        first_name: student.first_name ?? 'Playwright',
        last_name: student.last_name ?? 'Student',
      },
    });
    if (response.status() === 201) {
      return await response.json();
    }

    if (response.status() === 400) {
      const body = await response.json();
      if (body?.detail?.includes('Email already registered')) {
        return await getStudentByEmail(request, token, student.email);
      }
    }

    throw new Error(`Failed to create student ${student.email}: ${response.status()}`);
  }
}

export async function seedEnrollmentAgreement(
  request: APIRequestContext,
  token: string,
  userId: string,
  templateId?: string,
  courseType: string = 'twenty_week',
) {
  const payload: Record<string, unknown> = {
    user_id: userId,
    course_type: courseType,
  };
  if (templateId) {
    payload.template_id = templateId;
  }
  const response = await request.post(`${API_BASE_URL}/documents/enrollment/send`, {
    headers: { Authorization: `Bearer ${token}` },
    data: payload,
  });
  if (response.status() !== 200) {
    throw new Error(`Failed to seed agreement: ${response.status()}`);
  }
  return await response.json();
}

export async function listUserDocuments(
  request: APIRequestContext,
  token: string,
  userId: string,
) {
  const response = await request.get(`${API_BASE_URL}/documents/user/${userId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (response.status() !== 200) {
    throw new Error(`Failed to fetch documents for user ${userId}: ${response.status()}`);
  }
  return await response.json();
}

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export async function waitForDocumentStatus(
  request: APIRequestContext,
  token: string,
  userId: string,
  documentId: string,
  expectedStatus: string | string[],
  {
    timeoutMs = 15000,
    pollIntervalMs = 1000,
  }: { timeoutMs?: number; pollIntervalMs?: number } = {},
) {
  const deadline = Date.now() + timeoutMs;
  let lastStatus: string | undefined;
  const statuses = Array.isArray(expectedStatus) ? expectedStatus : [expectedStatus];

  while (Date.now() < deadline) {
    const payload = await listUserDocuments(request, token, userId);
    const documents = Array.isArray(payload?.documents)
      ? payload.documents
      : Array.isArray(payload)
        ? payload
        : [];
    const doc = documents.find((entry: any) => entry.id === documentId);
    if (doc) {
      lastStatus = doc.status;
      if (statuses.includes(doc.status)) {
        return doc;
      }
    }
    await sleep(pollIntervalMs);
  }

  throw new Error(
    `Document ${documentId} did not reach status ${statuses.join(', ')}. Last status: ${lastStatus ?? 'unknown'}`,
  );
}

export async function signDocumentViaToken(
  request: APIRequestContext,
  signingToken: string,
  typedName = 'Automated Student',
) {
  const response = await request.post(`${PUBLIC_SIGN_BASE}/${signingToken}`, {
    data: {
      signature_data: SAMPLE_SIGNATURE,
      typed_name: typedName,
    },
  });
  if (response.status() !== 200) {
    const body = await response.text();
    throw new Error(`Public sign failed: ${response.status()} ${body}`);
  }
  return await response.json();
}

export async function drawSignature(page: Page, selector: string) {
  const canvas = page.locator(selector).first();
  await canvas.waitFor();
  const box = await canvas.boundingBox();
  if (!box) throw new Error('Canvas bounding box not found');

  await page.mouse.move(box.x + 10, box.y + box.height / 2);
  await page.mouse.down();
  await page.mouse.move(box.x + box.width / 3, box.y + box.height / 2 - 20, { steps: 10 });
  await page.mouse.move(box.x + (box.width * 2) / 3, box.y + box.height / 2 + 10, { steps: 10 });
  await page.mouse.move(box.x + box.width - 10, box.y + box.height / 2, { steps: 10 });
  await page.mouse.up();
}
