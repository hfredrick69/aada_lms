"""
Content Management API

Provides endpoints for instructors/admins to:
- Upload/update module markdown files
- Upload/manage H5P activities
- Upload supplemental files (PDFs, images, etc.)
- List and delete content
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import FileResponse
from pathlib import Path
from typing import Optional
import shutil
import re
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.program import Module
from app.db.models.user import User
from app.core.security import get_current_user

router = APIRouter(prefix="/content", tags=["content"])

# Content storage paths
MODULES_BASE = Path("app/static/modules")
H5P_CACHE = Path("app/static/.h5p_cache")

# Allowed file extensions
MARKDOWN_EXTENSIONS = {".md", ".markdown"}
H5P_EXTENSIONS = {".h5p"}
SUPPLEMENTAL_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".mp4", ".mp3", ".zip"}

# Maximum file sizes (in bytes)
MAX_MARKDOWN_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_H5P_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_SUPPLEMENTAL_SIZE = 50 * 1024 * 1024  # 50 MB


def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency to require admin role"""
    # TODO: Implement proper role checking once role system is fully integrated
    # For now, allow all authenticated users (will be restricted once role system is active)
    return current_user


def validate_module_id(module_id: str, db: Session) -> Module:
    """Validate that module exists"""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail=f"Module {module_id} not found")
    return module


def get_module_numeric_id(module_code: str) -> str:
    """Map module code to numeric ID for file paths"""
    MODULE_CODE_TO_NUMERIC = {
        "MA-101": "1",
        "MA-201": "2",
        "MA-301": "3",
    }
    return MODULE_CODE_TO_NUMERIC.get(module_code, module_code)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal attacks"""
    # Remove any path components
    filename = Path(filename).name
    # Remove any non-alphanumeric characters except dots, dashes, underscores
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    return filename


# ==================== Module Markdown Management ====================

@router.post("/modules/{module_id}/markdown")
async def upload_module_markdown(
    module_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Upload or update module markdown file

    - Validates module exists
    - Checks file extension and size
    - Saves to app/static/modules/module{numeric_id}/Module_{numeric_id}_Lessons_Branded.md
    """
    # Validate module
    module = validate_module_id(module_id, db)

    # Validate file extension
    if not file.filename or Path(file.filename).suffix.lower() not in MARKDOWN_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(MARKDOWN_EXTENSIONS)}"
        )

    # Check file size
    contents = await file.read()
    if len(contents) > MAX_MARKDOWN_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_MARKDOWN_SIZE / (1024*1024):.1f} MB"
        )

    # Get numeric ID for file path
    numeric_id = get_module_numeric_id(module.code)

    # Create module directory if it doesn't exist
    module_dir = MODULES_BASE / f"module{numeric_id}"
    module_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    file_path = module_dir / f"Module_{numeric_id}_Lessons_Branded.md"

    # Backup existing file if it exists
    if file_path.exists():
        backup_path = file_path.with_suffix('.md.backup')
        shutil.copy2(file_path, backup_path)

    # Write new content
    with open(file_path, 'wb') as f:
        f.write(contents)

    message = "Module markdown uploaded successfully"
    return {
        "message": message,
        "module_id": str(module.id),
        "module_code": module.code,
        "file_path": str(file_path.relative_to(MODULES_BASE.parent))
    }


@router.get("/modules/{module_id}/markdown")
async def get_module_markdown(
    module_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get the raw markdown content for a module"""
    module = validate_module_id(module_id, db)
    numeric_id = get_module_numeric_id(module.code)

    file_path = MODULES_BASE / f"module{numeric_id}" / f"Module_{numeric_id}_Lessons_Branded.md"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Module markdown file not found")

    return FileResponse(
        file_path,
        media_type="text/markdown",
        filename=f"Module_{numeric_id}_Lessons_Branded.md"
    )


# ==================== H5P Activity Management ====================

@router.post("/modules/{module_id}/h5p")
async def upload_h5p_activity(
    module_id: str,
    file: UploadFile = File(...),
    activity_id: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Upload H5P activity package

    - Validates module exists
    - Checks file is .h5p and size limit
    - Saves to app/static/modules/module{numeric_id}/{activity_id}.h5p
    - Clears cached extraction
    """
    # Validate module
    module = validate_module_id(module_id, db)

    # Validate file extension
    if not file.filename or Path(file.filename).suffix.lower() not in H5P_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Must be .h5p"
        )

    # Sanitize activity_id
    activity_id = sanitize_filename(activity_id)
    if not activity_id.endswith('.h5p'):
        activity_id = f"{activity_id}.h5p"

    # Check file size
    contents = await file.read()
    if len(contents) > MAX_H5P_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_H5P_SIZE / (1024*1024):.1f} MB"
        )

    # Get numeric ID for file path
    numeric_id = get_module_numeric_id(module.code)

    # Create module directory if it doesn't exist
    module_dir = MODULES_BASE / f"module{numeric_id}"
    module_dir.mkdir(parents=True, exist_ok=True)

    # Save H5P file
    h5p_path = module_dir / activity_id

    with open(h5p_path, 'wb') as f:
        f.write(contents)

    # Clear cache for this activity (if exists)
    cache_dir = H5P_CACHE / activity_id.replace('.h5p', '')
    if cache_dir.exists():
        shutil.rmtree(cache_dir)

    return {
        "message": "H5P activity uploaded successfully",
        "module_id": str(module.id),
        "module_code": module.code,
        "activity_id": activity_id,
        "file_path": str(h5p_path.relative_to(MODULES_BASE.parent))
    }


