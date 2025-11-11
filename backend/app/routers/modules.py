from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from pathlib import Path
from sqlalchemy.orm import Session
from urllib.parse import urljoin
import markdown
import re

from app.db.session import get_db
from app.db.models.program import Module

router = APIRouter(prefix="/modules", tags=["modules"])

# Mapping from module codes to numeric IDs for file paths
MODULE_CODE_TO_NUMERIC = {
    "MA-101": "1",  # Orientation & Professional Foundations
    "MA-201": "2",  # Clinical Procedures (not yet created)
    "MA-301": "3",  # Externship (not yet created)
}


@router.get("/{module_id}", response_class=HTMLResponse)
async def get_module(module_id: str, request: Request, db: Session = Depends(get_db)):
    """Render module markdown as HTML"""
    # Look up module from database by UUID
    module = db.query(Module).filter(Module.id == module_id).first()

    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    # Map module code to numeric ID for file path
    numeric_id = MODULE_CODE_TO_NUMERIC.get(module.code, module.code)

    md_path = Path(f"app/static/modules/module{numeric_id}/Module_{numeric_id}_Lessons_Branded.md")

    if not md_path.exists():
        raise HTTPException(status_code=404, detail="Module not found")

    md_content = md_path.read_text()
    html_content = markdown.markdown(
        md_content,
        extensions=['extra', 'fenced_code', 'tables', 'nl2br', 'attr_list', 'toc']
    )

    # Convert H5P references to data attributes for frontend embedding
    # Pattern matches: (H5P: `M1_H5P_ActivityName`)
    h5p_pattern = r'\(H5P:\s*<code>([^<]+)</code>\)'
    html_content = re.sub(
        h5p_pattern,
        r'<div data-h5p-activity="\1" class="h5p-embed"></div>',
        html_content
    )

    base_url = str(request.base_url)

    def _absolutize_attr(attr: str, content: str) -> str:
        pattern = rf'{attr}="/([^"]+)"'

        def replacer(match: re.Match) -> str:
            relative_path = match.group(1)
            absolute_path = urljoin(base_url, relative_path)
            return f'{attr}="{absolute_path}"'

        return re.sub(pattern, replacer, content)

    html_content = _absolutize_attr("src", html_content)
    html_content = _absolutize_attr("href", html_content)

    return HTMLResponse(content=html_content)
