# Engagement Tracking System

## Overview

The AADA LMS engagement tracking system monitors student interaction with course modules, capturing scroll position, active time, and sections viewed. This enables resume functionality and provides compliance metrics for student engagement.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Student Browser                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  ModuleProgressTracker Component                       │ │
│  │  - Tracks scroll position                              │ │
│  │  - Monitors active time (focus + activity)             │ │
│  │  - Detects sections viewed (IntersectionObserver)      │ │
│  │  - Auto-saves every 30 seconds                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                          │                                    │
│                          ▼ POST /api/progress/               │
└──────────────────────────┼──────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────────┐
│                   Backend API                                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  /api/progress/ Endpoints                              │ │
│  │  - POST / (create/update progress)                     │ │
│  │  - GET /{user_id} (overall progress)                   │ │
│  │  - GET /{user_id}/module/{module_id} (module progress) │ │
│  └────────────────────────────────────────────────────────┘ │
│                          │                                    │
│                          ▼                                    │
└──────────────────────────┼──────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────────┐
│                   PostgreSQL Database                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  module_progress table                                 │ │
│  │  - last_scroll_position (INTEGER)                      │ │
│  │  - active_time_seconds (INTEGER)                       │ │
│  │  - sections_viewed (JSONB array)                       │ │
│  │  - last_accessed_at (TIMESTAMP)                        │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema

### Table: `module_progress`

```sql
-- Engagement tracking columns
last_scroll_position INTEGER DEFAULT 0
active_time_seconds INTEGER DEFAULT 0
sections_viewed JSONB DEFAULT '[]'::jsonb
last_accessed_at TIMESTAMP WITH TIME ZONE
```

**Field Descriptions:**

- `last_scroll_position`: Scroll position in pixels for resume functionality
- `active_time_seconds`: Total seconds student was actively engaged (focused + recent activity)
- `sections_viewed`: Array of section IDs that student has viewed
- `last_accessed_at`: Timestamp of last progress update

## API Documentation

### Base URL
`http://localhost:8000/api/progress`

### Authentication
All endpoints require authentication via httpOnly cookies.

---

### POST `/api/progress/`

Create or update progress for a module.

**Request Body:**
```json
{
  "enrollment_id": "6a284f0b-f5a1-4068-9f6a-76b7f7551507",
  "module_id": "2e7e1cf1-764d-4afb-a821-dfee913a8d40",
  "last_scroll_position": 1250,
  "active_time_seconds": 45,
  "sections_viewed": ["section-intro", "section-chapter1", "section-chapter2"]
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "enrollment_id": "6a284f0b-f5a1-4068-9f6a-76b7f7551507",
  "module_id": "2e7e1cf1-764d-4afb-a821-dfee913a8d40",
  "module_code": "M1",
  "module_title": "Module 1: Introduction",
  "scorm_status": "incomplete",
  "score": null,
  "progress_pct": 0,
  "last_activity": null,
  "last_scroll_position": 1250,
  "active_time_seconds": 45,
  "sections_viewed": ["section-intro", "section-chapter1", "section-chapter2"],
  "last_accessed_at": "2025-11-06T00:51:49.015751Z"
}
```

**cURL Example:**
```bash
curl -b /tmp/cookies.txt \
  -X POST http://localhost:8000/api/progress/ \
  -H "Content-Type: application/json" \
  -d '{
    "enrollment_id": "6a284f0b-f5a1-4068-9f6a-76b7f7551507",
    "module_id": "2e7e1cf1-764d-4afb-a821-dfee913a8d40",
    "last_scroll_position": 1250,
    "active_time_seconds": 45,
    "sections_viewed": ["section-intro", "section-chapter1"]
  }'
```

---

### GET `/api/progress/{user_id}/module/{module_id}`

Retrieve progress for a specific module.

**Response (200 OK):**
```json
{
  "id": "uuid",
  "enrollment_id": "6a284f0b-f5a1-4068-9f6a-76b7f7551507",
  "module_id": "2e7e1cf1-764d-4afb-a821-dfee913a8d40",
  "module_code": "M1",
  "module_title": "Module 1: Introduction",
  "scorm_status": "incomplete",
  "score": null,
  "progress_pct": 0,
  "last_activity": null,
  "last_scroll_position": 1250,
  "active_time_seconds": 45,
  "sections_viewed": ["section-intro", "section-chapter1"],
  "last_accessed_at": "2025-11-06T00:51:49.015751Z"
}
```

