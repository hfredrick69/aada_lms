# AADA LMS - Testing Strategy

## Overview

The AADA LMS employs a comprehensive testing strategy covering unit tests, integration tests, and end-to-end tests to ensure reliability and correctness across all system components.

## Testing Pyramid

```
         /\
        /  \       E2E Tests (Few)
       /    \      - Playwright
      /------\     - Full user workflows
     /        \
    /  Integr. \   Integration Tests (Some)
   /    Tests   \  - API endpoint tests
  /--------------\ - Database integration
 /                \
/  Unit Tests      \ Unit Tests (Many)
--------------------  - Business logic
                      - Utilities
                      - Components
```

## Test Coverage Goals

| Component | Target Coverage | Current Status |
|-----------|----------------|----------------|
| Backend (Python) | 80%+ | In progress |
| Frontend (TypeScript) | 70%+ | Planned |
| E2E Scenarios | Critical paths | ✅ Implemented |

## Backend Testing

### Unit Tests (pytest)

**Location**: `backend/tests/`

**Framework**: pytest with fixtures

**Example Test** (`backend/tests/test_auth.py`):
```python
import pytest
from app.core.security import hash_password, verify_password, create_access_token

def test_password_hashing():
    """Test password hashing and verification"""
    password = "TestPassword123!"
    hashed = hash_password(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_create_access_token():
    """Test JWT token creation"""
    token = create_access_token(data={"sub": "test@example.com"})
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0
```

**Running Tests**:
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run tests matching pattern
pytest -k "test_login"

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Integration Tests

**Database Integration** (`backend/tests/test_db.py`):
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.db.models import User, Program, Enrollment

