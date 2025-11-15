# AADA Admin Portal

Secure, role-aware administration dashboard for the AADA Learning Management System. The portal is a React + Vite SPA styled with TailwindCSS and communicates with the FastAPI backend via JWT authentication.

## Prerequisites

- Docker & Docker Compose (used for the LMS stack)
- Existing backend and PostgreSQL containers running from the LMS project

## Project Structure

```
admin_portal/
├── Dockerfile
├── package.json
├── tailwind.config.js
├── postcss.config.js
├── vite.config.js
├── .env
├── public/
│   └── favicon.svg
└── src/
    ├── api/          # Axios client + domain specific API helpers
    ├── components/   # Layout shell, route guards, shared UI
    ├── context/      # Auth provider storing JWT in memory
    ├── pages/        # Feature pages (Dashboard, Students, etc.)
    ├── main.jsx
    ├── App.jsx
    └── index.css
```

## Environment Variables

Configured in `admin_portal/.env` (used at build-time by Vite):

| Variable | Description | Default |
| --- | --- | --- |
| `VITE_API_BASE_URL` | Internal URL for backend (Docker network). | `http://backend:8000` |
| `VITE_APP_NAME` | Display name used inside the UI. | `AADA Admin Portal` |
| `VITE_JWT_SECRET` | Must match FastAPI `SECRET_KEY` for token validation helpers. | `supersecretkey_change_me` |

> When running outside Docker (e.g., `npm run dev` locally), point `VITE_API_BASE_URL` to `http://localhost:8000`.

## Roles & Permissions

| Role | Description | Key Capabilities |
| --- | --- | --- |
| **Admin** | Superuser for policy & infrastructure oversight. | All sections (Students, Courses, Payments, Externships, Reports, Settings). |
| **Instructor** | Faculty operations & clinical oversight. | Dashboard, Courses, Externships. |
| **Finance** | Tuition, invoices, and refund compliance. | Dashboard, Payments, Reports. |
| **Registrar** | Enrollment and academic record custody. | Dashboard, Students, Reports. |

Role enforcement happens client-side (route guard) and should be mirrored server-side on protected endpoints.

## Local Development (Optional)

```bash
cd admin_portal
npm install
npm run dev
```

The Vite dev server runs on <http://localhost:5173>. Adjust `VITE_API_BASE_URL` in `.env` if you are not running inside Docker.

## Docker Deployment

1. From the LMS project root:
   ```bash
   docker-compose build admin_portal
   docker-compose up admin_portal
   ```
2. Visit <http://localhost:5173> for the portal.
3. The service joins the default Docker network and talks to the FastAPI container via the `backend` alias (added in `docker-compose.yml`).

### Networking Notes

- The existing backend service (named `web`) has a network alias `backend` ensuring requests to `http://backend:8000` resolve inside the Compose network.
- CORS must allow `http://localhost:5173`; update FastAPI middleware if requests are blocked.

## Authentication Flow

1. User submits credentials to `POST /api/auth/login`.
2. JWT (access token) is stored in the in-memory auth context (never persisted to `localStorage`).
3. An Axios interceptor appends `Authorization: Bearer <token>` on subsequent requests.
4. `GET /api/auth/me` resolves user profile + roles for route gating.

> Seed data creates an admin account: `admin@aada.edu` / `AdminPass!23`. Update or disable via `app/db/seed.py` as needed.

If authentication fails, the portal resets state and displays the API error message.

## Feature Overview

- **Dashboard:** Enrollment, program, finance, and externship snapshots.
- **Students:** CRUD interface with enrollment visibility (Registrar/Admin).
- **Courses:** Program/module explorer with clock-hour tracking (Instructor/Admin).
- **Payments:** Invoice list & mark-as-paid controls (Finance/Admin).
- **Externships:** Assignment, hour tracking, verification workflow (Instructor/Admin).
- **Reports:** CSV/PDF exports via `/reports/compliance/{resource}`.
- **Settings:** Reference for role capabilities and API directions.

## Troubleshooting

| Issue | Fix |
| --- | --- |
| 401 Unauthorized | Ensure the FastAPI backend has matching `SECRET_KEY` and the LMS auth endpoints are reachable. |
| CORS errors | Update FastAPI CORS middleware to allow `http://localhost:5173` (and Docker hostnames). |
| Network name resolution | Confirm `web` service exposes alias `backend` (provided in `docker-compose.yml`). |
| Missing API endpoints | Placeholder data renders when API calls fail; verify backend routers expose the required paths. |

## Production Notes

- For production builds use `npm run build` and serve `dist/` with a static server (e.g., Nginx). Update Dockerfile accordingly.
- Consider securing the portal with SSO and HTTPS termination at the ingress or reverse proxy.

---

Maintained alongside the AADA LMS backend. For changes to backend endpoints, update the API helpers in `src/api/`.
