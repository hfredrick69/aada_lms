# H5P Content Infrastructure

**Last Updated:** November 3, 2025

## Overview

The AADA LMS includes a complete H5P content creation and delivery system. H5P (HTML5 Package) allows creation of interactive content like quizzes, branching scenarios, matching exercises, and more - all playable in web browsers and mobile apps.

---

## 🏗️ Architecture Components

### 1. **H5P Content Serving System**

**Location:** `backend/app/routers/h5p.py`

**Endpoints:**
- `GET /api/h5p/{activity_id}` - Serves H5P player HTML for an activity
- `GET /api/h5p/{activity_id}/content/{file_path}` - Serves H5P assets (JSON, JS, CSS, images)
- `GET /api/h5p/matching/generator` - H5P Matching generator web form
- `POST /api/h5p/matching/generator` - Creates and downloads Matching H5P package

**Key Features:**
- Automatic H5P package extraction and caching
- H5P Standalone player integration (browser-based, no server-side rendering)
- Security: Path traversal protection for content serving
- Smart caching based on file modification time

**Example URL:** http://localhost:8000/api/h5p/M1_H5P_EthicsBranching

### 2. **H5P Handler Utility**

**Location:** `backend/app/utils/h5p_handler.py`

**Responsibilities:**
- Locates .h5p files in module directories
- Extracts .h5p packages (ZIP files) to cache
- Manages library dependencies
- Provides metadata access (h5p.json)

**Key Methods:**
```python
H5PHandler.extract_h5p(activity_id)      # Extract H5P to cache
H5PHandler.get_h5p_json(activity_id)     # Get metadata
H5PHandler.get_content_path(activity_id) # Get extracted content path
```

**Cache Location:** `backend/app/static/.h5p_cache/`

### 3. **H5P Matching Generator**

**Location:** `backend/app/utils/h5p_matching_builder.py`

**Purpose:** Create H5P.Matching activities programmatically without manual authoring tools.

**Why This Exists:**
- Manual H5P authoring is inefficient
- Allows rapid creation of matching/flashcard activities
- Accepts simple CSV/TSV/Markdown table input
- Generates production-ready .h5p packages

**Input Format:**
```
Term,Definition
Asepsis,Removal of pathogenic microorganisms
PPE,Protective gear worn to minimize exposure
Sterilization,Process that destroys all microbial life
```

**Output:** Downloadable .h5p file ready for upload anywhere

**Example URL:** http://localhost:8000/api/h5p/matching/generator

**Technical Details:**
- Builds complete H5P packages with all dependencies
- Includes H5P.Matching library + dependencies (H5P.JoubelUI, FontAwesome, etc.)
- Creates proper h5p.json and content.json structure
- Validates library assets exist before packaging

---

## 📂 Directory Structure

```
backend/app/static/
├── h5p_libraries/                    # H5P library source files
│   ├── H5P.Matching-1.0/
│   ├── H5P.BranchingScenario-1.7/
│   ├── H5P.InteractiveVideo-1.27/
│   ├── H5P.JoubelUI-1.3/
│   ├── FontAwesome-4.5/
│   └── [60+ other libraries]
│
├── modules/
│   └── module1/
│       ├── Module_1_Lessons_Branded.md          # Course content
│       ├── M1_H5P_EthicsBranching.h5p          # Branching scenario
│       ├── M1_H5P_EthicsBranching/             # Extracted (unzipped)
│       ├── M1_H5P_HIPAAHotspot/                # HIPAA Hotspot activity
│       │   ├── content/
│       │   │   ├── content.json
│       │   │   ├── images/
│       │   │   └── videos/
│       │   ├── extracted/                       # Libraries
│       │   ├── h5p.json
│       │   └── HIPAA_Hotspot_Fixed.h5p
│       └── assets/
│           └── aada_logo.png
│
└── .h5p_cache/                      # Auto-extracted H5P content (gitignored)
    └── [md5-hashes]/
```

---

## 🎓 Module 1 Content Delivery

### Module Content Router

**Location:** `backend/app/routers/modules.py`

**Endpoint:** `GET /api/modules/{module_id}`

**What It Does:**
- Reads markdown file: `app/static/modules/module{id}/Module_{id}_Lessons_Branded.md`
- Converts markdown to styled HTML using Python `markdown` library
- Returns complete HTML page with embedded CSS
- Supports: tables, code blocks, links, images, iframes (for H5P embeds)

**Example URL:** http://localhost:8000/api/modules/1

**HTML Features:**
- Responsive design (max-width: 900px)
- Smooth scrolling for anchor links
- Professional typography
- Styled tables, code blocks, blockquotes
- Ready for H5P iframe embedding

### Module 1 Content Structure

**Markdown File:** `backend/app/static/modules/module1/Module_1_Lessons_Branded.md`