@router.get("/modules/{module_id}/h5p")
async def list_h5p_activities(
    module_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """List all H5P activities for a module"""
    module = validate_module_id(module_id, db)
    numeric_id = get_module_numeric_id(module.code)

    module_dir = MODULES_BASE / f"module{numeric_id}"

    if not module_dir.exists():
        return {"activities": []}

    activities = []
    for file_path in module_dir.glob("*.h5p"):
        activities.append({
            "activity_id": file_path.name,
            "file_size": file_path.stat().st_size,
            "modified": file_path.stat().st_mtime
        })

    return {"activities": activities}


@router.delete("/modules/{module_id}/h5p/{activity_id}")
async def delete_h5p_activity(
    module_id: str,
    activity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete an H5P activity"""
    module = validate_module_id(module_id, db)
    numeric_id = get_module_numeric_id(module.code)

    # Sanitize activity_id
    activity_id = sanitize_filename(activity_id)
    if not activity_id.endswith('.h5p'):
        activity_id = f"{activity_id}.h5p"

    h5p_path = MODULES_BASE / f"module{numeric_id}" / activity_id

    if not h5p_path.exists():
        raise HTTPException(status_code=404, detail="H5P activity not found")

    # Delete file
    h5p_path.unlink()

    # Clear cache
    cache_dir = H5P_CACHE / activity_id.replace('.h5p', '')
    if cache_dir.exists():
        shutil.rmtree(cache_dir)

    return {"message": "H5P activity deleted successfully"}


# ==================== Supplemental Files Management ====================

@router.post("/modules/{module_id}/files")
async def upload_supplemental_file(
    module_id: str,
    file: UploadFile = File(...),
    subfolder: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Upload supplemental file (PDF, image, video, etc.)

    - Saves to app/static/modules/module{numeric_id}/{subfolder}/{filename}
    - subfolder is optional (e.g., "images", "pdfs", "videos")
    """
    # Validate module
    module = validate_module_id(module_id, db)

    # Validate filename
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    # Sanitize filename
    safe_filename = sanitize_filename(file.filename)

    # Validate file extension
    if Path(safe_filename).suffix.lower() not in SUPPLEMENTAL_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(SUPPLEMENTAL_EXTENSIONS)}"
        )

    # Check file size
    contents = await file.read()
    if len(contents) > MAX_SUPPLEMENTAL_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_SUPPLEMENTAL_SIZE / (1024*1024):.1f} MB"
        )

    # Get numeric ID for file path
    numeric_id = get_module_numeric_id(module.code)

    # Create target directory
    module_dir = MODULES_BASE / f"module{numeric_id}"
    if subfolder:
        # Sanitize subfolder name
        safe_subfolder = re.sub(r'[^a-zA-Z0-9_-]', '_', subfolder)
        target_dir = module_dir / safe_subfolder
    else:
        target_dir = module_dir / "files"

    target_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    file_path = target_dir / safe_filename

    with open(file_path, 'wb') as f:
        f.write(contents)

    return {
        "message": "File uploaded successfully",
        "module_id": str(module.id),
        "filename": safe_filename,
        "file_path": str(file_path.relative_to(MODULES_BASE.parent))
    }


@router.get("/modules/{module_id}/files")
async def list_supplemental_files(
    module_id: str,
    subfolder: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """List all supplemental files for a module"""
    module = validate_module_id(module_id, db)
    numeric_id = get_module_numeric_id(module.code)

    module_dir = MODULES_BASE / f"module{numeric_id}"

    if subfolder:
        safe_subfolder = re.sub(r'[^a-zA-Z0-9_-]', '_', subfolder)
        search_dir = module_dir / safe_subfolder
    else:
        search_dir = module_dir

    if not search_dir.exists():
        return {"files": []}

    files = []
    for file_path in search_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in SUPPLEMENTAL_EXTENSIONS:
            files.append({
                "filename": file_path.name,
                "path": str(file_path.relative_to(module_dir)),
                "file_size": file_path.stat().st_size,
                "modified": file_path.stat().st_mtime,
                "type": file_path.suffix[1:]  # Remove leading dot
            })

    return {"files": files}


@router.delete("/modules/{module_id}/files/{file_path:path}")
async def delete_supplemental_file(
    module_id: str,
    file_path: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a supplemental file"""
    module = validate_module_id(module_id, db)
    numeric_id = get_module_numeric_id(module.code)

    # Construct full path
    full_path = MODULES_BASE / f"module{numeric_id}" / file_path

    # Security check - ensure file is within module directory
    try:
        full_path = full_path.resolve()
        module_dir = (MODULES_BASE / f"module{numeric_id}").resolve()
        if not str(full_path).startswith(str(module_dir)):
            raise HTTPException(status_code=403, detail="Access denied")
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid path")

    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # Delete file
    full_path.unlink()

    return {"message": "File deleted successfully"}


# ==================== Module List ====================

@router.get("/modules")
async def list_all_modules(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """List all modules with their content status"""
    modules = db.query(Module).order_by(Module.position).all()

    result = []
    for module in modules:
        numeric_id = get_module_numeric_id(module.code)
        module_dir = MODULES_BASE / f"module{numeric_id}"
        markdown_path = module_dir / f"Module_{numeric_id}_Lessons_Branded.md"

        # Count H5P activities
        h5p_count = len(list(module_dir.glob("*.h5p"))) if module_dir.exists() else 0

        result.append({
            "id": str(module.id),
            "code": module.code,
            "title": module.title,
            "has_markdown": markdown_path.exists(),
            "h5p_count": h5p_count,
            "directory": str(module_dir.relative_to(MODULES_BASE.parent)) if module_dir.exists() else None
        })

    return {"modules": result}
