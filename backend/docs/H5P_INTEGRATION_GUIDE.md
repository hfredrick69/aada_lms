# H5P Integration Guide

This guide explains how to add H5P interactive activities to module content.

## Overview

H5P activities are embedded inline in module markdown documents. The system automatically:
1. Converts markdown H5P references into HTML divs with `data-h5p-activity` attributes
2. Injects interactive H5P players into those divs on the frontend
3. Tracks completion and sends xAPI statements

## Adding H5P Activities to Modules

### Step 1: Prepare the H5P Package

1. **Ensure all dependencies are included** in the `.h5p` package:
   - Extract a working `.h5p` file to inspect its structure
   - Check `h5p.json` for required `preloadedDependencies`
   - Common dependencies: jQuery.ui, H5P.Question, H5P.JoubelUI, FontAwesome

2. **Update `h5p.json`** if dependencies are missing:
   ```json
   {
     "title": "Activity Title",
     "language": "en",
     "mainLibrary": "H5P.SingleChoiceSet",
     "preloadedDependencies": [
       {
         "machineName": "H5P.SingleChoiceSet",
         "majorVersion": 1,
         "minorVersion": 11
       },
       {
         "machineName": "jQuery.ui",
         "majorVersion": 1,
         "minorVersion": 10
       }
     ]
   }
   ```

3. **Copy missing libraries** from another working H5P package:
   ```bash
   # Extract the working package
   unzip -d /tmp/working_h5p M1_H5P_EthicsBranching.h5p

   # Copy missing library to your package
   cp -r /tmp/working_h5p/jQuery.ui-1.10 /tmp/your_package/
   ```

4. **Repackage** the H5P file:
   ```bash
   cd /tmp/your_package
   zip -r ../M1_H5P_YourActivity.h5p .
   ```

### Step 2: Deploy the H5P Package

Copy the `.h5p` file to the module's static directory:

```bash
cp /tmp/M1_H5P_YourActivity.h5p \
   backend/app/static/modules/module1/M1_H5P_YourActivity.h5p
```

**Naming convention**: `M{module_number}_H5P_{ActivityName}.h5p`

### Step 3: Reference in Markdown

Add the H5P reference in your module markdown file at the desired location:

```markdown
## Section Title

Some instructional content here...

### Interactive Activity 3 – Your Activity

(H5P: `M1_H5P_YourActivity`)

More content follows...
```

**Pattern**: `(H5P: \`ActivityID\`)`

The backticks are required - they create a `<code>` tag that the backend regex matches.

### Step 4: Verify Content Security Policy

If the H5P activity uses media, fonts, or other resources, ensure the CSP in `backend/app/middleware/security.py` allows them:

```python
csp_directives = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
    "img-src 'self' data: blob: https:",
    "media-src 'self' blob: data:",  # Required for audio/video
    "font-src 'self' data: https://cdn.jsdelivr.net",  # Required for icon fonts
    "connect-src 'self' https:",
    "frame-ancestors 'self' http://localhost:5173 http://localhost:5174",
    "base-uri 'self'",
    "form-action 'self'",
]
```

## How It Works

### Backend Processing (modules.py)

1. Markdown is converted to HTML
2. Regex pattern matches `(H5P: <code>ActivityID</code>)`
3. Replaced with: `<div data-h5p-activity="ActivityID" class="h5p-embed"></div>`

```python
h5p_pattern = r'\(H5P:\s*<code>([^<]+)</code>\)'
html_content = re.sub(
    h5p_pattern,
    r'<div data-h5p-activity="\1" class="h5p-embed"></div>',
    html_content
)
```

### Frontend Rendering (ModulePlayerPage.tsx)

1. HTML content is rendered with `dangerouslySetInnerHTML`
2. useEffect queries for `[data-h5p-activity]` divs
3. React's `createRoot` injects `<H5PPlayer>` components into each div
4. Activities appear inline where referenced in the document