**cURL Example:**
```bash
USER_ID="4c89b4db-9989-4886-acef-39540ecec854"
MODULE_ID="2e7e1cf1-764d-4afb-a821-dfee913a8d40"

curl -b /tmp/cookies.txt \
  "http://localhost:8000/api/progress/$USER_ID/module/$MODULE_ID"
```

---

### GET `/api/progress/{user_id}`

Retrieve overall progress for a user across all modules.

**Response (200 OK):**
```json
{
  "user_id": "4c89b4db-9989-4886-acef-39540ecec854",
  "enrollment_id": "6a284f0b-f5a1-4068-9f6a-76b7f7551507",
  "program_name": "Dental Assistant Program",
  "total_modules": 10,
  "completed_modules": 3,
  "completion_percentage": 30.0,
  "modules": [
    {
      "id": "uuid",
      "enrollment_id": "6a284f0b-f5a1-4068-9f6a-76b7f7551507",
      "module_id": "2e7e1cf1-764d-4afb-a821-dfee913a8d40",
      "module_code": "M1",
      "module_title": "Module 1: Introduction",
      "scorm_status": "completed",
      "score": 95,
      "progress_pct": 100,
      "last_activity": null,
      "last_scroll_position": 3500,
      "active_time_seconds": 1820,
      "sections_viewed": ["intro", "chapter1", "chapter2", "conclusion"],
      "last_accessed_at": "2025-11-06T00:51:49.015751Z"
    }
    // ... more modules
  ]
}
```

## Frontend Component

### ModuleProgressTracker

React component that automatically tracks engagement metrics.

**Location:** `frontend/aada_web/src/components/ModuleProgressTracker.tsx`

**Usage:**

```tsx
import ModuleProgressTracker from '@/components/ModuleProgressTracker';

function ModuleContentPage() {
  const enrollmentId = "6a284f0b-f5a1-4068-9f6a-76b7f7551507";
  const moduleId = "2e7e1cf1-764d-4afb-a821-dfee913a8d40";

  return (
    <div>
      <ModuleProgressTracker
        enrollmentId={enrollmentId}
        moduleId={moduleId}
        enabled={true}
        sectionSelector="h2, h3"
        saveInterval={30000}
      />

      <div>
        <h2 id="section-intro">Introduction</h2>
        <p>Module content here...</p>

        <h2 id="section-chapter1">Chapter 1</h2>
        <p>More content...</p>
      </div>
    </div>
  );
}
```

**Props:**

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `enrollmentId` | string | Yes | - | Student's enrollment UUID |
| `moduleId` | string | Yes | - | Module UUID |
| `enabled` | boolean | No | true | Enable/disable tracking |
| `sectionSelector` | string | No | "h2, h3" | CSS selector for sections to track |
| `saveInterval` | number | No | 30000 | Auto-save interval in milliseconds |

**Features:**

1. **Scroll Position Tracking**
   - Captures scroll position in real-time
   - Auto-restores scroll position on page load

2. **Active Time Tracking**
   - Only counts time when page is focused
   - Requires recent activity (mouse move, keyboard, scroll)
   - 5-second inactivity threshold

3. **Section Viewing Detection**
   - Uses IntersectionObserver API
   - 50% visibility threshold
   - Automatically generates IDs for sections without them

4. **Auto-Save**
   - Saves progress every 30 seconds by default
   - Saves on component unmount
   - Debounced to prevent excessive API calls

## How It Works

### 1. Scroll Position Tracking

```typescript
useEffect(() => {
  const handleScroll = () => {
    setScrollPosition(window.scrollY);
    lastActivityRef.current = Date.now();
  };

  window.addEventListener('scroll', handleScroll, { passive: true });
  return () => window.removeEventListener('scroll', handleScroll);
}, []);
```

- Listens to scroll events
- Updates scroll position state
- Marks as recent activity

### 2. Active Time Tracking