# Test database fixture
@pytest.fixture(scope="function")
def db_session():
    """Create test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()

def test_create_user(db_session):
    """Test user creation in database"""
    user = User(
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User",
        role="student"
    )
    db_session.add(user)
    db_session.commit()
    
    # Query back
    retrieved = db_session.query(User).filter(User.email == "test@example.com").first()
    assert retrieved is not None
    assert retrieved.full_name == "Test User"

def test_enrollment_relationship(db_session):
    """Test enrollment relationship"""
    # Create user and program
    user = User(email="student@test.com", hashed_password="hash", full_name="Student", role="student")
    program = Program(name="Test Program", description="Test", total_credits=60)
    
    db_session.add_all([user, program])
    db_session.commit()
    
    # Create enrollment
    enrollment = Enrollment(user_id=user.id, program_id=program.id, status="active")
    db_session.add(enrollment)
    db_session.commit()
    
    # Test relationship
    assert user.enrollments[0].program.name == "Test Program"
```

### API Endpoint Tests

**FastAPI Test Client** (`backend/tests/test_api.py`):
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_login_success(db_session):
    """Test successful login"""
    # Create test user
    from app.core.security import hash_password
    user = User(
        email="test@example.com",
        hashed_password=hash_password("TestPass123!"),
        full_name="Test User",
        role="student"
    )
    db_session.add(user)
    db_session.commit()
    
    # Attempt login
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    
    assert response.status_code == 200
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

def test_protected_route_without_auth():
    """Test protected route requires authentication"""
    response = client.get("/api/users/")
    assert response.status_code == 401

def test_protected_route_with_auth(db_session):
    """Test protected route with authentication"""
    # Login first
    response = client.post("/api/auth/login", json={
        "email": "admin@aada.edu",
        "password": "AdminPass!23"
    })
    
    # Access protected route with cookies
    response = client.get("/api/users/", cookies=response.cookies)
    assert response.status_code == 200
```

### pytest Configuration

**pytest.ini**:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --strict-markers
    --cov=app
    --cov-report=term-missing
    --cov-report=html
```

**conftest.py** (shared fixtures):
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base

@pytest.fixture(scope="session")
def engine():
    """Create test database engine"""
    return create_engine("sqlite:///:memory:")

@pytest.fixture(scope="function")
def db_session(engine):
    """Create clean database session for each test"""
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)
```

## Frontend Testing

### Component Tests (Vitest + React Testing Library)

**Planned Setup**:
```bash
cd frontend/aada_web
npm install -D vitest @testing-library/react @testing-library/jest-dom
```

**Example Component Test**:
```typescript
// src/components/PageHeader.test.tsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { PageHeader } from './PageHeader';

describe('PageHeader', () => {
  it('renders title correctly', () => {
    render(<PageHeader title="Test Title" subtitle="Test Subtitle" />);
    
    expect(screen.getByText('Test Title')).toBeInTheDocument();
    expect(screen.getByText('Test Subtitle')).toBeInTheDocument();
  });
  
  it('renders action button when provided', () => {
    const action = <button>Click Me</button>;
    render(<PageHeader title="Title" action={action} />);
    
    expect(screen.getByText('Click Me')).toBeInTheDocument();
  });
});
```

**Hook Tests**:
```typescript
// src/api/hooks.test.ts
import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useUserQuery } from './hooks';

describe('useUserQuery', () => {
  it('fetches user data', async () => {
    const queryClient = new QueryClient();
    const wrapper = ({ children }) => (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );
    
    const { result } = renderHook(() => useUserQuery(1), { wrapper });
    
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toHaveProperty('email');
  });
});
```

## End-to-End Testing

### Playwright Tests

**Location**: `e2e-tests/`

**Configuration** (`playwright.config.ts`):
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e-tests',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
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
});
```

**Running locally (Docker-required browsers)**:
1. Ensure the Docker stack is up: `docker compose up -d`.
2. Execute tests through the wrapper (runs the official Playwright container, pointing back to the host services):
   ```bash
   ./scripts/run_playwright.sh e2e-tests/admin-portal.spec.ts
   ./scripts/run_playwright.sh e2e-tests/student-portal.spec.ts
   ```
   The script sets `E2E_HOST=host.docker.internal` so the container reaches the host’s backend (`:8000`) and portals (`:5173` / `:5174`). Override any of the following if needed:
   - `E2E_HOST`
   - `ADMIN_PORTAL_URL`, `STUDENT_PORTAL_URL`
   - `PLAYWRIGHT_API_ORIGIN`, `PLAYWRIGHT_API_BASE_URL`

### Test Structure

**Student Portal Tests** (`e2e-tests/student-portal.spec.ts`):
```typescript
import { test, expect } from '@playwright/test';

const STUDENT_EMAIL = 'alice.student@aada.edu';
const STUDENT_PASSWORD = 'AlicePass!23';
const E2E_HOST = process.env.E2E_HOST ?? 'localhost';
const STUDENT_PORTAL_URL = process.env.STUDENT_PORTAL_URL ?? `http://${E2E_HOST}:5174`;

test.describe('Student Portal - Authentication', () => {
  test('should login with valid credentials', async ({ page }) => {
    await page.goto(STUDENT_PORTAL_URL + '/login');
    
    await page.getByLabel('Email', { exact: false }).fill(STUDENT_EMAIL);
    await page.getByLabel('Password', { exact: false }).fill(STUDENT_PASSWORD);
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Verify redirect to dashboard
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    expect(page.url()).toContain('/dashboard');
    
    // Verify cookies set
    const cookies = await page.context().cookies();
    expect(cookies.some(c => c.name === 'access_token')).toBeTruthy();
    expect(cookies.some(c => c.name === 'refresh_token')).toBeTruthy();
  });
});

test.describe('Student Portal - Module Access', () => {
  test.beforeEach(async ({ page }) => {
    // Login helper
    await page.goto(STUDENT_PORTAL_URL + '/login');
    await page.getByLabel('Email').fill(STUDENT_EMAIL);
    await page.getByLabel('Password').fill(STUDENT_PASSWORD);
    await page.getByRole('button', { name: /sign in/i }).click();
    await page.waitForURL('**/dashboard', { timeout: 10000 });
  });
  
  test('should display enrolled modules', async ({ page }) => {
    await page.click('text=Modules');
    await expect(page.getByRole('heading', { name: /Program Modules/i })).toBeVisible();
    
    // Should show at least one module
    const modules = page.locator('[data-testid="module-card"]');
    await expect(modules.first()).toBeVisible();
  });
});
```

**Admin Portal Tests** (`e2e-tests/admin-portal.spec.ts`):
```typescript
import { test, expect } from '@playwright/test';

test.describe('Admin Portal - Student Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await page.getByLabel('Email').fill('admin@aada.edu');
    await page.getByLabel('Password').fill('AdminPass!23');
    await page.getByRole('button', { name: /sign in/i }).click();
    await page.waitForURL('**/dashboard', { timeout: 10000 });
  });
  
  test('should list all students', async ({ page }) => {
    await page.click('text=Students');
    await page.waitForTimeout(2000);
    
    // Verify student list loads
    const table = page.locator('table');
    await expect(table).toBeVisible();
    
    // Should contain at least one student
    const rows = page.locator('tbody tr');
    await expect(rows.first()).toBeVisible();
  });
});
```

### Running E2E Tests

```bash
# Install Playwright browsers (first time only)
npx playwright install

# Run all E2E tests
npm run test:e2e

# Run specific test file
npx playwright test e2e-tests/student-portal.spec.ts

# Run with UI (interactive mode)
npx playwright test --ui

# Run headed (see browser)
npx playwright test --headed

# Debug mode
npx playwright test --debug

# Generate report
npx playwright show-report
```

### Test Helpers

**Page Object Model**:
```typescript
// e2e-tests/pages/LoginPage.ts
import { Page } from '@playwright/test';

export class LoginPage {
  constructor(private page: Page) {}
  
  async goto() {
    await this.page.goto('/login');
  }
  
  async login(email: string, password: string) {
    await this.page.getByLabel('Email').fill(email);
    await this.page.getByLabel('Password').fill(password);
    await this.page.getByRole('button', { name: /sign in/i }).click();
    await this.page.waitForURL('**/dashboard', { timeout: 10000 });
  }
  
  async expectLoginError() {
    await this.page.waitForTimeout(2000);
    expect(this.page.url()).toContain('/login');
  }
}

// Usage in tests
import { LoginPage } from './pages/LoginPage';

test('login flow', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('alice@aada.edu', 'AlicePass!23');
});
```

## Visual Regression Testing (Future)

**Percy or Chromatic**:
```typescript
import { test } from '@playwright/test';
import percySnapshot from '@percy/playwright';

test('dashboard visual test', async ({ page }) => {
  await page.goto('/dashboard');
  await percySnapshot(page, 'Dashboard - Student View');
});
```

## Performance Testing

### Load Testing (Locust)

**locustfile.py**:
```python
from locust import HttpUser, task, between

class AADAUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login before tests"""
        self.client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123!"
        })
    
    @task(3)
    def view_dashboard(self):
        self.client.get("/api/users/me")
    
    @task(2)
    def view_modules(self):
        self.client.get("/api/modules/")
    
    @task(1)
    def view_transcripts(self):
        self.client.get("/api/transcripts/")