```typescript
useEffect(() => {
  if (!contentRef.current || !htmlContent) return;

  const h5pDivs = contentRef.current.querySelectorAll('[data-h5p-activity]');

  h5pDivs.forEach((div) => {
    const activityId = div.getAttribute('data-h5p-activity');
    if (!activityId) return;

    const root = createRoot(div);
    root.render(
      <H5PPlayer
        activityId={activityId}
        title={title}
        height={600}
        onComplete={(result) => handleH5PComplete(activityId, result)}
      />
    );
  });
}, [htmlContent]);
```

## Troubleshooting

### H5P Activity Not Rendering

1. **Check browser console** for errors:
   - 404 errors → Missing library files in the package
   - CSP violations → Update security.py middleware
   - JavaScript errors → Check H5P package integrity

2. **Verify markdown syntax**:
   - Correct: `(H5P: \`M1_H5P_ActivityName\`)`
   - Wrong: `(H5P: M1_H5P_ActivityName)` (missing backticks)

3. **Check file deployment**:
   ```bash
   ls -lh backend/app/static/modules/module1/M1_H5P_ActivityName.h5p
   ```

4. **Verify backend is serving the file**:
   ```bash
   curl http://localhost:8000/api/h5p/M1_H5P_ActivityName
   ```

### Missing Dependencies

If you see 404 errors for library files:

1. Extract a working H5P package to see required libraries
2. Copy missing libraries to your package's root directory
3. Update `h5p.json` preloadedDependencies
4. Repackage and redeploy

### CSP Blocking Resources

If console shows "violates Content Security Policy":

1. Identify resource type (font, media, script, etc.)
2. Add appropriate directive to CSP in `middleware/security.py`
3. Restart backend container

## Testing Checklist

- [ ] H5P package includes all required libraries
- [ ] Package deployed to correct module directory
- [ ] Markdown reference uses correct syntax with backticks
- [ ] Activity appears inline at correct location in document
- [ ] No console errors for missing files

## Dialog Cards Content Structure and Packaging

### File Layout

Create a working directory with the exact structure below before zipping it into `M1_H5P_DialogCards.h5p`:

```
M1_H5P_DialogCards/
├── content/
│   └── content.json          # Dialog definitions and behavior flags
├── h5p.json                  # Metadata + dependency list
└── libraries/
    ├── FontAwesome-4.5/
    ├── H5P.Audio-1.5/
    ├── H5P.Dialogcards-1.9/
    ├── H5P.FontIcons-1.0/
    ├── H5P.JoubelUI-1.3/
    └── H5P.Transition-1.0/
```

### `content/content.json`

Minimum keys:

```jsonc
{
  "title": "Professional Dialog Cards – Module 1",
  "mode": "normal",
  "description": "<p>Intro text...</p>",
  "dialogs": [
    {
      "question": {
        "text": "<p><strong>Front of card</strong></p><p>Prompt.</p>",
        "answer": "<p><strong>Back of card</strong></p><p>Response.</p>",
        "image": null,
        "audio": null,
        "tips": { "front": "", "back": "" }
      }
    }
  ],
  "behaviour": {
    "enableRetry": true,
    "randomCards": true,
    "disableBackwardsNavigation": false,
    "scaleTextNotCard": false
  },
  "answer": "Flip Card",
  "next": "Next",
  "prev": "Previous",
  "retry": "Retry Deck",
  "progressText": "Card @card of @total"
}
```

- Use inline HTML (`<p>`, `<ul>`) for emphasis.  
- Add optional images or audio files to each dialog entry when needed; store media under `content/` and reference via relative paths.  
- Keep cards focused on one behavior/term to limit cognitive load (<200 words per side).

### `h5p.json` Dependencies

