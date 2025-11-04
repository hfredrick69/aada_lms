# Claude Code Instructions: Web UI Theme and Style Sync

## Objective
Bring the AADA Web UI (React/MUI) into **visual and thematic alignment** with the existing Flutter mobile app,
while preserving the working FastAPI backend integration and React business logic.

## Context
- Flutter source directory:  
  `/Users/herbert/Development/AADA_flutter_full/NewAppScreens/aada_appv2/lib`
- Web UI directory (target):  
  `/Users/herbert/Projects/AADA/OnlineCourse/aada_lms/frontend/aada_web`
- Backend (FastAPI):  
  `http://localhost:8000/api`
- Environment file:  
  `.env.local` → `VITE_API_BASE_URL=http://localhost:8000/api`

The Flutter app defines AADA’s brand look — color palette, fonts, and layout patterns.  
The React web app already replicates functional modules (Login, Dashboard, Documents, Payments, etc.),  
but uses generic MUI defaults. Your task is to **synchronize the theme, not rebuild the logic**.

---

## Tasks for Claude Code

### 1. Extract Design Tokens from Flutter Source
From `/Users/herbert/Development/AADA_flutter_full/NewAppScreens/aada_appv2/lib`:
- Parse `ThemeData` definitions and constants (colors, typography, button styles).
- Collect all `Color(0xFF...)` values and map them to semantic tokens:
  - `primary`, `secondary`, `accent`, `background`, `surface`, `error`, etc.
- Identify primary font family (e.g., Montserrat, Poppins, or Roboto).
- Capture button and card radius or elevation defaults for consistent feel.

Output summary in comments at top of generated theme file.

---

### 2. Update the React Web App Theme
Modify or create a file at:
frontend/aada_web/src/theme/aadaTheme.ts
Implement using **Material UI v6’s `createTheme()`**:

- Apply extracted colors and fonts.
- Use consistent radii and elevation.
- Ensure MUI and Tailwind share the same palette via `tailwind.config.js`.

Also update:
frontend/aada_web/tailwind.config.js
to include:
```js
theme: {
  extend: {
    colors: { ...mappedFlutterColors },
    fontFamily: { sans: ['Montserrat', 'sans-serif'] },
  },
},

3. Apply the Theme Across the App

Ensure all existing MUI components (Button, TextField, Paper, Typography) use the updated theme.
Do not modify any logic, routing, or API integration.
Specifically, preserve:
	•	Zustand auth store
	•	React Query hooks
	•	Backend connections at VITE_API_BASE_URL
	•	File paths and component exports

Make small UI-level refinements where necessary:
	•	Consistent borderRadius and padding across forms and cards.
	•	Replace any hard-coded color props (e.g., #f0f6ff) with theme tokens.

⸻

4. Verification

When complete:
	•	The app at http://localhost:5173 should have consistent fonts, colors, and feel with the Flutter app.
	•	The login, dashboard, and documents screens should reflect AADA’s palette and typography.
	•	No API endpoints, store logic, or hooks should be changed.

⸻

5. Deliverables
	1.	Updated or newly created file:
	•	frontend/aada_web/src/theme/aadaTheme.ts
	2.	Updated Tailwind configuration:
	•	frontend/aada_web/tailwind.config.js
	3.	Theme import added in main app provider:
	•	frontend/aada_web/src/main.tsx
wrapping <App /> with:
<ThemeProvider theme={aadaTheme}>
  <CssBaseline />
  <App />
</ThemeProvider>
4.	Minor stylistic updates across existing feature components to apply theme tokens.

Output Expectations
	•	Use modern, minimal Material UI + Tailwind fusion.
	•	Preserve all functionality.
	•	Do not overwrite API, hooks, or Zustand logic.
	•	Commit-ready updates for AADA brand alignment.
---

### 💡 Next Step for You
1. Save that file as:
/Users/herbert/Projects/AADA/OnlineCourse/aada_lms/docs/claude_instructions_webui_sync.md
2. Then run this in your terminal:
```bash
cat docs/claude_instructions_webui_sync.md | claude code update .
	3.	Let Claude Code process both paths — it will automatically pull design data from your Flutter app
and restyle the React app for color and typography consistency.
