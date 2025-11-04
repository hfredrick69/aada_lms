# Task
Build a **responsive Web UI/UX** for the Atlanta Academy of Dental Assisting (AADA)
that mirrors the functionality and flow of the **Flutter mobile app**
(`AADA_flutter_audit.md` describes its modules, endpoints, and architecture)
but connects to the **new FastAPI backend** at `http://localhost:8000/api`.

# Objectives
1. Create a **React 18 + Vite + TypeScript** web project named `aada_web`.
2. Reproduce all major Flutter modules and screens:
   - **Login / Authentication**
   - **Student Dashboard**
   - **Modules / Lessons**
   - **Payments**
   - **Externships**
   - **Documents / Uploads**
3. Use the **same API endpoints** listed in the Flutter audit,
   replacing old Azure URLs with `http://localhost:8000/api/...`.
4. Implement a **modern, responsive, accessible design**
   using **Tailwind CSS** and **MUI v6**.
5. Keep component and API structure simple enough for future AI-agent maintenance.

# Project Setup
- Framework: React 18 + TypeScript
- Builder: Vite
- CSS: Tailwind CSS + MUI (Material UI)
- Routing: React Router v6
- Data Layer: React Query (TanStack Query)
- State: Zustand (or React Context if simpler)
- API Client: OpenAPI-generated TypeScript client (`orval` or `openapi-typescript`)
- Auth: JWT (same logic as Flutter)
- Testing: Vitest + React Testing Library

# Design Guidelines
- Match the navigation and hierarchy from the Flutter app:
  - Bottom navigation → Responsive top navbar + side drawer.
  - Card-based module grid → Responsive 3-column desktop / 1-column mobile.
  - Consistent color palette and typography (medical / academic theme).
- Implement dark/light theme toggle.
- Ensure full accessibility (ARIA, keyboard navigation, semantic HTML).

# Components to Build
| Component | Purpose | Backend Endpoint |
|------------|----------|------------------|
| `LoginPage` | Auth with JWT | `/api/auth/login` |
| `DashboardPage` | Display modules, externships, payment summary | `/api/modules`, `/api/externships`, `/api/finance/payments` |
| `ModuleList` / `ModuleDetail` | List and details of lessons | `/api/modules/{id}` |
| `PaymentHistory` | Show transactions | `/api/finance/payments` |
| `ExternshipTracker` | Hours and progress | `/api/externships` |
| `DocumentUpload` | File upload form | `/api/documents` |

# API Integration
1. Read FastAPI schema from `http://localhost:8000/openapi.json`.
2. Generate typed API client (e.g., with Orval).
3. Use React Query hooks for all network requests:
   ```ts
   const { data, isLoading } = useGetModulesQuery();