| Library              | Version | Location in repo                                           | Reason                          |
|----------------------|---------|------------------------------------------------------------|---------------------------------|
| H5P.Dialogcards      | 1.9     | `backend/app/static/h5p_libraries/H5P.Dialogcards-1.9`     | Main content type               |
| H5P.Audio            | 1.5     | `backend/app/static/h5p_libraries/H5P.Audio-1.5`           | Optional per-card narration     |
| H5P.JoubelUI         | 1.3     | `backend/app/static/h5p_libraries/H5P.JoubelUI-1.3`        | Buttons, progress indicators    |
| H5P.Transition       | 1.0     | `backend/app/static/h5p_libraries/H5P.Transition-1.0`      | Animation helper for dialogs    |
| H5P.FontIcons        | 1.0     | `backend/app/static/h5p_libraries/H5P.FontIcons-1.0`       | Icon sprites used by Joubel UI  |
| FontAwesome          | 4.5     | `backend/app/static/h5p_libraries/FontAwesome-4.5`         | Icon font for controls          |

Declare the same versions inside `h5p.json → preloadedDependencies` and copy the folders into `libraries/` before zipping.

> **Build note:** Some upstream H5P libraries (including Dialog Cards) ship with only `src/` files in this repo. Before copying them into a package, run `npm install && npm run build` inside the library folder (e.g., `backend/app/static/h5p_libraries/H5P.Dialogcards-1.9`). This creates `dist/h5p-dialogcards.{js,css}` which the runtime loads. Remove the temporary `node_modules/` afterward to keep the repo lean.

### Packaging Steps

1. **Author content** in Lumi or a text editor (`content/content.json`).  
2. **Copy libraries** listed above from `backend/app/static/h5p_libraries/` into `libraries/`.  
3. **Zip the package** from the build folder:
   ```bash
   cd tmp/M1_H5P_DialogCards_build
   zip -r ../../backend/app/static/modules/module1/M1_H5P_DialogCards.h5p .
   ```
4. **Spot-check** by extracting with `unzip -l` to verify only expected libraries plus `content/` and `h5p.json` exist.  
5. **Deploy** the `.h5p` file to `backend/app/static/modules/module1/` and keep the unzipped copy (`M1_H5P_DialogCards/`) under version control for easy edits.
6. **Refresh cache** by deleting the activity’s folder under `backend/app/static/.h5p_cache/` (or restarting the backend) so the next request extracts the updated archive.

### Automation via `scripts/h5p_builder.py`

Manually copying dozens of dependencies is error-prone. Use the builder script to package any activity from the unzipped author folder:

```bash
python scripts/h5p_builder.py package \
  --activity-id M1_H5P_DialogCards \
  --source backend/app/static/modules/module1/M1_H5P_DialogCards \
  --output backend/app/static/modules/module1/M1_H5P_DialogCards.h5p
```

What the script does:

- Reads `h5p.json` to gather `preloadedDependencies` and recursively loads their `library.json` files so every nested library ships with the package.
- Uses the master copies under `backend/app/static/h5p_libraries/` as the source of truth. If a library has a `package.json` + `npm run build` script (e.g., Dialog Cards), it compiles the assets inside `tmp/h5p_build/library_workspaces/` and stores the ready-to-ship version under `tmp/h5p_build/library_cache/`. The repo stays clean—no `node_modules` or `dist` files are committed.
- Creates a disposable build folder `tmp/h5p_build/<activity>_package/` that contains `content/`, `h5p.json`, and the dependency tree. It then zips the folder into the requested `.h5p`.

Re-run the script any time the content JSON or dependencies change. Remove `backend/app/static/.h5p_cache/<activity>` (or restart the backend container) so the LMS serves the new archive.

## Recommended H5P Content Types for Medical Assistant Training

### Dialog Cards (H5P.Dialogcards)
- **Use when:** Coaching soft skills, HIPAA phrasing, terminology flashcards.  
- **Tools:** Lumi desktop editor, H5P.org, or manual JSON editing via `content/content.json`.  
- **Structure:** `dialogs` array with `question.text` and `question.answer` HTML blocks; optional `image`, `audio`, and `tips`.  
- **Dependencies:** See table above.  
- **Authoring tips:** Keep each card scenario-driven, add `<ul>` lists for checklists, and enable `randomCards` for better spaced practice.

