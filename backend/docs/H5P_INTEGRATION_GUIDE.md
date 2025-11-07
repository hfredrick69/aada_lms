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
- [ ] No CSP violations
- [ ] Activity is interactive and functional
- [ ] Completion callback fires when activity finished

## Example: Adding a New Activity

```bash
# 1. Prepare package
cd /tmp
mkdir M1_H5P_NewActivity
# ... add content, libraries, h5p.json ...
zip -r M1_H5P_NewActivity.h5p M1_H5P_NewActivity

# 2. Deploy
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
