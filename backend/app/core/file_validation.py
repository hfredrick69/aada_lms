"""
File Upload Validation

Security-hardened validation for all file uploads:
- Extension validation
- Magic bytes verification
- File structure validation (PDF, images)
- Size limits
- Content scanning (future: virus scanning)

Usage:
    from app.core.file_validation import validate_pdf, validate_image

    content = await file.read()
    validate_pdf(content, filename="doc.pdf", max_size_mb=10)
    validate_image(content, filename="photo.jpg", max_size_mb=5)
"""

from io import BytesIO
from pathlib import Path
from typing import Optional
import logging
from fastapi import HTTPException
import PyPDF2
from PIL import Image

# Optional ClamAV virus scanning
try:
    import clamd
    CLAMAV_AVAILABLE = True
except ImportError:
    CLAMAV_AVAILABLE = False

logger = logging.getLogger(__name__)


# File type magic bytes (first few bytes that identify file type)
MAGIC_BYTES = {
    'pdf': b'%PDF-',
    'png': b'\x89PNG\r\n\x1a\n',
    'jpg': b'\xff\xd8\xff',
    'jpeg': b'\xff\xd8\xff',
}

# Allowed MIME types
ALLOWED_MIME_TYPES = {
    'pdf': ['application/pdf'],
    'png': ['image/png'],
    'jpg': ['image/jpeg'],
    'jpeg': ['image/jpeg'],
}


def validate_file_extension(filename: str, allowed_extensions: set[str]) -> str:
    """
    Validate file extension

    Args:
        filename: Original filename
        allowed_extensions: Set of allowed extensions (e.g., {'.pdf', '.jpg'})

    Returns:
        Lowercase extension including dot (e.g., '.pdf')

    Raises:
        HTTPException: If extension not allowed
    """
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    ext = Path(filename).suffix.lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )

    return ext