### Single Choice Set (H5P.SingleChoiceSet)
- **Use when:** Quick knowledge checks after policies or anatomy reviews.  
- **Tools:** Lumi or existing `M1_H5P_PolicyMatch` as a template.  
- **Structure:** `content/content.json` uses `choices` arrays with `text` and `correct` flags plus `behaviour` settings (`autoContinue`, `overallFeedback`).  
- **Dependencies:** `H5P.SingleChoiceSet-1.11`, `H5P.Question-1.5`, `H5P.JoubelUI-1.3`, `H5P.Components-1.0`, `FontAwesome-4.5`, `jQuery.ui-1.10`.  
- **Authoring tips:** Limit each question to one learning objective, use distractors reflecting common clinical errors, and enable `behaviour.autoContinue` for rapid drills.

### Drag and Drop Question (H5P.DragQuestion)
- **Use when:** Teaching instrument setup order, PPE don/doff sequencing, or workflow checklists.  
- **Tools:** Lumi (supports Drag and Drop), or copy from `backend/app/static/h5p_libraries/H5P.DragQuestion-1.14` plus `H5PEditor.DragQuestion-1.10` for authoring.  
- **Structure:** `content.json` defines `background`, `draggables`, `dropZones`, and scoring rules. Media assets (PNG/SVG) go under `content/`.  
- **Dependencies:** `H5P.DragQuestion-1.14`, `H5P.Question-1.5`, `H5P.JoubelUI-1.3`, `H5P.FontIcons-1.0`, `FontAwesome-4.5`, `H5P.Transition-1.0`.  
- **Authoring tips:** Use high-contrast transparent PNGs, set `behaviour.applyPenalties` for incorrect placements, and provide textual descriptions for accessibility.

### Image Hotspots / Image Hotspot Question (H5P.ImageHotspotQuestion)
- **Use when:** Identifying anatomy, clinic-room safety hazards, or equipment locations.  
- **Tools:** Lumi (Image Hotspots) or manual editing of `content/content.json` with `hotspotSettings` arrays.  
- **Structure:** Background image plus `hotspots` each containing coordinates, `content` HTML, and optional correct/incorrect feedback.  
- **Dependencies:** `H5P.ImageHotspotQuestion-1.8`, `H5P.Image-1.1`, `H5P.JoubelUI-1.3`, `H5P.FontIcons-1.0`, `FontAwesome-4.5`.  
- **Authoring tips:** Export annotated floor plans at 1200px width, keep hotspot text under 150 words, and enable zoom for mobile users.

### Mark the Words (H5P.MarkTheWords)
- **Use when:** Rapid-fire medical terminology or abbreviation reviews.  
- **Tools:** Lumi or manual editing (`textField` with `*correct*` tokens).  
- **Structure:** `content.json` contains `textField` (string with marked items) and `behaviour` options like `enableRetry`.  
- **Dependencies:** `H5P.MarkTheWords-1.11`, `H5P.Question-1.5`, `H5P.JoubelUI-1.3`, `FontAwesome-4.5`.  
- **Authoring tips:** Mix no more than 8–10 target words per passage, add rationales in `overallFeedback`, and apply scenario-based prompts (“Identify sterile supplies in this note.”).

### Branching Scenario (H5P.BranchingScenario)
- **Use when:** Practicing escalation paths (e.g., medication errors, professionalism dilemmas).  
- **Tools:** Lumi or the H5P Hub (requires `H5P.BranchingScenario-1.8` plus supporting libraries such as `H5P.Column`, `H5P.Video`, etc.).  
- **Structure:** `content.json` defines `contentId`, `startScreen`, and `branches` referencing other H5P subcontent (Column, Video, QuestionSet). Author small sub-H5P content items and reference them via `contentId`.  
- **Dependencies:** `H5P.BranchingScenario-1.8`, `H5P.BranchingQuestion-1.0`, `H5P.Column-1.18`, `H5P.GoToQuestion-1.3`, `H5P.JoubelUI-1.3`, `FontAwesome-4.5`, plus any nested activity libraries.  
- **Authoring tips:** Keep each branch ≤3 steps to avoid decision fatigue, label choices with actions (“Call supervising RN”) rather than outcomes, and set `endScreens` that summarize policy references.

