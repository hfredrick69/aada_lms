# Task
Generate a new Student Dashboard page for the AADA LMS.

# Context
- The backend exposes a FastAPI endpoint at `/api/modules` that returns module data.
- The frontend stack uses React 18 + Vite + TypeScript + Tailwind CSS + MUI.
- The page should list available modules with name, description, and progress.
- Clicking a module navigates to `/modules/:id` for details.

# Requirements
- Use modern React functional components.
- Fetch data via the generated OpenAPI TypeScript client (or `fetch` if not available).
- Style with Tailwind + MUI.
- Include responsive design for desktop and mobile.
- Add placeholder components for student progress and quick actions.
- Output files under `frontend/src/pages/StudentDashboard.tsx` and `frontend/src/components/`.

# Output
Write complete TypeScript/React code, ready to run in Vite.
