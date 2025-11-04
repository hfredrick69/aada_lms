from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
import markdown

router = APIRouter(prefix="/modules", tags=["modules"])

# Mapping from database module UUIDs to numeric module IDs
MODULE_UUID_TO_NUMERIC = {
    "2a1e7233-cd90-40e1-9319-618a81539220": "1",  # MA-101 -> Module 1
    "0b2c61a9-fe24-42ea-8c4f-6f738e71ffee": "2",  # MA-201 -> Module 2 (not yet created)
    "aa23b7e3-0ad3-4ca5-8761-7eb57d7c7eaa": "3",  # MA-301 -> Module 3 (not yet created)
}


@router.get("/{module_id}", response_class=HTMLResponse)
async def get_module(module_id: str):
    """Render module markdown as HTML"""
    # Handle UUID lookups from database
    numeric_id = MODULE_UUID_TO_NUMERIC.get(module_id, module_id)

    md_path = Path(f"app/static/modules/module{numeric_id}/Module_{numeric_id}_Lessons_Branded.md")

    if not md_path.exists():
        raise HTTPException(status_code=404, detail="Module not found")

    md_content = md_path.read_text()
    html_content = markdown.markdown(
        md_content,
        extensions=['extra', 'fenced_code', 'tables', 'nl2br', 'attr_list', 'toc']
    )

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Module {numeric_id}</title>
        <style>
            html {{
                scroll-behavior: smooth;
            }}
            body {{
                max-width: 900px;
                margin: 40px auto;
                padding: 20px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            h1, h2, h3 {{
                color: #2c3e50;
                scroll-margin-top: 20px;
            }}
            h1 {{ border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            h2 {{ border-bottom: 1px solid #ecf0f1; padding-bottom: 8px; margin-top: 30px; }}
            iframe {{
                border: 1px solid #ddd;
                border-radius: 4px;
                margin: 20px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            code {{
                background: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }}
            pre {{
                background: #f4f4f4;
                padding: 15px;
                border-radius: 4px;
                overflow-x: auto;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #3498db;
                color: white;
            }}
            blockquote {{
                border-left: 4px solid #3498db;
                padding-left: 20px;
                margin-left: 0;
                color: #555;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