### Workflow for Any Content Type
1. Prototype in Lumi/H5P.org to validate layout and export a starter `.h5p`.  
2. Extract the file and commit the unzipped folder (for diffs) plus the zipped `.h5p` (for deployment).  
3. Copy required libraries from `backend/app/static/h5p_libraries/` and update `h5p.json`.  
4. Zip, deploy to `backend/app/static/modules/<module>/`, and reference in markdown with `(H5P: \`ActivityID\`)`.
- [ ] No CSP violations
- [ ] Activity is interactive and functional
- [ ] Completion callback fires when activity finished

## Content Management API

The system includes a content management API for instructors/admins to upload and manage module content programmatically.

### Available Endpoints

**Module Markdown**
- `POST /api/content/modules/{module_id}/markdown` - Upload/update module markdown file
- `GET /api/content/modules/{module_id}/markdown` - Download raw markdown

**H5P Activities**
- `POST /api/content/modules/{module_id}/h5p` - Upload H5P activity package
- `GET /api/content/modules/{module_id}/h5p` - List all H5P activities for a module
- `DELETE /api/content/modules/{module_id}/h5p/{activity_id}` - Delete H5P activity

**Supplemental Files**
- `POST /api/content/modules/{module_id}/files` - Upload supplemental file (PDF, image, video, etc.)
- `GET /api/content/modules/{module_id}/files` - List supplemental files
- `DELETE /api/content/modules/{module_id}/files/{file_path}` - Delete supplemental file

**Module List**
- `GET /api/content/modules` - List all modules with content status

### File Size Limits
- Markdown: 10 MB
- H5P: 100 MB
- Supplemental: 50 MB

### Allowed File Types
- Markdown: `.md`, `.markdown`
- H5P: `.h5p`
- Supplemental: `.pdf`, `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.mp4`, `.mp3`, `.zip`

### Security
- All endpoints require authentication (instructor or admin role)
- Filenames are sanitized to prevent directory traversal
- File uploads are validated for type and size
- Automatic backup of existing markdown files before overwrite

### Example: Upload H5P Activity via API

```bash
# Upload H5P activity to module
curl -X POST "http://localhost:8000/api/content/modules/{module_id}/h5p" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@M1_H5P_NewActivity.h5p" \
  -F "activity_id=M1_H5P_NewActivity"

# List activities
curl "http://localhost:8000/api/content/modules/{module_id}/h5p" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Example: Upload Module Markdown via API

```bash
# Upload markdown file
curl -X POST "http://localhost:8000/api/content/modules/{module_id}/markdown" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@Module_1_Lessons_Branded.md"

# Download markdown
curl "http://localhost:8000/api/content/modules/{module_id}/markdown" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o Module_1_Lessons_Branded.md
```

## Example: Adding a New Activity (Manual Deployment)

```bash
# 1. Prepare package
cd /tmp
mkdir M1_H5P_NewActivity
# ... add content, libraries, h5p.json ...
zip -r M1_H5P_NewActivity.h5p M1_H5P_NewActivity

# 2. Deploy manually (or use API)
cp M1_H5P_NewActivity.h5p \
   backend/app/static/modules/module1/

# 3. Reference in markdown
# Edit: backend/app/static/modules/module1/Module_1_Lessons_Branded.md
# Add: (H5P: `M1_H5P_NewActivity`)

# 4. Test
# Navigate to module page in browser
# Verify activity renders inline
# Check console for errors
```
