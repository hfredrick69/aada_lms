import io
from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from pathlib import Path
from app.utils.h5p_handler import H5PHandler
from app.utils.h5p_matching_builder import (
    H5PGenerationError,
    generate_matching_h5p,
    parse_pairs_from_table,
)

router = APIRouter(prefix="/h5p", tags=["h5p"])

# Initialize H5P handler
H5P_STORAGE = Path("app/static/modules")
H5P_CACHE = Path("app/static/.h5p_cache")
h5p_handler = H5PHandler(H5P_STORAGE, H5P_CACHE)


def _render_matching_form(message: str = "", is_error: bool = False) -> str:
    alert_html = ""
    if message:
        css_class = "error" if is_error else "info"
        alert_html = f'<div class="alert {css_class}">{message}</div>'

    example_rows = "Term,Definition\nSterilization,Process that destroys all microbial life\nPPE,Protective gear worn to minimize exposure\n"  # noqa: E501

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Matching H5P</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            margin: 0;
            padding: 24px;
            background: #f5f5f5;
            color: #222;
        }}
        .container {{
            max-width: 840px;
            margin: 0 auto;
            background: #fff;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 6px 20px rgba(15, 23, 42, 0.08);
        }}
        h1 {{
            margin-top: 0;
            font-size: 1.8rem;
        }}
        label {{
            display: block;
            font-weight: 600;
            margin-top: 18px;
            margin-bottom: 6px;
        }}
        input[type="text"], textarea {{
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid #ccd4e0;
            font-size: 1rem;
            box-sizing: border-box;
            resize: vertical;
        }}
        textarea {{
            min-height: 200px;
            font-family: ui-monospace, SFMono-Regular, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;  # noqa: E501
        }}
        .helper {{
            color: #4a5568;
            font-size: 0.9rem;
            margin-top: 4px;
        }}
        button {{
            margin-top: 24px;
            background: #2563eb;
            color: #fff;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 1rem;
            cursor: pointer;
            transition: background 0.2s ease;
        }}
        button:hover {{
            background: #1d4ed8;
        }}
        .alert {{
            margin-bottom: 16px;
            padding: 12px 16px;
            border-radius: 8px;
        }}
        .alert.info {{
            background: #ebf5ff;
            color: #1d4ed8;
            border: 1px solid #bfdbfe;
        }}
        .alert.error {{
            background: #fef2f2;
            color: #b91c1c;
            border: 1px solid #fecaca;
        }}
        pre {{
            background: #f1f5f9;
            padding: 12px;
            border-radius: 8px;
            overflow-x: auto;
            margin-top: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Generate a Matching H5P Activity</h1>
        <p class="helper">
            Paste a two-column table (comma or tab separated) with one term and one definition per line. You&apos;ll receive a downloadable <code>.h5p</code> file you can upload to any H5P-compatible platform.  # noqa: E501
        </p>
        {alert_html}
        <form method="post">
            <label for="title">Activity title</label>
            <input type="text" id="title" name="title" placeholder="GNPEC Policy Match" required>

            <label for="description">Intro / instructions (optional)</label>
            <textarea id="description" name="description" rows="3" placeholder="Match each policy term with the correct GNPEC requirement."></textarea>  # noqa: E501

            <label for="pairs">Terms and definitions</label>
            <textarea id="pairs" name="pairs" required placeholder="Term,Definition&#10;Asepsis,Removal of pathogenic microorganisms"></textarea>  # noqa: E501
            <p class="helper">Example format (comma, tab, or markdown table supported):</p>
            <pre>{example_rows}</pre>

            <input type="hidden" name="choice_type" value="text">
            <button type="submit">Download .h5p</button>
        </form>
    </div>
</body>
</html>
    """


@router.get("/matching/generator", response_class=HTMLResponse)
async def matching_generator_form():
    return _render_matching_form()


@router.post("/matching/generator")
async def matching_generator(
    title: str = Form(...),
    pairs: str = Form(...),
    choice_type: str = Form("text"),
    description: str = Form(""),
):
    try:
        parsed_pairs = parse_pairs_from_table(pairs)
        content_bytes, filename = generate_matching_h5p(
            title=title,
            pairs=parsed_pairs,
            choice_type=choice_type,
            description=description or title,
        )
    except H5PGenerationError as exc:
        return HTMLResponse(_render_matching_form(str(exc), is_error=True), status_code=400)

    response = StreamingResponse(
        io.BytesIO(content_bytes),
        media_type="application/vnd.h5p+zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
    return response


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
    # cache_key = content_path.name

    # Get backend base URL for absolute paths
    # backend_base_url = os.getenv('BACKEND_BASE_URL', 'http://localhost:8000')

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
        .h5p-question-container {{
            position: relative;
        }}
        .h5p-question-container .h5p-prevent-interaction {{
            display: none !important;
        }}
        .h5p-question-container .h5p-question-full-screen,
        .h5p-question-container .h5p-question-full-screen.h5p-question-button {{
            position: absolute;
            top: 12px;
            right: 12px;
            width: 32px;
            height: 32px;
            z-index: 4;
        }}
        .h5p-question-container .h5p-question-full-screen button {{
            width: 32px;
            height: 32px;
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
                h5pJsonPath: '{activity_id}/content',
                frameJs: 'https://cdn.jsdelivr.net/npm/h5p-standalone@3.6.0/dist/frame.bundle.js',
                frameCss: 'https://cdn.jsdelivr.net/npm/h5p-standalone@3.6.0/dist/styles/h5p.css',
            }};

            console.log('Initializing H5P with path:', options.h5pJsonPath);
            console.log('Document location:', window.location.href);

            const stripIframeBlockers = () => {{
                const iframe = el.querySelector('iframe.h5p-iframe');
                if (!iframe || !iframe.contentDocument) {{
                    return;
                }}
                const iframeDoc = iframe.contentDocument;
                const removeBlockers = () => {{
                    iframeDoc.querySelectorAll('.h5p-prevent-interaction').forEach((node) => node.remove());
                }};
                removeBlockers();

                const iframeObserver = new MutationObserver(removeBlockers);
                iframeObserver.observe(iframeDoc.documentElement, {{
                    childList: true,
                    subtree: true
                }});
            }};
            const containerObserver = new MutationObserver(stripIframeBlockers);
            containerObserver.observe(el, {{ childList: true, subtree: true }});

            try {{
                if (window.H5PStandalone && window.H5PStandalone.H5P) {{
                    new window.H5PStandalone.H5P(el, options);
                    console.log('H5P initialized with H5PStandalone.H5P');
                    setTimeout(stripIframeBlockers, 500);
                    setTimeout(() => {{
                        const inputs = el.querySelectorAll('input');
                        console.log(
                            '[H5P debug] inputs',
                            Array.from(inputs).map((node) => ({{
                                disabled: node.disabled,
                                pointer: window.getComputedStyle(node).pointerEvents
                            }}))
                        );
                    }}, 1200);
                }} else if (window.H5PStandalone) {{
                    new window.H5PStandalone(el, options);
                    console.log('H5P initialized with H5PStandalone');
                    setTimeout(stripIframeBlockers, 500);
                }} else {{
                    console.error('H5PStandalone not loaded');
                }}
            }} catch (error) {{
                console.error('Error initializing H5P:', error);
            }}
        }});
    </script>
</body>
</html>
    """


@router.get("/{activity_id}/content")
async def serve_h5p_json(activity_id: str):
    """Serve h5p.json for H5P Standalone player"""
    content_path = h5p_handler.get_content_path(activity_id)
    if not content_path:
        raise HTTPException(status_code=404, detail=f"H5P activity '{activity_id}' not found")

    h5p_json_file = content_path / "h5p.json"
    if not h5p_json_file.exists():
        raise HTTPException(status_code=404, detail="h5p.json not found")

    return FileResponse(h5p_json_file, media_type='application/json')


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
