# File Upload Security

## Overview

All file uploads in the AADA LMS system undergo multi-layered security validation to prevent malicious files, exploits, and attacks.

## Validation Layers

### 1. **Extension Validation**
- Whitelist-only approach
- Validates file extension matches allowed types
- Rejects any non-whitelisted extensions

**Templates**: PDF only (`.pdf`)
**Student Uploads**: PDF, PNG, JPG/JPEG (`.pdf`, `.png`, `.jpg`, `.jpeg`)
**Content Uploads**: Varies by content type

### 2. **Size Limits**
- Prevents denial-of-service via large files
- Prevents storage exhaustion

**Limits**:
- Document templates: 10MB
- Student documents: 10MB
- H5P packages: 100MB
- Supplemental files: 50MB

### 3. **Magic Bytes Validation**
- Verifies actual file type matches extension
- Prevents extension spoofing (e.g., `malware.exe` renamed to `doc.pdf`)

**Verified Magic Bytes**:
- PDF: `%PDF-`
- PNG: `\x89PNG\r\n\x1a\n`
- JPG/JPEG: `\xff\xd8\xff`

### 4. **Structure Validation**

#### PDF Files (PyPDF2)
- Parses PDF structure
- Verifies PDF is valid and readable
- Checks page count > 0
- Attempts to read first page
- Catches corrupted/malformed PDFs

#### Images (Pillow/PIL)
- Loads image to verify validity
- Checks image can be parsed
- Validates dimensions (optional)
- Catches corrupted/malicious images

## File Upload Flows

### Admin Document Template Upload
```
POST /api/documents/templates
├─ Extension check (.pdf only)
├─ Size check (10MB max)
├─ Magic bytes check (%PDF-)
├─ PDF structure validation (PyPDF2)
└─ Save to templates directory
```

### Student Document Upload
```
POST /api/documents/upload
├─ Extension check (.pdf, .png, .jpg, .jpeg)
├─ Size check (10MB max)
├─ Magic bytes check (based on extension)
├─ PDF/Image structure validation
└─ Save to user-specific directory
```

### Content Upload (Images, PDFs, Media)
```
POST /api/content/modules/{id}/supplemental
├─ Extension check (varies by type)
├─ Size check (50MB max)
├─ Magic bytes check
├─ Structure validation (if PDF/image)
└─ Save to module directory
```

## Implementation

### Validation Module
All validation logic centralized in:
```
backend/app/core/file_validation.py
```

**Functions**:
- `validate_pdf(content, filename, max_size_mb)` - Complete PDF validation
- `validate_image(content, filename, max_size_mb)` - Complete image validation
- `validate_file(content, filename, allowed_types, max_size_mb)` - Generic dispatcher

### Usage Example
```python
from app.core.file_validation import validate_pdf, validate_image

# PDF validation
content = await file.read()
validate_pdf(content, file.filename, max_size_mb=10)

# Image validation
content = await file.read()
validate_image(content, file.filename, max_size_mb=5)

# Generic validation
content = await file.read()
file_type = validate_file(
    content,
    file.filename,
    allowed_types={'.pdf', '.png', '.jpg'},
    max_size_mb=10
)
```

## Current Security Status

### ✅ Implemented
- ✅ Extension whitelisting
- ✅ File size limits
- ✅ Magic bytes verification
- ✅ PDF structure validation (PyPDF2)
- ✅ Image structure validation (Pillow)
- ✅ Centralized validation module
- ✅ Admin-only access for templates
- ✅ User-specific upload directories
- ✅ Duplicate template prevention

### ⚠️ Recommended (Before Production)
- ⚠️ **Virus scanning** (ClamAV integration)
- ⚠️ **Content sanitization** (strip JavaScript from PDFs, EXIF from images)
- ⚠️ **Rate limiting** (per user upload quotas)
- ⚠️ **Quarantine workflow** (scan before approval)
- ⚠️ **Storage quotas** (per user limits)

### 📋 Future Enhancements
- Content-type validation (verify MIME types)
- Async virus scanning
- File encryption at rest
- Automated malware scanning pipeline
- Integration with cloud scanning services (VirusTotal)

## Production Requirements

### Before Going Live

#### 1. Install and Configure ClamAV
```bash
# Install ClamAV daemon
apt-get install clamav clamav-daemon

# Install Python library
pip install clamd

# Start daemon
systemctl start clamav-daemon

# Update virus definitions
freshclam
```

#### 2. Add Virus Scanning to Validation
```python
import clamd

def scan_file_for_viruses(content: bytes):
    """Scan file content for viruses using ClamAV"""
    cd = clamd.ClamdUnixSocket()
    scan_result = cd.scan_stream(content)

    if scan_result['stream'][0] == 'FOUND':
        raise HTTPException(
            status_code=400,
            detail="Malicious file detected"
        )
```

#### 3. Implement Quarantine Workflow
1. Upload to temporary quarantine directory
2. Scan with ClamAV
3. Admin reviews and approves
4. Move to permanent storage
5. Log all actions in audit trail

#### 4. Add Rate Limiting
```python
from slowapi import Limiter

# Limit uploads per user
@router.post("/upload")
@limiter.limit("10/hour")  # 10 uploads per hour
async def upload_document(...):
    ...
```

## Attack Vectors Mitigated

### ✅ Prevented
1. **Extension spoofing** - Magic bytes validation
2. **Malformed PDFs** - PyPDF2 structure validation
3. **Image exploits** - Pillow validation
4. **Large file DoS** - Size limits
5. **Storage exhaustion** - Size limits + quotas
6. **Duplicate uploads** - Filename deduplication

### ⚠️ Partial Mitigation (Requires Production Hardening)
1. **PDF JavaScript exploits** - Need sanitization
2. **EXIF exploits** - Need image re-rendering
3. **Virus/malware** - Need ClamAV scanning
4. **Advanced PDF exploits** - Need additional hardening
5. **Social engineering** - Need user education

## Compliance

### FERPA (Student Records)
- ✅ User-specific upload directories
- ✅ Access control (students see own only)
- ✅ Audit logging

### ESIGN Act (Document Signing)
- ✅ Secure template storage
- ✅ File integrity validation
- ✅ Audit trail
- ✅ Tamper detection (structure validation)

## Monitoring & Alerts

### Recommended Logging
- All file upload attempts
- Validation failures
- Virus detection events
- Unusual upload patterns
- Storage quota warnings

### Alert Triggers
- Multiple validation failures from same IP
- Virus detected
- Storage quota exceeded
- Unusual file types attempted

## Testing

### Security Testing Checklist
- [ ] Upload file with wrong extension (should fail)
- [ ] Upload file > size limit (should fail)
- [ ] Upload file with spoofed extension (should fail magic bytes check)
- [ ] Upload corrupted PDF (should fail structure check)
- [ ] Upload corrupted image (should fail structure check)
- [ ] Upload malware/virus (should fail ClamAV scan - production only)
- [ ] Upload extremely large file (should fail size check)
- [ ] Rapid upload attempts (should trigger rate limit)

### Test Files
Located in `backend/tests/fixtures/`:
- `valid.pdf` - Valid PDF
- `invalid_extension.pdf.exe` - Spoofed extension
- `corrupted.pdf` - Malformed PDF
- `oversized.pdf` - File > size limit

## References

- [OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
- [PyPDF2 Documentation](https://pypdf2.readthedocs.io/)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [ClamAV Documentation](https://docs.clamav.net/)

---

**Last Updated**: 2025-11-08
**Owner**: Security Team
**Review Cycle**: Quarterly
