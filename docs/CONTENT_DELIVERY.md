# AADA LMS - Content Delivery System

## Overview

The AADA LMS delivers interactive educational content through H5P and SCORM packages. This document describes the content delivery architecture, integration methods, and tracking mechanisms.

## Content Types

### H5P (HTML5 Package)

**Purpose**: Interactive learning content (quizzes, hotspots, branching scenarios, presentations)

**Format**: Zip archive containing HTML5 assets and content.json

**Examples**:
- `M1_H5P_WelcomeCarousel` - Interactive carousel introduction
- `M1_H5P_EthicsBranching` - Branching scenario for ethics training
- `M1_H5P_HIPAAHotspot` - Interactive HIPAA training

**Storage Location**: `backend/app/static/modules/module1/`

### SCORM (Sharable Content Object Reference Model)

**Purpose**: Standards-compliant e-learning content with built-in tracking

**Versions Supported**:
- SCORM 1.2 (current)
- SCORM 2004 (planned)

**Format**: Zip package with manifest (imsmanifest.xml)

### Video Content

**Formats**: MP4, WebM
**Delivery**: Direct streaming or HLS for adaptive bitrate
**Storage**: Local filesystem (development), S3/CloudFront (production)

### Documents

**Formats**: PDF, DOCX
**Purpose**: Reading materials, handouts, forms
**Delivery**: Direct download links

## H5P Integration

### H5P Package Structure

```
M1_H5P_Example.h5p (zip file)
├── h5p.json                  # Package metadata
├── content/
│   ├── content.json          # Content definition
│   ├── images/               # Image assets
│   ├── videos/               # Video assets
│   └── audios/               # Audio assets
└── libraries/                # H5P library dependencies (if bundled)
    ├── H5P.InteractiveVideo-1.27/
    ├── H5P.SingleChoiceSet-1.11/
    └── ...
```

**h5p.json** (metadata):
```json
{
  "title": "HIPAA Hotspot Training",
  "language": "en",
  "mainLibrary": "H5P.InteractiveVideo",
  "embedTypes": ["iframe"],
  "license": "U"
}
```

**content/content.json** (content definition):
```json
{
  "params": {
    "interactiveVideo": {
      "video": {
        "files": [
          {
            "path": "videos/hipaa_intro.mp4",
            "mime": "video/mp4"
          }
        ]
      },
      "interactions": [
        {
          "x": 50,
          "y": 50,
          "duration": { "from": 0, "to": 10 },
          "libraryTitle": "Single Choice Set",
          "action": { ... }
        }
      ]
    }
  }
}
```

### Serving H5P Content

**Backend endpoint** (`backend/app/routers/modules.py`):
```python
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.get("/modules/{module_id}/lessons/{lesson_id}/content")
def get_lesson_content(module_id: int, lesson_id: int, db: Session = Depends(get_db)):
    """Serve H5P content for a lesson"""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson or lesson.module_id != module_id:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Get content path
    content_path = lesson.content_url  # e.g., "/static/modules/module1/M1_H5P_Example"
    full_path = os.path.join(STATIC_ROOT, content_path)
    
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Content not found")
    
    return {"content_url": content_path, "type": lesson.content_type}

# Serve static H5P files
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="app/static"), name="static")
```

**Frontend rendering** (Student Portal):
```typescript
// src/features/modules/LessonViewer.tsx
import { useEffect, useRef } from 'react';

export const H5PViewer = ({ contentUrl }: { contentUrl: string }) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  
  useEffect(() => {
    // Load H5P content in iframe
    if (iframeRef.current) {
      iframeRef.current.src = contentUrl;
    }
  }, [contentUrl]);
  
  return (
    <iframe
      ref={iframeRef}
      style={{ width: '100%', height: '600px', border: 'none' }}
      title="H5P Content"
      allowFullScreen
    />
  );
};
```

### H5P Event Tracking

**xAPI Statements**:
H5P emits xAPI (Experience API) statements for tracking user interactions.

```javascript
// Listen for H5P xAPI events
window.H5P = window.H5P || {};
window.H5P.externalDispatcher = window.H5P.externalDispatcher || (() => {});

window.H5P.externalDispatcher.on('xAPI', (event) => {
  const statement = event.data.statement;
  
  // Send to backend
  fetch('/api/xapi/statements', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(statement)
  });
});
```

**Common xAPI Verbs**:
- `attempted` - Started content
- `answered` - Answered a question
- `completed` - Finished content
- `passed` / `failed` - Assessment result
- `interacted` - Interacted with element

### H5P Libraries

**Core Libraries** (required):
- H5P.JoubelUI - UI components
- H5P.Question - Question framework
- H5P.FontIcons - Icon fonts
- H5P.Transition - Transitions/animations

**Content Type Libraries**:
- H5P.InteractiveVideo - Video with interactions
- H5P.SingleChoiceSet - Multiple choice questions
- H5P.Summary - Summary/review
- H5P.TrueFalse - True/false questions
- H5P.BranchingScenario - Branching narratives

