"""
Schema-driven PDF generation for enrollment agreements.
"""

from __future__ import annotations

import base64
import io
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Sequence, TYPE_CHECKING, Optional, Tuple

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)

if TYPE_CHECKING:  # pragma: no cover
    from app.db.models.document import DocumentSignature, SignedDocument


class SchemaDrivenPDFService:
    """Generate enrollment agreement PDFs from the shared schema/response payloads."""

    BRAND_GOLD = colors.HexColor("#D5AA42")
    BRAND_NAVY = colors.HexColor("#0F172A")
    BRAND_CREAM = colors.HexColor("#FFFDF9")
    BRAND_SLATE = colors.HexColor("#475569")

    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.styles = self._build_styles()

    def _build_styles(self) -> Dict[str, ParagraphStyle]:
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name="SectionTitle", fontSize=13, leading=16, spaceAfter=6,
            spaceBefore=6, fontName="Helvetica-Bold",
            textColor=self.BRAND_NAVY))
        styles.add(ParagraphStyle(
            name="Body", fontSize=10, leading=14, spaceAfter=4,
            textColor=self.BRAND_NAVY))
        styles.add(ParagraphStyle(
            name="Small", fontSize=9, leading=12, spaceAfter=2))
        styles.add(ParagraphStyle(
            name="TableLabel", fontSize=9, leading=12,
            fontName="Helvetica-Bold"))
        styles.add(ParagraphStyle(
            name="TableValue", fontSize=9, leading=12))
        styles.add(ParagraphStyle(
            name="BrandTitle", fontSize=18, leading=20, alignment=0,
            fontName="Helvetica-Bold", spaceAfter=2,
            textColor=colors.white))
        styles.add(ParagraphStyle(
            name="BrandSubtitle", fontSize=11, leading=14, alignment=0,
            spaceAfter=2, textColor=colors.white))
        styles.add(ParagraphStyle(
            name="BrandAccent", fontSize=9, leading=12, alignment=0,
            spaceAfter=2, textColor=colors.white))
        styles.add(ParagraphStyle(
            name="GoldHeader", fontSize=11, leading=14,
            textColor=colors.white, alignment=0,
            fontName="Helvetica-Bold"))
        styles.add(ParagraphStyle(
            name="SectionDescription", fontSize=10, leading=14,
            textColor=self.BRAND_SLATE))
        styles.add(ParagraphStyle(
            name="SignatureLabel", fontSize=9, leading=11, alignment=1,
            textColor=colors.HexColor("#475569")))
        return styles

    def generate_pdf(
        self,
        output_pdf_path: Path,
        document: "SignedDocument",
        form_data: Dict[str, Any] | None,
        signatures: Sequence["DocumentSignature"],
    ) -> bool:
        """
        Render the PDF and persist it to disk.

        Args:
            output_pdf_path: Destination file path.
            document: Signed document metadata.
            form_data: Responses captured from the schema-driven form.
            signatures: Ordered signatures attached to the document.
        """
        responses = form_data or {}
        output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            doc = SimpleDocTemplate(
                str(output_pdf_path),
                pagesize=letter,
                topMargin=90,  # Increased for gold banner
                bottomMargin=54,
                leftMargin=54,
                rightMargin=54,
                title=self.schema.get("title", "Enrollment Agreement"),
            )

            story: List[Any] = []
            story.extend(self._build_brand_block())
            story.extend(self._build_metadata_block(document))

            for section in self.schema.get("sections", []):
                story.extend(self._render_section(section, responses))

            story.extend(self._render_signatures(signatures))

            # Build with custom page template for gold banner
            doc.build(story, onFirstPage=self._add_gold_header, onLaterPages=self._add_gold_header)
            return True
        except Exception as exc:  # pragma: no cover - logged for debugging
            print(f"Failed to build schema-driven PDF: {exc}")
            return False

    def _add_gold_header(self, canvas_obj, doc):
        """Add gold banner header to each page."""
        canvas_obj.saveState()

        # Draw gold banner across top
        canvas_obj.setFillColor(self.BRAND_GOLD)
        canvas_obj.rect(0, letter[1] - 50, letter[0], 50, fill=1, stroke=0)

        # Add white text "Atlanta Academy of Dental Assisting" aligned right
        canvas_obj.setFillColor(colors.white)
        canvas_obj.setFont("Helvetica-Bold", 16)
        canvas_obj.drawRightString(
            letter[0] - 40,  # Right margin
            letter[1] - 30,   # Vertical center of banner
            "Atlanta Academy of Dental Assisting"
        )

        canvas_obj.restoreState()

    def _build_brand_block(self) -> List[Any]:
        brand = self.schema.get("brand") or {}
        if not brand:
            return []

        logo_image = None
        logo_path = brand.get("logoPath")
        if isinstance(logo_path, str) and logo_path.strip():
            candidate = Path(logo_path.strip())
            if not candidate.is_absolute():
                candidate = Path.cwd() / candidate
            if candidate.exists():
                logo_image = Image(str(candidate), width=1.25 * inch, height=1.25 * inch, kind="proportional")
                logo_image.hAlign = "CENTER"

        text_rows: List[List[Any]] = []
        school_name = brand.get("schoolName", "Atlanta Academy of Dental Assisting")
        text_rows.append([Paragraph(school_name, self.styles["BrandTitle"])])

        address = brand.get("address") or []
        if isinstance(address, list) and address:
            text_rows.append([Paragraph(" • ".join(address), self.styles["BrandSubtitle"])])

        contact_bits = []
        if brand.get("phone"):
            contact_bits.append(f"Phone: {brand['phone']}")
        if brand.get("website"):
            contact_bits.append(brand["website"])
        if contact_bits:
            text_rows.append([Paragraph(" • ".join(contact_bits), self.styles["BrandAccent"])])

        text_rows.append([Paragraph("STUDENT ENROLLMENT AGREEMENT – DENTAL ASSISTING", self.styles["GoldHeader"])])

        text_table = Table(text_rows, colWidths=[4.8 * inch])
        text_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )

        if logo_image:
            brand_layout = Table(
                [[logo_image, text_table]],
                colWidths=[1.5 * inch, 4.8 * inch],
            )
        else:
            brand_layout = Table([[text_table]], colWidths=[6.3 * inch])

        brand_layout.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), self.BRAND_GOLD),
                    ("BOX", (0, 0), (-1, -1), 1, self.BRAND_GOLD),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ]
            )
        )

        flowables: List[Any] = [brand_layout, Spacer(1, 18)]
        flowables.append(Spacer(1, 12))
        return flowables

    def _render_section(self, section: Dict[str, Any], responses: Dict[str, Any]) -> List[Any]:
        flowables: List[Any] = []
        title = section.get("title") or ""
        if title:
            # Gold banner section header (matching original design)
            header = Table([[Paragraph(title.upper(), self.styles["GoldHeader"])]], colWidths=[6.3 * inch])
            header.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), self.BRAND_GOLD),
                        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
                        ("LEFTPADDING", (0, 0), (-1, -1), 12),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ]
                )
            )
            flowables.append(header)

        description = section.get("description")
        if description:
            desc_table = Table([[Paragraph(description, self.styles["SectionDescription"])]], colWidths=[6.3 * inch])
            desc_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), self.BRAND_CREAM),
                        ("LEFTPADDING", (0, 0), (-1, -1), 10),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ]
                )
            )
            flowables.append(desc_table)

        for element in section.get("elements", []):
            flowables.extend(self._render_element(element, responses))

        flowables.append(Spacer(1, 12))
        return flowables

    def _render_field_group(self, element: Dict[str, Any], responses: Dict[str, Any]) -> Optional[Any]:
        fields = element.get("fields") or []
        if not fields:
            return None
        layout = element.get("layout", "single-column")
        if layout == "two-column":
            body = self._render_field_group_two_column(fields, responses)
        else:
            body = self._render_field_group_single_column(fields, responses)

        parts: List[Any] = []
        title = element.get("title")
        if title:
            # Gold banner subsection header
            header = Table([[Paragraph(title.upper(), self.styles["GoldHeader"])]], colWidths=[6.3 * inch])
            header.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), self.BRAND_GOLD),
                        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
                        ("LEFTPADDING", (0, 0), (-1, -1), 12),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ]
                )
            )
            parts.append(header)

        description = element.get("description")
        if description:
            desc = Table([[Paragraph(description, self.styles["SectionDescription"])]], colWidths=[6.3 * inch])
            desc.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), self.BRAND_CREAM),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )
            parts.append(desc)

        parts.append(body)
        return KeepTogether(parts) if len(parts) > 1 else body

    def _render_field_group_single_column(self, fields: List[Dict[str, Any]], responses: Dict[str, Any]) -> Any:
        rows = []
        for field in fields:
            value = self._format_value(self._get_value(responses, field.get("name", "")))
            label = Paragraph(f"<b>{field.get('label', '')}</b>", self.styles["TableLabel"])
            rows.append([label, Paragraph(value or "—", self.styles["TableValue"])])

        table = Table(rows, colWidths=[1.6 * inch, 4.7 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("TEXTCOLOR", (0, 0), (-1, -1), self.BRAND_NAVY),
                    ("LINEBELOW", (1, 0), (1, -1), 0.75, self.BRAND_NAVY),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        return table

    def _render_field_group_two_column(self, fields: List[Dict[str, Any]], responses: Dict[str, Any]) -> Any:
        data: List[List[Any]] = []
        spans: List[Tuple[str, Tuple[int, int], Tuple[int, int]]] = []
        row: List[Any] = ["", "", "", ""]
        col_index = 0

        def flush_row(force: bool = False) -> None:
            nonlocal row, col_index
            if force or any(cell not in ("", None) for cell in row):
                data.append(row)
                row = ["", "", "", ""]
                col_index = 0

        for field in fields:
            value = self._format_value(self._get_value(responses, field.get("name", "")))
            label = Paragraph(f"<b>{field.get('label', '')}</b>", self.styles["TableLabel"])
            value_para = Paragraph(value or "—", self.styles["TableValue"])
            width = field.get("width", "half")
            if width == "full":
                flush_row()
                row = [label, value_para, "", ""]
                data.append(row)
                row_index = len(data) - 1
                spans.append(("SPAN", (1, row_index), (3, row_index)))
                row = ["", "", "", ""]
                col_index = 0
            else:
                row[col_index] = label
                row[col_index + 1] = value_para
                col_index += 2
                if col_index >= 4:
                    flush_row()

        flush_row()

        table = Table(data, colWidths=[1.2 * inch, 1.9 * inch, 1.2 * inch, 1.9 * inch])
        style = [
            ("TEXTCOLOR", (0, 0), (-1, -1), self.BRAND_NAVY),
            ("LINEBELOW", (1, 0), (1, -1), 0.75, self.BRAND_NAVY),
            ("LINEBELOW", (3, 0), (3, -1), 0.75, self.BRAND_NAVY),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]
        for span in spans:
            style.append(span)
            _, start, end = span
            style.append(("LINEBELOW", (start[0], start[1]), (end[0], end[1]), 0.75, self.BRAND_NAVY))
        table.setStyle(TableStyle(style))
        return table

    def _build_metadata_block(self, document: "SignedDocument") -> List[Any]:
        version = self.schema.get("version", "v1")
        rows = [
            [Paragraph("<b>Agreement Version</b>",
                       self.styles["TableLabel"]),
             Paragraph(version, self.styles["TableValue"])],
            [Paragraph("<b>Document ID</b>",
                       self.styles["TableLabel"]),
             Paragraph(str(document.id), self.styles["TableValue"])],
        ]
        table = Table(rows, colWidths=[2.5 * inch, 4.5 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), self.BRAND_GOLD),  # Gold header row
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("BOX", (0, 0), (-1, -1), 0.75, self.BRAND_GOLD),  # Gold border
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E2E8F0")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )

        return [table, Spacer(1, 18)]

    def _render_element(self, element: Dict[str, Any], responses: Dict[str, Any]) -> List[Any]:
        element_type = element.get("type")
        flowables: List[Any] = []

        if element_type == "text":
            content = element.get("content", "")
            flowables.append(Paragraph(content, self.styles["Body"]))
            flowables.append(Spacer(1, 6))
            return flowables

        if element_type == "field_group":
            group = self._render_field_group(element, responses)
            if group:
                flowables.append(group)
                flowables.append(Spacer(1, 8))
            return flowables

        if element_type == "table":
            headers = element.get("headers", [])
            rows = [[Paragraph(h, self.styles["TableLabel"]) for h in headers]]
            for row in element.get("rows", []):
                rows.append([Paragraph(str(cell), self.styles["TableValue"]) for cell in row])
            table = Table(rows, colWidths=[2.5 * inch, 2 * inch, 2.5 * inch])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), self.BRAND_GOLD),  # Gold header row
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("BOX", (0, 0), (-1, -1), 0.75, self.BRAND_GOLD),  # Gold border
                        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E2E8F0")),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                        ("LEFTPADDING", (0, 0), (-1, -1), 10),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ]
                )
            )
            flowables.append(table)
            flowables.append(Spacer(1, 8))
            return flowables

        if element_type == "list":
            ordered = element.get("ordered", False)
            for idx, item in enumerate(element.get("items", []), start=1):
                prefix = f"{idx}." if ordered else "•"
                flowables.append(Paragraph(f"{prefix} {item}", self.styles["Body"]))
            flowables.append(Spacer(1, 8))
            return flowables

        if element_type == "acknowledgement_list":
            rows = [
                [
                    Paragraph("<b>Statement</b>", self.styles["TableLabel"]),
                    Paragraph("<b>Initials</b>", self.styles["TableLabel"]),
                ]
            ]
            ack_values = (responses or {}).get("acknowledgements", {})
            for ack in element.get("acknowledgements", []):
                rows.append(
                    [
                        Paragraph(ack.get("label", ""), self.styles["TableValue"]),
                        Paragraph(ack_values.get(ack.get("id"), "") or "—", self.styles["TableValue"]),
                    ]
                )
            table = Table(rows, colWidths=[4.5 * inch, 2.5 * inch])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), self.BRAND_GOLD),  # Gold header row
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("BOX", (0, 0), (-1, -1), 0.75, self.BRAND_GOLD),  # Gold border
                        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E2E8F0")),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                        ("LEFTPADDING", (0, 0), (-1, -1), 10),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]
                )
            )
            flowables.append(table)
            flowables.append(Spacer(1, 8))
            return flowables

        return flowables

    def _render_signatures(self, signatures: Sequence["DocumentSignature"]) -> List[Any]:
        if not signatures:
            return []

        flowables: List[Any] = [Spacer(1, 12), Paragraph("Signatures", self.styles["SectionTitle"])]
        for signature in signatures:
            flowables.extend(self._render_signature(signature))
        return flowables

    def _render_signature(self, signature: "DocumentSignature") -> List[Any]:
        flowables: List[Any] = []
        image = self._decode_signature(signature.signature_data)
        signed_at = signature.signed_at.astimezone(timezone.utc)
        label = signature.signature_type.replace("_", " ").title()
        signature_cell = image if image else Paragraph("Signature on file", self.styles["Body"])

        signature_column = Table(
            [
                [signature_cell],
                [Paragraph(f"{label} Signature", self.styles["SignatureLabel"])],
            ],
            colWidths=[3.2 * inch],
        )
        signature_column.setStyle(
            TableStyle(
                [
                    ("LINEABOVE", (0, 0), (-1, 0), 0.75, colors.HexColor("#475569")),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("ALIGN", (0, 1), (-1, 1), "CENTER"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ]
            )
        )

        details_text = (
            f"<b>Name:</b> {signature.typed_name or '—'}<br/>"
            f"<b>Email:</b> {signature.signer_email or '—'}<br/>"
            f"<b>Signed:</b> {signed_at.strftime('%Y-%m-%d %H:%M:%S %Z')}"
        )

        table = Table(
            [[signature_column, Paragraph(details_text, self.styles["Body"])]],
            colWidths=[3.2 * inch, 3.3 * inch],
        )
        table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        flowables.append(table)
        flowables.append(Spacer(1, 10))
        return flowables

    def _get_value(self, responses: Dict[str, Any], path: str) -> Any:
        if not path:
            return None
        parts = path.split(".")
        cursor: Any = responses
        for part in parts:
            if not isinstance(cursor, dict):
                return None
            cursor = cursor.get(part)
            if cursor is None:
                return None
        return cursor

    def _format_value(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        if isinstance(value, (int, float)):
            return f"{value}"
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")
        return str(value)

    def _decode_signature(self, signature_data: str | None) -> Image | None:
        if not signature_data:
            return None
        payload = signature_data.split(",", maxsplit=1)[-1]
        try:
            image_bytes = base64.b64decode(payload)
        except Exception:  # pragma: no cover - invalid signature data
            return None
        buffer = io.BytesIO(image_bytes)
        img = Image(buffer, width=2.0 * inch, height=0.75 * inch)
        return img