```

**Run load test**:
```bash
locust -f locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10
```

### Performance Metrics

**Targets**:
- API response time (p95): < 500ms
- Page load time: < 2 seconds
- Time to interactive: < 3 seconds
- Database query time: < 100ms

**Monitoring**:
```python
# Add timing middleware
from time import time

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## Continuous Integration

### GitHub Actions Workflow

**.github/workflows/test.yml**:
```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      
      - name: Start services
        run: docker-compose up -d
      
      - name: Install Playwright
        run: |
          npm install
          npx playwright install --with-deps
      
      - name: Run E2E tests
        run: npm run test:e2e
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
```

## Test Data Management

### Test Database Seeding

**Seed script** (`backend/app/db/seed.py`):
```python
from app.db.session import SessionLocal
from app.db.models import User, Program, Enrollment
from app.core.security import hash_password

def seed_test_data():
    db = SessionLocal()
    
    # Create test users
    admin = User(
        email="admin@aada.edu",
        hashed_password=hash_password("AdminPass!23"),
        full_name="Admin User",
        role="admin"
    )
    
    student = User(
        email="alice.student@aada.edu",
        hashed_password=hash_password("AlicePass!23"),
        full_name="Alice Student",
        role="student"
    )
    
    # Create test program
    program = Program(
        name="Dental Assistant Professional",
        description="Test program",
        total_credits=60.0,
        duration_weeks=52,
        tuition_amount_cents=1200000
    )
    
    db.add_all([admin, student, program])
    db.commit()
    
    # Create enrollment
    enrollment = Enrollment(
        user_id=student.id,
        program_id=program.id,
        status="active",
        enrolled_at=date.today()
    )
    
    db.add(enrollment)
    db.commit()
    
    print("Test data seeded successfully")

if __name__ == "__main__":
    seed_test_data()
```

### Test Fixtures

**Factories** (using factory_boy):
```python
import factory
from app.db.models import User

class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    full_name = factory.Faker("name")
    role = "student"
    hashed_password = "hashed_password_here"

# Usage in tests
def test_with_factory():
    user = UserFactory.create(email="specific@example.com")
    assert user.email == "specific@example.com"
```

## Test Coverage Reporting

**Generate coverage report**:
```bash
cd backend
pytest --cov=app --cov-report=html
open htmlcov/index.html  # View in browser
```

**Coverage badge** (README.md):
```markdown
![Coverage](https://img.shields.io/codecov/c/github/username/aada_lms)
```

## Best Practices

### Test Organization
- One test file per module/component
- Clear test names describing what is being tested
- Arrange-Act-Assert pattern
- Independent tests (no shared state)
- Fast execution (mock external dependencies)

### Naming Conventions
```python
# Good
def test_user_login_with_valid_credentials_succeeds()
def test_enrollment_creation_requires_active_program()

# Avoid
def test_1()
def test_stuff()
```

### Test Isolation
```python
# Use fixtures for setup/teardown
@pytest.fixture
def clean_database():
    setup_database()
    yield
    teardown_database()

def test_with_clean_db(clean_database):
    # Test runs with clean state
    pass
```

---

**Last Updated**: 2025-11-04  
**Maintained By**: QA Team