**Storage**: Libraries bundled with content or served from CDN

## SCORM Integration

### SCORM Package Structure

```
SCORM_Package.zip
├── imsmanifest.xml           # SCORM manifest
├── adlcp_rootv1p2.xsd        # Schema definitions
├── ims_xml.xsd
├── imscp_rootv1p1p2.xsd
├── imsmd_rootv1p2p1.xsd
└── content/
    ├── index.html            # Launch file
    ├── scormdriver/          # SCORM API adapter
    ├── assets/
    └── ...
```

**imsmanifest.xml** (SCORM manifest):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="com.aada.module1" version="1.0">
  <metadata>
    <schema>ADL SCORM</schema>
    <schemaversion>1.2</schemaversion>
  </metadata>
  <organizations default="org1">
    <organization identifier="org1">
      <title>Module 1: Introduction to Dental Assisting</title>
      <item identifier="item1" identifierref="resource1">
        <title>Lesson 1: Overview</title>
      </item>
    </organization>
  </organizations>
  <resources>
    <resource identifier="resource1" type="webcontent" href="content/index.html">
      <file href="content/index.html"/>
      <!-- Additional files -->
    </resource>
  </resources>
</manifest>
```

### SCORM API Implementation

**Backend SCORM API** (`backend/app/routers/scorm.py`):
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.models import SCORMData, User, Lesson

router = APIRouter()

@router.post("/api/scorm/commit")
def scorm_commit(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Store SCORM CMI data
    
    Expected data:
    {
        "lesson_id": 1,
        "cmi.core.lesson_status": "completed",
        "cmi.core.score.raw": 85,
        "cmi.core.score.max": 100,
        "cmi.suspend_data": "{...}"
    }
    """
    lesson_id = data.get("lesson_id")
    
    # Find or create SCORM data record
    scorm_data = db.query(SCORMData).filter(
        SCORMData.user_id == current_user.id,
        SCORMData.lesson_id == lesson_id
    ).first()
    
    if not scorm_data:
        scorm_data = SCORMData(user_id=current_user.id, lesson_id=lesson_id)
        db.add(scorm_data)
    
    # Update SCORM data
    scorm_data.cmi_core_lesson_status = data.get("cmi.core.lesson_status")
    scorm_data.cmi_core_score_raw = data.get("cmi.core.score.raw")
    scorm_data.cmi_core_score_max = data.get("cmi.core.score.max")
    scorm_data.cmi_suspend_data = data.get("cmi.suspend_data")
    
    db.commit()
    
    return {"success": True}

@router.get("/api/scorm/get/{lesson_id}")
def scorm_get(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve SCORM CMI data for resumption"""
    scorm_data = db.query(SCORMData).filter(
        SCORMData.user_id == current_user.id,
        SCORMData.lesson_id == lesson_id
    ).first()
    
    if not scorm_data:
        return {"status": "not_attempted"}
    
    return {
        "cmi.core.lesson_status": scorm_data.cmi_core_lesson_status,
        "cmi.core.score.raw": scorm_data.cmi_core_score_raw,
        "cmi.core.score.max": scorm_data.cmi_core_score_max,
        "cmi.suspend_data": scorm_data.cmi_suspend_data
    }
```

**Frontend SCORM Player**:
```typescript
// SCORM API implementation in iframe parent window
window.API = {
  LMSInitialize: (param: string) => {
    console.log('SCORM: Initialize', param);
    return "true";
  },
  
  LMSGetValue: (element: string) => {
    // Fetch from backend
    fetch(`/api/scorm/get/${lessonId}`)
      .then(res => res.json())
      .then(data => data[element] || "");
    return "";
  },
  
  LMSSetValue: (element: string, value: string) => {
    // Store locally, commit on finish
    scormData[element] = value;
    return "true";
  },
  
  LMSCommit: (param: string) => {
    // Send to backend
    fetch('/api/scorm/commit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lesson_id: lessonId, ...scormData })
    });
    return "true";
  },
  
  LMSFinish: (param: string) => {
    API.LMSCommit("");
    return "true";
  },
  
  LMSGetLastError: () => "0",
  LMSGetErrorString: (errorCode: string) => "",
  LMSGetDiagnostic: (errorCode: string) => ""
};
```

## xAPI (Tin Can API) Tracking

### xAPI Statement Format