**Current Status:**
- ~1,031 words written
- Target: 12,000-15,000 words
- **92% incomplete** ⚠️

**Sections Defined:**
1. Welcome to AADA (Georgia Context)
2. Professionalism & Ethics
3. HIPAA & OSHA Essentials
4. Communication & Team Dynamics
5. Orientation to LMS & Student Policies
6. Summary & Assessment
7. Georgia References
8. Appendices

**Total Time Allocation:** 40 hours
- Reading & Media: 19.5 h
- Interactive Practice: 11 h
- Live/Collaborative: 5.5 h
- Reflection & Assessment: 4 h

---

## 🎨 Available H5P Activities (Module 1)

### 1. Ethics Branching Scenario
**ID:** `M1_H5P_EthicsBranching`
**Type:** H5P.BranchingScenario
**File:** `backend/app/static/modules/module1/M1_H5P_EthicsBranching.h5p`
**Size:** 7.5 MB
**Status:** ✅ Working

**URL:** http://localhost:8000/api/h5p/M1_H5P_EthicsBranching

**Content:**
- Interactive decision-tree scenarios
- Ethical dilemmas in dental settings
- Multiple endings based on choices
- GIFs and images throughout

### 2. HIPAA Hotspot
**ID:** `M1_H5P_HIPAAHotspot`
**Type:** H5P.InteractiveVideo
**File:** `backend/app/static/modules/module1/M1_H5P_HIPAAHotspot/HIPAA_Hotspot_Fixed.h5p`
**Size:** 2.1 MB
**Status:** ✅ Working

**URL:** http://localhost:8000/api/h5p/M1_H5P_HIPAAHotspot

**Content:**
- Interactive video with hotspots
- HIPAA policy scenarios
- True/False questions
- Summary questions

### 3. (Planned) GNPEC Policy Match
**ID:** TBD
**Type:** H5P.Matching
**Status:** ❌ Not created yet

**Will Cover:** GNPEC compliance terminology matching

### 4. (Planned) Professional Dialog Cards
**ID:** TBD
**Type:** H5P.DialogCards
**Status:** ❌ Not created yet

**Will Cover:** Communication scenarios flashcards

---

## 🔧 H5P Library Ecosystem

### Available Libraries (60+)

**Core Interactive:**
- H5P.BranchingScenario-1.7
- H5P.InteractiveVideo-1.27
- H5P.Matching-1.0
- H5P.DialogCards-1.9
- H5P.DragQuestion-1.14
- H5P.MultiChoice-1.16
- H5P.Summary-1.10
- H5P.SingleChoiceSet-1.11

**Support Libraries:**
- H5P.JoubelUI-1.3 (UI components)
- FontAwesome-4.5 (icons)
- H5P.Question-1.5 (question framework)
- H5P.Video-1.6 (video player)

**Library Location:** `backend/app/static/h5p_libraries/`

### Adding New Libraries

To add a new H5P library type:

1. Download library from https://h5p.org/content-types-and-applications
2. Extract to `backend/app/static/h5p_libraries/LibraryName-X.Y/`
3. Ensure `library.json` exists
4. If library has build step (TypeScript/React):
   ```bash
   cd backend/app/static/h5p_libraries/LibraryName-X.Y/
   npm install
   npm run build
   ```
5. Verify preloaded assets exist (CSS/JS files referenced in library.json)

---

## 📝 Creating H5P Content

### Method 1: H5P Matching Generator (Fast)

**Best For:** Matching exercises, flashcards, vocabulary

**Steps:**
1. Visit http://localhost:8000/api/h5p/matching/generator
2. Enter activity title (e.g., "GNPEC Policy Match")
3. Paste term/definition pairs (CSV, TSV, or Markdown table)
4. Click "Download .h5p"
5. Upload to `backend/app/static/modules/module1/`
6. Access at `/api/h5p/YourActivityName`

**Example Input:**
```
Asepsis,Removal of pathogenic microorganisms
PPE,Protective gear worn to minimize exposure
Sterilization,Process that destroys all microbial life
```

### Method 2: H5P.org Editor (Full-Featured)

**Best For:** Complex activities (branching scenarios, interactive videos)

**Steps:**
1. Go to https://h5p.org/node/add/h5p-content
2. Create account (free)
3. Choose content type
4. Author content in visual editor
5. Download .h5p file
6. Upload to `backend/app/static/modules/module1/`

### Method 3: Lumi Desktop App (Offline)

**Best For:** Offline authoring, testing

**Download:** https://lumi.education/

---

## 🚀 Integration with Student Portal

### Current State

**Backend:** ✅ Fully functional
- H5P serving working
- Module markdown rendering working
- All content accessible via API

**Frontend:** ⚠️ Not integrated yet
- Student portal exists (localhost:5174)
- "Modules" navigation exists
- **No module player/H5P integration**