def validate_file_size(content: bytes, max_size_mb: int, file_type: str = "file"):
    """
    Validate file size

    Args:
        content: File content bytes
        max_size_mb: Maximum allowed size in megabytes
        file_type: Description of file type for error message

    Raises:
        HTTPException: If file exceeds size limit
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    if len(content) > max_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"{file_type.capitalize()} too large. Maximum size is {max_size_mb}MB"
        )


def validate_magic_bytes(content: bytes, filename: str):
    """
    Validate file magic bytes match extension

    Args:
        content: File content bytes
        filename: Original filename

    Raises:
        HTTPException: If magic bytes don't match extension
    """
    ext = Path(filename).suffix.lower().lstrip('.')

    if ext not in MAGIC_BYTES:
        return  # No magic byte check for this extension

    expected_magic = MAGIC_BYTES[ext]
    if not content.startswith(expected_magic):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {ext.upper()} file. File content doesn't match extension."
        )


def scan_for_viruses(content: bytes, filename: str):
    """
    Optional virus scanning using ClamAV (if available)

    Args:
        content: File content bytes
        filename: Original filename

    Raises:
        HTTPException: If virus detected
    """
    if not CLAMAV_AVAILABLE:
        logger.warning("ClamAV not available - skipping virus scan. Install 'clamd' for virus scanning.")
        return

    try:
        cd = clamd.ClamdUnixSocket()
        result = cd.scan_stream(content)

        # Check result
        for key, (status, virus_name) in result.items():
            if status == 'FOUND':
                logger.error(f"Virus detected in {filename}: {virus_name}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Malicious file detected: {virus_name}"
                )
    except clamd.ConnectionError:
        logger.warning("ClamAV daemon not running - skipping virus scan. Start clamd for virus protection.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Virus scan error for {filename}: {str(e)}")
        # Don't fail upload if scanner errors - log and continue


def validate_pdf(
    content: bytes,
    filename: str,
    max_size_mb: int = 10,
    check_structure: bool = True
) -> bool:
    """
    Comprehensive PDF validation

    Args:
        content: PDF file content bytes
        filename: Original filename
        max_size_mb: Maximum allowed size in MB
        check_structure: Whether to validate PDF structure with PyPDF2

    Returns:
        True if valid

    Raises:
        HTTPException: If validation fails
    """
    # 1. Extension check
    validate_file_extension(filename, {'.pdf'})

    # 2. Size check
    validate_file_size(content, max_size_mb, "PDF")

    # 3. Magic bytes check
    validate_magic_bytes(content, filename)

    # 3.5. Optional virus scan (if ClamAV available)
    scan_for_viruses(content, filename)

    # 4. PDF structure validation using PyPDF2
    if check_structure:
        try:
            pdf_file = BytesIO(content)
            reader = PyPDF2.PdfReader(pdf_file)

            # Verify we can read metadata
            _ = reader.metadata

            # Verify we can count pages
            num_pages = len(reader.pages)

            if num_pages == 0:
                raise HTTPException(status_code=400, detail="PDF has no pages")

            # Try to read first page (catches many malformed PDFs)
            try:
                _ = reader.pages[0]
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"PDF structure invalid: {str(e)}"
                )

        except PyPDF2.errors.PdfReadError as e:
            raise HTTPException(status_code=400, detail=f"Invalid PDF structure: {str(e)}")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PDF validation failed: {str(e)}")

    return True


def validate_image(
    content: bytes,
    filename: str,
    max_size_mb: int = 5,
    allowed_formats: Optional[set[str]] = None,
    max_dimensions: Optional[tuple[int, int]] = None
) -> dict:
    """
    Comprehensive image validation

    Args:
        content: Image file content bytes
        filename: Original filename
        max_size_mb: Maximum allowed size in MB
        allowed_formats: Set of allowed formats (e.g., {'PNG', 'JPEG'}). None = all.
        max_dimensions: Optional (width, height) maximum dimensions

    Returns:
        Dict with image info: {'format': 'JPEG', 'width': 1920, 'height': 1080, 'mode': 'RGB'}

    Raises:
        HTTPException: If validation fails
    """
    # 1. Extension check
    validate_file_extension(filename, {'.png', '.jpg', '.jpeg'})

    # 2. Size check
    validate_file_size(content, max_size_mb, "Image")

    # 3. Magic bytes check
    validate_magic_bytes(content, filename)

    # 3.5. Optional virus scan (if ClamAV available)
    scan_for_viruses(content, filename)

    # 4. Image structure validation using Pillow
    try:
        image_file = BytesIO(content)
        img = Image.open(image_file)

        # Verify image can be loaded
        img.verify()

        # Re-open for metadata (verify() closes the file)
        image_file.seek(0)
        img = Image.open(image_file)

        # Get image info
        info = {
            'format': img.format,
            'width': img.width,
            'height': img.height,
            'mode': img.mode
        }

        # Check format if specified
        if allowed_formats and img.format not in allowed_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Image format {img.format} not allowed. Allowed: {', '.join(allowed_formats)}"
            )

        # Check dimensions if specified
        if max_dimensions:
            max_w, max_h = max_dimensions
            if img.width > max_w or img.height > max_h:
                raise HTTPException(
                    status_code=400,
                    detail=f"Image too large. Maximum dimensions: {max_w}x{max_h}"
                )

        return info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")


def validate_file(
    content: bytes,
    filename: str,
    allowed_types: set[str],
    max_size_mb: int = 10
) -> str:
    """
    Generic file validation dispatcher

    Args:
        content: File content bytes
        filename: Original filename
        allowed_types: Set of allowed extensions (e.g., {'.pdf', '.jpg', '.png'})
        max_size_mb: Maximum allowed size in MB

    Returns:
        Detected file type (e.g., 'pdf', 'image')

    Raises:
        HTTPException: If validation fails
    """
    ext = validate_file_extension(filename, allowed_types)
    validate_file_size(content, max_size_mb)

    # Route to specific validator based on extension
    ext_clean = ext.lstrip('.')

    if ext_clean == 'pdf':
        validate_pdf(content, filename, max_size_mb)
        return 'pdf'

    elif ext_clean in {'png', 'jpg', 'jpeg'}:
        validate_image(content, filename, max_size_mb)
        return 'image'

    else:
        # Basic validation only (magic bytes)
        validate_magic_bytes(content, filename)
        return 'other'


# TODO: Production security enhancements
# 1. Add virus scanning using ClamAV:
#    - pip install clamd
#    - Run ClamAV daemon
#    - Scan files before storage
#
# 2. Add content sanitization:
#    - Strip PDF JavaScript/actions
#    - Re-render images to remove EXIF exploits
#    - Validate ZIP archives if allowed
#
# 3. Add rate limiting:
#    - Limit uploads per user per hour
#    - Track total storage per user
#
# 4. Add quarantine workflow:
#    - Store uploads in temp directory
#    - Scan asynchronously
#    - Move to permanent storage after approval