```json
{
  "actor": {
    "name": "Alice Student",
    "mbox": "mailto:alice.student@aada.edu",
    "objectType": "Agent"
  },
  "verb": {
    "id": "http://adlnet.gov/expapi/verbs/completed",
    "display": { "en-US": "completed" }
  },
  "object": {
    "id": "http://aada.edu/modules/1/lessons/5",
    "objectType": "Activity",
    "definition": {
      "name": { "en-US": "HIPAA Hotspot Training" },
      "description": { "en-US": "Interactive HIPAA compliance training" },
      "type": "http://adlnet.gov/expapi/activities/module"
    }
  },
  "result": {
    "score": {
      "scaled": 0.95,
      "raw": 95,
      "min": 0,
      "max": 100
    },
    "success": true,
    "completion": true,
    "duration": "PT15M32S"
  },
  "context": {
    "registration": "ec531277-b57b-4c15-8d91-d292c5b2b8f7",
    "contextActivities": {
      "parent": [{
        "id": "http://aada.edu/modules/1",
        "objectType": "Activity"
      }]
    }
  },
  "timestamp": "2025-11-04T12:34:56.789Z"
}
```

### xAPI Endpoint

**Backend** (`backend/app/routers/xapi.py`):
```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class XAPIStatement(BaseModel):
    actor: dict
    verb: dict
    object: dict
    result: dict | None = None
    context: dict | None = None
    timestamp: datetime

@router.post("/api/xapi/statements")
def record_xapi_statement(
    statement: XAPIStatement,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record xAPI statement"""
    xapi_record = XAPIStatement(
        user_id=current_user.id,
        verb=statement.verb["id"],
        object_id=statement.object["id"],
        result=statement.result,
        context=statement.context,
        timestamp=statement.timestamp
    )
    
    db.add(xapi_record)
    db.commit()
    
    return {"success": True, "id": xapi_record.id}
```

## Content Security Policy (CSP)

**H5P content requires specific CSP directives**:

```nginx
# Allow H5P content to load resources
add_header Content-Security-Policy "
  default-src 'self';
  script-src 'self' 'unsafe-inline' 'unsafe-eval';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: blob:;
  media-src 'self' blob:;
  frame-src 'self';
  font-src 'self' data:;
" always;
```

**Note**: `unsafe-inline` and `unsafe-eval` required for H5P JavaScript execution.

## Progress Tracking

### Completion Criteria

**Lesson Completion**:
- H5P: `completed` xAPI statement received
- SCORM: `cmi.core.lesson_status` = "completed" or "passed"
- Video: Watched 80%+ of duration
- Document: Downloaded or viewed

**Module Completion**:
- All lessons in module marked complete
- Minimum score achieved (if applicable)

**Program Completion**:
- All modules completed
- Externship hours fulfilled
- Final assessment passed

### Progress Calculation

```python
# backend/app/services/progress.py
def calculate_enrollment_progress(enrollment_id: int, db: Session) -> int:
    """Calculate enrollment progress percentage"""
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    program = enrollment.program
    
    # Get all lessons in program
    total_lessons = (
        db.query(Lesson)
        .join(Module)
        .filter(Module.program_id == program.id)
        .count()
    )
    
    if total_lessons == 0:
        return 0
    
    # Count completed lessons
    completed_lessons = (
        db.query(XAPIStatement)
        .filter(
            XAPIStatement.user_id == enrollment.user_id,
            XAPIStatement.verb.contains("completed")
        )
        .count()
    )
    
    # Also count SCORM completions
    completed_scorm = (
        db.query(SCORMData)
        .filter(
            SCORMData.user_id == enrollment.user_id,
            SCORMData.cmi_core_lesson_status.in_(["completed", "passed"])
        )
        .count()
    )
    
    total_completed = completed_lessons + completed_scorm
    progress_pct = int((total_completed / total_lessons) * 100)
    
    # Update enrollment
    enrollment.progress_pct = progress_pct
    db.commit()
    
    return progress_pct
```

## Content Management

### Uploading New Content

**Admin workflow**:
1. Upload H5P/SCORM package via admin portal
2. Backend extracts and validates package
3. Content stored in filesystem
4. Lesson record created in database
5. Content available to students

**Future**: Content management UI for admins to upload/manage packages

### Content Versioning

**Strategy**:
- Store content with version suffix (e.g., `M1_H5P_Example_v1.2`)
- Database tracks current version for each lesson
- Students always see latest version
- Previous versions retained for auditing

## Offline Access (Future)

**Service Worker** for content caching:
```typescript
// Cache H5P content for offline access
self.addEventListener('fetch', (event) => {
  if (event.request.url.includes('/static/modules/')) {
    event.respondWith(
      caches.match(event.request).then((response) => {
        return response || fetch(event.request);
      })
    );
  }
});
```

## Analytics & Reporting

### Content Engagement Metrics

- Time spent per lesson
- Completion rates by module
- Assessment scores distribution
- Most/least engaging content
- Drop-off points in modules

**Query example**:
```sql
-- Average time spent per lesson
SELECT 
  l.title,
  AVG(EXTRACT(EPOCH FROM (x.timestamp - x.started_at))) AS avg_seconds
FROM xapi_statements x
JOIN lessons l ON x.object_id = l.id
WHERE x.verb = 'completed'
GROUP BY l.id, l.title
ORDER BY avg_seconds DESC;
```

---

**Last Updated**: 2025-11-04  
**Maintained By**: Content Team