```typescript
useEffect(() => {
  activeTimeIntervalRef.current = setInterval(() => {
    const timeSinceActivity = Date.now() - lastActivityRef.current;
    const isActive = isPageFocusedRef.current && timeSinceActivity < 5000;

    if (isActive) {
      setActiveTimeSeconds((prev) => prev + 1);
    }
  }, 1000);

  return () => clearInterval(activeTimeIntervalRef.current);
}, []);
```

- Checks every second if student is active
- Requires page focus AND activity within last 5 seconds
- Activity = mouse move, keyboard input, scroll

### 3. Section Viewing Detection

```typescript
observerRef.current = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting && entry.target.id) {
        setSectionsViewed((prev) => {
          const updated = new Set(prev);
          updated.add(entry.target.id);
          return updated;
        });
      }
    });
  },
  {
    threshold: 0.5,
    rootMargin: '-50px 0px',
  }
);
```

- Observes all sections matching selector
- Triggers when section is 50% visible
- Adds section ID to viewed set

### 4. Auto-Save Mechanism

```typescript
useEffect(() => {
  if (!enabled) return;

  saveIntervalRef.current = setInterval(() => {
    saveProgress();
  }, saveInterval);

  return () => {
    if (saveIntervalRef.current) {
      clearInterval(saveIntervalRef.current);
    }
    // Save on unmount
    saveProgress();
  };
}, [enabled, saveInterval, saveProgress]);
```

- Saves progress at configured interval (default 30s)
- Saves on component unmount
- Only saves if tracking is enabled

## Testing

### E2E Test Suite

**Location:** `e2e-tests/progress-tracking.spec.ts`

**Test Coverage:**

1. **API Tests (5 tests)**
   - Save progress with engagement data
   - Retrieve saved progress
   - Update existing progress
   - Retrieve overall user progress
   - Prevent unauthorized access

2. **Component Tests (3 tests)**
   - Track scroll position and save progress
   - Resume from last scroll position
   - Track active time accurately

3. **Integration Tests (1 test)**
   - Persist progress across page reloads

**Running Tests:**

```bash
# Run all E2E tests
npm run test:e2e

# Run only progress tracking tests
npm run test:e2e -- progress-tracking.spec.ts
```

### Manual Testing

**1. Login:**
```bash
curl -s -c /tmp/cookies.txt \
  -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice.student@aada.edu","password":"AlicePass!23"}'
```

**2. Save Progress:**
```bash
curl -b /tmp/cookies.txt \
  -X POST http://localhost:8000/api/progress/ \
  -H "Content-Type: application/json" \
  -d '{
    "enrollment_id": "6a284f0b-f5a1-4068-9f6a-76b7f7551507",
    "module_id": "2e7e1cf1-764d-4afb-a821-dfee913a8d40",
    "last_scroll_position": 1250,
    "active_time_seconds": 45,
    "sections_viewed": ["section-intro", "section-chapter1"]
  }'
```

**3. Retrieve Progress:**
```bash
USER_ID="4c89b4db-9989-4886-acef-39540ecec854"
MODULE_ID="2e7e1cf1-764d-4afb-a821-dfee913a8d40"

curl -b /tmp/cookies.txt \
  "http://localhost:8000/api/progress/$USER_ID/module/$MODULE_ID"
```

**4. Verify in Database:**
```bash
docker exec -it aada_lms-db-1 psql -U aada_user -d aada_lms -c \
  "SELECT last_scroll_position, active_time_seconds, sections_viewed, last_accessed_at
   FROM module_progress
   WHERE module_id = '2e7e1cf1-764d-4afb-a821-dfee913a8d40'
   LIMIT 1;"
```

## Security & Authorization

### Authorization Rules

1. **Students:**
   - Can only view their own progress
   - Can only update their own progress
   - Verified via enrollment ownership check

2. **Instructors/Admins:**
   - Can view any student's progress
   - Can update any student's progress
   - Role-based access check

### Implementation

```python
# Students can only see their own progress
if user_id != current_user.id and not any(role in ["admin", "instructor"] for role in current_user.roles):
    raise HTTPException(status_code=403, detail="Not authorized to view this progress")

# Students can only update their own progress
is_owner = enrollment.user_id == current_user.id
is_authorized = any(role in ["admin", "instructor"] for role in current_user.roles)
if not is_owner and not is_authorized:
    raise HTTPException(status_code=403, detail="Not authorized to update this progress")
```

## Configuration

