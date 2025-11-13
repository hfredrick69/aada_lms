import { test, expect } from '@playwright/test';

/**
 * API Endpoint Tests
 *
 * Tests the new backend API endpoints directly
 */

const ADMIN_EMAIL = 'admin@aada.edu';
const ADMIN_PASSWORD = 'AdminPass!23';
const STUDENT_EMAIL = 'alice.student@aada.edu';
const STUDENT_PASSWORD = 'AlicePass!23';
const API_ORIGIN = process.env.PLAYWRIGHT_API_ORIGIN ?? 'http://localhost:8000';
const API_BASE_URL = process.env.PLAYWRIGHT_API_BASE_URL ?? `${API_ORIGIN}/api`;

// Helper to get auth cookies
async function loginUser(request: any, email: string, password: string) {
  const response = await request.post(`${API_BASE_URL}/auth/login`, {
    data: { email, password }
  });
  expect(response.ok()).toBeTruthy();
  return response;
}

test.describe('Students API - /api/students', () => {
  let testStudentId: string;

  test('should create new student (admin only)', async ({ request }) => {
    // Login as admin
    await loginUser(request, ADMIN_EMAIL, ADMIN_PASSWORD);

    // Create new student
    const newStudent = {
      email: `test.student.${Date.now()}@aada.edu`,
      password: 'TestPass!234',
      first_name: 'Test',
      last_name: 'Student'
    };

    const response = await request.post(`${API_BASE_URL}/students/`, {
      data: newStudent
    });

    if (response.status() === 201) {
      const created = await response.json();
      expect(created.email).toBe(newStudent.email);
      expect(created.first_name).toBe(newStudent.first_name);
      expect(created.last_name).toBe(newStudent.last_name);
      testStudentId = created.id;
      return;
    }

    if (response.status() === 400) {
      const body = await response.json();
      expect(body?.detail).toContain('Email already registered');
      const fallbackList = await request.get(`${API_BASE_URL}/students/`);
      const existingStudents = await fallbackList.json();
      const existing = existingStudents.find((s: any) => s.email === newStudent.email);
      expect(existing).toBeTruthy();
      testStudentId = existing.id;
      return;
    }

    expect(response.status(), 'Unexpected status when creating student').toBe(201);
  });

  test('should list students (admin only)', async ({ request }) => {
    // Login as admin
    await loginUser(request, ADMIN_EMAIL, ADMIN_PASSWORD);

    // Get students list
    const response = await request.get(`${API_BASE_URL}/students/`);
    expect(response.ok()).toBeTruthy();

    const students = await response.json();
    expect(Array.isArray(students)).toBeTruthy();
    // Now we should have at least one student from previous test
    expect(students.length).toBeGreaterThan(0);

    // Verify student structure
    const student = students[0];
    expect(student).toHaveProperty('id');
    expect(student).toHaveProperty('email');
    expect(student).toHaveProperty('first_name');
    expect(student).toHaveProperty('last_name');
    expect(student).toHaveProperty('status');
  });

  test('should get student by ID', async ({ request }) => {
    // Login as admin
    await loginUser(request, ADMIN_EMAIL, ADMIN_PASSWORD);

    // Get students list first
    const listResponse = await request.get(`${API_BASE_URL}/students/`);
    const students = await listResponse.json();
    expect(students.length).toBeGreaterThan(0);

    // Get specific student
    const studentId = students[0].id;
    const response = await request.get(`${API_BASE_URL}/students/${studentId}`);
    expect(response.ok()).toBeTruthy();

    const student = await response.json();
    expect(student.id).toBe(studentId);
  });
});