### Required Integration Steps

1. **Create Module Player Page** (`frontend/aada_web/src/pages/ModulePage.tsx`)
   - Fetch Module 1 content from `/api/modules/1`
   - Render HTML content
   - Detect H5P activity links
   - Embed H5P iframes inline

2. **Add H5P Player Component** (`frontend/aada_web/src/components/H5PPlayer.tsx`)
   - Accept `activityId` prop
   - Render iframe pointing to `/api/h5p/{activityId}`
   - Track completion via xAPI

3. **Track Progress**
   - Capture H5P xAPI statements
   - POST to `/api/xapi/statements`
   - Update module completion status

4. **Navigation**
   - Add "My Courses" page
   - List enrolled modules
   - Show progress indicators
   - Link to Module 1 player

---

## 📊 xAPI Tracking

H5P activities automatically generate xAPI statements when students interact with them.

**Example Statement:**
```json
{
  "actor": {
    "name": "Alice Student",
    "mbox": "mailto:alice.student@aada.edu"
  },
  "verb": {
    "id": "http://adlnet.gov/expapi/verbs/completed",
    "display": {"en-US": "completed"}
  },
  "object": {
    "id": "http://localhost:8000/api/h5p/M1_H5P_EthicsBranching",
    "objectType": "Activity"
  },
  "result": {
    "score": {"scaled": 0.85},
    "completion": true,
    "success": true
  }
}
```

**Backend Endpoint:** `POST /api/xapi/statements`

**Storage:** PostgreSQL `xapi_statements` table

---

## 🔄 Workflow: Adding New H5P Content

### For Matching Activities (Quick)

```bash
# 1. Create term/definition list
echo "Term,Definition
Asepsis,Removal of pathogenic microorganisms
PPE,Protective gear" > terms.csv

# 2. Use generator (or visit web form)
curl -X POST http://localhost:8000/api/h5p/matching/generator \
  -F "title=GNPEC Policy Match" \
  -F "pairs=@terms.csv" \
  -o gnpec-policy-match.h5p

# 3. Upload to module directory
mv gnpec-policy-match.h5p backend/app/static/modules/module1/

# 4. Access at:
# http://localhost:8000/api/h5p/gnpec-policy-match
```

### For Other Activity Types

1. Author on H5P.org or Lumi
2. Download .h5p file
3. Copy to `backend/app/static/modules/module1/`
4. Access at `/api/h5p/{filename-without-extension}`

---

## 🎯 Next Steps for H5P Content

### Immediate (High Priority)

1. **Create Missing H5P Activities:**
   - GNPEC Policy Match (use generator)
   - Professional DialogCards (use H5P.org)

2. **Integrate with Student Portal:**
   - Build Module Player page
   - Embed H5P activities
   - Add navigation

3. **Complete Module 1 Content:**
   - Write remaining 11,000 words
   - Insert H5P activity references in markdown
   - Add assessment sections

### Future Enhancements

1. **H5P Studio Generator:**
   - Extend generator to support more content types
   - Add DialogCards generator
   - Add Timeline generator

2. **Mobile App Integration:**
   - Use same H5P serving endpoints
   - H5P Standalone works in WebView
   - Track xAPI from mobile

3. **Analytics Dashboard:**
   - Visualize H5P completion rates
   - Track time-on-task per activity
   - Identify struggling students

---

## 📖 References

- **H5P Official:** https://h5p.org
- **H5P Standalone:** https://github.com/tunapanda/h5p-standalone
- **H5P Content Types:** https://h5p.org/content-types-and-applications
- **Lumi Desktop:** https://lumi.education
- **xAPI Spec:** https://xapi.com/overview/

---

## 🐛 Troubleshooting

### H5P Activity Not Loading

**Error:** "H5P activity 'xyz' not found"

**Fix:**
1. Check file exists: `ls backend/app/static/modules/module1/*.h5p`
2. Verify activity_id matches filename (without .h5p)
3. Check cache: `ls backend/app/static/.h5p_cache/`
4. Force refresh: add `?refresh=1` to URL

### Library Missing Error

**Error:** "Required library X.Y not found"

**Fix:**
1. Check `backend/app/static/h5p_libraries/LibraryName-X.Y/`
2. Verify `library.json` exists
3. If library needs building:
   ```bash
   cd backend/app/static/h5p_libraries/LibraryName-X.Y/
   npm install && npm run build
   ```

### Generator Fails

**Error:** "Provide at least two valid rows"

**Fix:**
- Ensure CSV has at least 2 rows
- Check delimiter (comma vs tab)
- Remove header row if present
- Use example format from form

---

## 📞 Support

For H5P content creation assistance:
- Email: compliance@aada.edu
- Internal: Check #h5p-content Slack channel
- Documentation: This file!
