"""
PDF Service for E-Signature System

Handles PDF manipulation for digital signatures:
- Overlay signature images onto PDFs
- Generate signed PDFs with audit information
- Create certificate of completion
"""

from pathlib import Path
from datetime import datetime, timezone
import base64
import io
from typing import List, Tuple

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader, PdfWriter


class PDFSignatureService:
    """Service for adding signatures to PDF documents"""

    @staticmethod
    def overlay_signatures(
        template_pdf_path: Path,
        output_pdf_path: Path,
        signatures: List[Tuple[str, str, int, int]],  # [(base64_image, type, x, y), ...]
        metadata: dict = None,
        acknowledgements: List[Tuple[str, int, int]] | None = None,
    ) -> bool:
        """
        Overlay signature images onto a PDF template

        Args:
            template_pdf_path: Path to source PDF
            output_pdf_path: Path to save signed PDF
            signatures: List of (base64_image, type, x_position, y_position)
            metadata: Additional metadata to add to PDF

        Returns:
            True if successful, False otherwise
        """
        try:
            # Read the template PDF
            reader = PdfReader(str(template_pdf_path))
            writer = PdfWriter()

            # Get the last page (where signatures usually go)
            last_page_num = len(reader.pages) - 1  # noqa: F841

            # Create overlay with signatures
            overlay_buffer = io.BytesIO()
            c = canvas.Canvas(overlay_buffer, pagesize=letter)

            # Add each signature to the overlay
            for sig_data, sig_type, x, y in signatures:
                # Decode base64 signature image
                img_data = base64.b64decode(sig_data.split(',')[1] if ',' in sig_data else sig_data)
                img_buffer = io.BytesIO(img_data)

                # Add signature image to PDF
                img = ImageReader(img_buffer)
                c.drawImage(img, x, y, width=200, height=50, preserveAspectRatio=True, mask='auto')

                # Add signature type label
                c.setFont("Helvetica", 8)
                c.drawString(x, y - 10, f"{sig_type.replace('_', ' ').title()} Signature")

            # Add acknowledgement initials
            if acknowledgements:
                c.setFont("Helvetica-Bold", 10)
                for initials, x, y in acknowledgements:
                    c.drawString(x, y, initials)

            # Add timestamp and metadata
            if metadata:
                c.setFont("Helvetica", 6)
                y_pos = 30
                signed_date = metadata.get(
                    'signed_date', datetime.now(timezone.utc).isoformat()
                )
                c.drawString(50, y_pos, f"Digitally signed on: {signed_date}")
                doc_id = metadata.get('document_id', 'N/A')
                c.drawString(50, y_pos - 10, f"Document ID: {doc_id}")

            c.save()

            # Merge overlay with original PDF
            overlay_buffer.seek(0)
            overlay_pdf = PdfReader(overlay_buffer)

            # Copy all pages from original
            for i, page in enumerate(reader.pages):
                if i == last_page_num:
                    # Merge signature overlay on last page
                    page.merge_page(overlay_pdf.pages[0])
                writer.add_page(page)

            # Add metadata to PDF
            if metadata:
                writer.add_metadata({
                    '/Title': metadata.get('title', 'Signed Document'),
                    '/Author': metadata.get('author', 'AADA LMS'),
                    '/Subject': metadata.get('subject', 'Enrollment Agreement'),
                    '/Creator': 'AADA E-Signature System',
                    '/Producer': 'AADA LMS PDF Service',
                    '/CreationDate': datetime.now(timezone.utc).strftime('D:%Y%m%d%H%M%S')
                })

            # Write output PDF
            output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_pdf_path, 'wb') as output_file:
                writer.write(output_file)

            return True

        except Exception as e:
            print(f"Error overlaying signatures: {e}")
            return False

    @staticmethod
    def generate_signature_certificate(
        document_id: str,
        student_name: str,
        student_signature_date: datetime,
        official_name: str = None,
        official_signature_date: datetime = None,
        output_path: Path = None
    ) -> bytes:
        """
        Generate a certificate of completion PDF for audit purposes

        Returns PDF as bytes if output_path not provided
        """
        buffer = io.BytesIO() if not output_path else None
        c = canvas.Canvas(str(output_path) if output_path else buffer, pagesize=letter)

        # Title
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(300, 750, "Certificate of Digital Signature")

        # Document info
        c.setFont("Helvetica", 12)
        y = 680
        c.drawString(100, y, f"Document ID: {document_id}")
        y -= 30
        c.drawString(100, y, f"Student: {student_name}")
        y -= 20
        c.drawString(100, y, f"Student Signature Date: {student_signature_date.strftime('%Y-%m-%d %H:%M:%S UTC')}")

        if official_name and official_signature_date:
            y -= 30
            c.drawString(100, y, f"School Official: {official_name}")
            y -= 20
            sig_date = official_signature_date.strftime('%Y-%m-%d %H:%M:%S UTC')
            c.drawString(100, y, f"Official Signature Date: {sig_date}")

        # Legal statement
        y -= 50
        c.setFont("Helvetica", 10)
        legal_text = [
            "This certificate verifies that the above-named parties have digitally signed",
            "the enrollment agreement using the AADA Learning Management System.",
            "All signatures are legally binding under the Electronic Signatures in Global",
            "and National Commerce Act (ESIGN Act) and are maintained with a complete",
            "audit trail including timestamps, IP addresses, and user authentication."
        ]
        for line in legal_text:
            c.drawString(100, y, line)
            y -= 15

        # Footer
        c.setFont("Helvetica", 8)
        c.drawCentredString(300, 50, f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        c.drawCentredString(300, 35, "AADA E-Signature System - Legally Binding Digital Signatures")

        c.save()

        if buffer:
            return buffer.getvalue()
        return None
