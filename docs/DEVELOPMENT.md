# AADA LMS - Development Workflow

## Getting Started

### Prerequisites

**Required**:
- Docker Desktop (latest)
- Node.js 20+ with npm
- Python 3.11+
- Git
- Text editor (VS Code recommended)

**Optional**:
- Playwright browsers (for E2E tests)
- PostgreSQL client (psql, TablePlus, DBeaver)

### Initial Setup

1. **Clone repository**:
```bash
git clone <repository-url>
cd aada_lms
```

2. **Environment configuration**:
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your local settings
# Most defaults will work for development
```

3. **Start services**:
```bash
docker-compose up -d
```

4. **Verify services**:
```bash
docker-compose ps  # All services should be "Up"
```

5. **Access portals**:
- Admin Portal: http://localhost:5173
- Student Portal: http://localhost:5174
- API Docs: http://localhost:8000/docs

### Default Credentials

**Admin User**:
- Email: `admin@aada.edu`
- Password: `AdminPass!23`

**Student User**:
- Email: `alice.student@aada.edu`
- Password: `AlicePass!23`

## Development Environment

### Docker Compose Services

```yaml
services:
  db:          # PostgreSQL 17 on :5432
  backend:     # FastAPI on :8000
  admin:       # Admin Portal (Vite) on :5173
  student:     # Student Portal (Vite) on :5174
```

**Start all services**:
```bash
docker-compose up -d
```

**View logs**:
```bash
docker-compose logs -f              # All services
docker-compose logs -f backend      # Backend only
docker-compose logs -f admin        # Admin portal only
```

**Restart a service**:
```bash
docker-compose restart backend
docker-compose restart admin
```

**Stop services**:
```bash
docker-compose down                 # Stop all
docker-compose down -v              # Stop and remove volumes (⚠️ deletes database)
```

### Local Development (Without Docker)

**Backend**:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

**Admin Portal**:
```bash
cd admin_portal
npm install
npm run dev  # Runs on :5173
```

**Student Portal**:
```bash
cd frontend/aada_web
npm install
npm run dev  # Runs on :5174
```

**PostgreSQL** (local):
```bash
# Install PostgreSQL 17
# Create database
createdb aada_lms

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@localhost:5432/aada_lms
```

## Project Structure

```
aada_lms/
├── admin_portal/              # Admin React app
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API client services
│   │   └── App.jsx            # Main app component
│   ├── public/                # Static assets
│   ├── package.json
│   └── vite.config.js
│
├── frontend/aada_web/         # Student React app
│   ├── src/
│   │   ├── api/               # Generated API clients
│   │   │   ├── generated/     # OpenAPI generated code
│   │   │   └── hooks.ts       # Custom React Query hooks
│   │   ├── features/          # Feature modules
│   │   │   ├── auth/
│   │   │   ├── dashboard/
│   │   │   ├── modules/
│   │   │   ├── payments/
│   │   │   ├── externships/
│   │   │   └── documents/
│   │   ├── components/        # Shared components
│   │   ├── stores/            # Zustand state stores
│   │   ├── types/             # TypeScript type definitions
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                   # FastAPI application
│   ├── app/
│   │   ├── routers/           # API endpoint routers
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── programs.py
│   │   │   ├── enrollments.py
│   │   │   ├── modules.py
│   │   │   ├── externships.py
│   │   │   ├── finance.py
│   │   │   └── ...
│   │   ├── db/
│   │   │   ├── models/        # SQLAlchemy models
│   │   │   │   ├── user.py
│   │   │   │   ├── program.py
│   │   │   │   ├── enrollment.py
│   │   │   │   └── compliance/
│   │   │   ├── base.py        # Base model class
│   │   │   └── session.py     # Database session
│   │   ├── schemas/           # Pydantic schemas (request/response)
│   │   ├── core/
│   │   │   ├── config.py      # Configuration
│   │   │   ├── security.py    # Auth utilities
│   │   │   └── utils.py       # Helper functions
│   │   ├── static/            # Static files (H5P content)
│   │   └── main.py            # FastAPI app initialization
│   ├── alembic/               # Database migrations
│   │   ├── versions/          # Migration scripts
│   │   └── env.py
│   ├── tests/                 # Backend tests
│   ├── requirements.txt
│   └── alembic.ini
│
├── e2e-tests/                 # Playwright E2E tests
│   ├── admin-portal.spec.ts
│   └── student-portal.spec.ts
│
├── docs/                      # Project documentation
│   ├── ARCHITECTURE.md
│   ├── AUTH_SECURITY.md
│   ├── SECURITY_COMPLIANCE.md
│   └── ...
│
├── agents/                    # AI automation agents
│   ├── config.yaml
│   └── supervisor_agent.py
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
└── package.json               # Root package.json (E2E tests)
```

## Common Development Tasks

### Database Operations

**Run migrations**:
```bash
# Inside backend container
docker-compose exec backend alembic upgrade head

