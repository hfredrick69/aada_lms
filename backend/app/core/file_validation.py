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
        logger.warning(
            "ClamAV not available - skipping virus scan. "
            "Install 'clamd' for virus scanning."
        )
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
        logger.warning(
            "ClamAV daemon not running - skipping virus scan. "
            "Start clamd for virus protection."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Virus scan error for {filename}: {str(e)}")
        # Don't fail upload if scanner errors - log and continue


def sanitize_pdf(content: bytes) -> bytes:
    """
    Sanitize PDF by removing JavaScript, forms, and dangerous content

    Strips:
    - JavaScript actions
    - Form fields and submit actions
    - Launch actions
    - Embedded files
    - URI actions

    Args:
        content: PDF file content bytes

    Returns:
        Sanitized PDF content bytes

    Raises:
        HTTPException: If sanitization fails
    """
    try:
        pdf_input = BytesIO(content)
        pdf_output = BytesIO()

        reader = PyPDF2.PdfReader(pdf_input)
        writer = PyPDF2.PdfWriter()

        # Process each page
        for page in reader.pages:
            # Remove page-level actions
            if '/AA' in page:
                del page['/AA']  # Additional Actions
            if '/A' in page:
                del page['/A']  # Action
            if '/OpenAction' in page:
                del page['/OpenAction']

            # Remove annotations with actions
            if '/Annots' in page:
                annots = page['/Annots']
                if annots:
                    safe_annots = []
                    for annot in annots:
                        annot_obj = annot.get_object()
                        # Remove action-related entries
                        if '/A' in annot_obj:
                            del annot_obj['/A']
                        if '/AA' in annot_obj:
                            del annot_obj['/AA']
                        safe_annots.append(annot_obj)

            writer.add_page(page)

        # Remove document-level JavaScript
        if reader.trailer.get('/Root'):
            root = reader.trailer['/Root']
            if '/AA' in root:
                del root['/AA']
            if '/OpenAction' in root:
                del root['/OpenAction']
            if '/AcroForm' in root:
                del root['/AcroForm']  # Remove forms
            if '/Names' in root:
                names = root['/Names']
                if '/JavaScript' in names:
                    del names['/JavaScript']
                if '/EmbeddedFiles' in names:
                    del names['/EmbeddedFiles']

        writer.write(pdf_output)
        return pdf_output.getvalue()

    except Exception as e:
        logger.error(f"PDF sanitization failed: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"PDF sanitization failed: {str(e)}"
        )


def sanitize_image(content: bytes, format: str = 'PNG') -> bytes:
    """
    Sanitize image by re-rendering to strip EXIF and metadata

    Strips:
    - EXIF metadata
    - GPS coordinates
    - Camera information
    - Embedded thumbnails
    - Color profiles (converts to sRGB)

    Args:
        content: Image file content bytes
        format: Output format ('PNG' or 'JPEG')

    Returns:
        Sanitized image content bytes

    Raises:
        HTTPException: If sanitization fails
    """
    try:
        img = Image.open(BytesIO(content))

        # Convert to RGB (removes alpha channel exploits, normalizes color)
        if img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')

        # Re-render to new image (strips all metadata)
        output = BytesIO()

        # Save with optimization, no metadata
        if format.upper() == 'JPEG':
            img.save(output, format='JPEG', quality=95, optimize=True)
        else:
            img.save(output, format='PNG', optimize=True)

        return output.getvalue()

    except Exception as e:
        logger.error(f"Image sanitization failed: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Image sanitization failed: {str(e)}"
        )


def validate_pdf(
    content: bytes,
    filename: str,
    max_size_mb: int = 10,
    check_structure: bool = True,
    sanitize: bool = True
) -> bytes:
    """
    Comprehensive PDF validation and sanitization

    Args:
        content: PDF file content bytes
        filename: Original filename
        max_size_mb: Maximum allowed size in MB
        check_structure: Whether to validate PDF structure with PyPDF2
        sanitize: Whether to strip JavaScript and dangerous content

    Returns:
        Sanitized PDF content bytes (or original if sanitize=False)

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

    # 5. Optional sanitization (strip JavaScript, forms, etc.)
    if sanitize:
        logger.info(f"Sanitizing PDF: {filename}")
        content = sanitize_pdf(content)

    return content


def validate_image(
    content: bytes,
    filename: str,
    max_size_mb: int = 5,
    allowed_formats: Optional[set[str]] = None,
    max_dimensions: Optional[tuple[int, int]] = None,
    sanitize: bool = True
) -> tuple[bytes, dict]:
    """
    Comprehensive image validation and sanitization

    Args:
        content: Image file content bytes
        filename: Original filename
        max_size_mb: Maximum allowed size in MB
        allowed_formats: Set of allowed formats (e.g., {'PNG', 'JPEG'}). None = all.
        max_dimensions: Optional (width, height) maximum dimensions
        sanitize: Whether to strip EXIF metadata

    Returns:
        Tuple of (sanitized_content, info_dict)
        - sanitized_content: Image bytes with EXIF stripped (or original if sanitize=False)
        - info_dict: {'format': 'JPEG', 'width': 1920, 'height': 1080, 'mode': 'RGB'}

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
            formats_str = ', '.join(allowed_formats)
            raise HTTPException(
                status_code=400,
                detail=f"Image format {img.format} not allowed. Allowed: {formats_str}"
            )

        # Check dimensions if specified
        if max_dimensions:
            max_w, max_h = max_dimensions
            if img.width > max_w or img.height > max_h:
                raise HTTPException(
                    status_code=400,
                    detail=f"Image too large. Maximum dimensions: {max_w}x{max_h}"
                )

        # 5. Optional sanitization (strip EXIF metadata)
        if sanitize:
            logger.info(f"Sanitizing image: {filename}")
            # Determine output format based on original
            output_format = 'JPEG' if img.format in ('JPEG', 'JPG') else 'PNG'
            content = sanitize_image(content, format=output_format)

        return content, info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")


def validate_file(
    content: bytes,
    filename: str,
    allowed_types: set[str],
    max_size_mb: int = 10,
    sanitize: bool = True
) -> tuple[bytes, str]:
    """
    Generic file validation dispatcher with sanitization

    Args:
        content: File content bytes
        filename: Original filename
        allowed_types: Set of allowed extensions (e.g., {'.pdf', '.jpg', '.png'})
        max_size_mb: Maximum allowed size in MB
        sanitize: Whether to sanitize files (strip dangerous content)

    Returns:
        Tuple of (sanitized_content, file_type)
        - sanitized_content: Sanitized file bytes (or original if sanitize=False)
        - file_type: Detected file type (e.g., 'pdf', 'image')

    Raises:
        HTTPException: If validation fails
    """
    ext = validate_file_extension(filename, allowed_types)
    validate_file_size(content, max_size_mb)

    # Route to specific validator based on extension
    ext_clean = ext.lstrip('.')

    if ext_clean == 'pdf':
        sanitized_content = validate_pdf(content, filename, max_size_mb, sanitize=sanitize)
        return sanitized_content, 'pdf'

    elif ext_clean in {'png', 'jpg', 'jpeg'}:
        sanitized_content, _ = validate_image(content, filename, max_size_mb, sanitize=sanitize)
        return sanitized_content, 'image'

    else:
        # Basic validation only (magic bytes)
        validate_magic_bytes(content, filename)
        return content, 'other'


# Security enhancements completed:
# ✅ 1. Virus scanning using ClamAV (optional, graceful degradation)
# ✅ 2. Content sanitization:
#    ✅ - Strip PDF JavaScript/actions/forms
#    ✅ - Re-render images to remove EXIF exploits
#
# TODO: Additional production hardening
# 3. Rate limiting:
#    - Limit uploads per user per hour
#    - Track total storage per user
#
# 4. Quarantine workflow:
#    - Store uploads in temp directory
#    - Scan asynchronously
#    - Move to permanent storage after approval
#
# 5. Advanced threat detection:
#    - VirusTotal API integration (multi-engine scanning)
#    - Behavioral analysis / sandboxing
