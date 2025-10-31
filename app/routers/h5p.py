from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
from app.utils.h5p_handler import H5PHandler

router = APIRouter(prefix="/h5p", tags=["h5p"])

# Initialize H5P handler
H5P_STORAGE = Path("app/static/modules")
H5P_CACHE = Path("app/static/.h5p_cache")
h5p_handler = H5PHandler(H5P_STORAGE, H5P_CACHE)


@router.get("/{activity_id}", response_class=HTMLResponse)
async def serve_h5p_player(activity_id: str):
    """Serve H5P player HTML for a specific activity"""

    # Extract H5P content if not already cached
    content_path = h5p_handler.extract_h5p(activity_id)
    if not content_path:
        raise HTTPException(status_code=404, detail=f"H5P activity '{activity_id}' not found")

    # Get h5p.json to extract title
    h5p_json = h5p_handler.get_h5p_json(activity_id)
    title = h5p_json.get('title', 'H5P Activity') if h5p_json else 'H5P Activity'

    # Generate cache key for content path
    cache_key = content_path.name

    # Return HTML player
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>

    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/h5p-standalone@3.6.0/dist/styles/h5p.css">
    <script src="https://cdn.jsdelivr.net/npm/h5p-standalone@3.6.0/dist/main.bundle.js"></script>

    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: #f5f5f5;
        }}
        .h5p-container {{
            max-width: 1024px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="h5p-container">
        <div id="h5p-container"></div>
    </div>

    <script>
        window.addEventListener('load', function() {{
            const el = document.getElementById('h5p-container');

            const options = {{
                h5pJsonPath: '/api/h5p/{activity_id}/content',
                frameJs: 'https://cdn.jsdelivr.net/npm/h5p-standalone@3.6.0/dist/frame.bundle.js',
                frameCss: 'https://cdn.jsdelivr.net/npm/h5p-standalone@3.6.0/dist/styles/h5p.css',
            }};

            if (window.H5PStandalone && window.H5PStandalone.H5P) {{
                new window.H5PStandalone.H5P(el, options);
            }} else if (window.H5PStandalone) {{
                new window.H5PStandalone(el, options);
            }} else {{
                console.error('H5PStandalone not loaded');
            }}
        }});
    </script>
</body>
</html>
    """


@router.get("/{activity_id}/content/{file_path:path}")
async def serve_h5p_content(activity_id: str, file_path: str):
    """Serve H5P content files (h5p.json, content.json, images, libraries, etc.)"""

    content_path = h5p_handler.get_content_path(activity_id)
    if not content_path:
        raise HTTPException(status_code=404, detail=f"H5P activity '{activity_id}' not found")

    # Construct full file path
    requested_file = content_path / file_path

    # Security check - ensure the file is within the content directory
    try:
        requested_file = requested_file.resolve()
        content_path = content_path.resolve()
        if not str(requested_file).startswith(str(content_path)):
            raise HTTPException(status_code=403, detail="Access denied")
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid path")

    if not requested_file.exists() or not requested_file.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

    # Determine media type
    media_type = None
    if requested_file.suffix == '.json':
        media_type = 'application/json'
    elif requested_file.suffix == '.js':
        media_type = 'application/javascript'
    elif requested_file.suffix == '.css':
        media_type = 'text/css'
    elif requested_file.suffix in ['.jpg', '.jpeg']:
        media_type = 'image/jpeg'
    elif requested_file.suffix == '.png':
        media_type = 'image/png'
    elif requested_file.suffix == '.gif':
        media_type = 'image/gif'
    elif requested_file.suffix == '.svg':
        media_type = 'image/svg+xml'

    return FileResponse(requested_file, media_type=media_type)