# Or locally
cd backend
alembic upgrade head
```

**Create new migration**:
```bash
# After modifying models
cd backend
alembic revision --autogenerate -m "Add new table"

# Review generated migration in alembic/versions/
# Edit if necessary

# Apply migration
alembic upgrade head
```

**Reset database** (⚠️ deletes all data):
```bash
docker-compose down -v          # Remove volumes
docker-compose up -d db         # Start database
docker-compose exec backend alembic upgrade head  # Run migrations
docker-compose exec backend python -m app.db.seed  # (if seed script exists)
```

**Database access**:
```bash
# Connect to database container
docker-compose exec db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}

# Or use DATABASE_URL from .env with external client
```

### Frontend Development

**Install dependencies**:
```bash
# Admin portal
cd admin_portal
npm install

# Student portal
cd frontend/aada_web
npm install
```

**Generate API client** (Student Portal):
```bash
cd frontend/aada_web

# Ensure backend is running on :8000
npm run generate:api

# This fetches OpenAPI spec and generates TypeScript types
```

**Linting & Formatting**:
```bash
# Run ESLint
npm run lint

# Fix auto-fixable issues
npm run lint:fix

# Format with Prettier (if configured)
npm run format
```

**Build for production**:
```bash
# Admin portal
cd admin_portal
npm run build  # Output to dist/

# Student portal
cd frontend/aada_web
npm run build  # Output to dist/
```

### Backend Development

**Install dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

**Add new dependency**:
```bash
pip install <package-name>
pip freeze > requirements.txt  # Update requirements
```

**Linting & Formatting**:
```bash
# Install dev tools
pip install flake8 autopep8

# Run flake8
flake8 app/

# Auto-format
autopep8 --in-place --recursive app/
```

**Run tests**:
```bash
cd backend
pytest                          # All tests
pytest tests/test_auth.py       # Specific test file
pytest -v                       # Verbose output
pytest --cov=app                # With coverage report
```

### Running Tests

**E2E Tests** (Playwright):
```bash
# Install Playwright browsers (first time only)
npx playwright install

# Run all E2E tests
npm run test:e2e

# Run specific test file
npx playwright test e2e-tests/student-portal.spec.ts

# Run with UI mode
npm run test:ui

# Generate test report
npm run test:e2e:report
```

**Backend Tests** (pytest):
```bash
cd backend
pytest                          # All tests
pytest tests/test_auth.py       # Specific file
pytest -k "test_login"          # Tests matching pattern
pytest -v                       # Verbose
pytest --cov=app --cov-report=html  # Coverage report
```

**Frontend Tests** (Vitest - if configured):
```bash
cd frontend/aada_web
npm test                        # Run tests
npm test -- --watch             # Watch mode
npm test -- --coverage          # With coverage
```

## Git Workflow

### Branch Strategy

**Main Branches**:
- `main` - Production-ready code
- `develop` - Integration branch for features

**Feature Branches**:
```bash
git checkout -b feature/feature-name develop
# Work on feature
git add .
git commit -m "Add feature: description"
git push origin feature/feature-name
# Create pull request to develop
```

**Bugfix Branches**:
```bash
git checkout -b bugfix/bug-description develop
# Fix bug
git commit -m "Fix: bug description"
git push origin bugfix/bug-description
# Create pull request to develop
```

**Hotfix Branches** (urgent production fixes):
```bash
git checkout -b hotfix/issue-description main
# Fix issue
git commit -m "Hotfix: issue description"
# Merge to main AND develop
```

### Commit Message Format

**Format**:
```
<type>: <subject>

<body (optional)>

<footer (optional)>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat: Add student transcript download feature

Implements PDF generation for student transcripts with official formatting.
Includes download button in Documents page.

Closes #123

---

fix: Correct externship hours calculation

Hours were being summed incorrectly when placements overlapped.
Now uses proper date range logic.

---

docs: Update API documentation for auth endpoints

Added examples for JWT cookie authentication flow.
```

### Pull Request Process

1. **Create feature branch**
2. **Make changes and commit**
3. **Push to remote**
4. **Create pull request** to `develop` (or `main` for hotfixes)
5. **Ensure tests pass** (CI/CD)
6. **Request review** from team member
7. **Address review comments**
8. **Merge** after approval

**PR Template**:
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] E2E tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests pass locally
```

## Debugging

### Backend Debugging