### Environment Variables

No special environment variables required. Uses existing database connection.

### Component Configuration

```tsx
// Default configuration
<ModuleProgressTracker
  enrollmentId={enrollmentId}
  moduleId={moduleId}
  enabled={true}              // Enable tracking
  sectionSelector="h2, h3"    // Track h2 and h3 headings
  saveInterval={30000}        // Save every 30 seconds
/>

// Custom configuration for detailed tracking
<ModuleProgressTracker
  enrollmentId={enrollmentId}
  moduleId={moduleId}
  enabled={true}
  sectionSelector="section[data-track]"  // Track only specific sections
  saveInterval={15000}                    // Save every 15 seconds
/>
```

## Compliance & Reporting

### Metrics Available

1. **Scroll Position**
   - Shows how far student progressed through content
   - Enables resume functionality

2. **Active Time**
   - Accurate measure of engaged learning time
   - Excludes idle/unfocused time
   - Useful for compliance reporting

3. **Sections Viewed**
   - Shows which content sections student viewed
   - Identifies skipped sections
   - Validates content completion

4. **Last Accessed**
   - Timestamp of last activity
   - Tracks engagement recency
   - Identifies inactive students

### Compliance Use Cases

- **Minimum engagement hours:** Sum `active_time_seconds` across modules
- **Content coverage:** Check `sections_viewed` completeness
- **Progress tracking:** Monitor `last_accessed_at` for inactive students
- **Audit trail:** All updates timestamped in database

## Known Limitations

1. **xAPI Integration Disabled**
   - xAPI statement queries temporarily disabled due to SQLAlchemy JSONB syntax issues
   - Does not affect engagement tracking functionality
   - To be fixed in future update

2. **Browser Compatibility**
   - Requires IntersectionObserver support (all modern browsers)
   - Fallback: Manual section tracking if needed

3. **Activity Detection**
   - 5-second inactivity threshold
   - May not capture reading-only activities
   - Adjustable via component modification

## Troubleshooting

### Progress Not Saving

**Check:**
1. Component mounted correctly
2. Authentication cookies valid
3. Backend logs for errors
4. Network tab in browser DevTools

**Fix:**
```bash
# Check backend logs
docker logs aada_lms-backend-1 --tail 50

# Verify authentication
curl -b /tmp/cookies.txt http://localhost:8000/api/auth/me
```

### Scroll Position Not Restoring

**Check:**
1. Progress loaded before scroll restoration
2. `hasLoadedProgress` state is true
3. Content height sufficient for scroll

**Fix:**
```typescript
// Increase delay if needed
useEffect(() => {
  if (hasLoadedProgress && savedProgress?.last_scroll_position) {
    setTimeout(() => {
      window.scrollTo(0, savedProgress.last_scroll_position);
    }, 500); // Increase from 100ms to 500ms
  }
}, [hasLoadedProgress, savedProgress]);
```

### Sections Not Being Tracked

**Check:**
1. Sections have unique IDs
2. Sections match `sectionSelector`
3. Sections are visible during testing

**Fix:**
```tsx
// Ensure sections have IDs
<h2 id="section-intro">Introduction</h2>
<h2 id="section-chapter1">Chapter 1</h2>

// Or use data attributes
<section data-track id="custom-section">Content</section>
// Update selector:
sectionSelector="section[data-track]"
```

## Future Enhancements

1. **Video Engagement Tracking**
   - Track video play/pause/seek events
   - Monitor video watch time
   - Detect video completion

2. **Quiz Interaction Tracking**
   - Track attempts per question
   - Monitor time spent per question
   - Record answer changes

3. **Mobile Optimization**
   - Touch event tracking
   - Mobile-specific activity detection
   - Reduced save frequency on mobile

4. **Analytics Dashboard**
   - Visual progress charts
   - Engagement heatmaps
   - Completion trends

5. **xAPI Integration**
   - Fix SQLAlchemy JSONB queries
   - Full xAPI statement support
   - LRS integration

## Support

For issues or questions:
- Check backend logs: `docker logs aada_lms-backend-1`
- Check frontend console: Browser DevTools
- Review test cases: `e2e-tests/progress-tracking.spec.ts`
- Reference implementation: `frontend/aada_web/src/components/ModuleProgressTracker.tsx`
