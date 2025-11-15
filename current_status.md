⏺ Comprehensive Summary: Current State & Issues

  Where We Are

  Actions Taken This Session:

  1. Identified Root Cause: Base URL configuration included /api suffix, causing double /api/api/... paths
  2. Updated Configuration File: Modified /Users/herbert/Projects/AADA/OnlineCourse/aada_lms/rebuild-frontends.sh
    - Changed: BACKEND_URL="https://aada-backend.nicedune-8fdc50bb.eastus2.azurecontainerapps.io/api" (OLD)
    - To: BACKEND_URL="https://aada-backend.nicedune-8fdc50bb.eastus2.azurecontainerapps.io" (NEW)
  3. Rebuilt Docker Images: Used --no-cache flag to prevent Docker layer caching
  4. Deployed New Revisions: Both portals updated to revision --0000003

  Current Deployed State:

  - Admin Portal:
    - Revision: aada-admin--0000003 (Active, 100% traffic)
    - JS File: index-BJS8OkzL.js
    - Base URL in Code: https://aada-backend.nicedune-8fdc50bb.eastus2.azurecontainerapps.io ✅ (CORRECT - no /api suffix)
  - Student Portal:
    - Revision: aada-student--0000003 (Active, 100% traffic)
    - JS File: index-BsH1yxRI.js
    - Base URL in Code: https://aada-backend.nicedune-8fdc50bb.eastus2.azurecontainerapps.io ✅ (CORRECT - no /api suffix)
  - Backend:
    - URL: https://aada-backend.nicedune-8fdc50bb.eastus2.azurecontainerapps.io
    - Status: Running
    - Expected endpoint: /api/auth/login

  Current Issue Analysis

  What Your Screenshots Show:

  1. Console Errors:
    - Failed to load resource: the server responded with a status of 404 ()
    - URLs shown: aada-backend.nicedun-pgs.io/auth/login1

  2. Red Flags:
    - ❌ Domain is corrupted/truncated: "nicedun-pgs" instead of "nicedune-8fdc50bb.eastus2.azurecontainerapps"
    - ❌ Endpoint has extra "1": login1 instead of login
    - ❌ Missing protocol: shows relative path format
  3. JavaScript File Being Loaded:
    - Your browser: index-BJS8OkzL.js
    - Server serving: index-BJS8OkzL.js
    - ✅ They match (not a caching issue)

  The Paradox:

  - Server code is CORRECT: URL without /api suffix ✅
  - Browser showing WRONG URLs: Corrupted hostnames with "login1" ❌
  - Files match: Not a browser cache issue ❌

  Possible Root Causes

  Theory 1: Admin Portal URL Construction Logic

  The admin portal uses inferBrowserBase() function that dynamically constructs URLs based on window.location. If there's a fallback or error condition, it might generate malformed URLs.

  File: /Users/herbert/Projects/AADA/OnlineCourse/aada_lms/admin_portal/src/api/axiosClient.js:57

  const inferBrowserBase = () => {
    if (typeof window === "undefined") {
      return "http://localhost:8000/api";
    }
    const { protocol, hostname } = window.location;
    const apiPort = import.meta.env.VITE_API_PORT || "8000";
    return `${protocol}//${hostname}:${apiPort}/api`;  // Adds /api
  };

  This function expects the admin portal to be on the same domain as the API, but you're using separate Azure Container Apps for admin portal and backend.

  Theory 2: Environment Variable Not Being Used

  The admin portal might be falling back to the inferBrowserBase() logic instead of using the build-time VITE_API_BASE_URL environment variable.

  Theory 3: Multiple HTTP Clients

  Admin portal might have multiple axios instances or API clients, and some are using old/fallback configurations.

  Expected Behavior vs Actual

  | Component      | Expected                                                             | Actual (Your Screenshot)                   |
  |----------------|----------------------------------------------------------------------|--------------------------------------------|
  | Base URL       | https://aada-backend.nicedune-8fdc50bb.eastus2.azurecontainerapps.io | aada-backend.nicedun-pgs.io (corrupted)    |
  | Login Endpoint | /api/auth/login                                                      | /auth/login1 (missing /api, has extra "1") |
  | Protocol       | https://                                                             | Missing (relative URL)                     |

  Key Files Involved

  1. /Users/herbert/Projects/AADA/OnlineCourse/aada_lms/rebuild-frontends.sh ✅ FIXED
    - Line 5: BACKEND_URL now correct (without /api)
  2. /Users/herbert/Projects/AADA/OnlineCourse/aada_lms/admin_portal/src/api/axiosClient.js ⚠️ SUSPECT
    - Has dynamic URL construction logic
    - Might not be using VITE_API_BASE_URL correctly
    - Line 57: inferBrowserBase() assumes admin portal runs on same domain as API
  3. /Users/herbert/Projects/AADA/OnlineCourse/aada_lms/admin_portal/Dockerfile.prod ✅ OK
    - Accepts VITE_API_BASE_URL build arg correctly

  Database & Auth State

  - ✅ PostgreSQL: Running with pgcrypto encryption
  - ✅ Test Data: 16 users loaded
  - ✅ Admin User: admin@aada.edu / AdminPass!23
  - ✅ Admin Role: Assigned to admin user

  Next Steps to Diagnose

  We need to determine:
  1. Is VITE_API_BASE_URL actually being set during Docker build?
  2. Is the admin portal using the environment variable or falling back to inferBrowserBase()?
  3. Why are URLs getting corrupted with "login1" and truncated hostnames?

  This is where we are before attempting the fix.