**Print statements**:
```python
# Simple logging
print(f"User: {user.email}")

# Structured logging
import logging
logger = logging.getLogger(__name__)
logger.info(f"User logged in: {user.email}")
logger.error(f"Authentication failed for {email}")
```

**Interactive debugger** (pdb):
```python
import pdb; pdb.set_trace()  # Breakpoint
# Or in Python 3.7+
breakpoint()
```

**VS Code debugger**:
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload"],
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```

**Database queries**:
```python
# Enable SQL echo
engine = create_engine(DATABASE_URL, echo=True)  # Prints all SQL
```

### Frontend Debugging

**Browser DevTools**:
- Console tab: JavaScript errors, console.log() output
- Network tab: API requests/responses
- Application tab: Cookies, localStorage
- React DevTools extension: Component state inspection

**Console debugging**:
```typescript
console.log('User:', user);
console.error('Error:', error);
console.table(data);  // Tabular data
debugger;  // Breakpoint in DevTools
```

**React Query DevTools**:
```typescript
// Already included in Student Portal
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

<QueryClientProvider client={queryClient}>
  <App />
  <ReactQueryDevtools initialIsOpen={false} />
</QueryClientProvider>
```

### Docker Debugging

**Container logs**:
```bash
docker-compose logs -f backend    # Tail backend logs
docker-compose logs --tail=100 db # Last 100 lines
```

**Execute commands in container**:
```bash
docker-compose exec backend bash  # Shell in backend container
docker-compose exec db psql -U postgres -d aada_lms
```

**Inspect container**:
```bash
docker-compose ps                 # Running containers
docker-compose exec backend env   # Environment variables
```

**Restart with clean state**:
```bash
docker-compose down -v            # Remove volumes
docker-compose up -d              # Rebuild and start
```

## Code Style Guidelines

### Python (Backend)

**Follow PEP 8**:
- 4 spaces for indentation
- Max line length: 100 characters
- Snake_case for variables and functions
- PascalCase for classes

**Example**:
```python
# Good
def get_user_by_email(email: str, db: Session) -> User | None:
    """Fetch user by email address."""
    return db.query(User).filter(User.email == email).first()

# Avoid
def GetUserByEmail(Email):
    return db.query(User).filter(User.email==Email).first()
```

### TypeScript/JavaScript (Frontend)

**Follow Airbnb style guide** (loosely):
- 2 spaces for indentation
- camelCase for variables and functions
- PascalCase for components and classes
- Meaningful variable names

**Example**:
```typescript
// Good
const fetchUserData = async (userId: number): Promise<User> => {
  const response = await api.get(`/users/${userId}`);
  return response.data;
};

// Avoid
const fetchUserData = async (id) => {
  const r = await api.get(`/users/${id}`);
  return r.data;
};
```

### React Components

**Functional components with hooks**:
```typescript
// Good
export const UserProfile = ({ userId }: { userId: number }) => {
  const { data: user, isLoading } = useUserQuery(userId);
  
  if (isLoading) return <LoadingState />;
  
  return (
    <Box>
      <Typography variant="h4">{user.name}</Typography>
      ...
    </Box>
  );
};

// Avoid class components for new code
```

## Environment Variables

### Backend (.env)

```bash
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=aada_lms
DATABASE_URL=postgresql://postgres:postgres@db:5432/aada_lms

# Security
SECRET_KEY=<generate-strong-random-key>
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174

# Application
DEBUG=True
LOG_LEVEL=INFO
```

### Frontend (Vite)

**Admin Portal**:
```bash
# vite.config.js uses proxy
# No env vars needed for API URL
```

**Student Portal**:
```bash
# Auto-detected from proxy config
VITE_API_URL=http://localhost:8000  # Optional override
```

## CI/CD Pipeline (Future)

**Planned Automation**:

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run backend tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run E2E tests
        run: |
          docker-compose up -d
          npm install
          npx playwright test

  deploy:
    needs: [test-backend, test-frontend]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: echo "Deploy scripts here"
```

## Troubleshooting

### Common Issues

**Issue**: Port already in use
```bash
# Solution: Change port in docker-compose.yml or kill process
lsof -ti:8000 | xargs kill -9  # Kill process on port 8000
```

**Issue**: Database connection refused
```bash
# Solution: Ensure database is running
docker-compose ps db
docker-compose up -d db
```

**Issue**: npm install fails
```bash
# Solution: Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

**Issue**: Alembic migration conflicts
```bash
# Solution: Reset migrations (development only)
rm -rf alembic/versions/*
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

**Issue**: CORS errors in browser
```bash
# Solution: Check ALLOWED_ORIGINS in backend .env
# Ensure frontend URL is listed
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174
```

---

**Last Updated**: 2025-11-04  
**Maintained By**: Development Team