test.describe('Payments API - /api/payments', () => {
  test('should list all transactions (admin)', async ({ request }) => {
    // Login as admin
    await loginUser(request, ADMIN_EMAIL, ADMIN_PASSWORD);

    // Get all transactions
    const response = await request.get(`${API_BASE_URL}/payments/`);
    expect(response.ok()).toBeTruthy();

    const transactions = await response.json();
    expect(Array.isArray(transactions)).toBeTruthy();
  });

  test('should get student balance', async ({ request }) => {
    // Login as admin
    await loginUser(request, ADMIN_EMAIL, ADMIN_PASSWORD);

    // Get students first to get a student ID
    const studentsResponse = await request.get(`${API_BASE_URL}/students/`);
    const students = await studentsResponse.json();

    if (students.length > 0) {
      const studentId = students[0].id;

      // Get balance
      const response = await request.get(`${API_BASE_URL}/payments/balance/${studentId}`);
      expect(response.ok()).toBeTruthy();

      const balance = await response.json();
      expect(balance).toHaveProperty('user_id');
      expect(balance).toHaveProperty('total_charges_cents');
      expect(balance).toHaveProperty('total_payments_cents');
      expect(balance).toHaveProperty('balance_cents');
      expect(balance.user_id).toBe(studentId);
    }
  });

  test('should record payment (admin only)', async ({ request }) => {
    // Login as admin
    await loginUser(request, ADMIN_EMAIL, ADMIN_PASSWORD);

    // Get a student ID
    const studentsResponse = await request.get(`${API_BASE_URL}/students/`);
    const students = await studentsResponse.json();
    expect(students.length).toBeGreaterThan(0);

    const studentId = students[0].id;

    // Record a payment
    const payment = {
      user_id: studentId,
      amount_cents: 50000, // $500.00
      description: 'Test payment - E2E test'
    };

    const response = await request.post(`${API_BASE_URL}/payments/`, {
      data: payment
    });
    expect(response.status()).toBe(201);

    const recorded = await response.json();
    expect(recorded.user_id).toBe(studentId);
    expect(recorded.amount_cents).toBe(payment.amount_cents);
    expect(recorded.line_type).toBe('payment');
  });

  test('should get payment history', async ({ request }) => {
    // Login as admin
    await loginUser(request, ADMIN_EMAIL, ADMIN_PASSWORD);

    // Get a student ID
    const studentsResponse = await request.get(`${API_BASE_URL}/students/`);
    const students = await studentsResponse.json();
    expect(students.length).toBeGreaterThan(0);

    const studentId = students[0].id;

    // Get payment history
    const response = await request.get(`${API_BASE_URL}/payments/history/${studentId}`);
    expect(response.ok()).toBeTruthy();

    const history = await response.json();
    expect(Array.isArray(history)).toBeTruthy();
  });

  test('student should see own balance', async ({ request }) => {
    // Login as student
    await loginUser(request, STUDENT_EMAIL, STUDENT_PASSWORD);

    // Get current user (to get student ID)
    const meResponse = await request.get(`${API_BASE_URL}/auth/me`);
    const currentUser = await meResponse.json();

    // Get own balance
    const response = await request.get(`${API_BASE_URL}/payments/balance/${currentUser.id}`);
    expect(response.ok()).toBeTruthy();

    const balance = await response.json();
    expect(balance.user_id).toBe(currentUser.id);
  });

  test('student should NOT record payments', async ({ request }) => {
    // Login as student
    await loginUser(request, STUDENT_EMAIL, STUDENT_PASSWORD);

    // Get current user
    const meResponse = await request.get(`${API_BASE_URL}/auth/me`);
    const currentUser = await meResponse.json();

    // Try to record a payment (should fail)
    const payment = {
      user_id: currentUser.id,
      amount_cents: 10000,
      description: 'Unauthorized attempt'
    };

    const response = await request.post(`${API_BASE_URL}/payments/`, {
      data: payment
    });
    expect(response.status()).toBe(403);
  });
});

test.describe('xAPI Statements - /api/xapi/statements', () => {
  test('should post xAPI statement', async ({ request }) => {
    // Login as student
    await loginUser(request, STUDENT_EMAIL, STUDENT_PASSWORD);

    // Create xAPI statement
    const statement = {
      actor: {
        objectType: 'Agent',
        name: 'Test Student',
        mbox: 'mailto:test@aada.edu'
      },
      verb: {
        id: 'http://adlnet.gov/expapi/verbs/completed',
        display: { 'en-US': 'completed' }
      },
      object: {
        objectType: 'Activity',
        id: `${API_BASE_URL}/h5p/M1_H5P_EthicsBranching`,
        definition: {
          name: { 'en-US': 'Ethics Branching Scenario' }
        }
      },
      result: {
        score: { scaled: 0.85 },
        success: true,
        completion: true
      },
      timestamp: new Date().toISOString()
    };

    const response = await request.post(`${API_BASE_URL}/xapi/statements`, {
      data: statement
    });
    expect(response.status()).toBe(201);

    const created = await response.json();
    expect(created).toHaveProperty('id');
    expect(created).toHaveProperty('stored_at');
    expect(created.actor).toEqual(statement.actor);
    expect(created.verb).toEqual(statement.verb);
  });

  test('should list xAPI statements', async ({ request }) => {
    // Login as admin
    await loginUser(request, ADMIN_EMAIL, ADMIN_PASSWORD);

    // Get statements
    const response = await request.get(`${API_BASE_URL}/xapi/statements`);
    expect(response.ok()).toBeTruthy();

    const statements = await response.json();
    expect(Array.isArray(statements)).toBeTruthy();
  });

  test('should filter xAPI statements by verb', async ({ request }) => {
    // Login as admin
    await loginUser(request, ADMIN_EMAIL, ADMIN_PASSWORD);

    // Get statements filtered by "completed" verb
    const response = await request.get(`${API_BASE_URL}/xapi/statements?verb=completed`);
    expect(response.ok()).toBeTruthy();

    const statements = await response.json();
    expect(Array.isArray(statements)).toBeTruthy();
  });
});
