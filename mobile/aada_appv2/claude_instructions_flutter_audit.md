# Task
Audit and analyze the **AADA Flutter** project that is connected to this Claude Code session
to prepare it for migration to the new **AADA FastAPI backend**.

# Backend Context
The new backend service runs locally at  
`http://localhost:8000`  

and its full OpenAPI schema is available at  
`http://localhost:8000/openapi.json`.

Use this schema to map the Flutter app’s current REST calls to the new `/api/...` endpoints.

# Objectives
1. Identify every REST or GraphQL API call used in the Flutter app.  
2. Map those calls to the equivalent or new routes in the FastAPI backend.  
3. Summarize:
   - Networking layer design (HTTP/Dio configuration).  
   - Data-model definitions (`/lib/models`).  
   - State-management approach (`provider`, `riverpod`, `bloc`, etc.).  
4. Produce a technical migration report describing what needs to change for the app
   to communicate with the unified backend.

# Output Format
Markdown summary saved as **AADA_flutter_audit.md** that includes:

- **Project Overview** – Flutter SDK version, dependencies, architecture pattern.  
- **API Inventory** – Table of current endpoints, HTTP methods, and usage files.  
- **Model Mapping** – Comparison between Dart models and Pydantic schemas inferred
  from `openapi.json`.  
- **Auth Flow** – Current authentication method and updates needed for JWT login.  
- **Refactor Recommendations** – Organized by module (Login, Dashboard, Modules, Payments, Externships).  
- **Next-Step Checklist** – Ordered tasks for Codex, Backend Agent, and QA Agent.

# Analysis Steps
1. Read `pubspec.yaml` → record SDK constraint and dependency list.  
2. Inspect `/lib/services`, `/lib/networking`, or similar folders for base URLs and HTTP logic.  
3. List all Dart models under `/lib/models` with key fields.  
4. Map `/lib/screens` folders to their functional areas.  
5. Compare discovered endpoints with those in `http://localhost:8000/openapi.json`.  
6. Build a migration table:  

   | Old Endpoint | File(s) | New FastAPI Endpoint | Change Required |
   |---------------|----------|----------------------|----------------|

7. Describe navigation and state-management structure.  
8. Provide concise, actionable recommendations for each module.

# Notes for Claude
- Treat any file named `api_service.dart`, `network.dart`, `dio_client.dart`,
  or similar as the primary HTTP layer.  
- Keep tone concise and technical—this report will be consumed by developer agents.  
- End the report with a section titled **“Ready for Codex Refactor”** listing the files
  Codex should modify first.

# Deliverable
Write the audit results to a new Markdown file named  
`AADA_flutter_audit.md` at the repository root.
