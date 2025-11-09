import csv
from datetime import datetime
from decimal import Decimal
from io import BytesIO, StringIO
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session

from app.db.models.compliance.attendance import AttendanceLog
from app.db.models.compliance.complaint import Complaint
from app.db.models.compliance.credential import Credential
from app.db.models.compliance.extern import Externship
from app.db.models.compliance.skills import SkillCheckoff
from app.db.models.compliance.transcript import Transcript
from app.db.models.compliance.withdraw_refund import Refund, Withdrawal
from app.db.models.user import User
from app.db.session import get_db
from app.utils.encryption import decrypt_value

router = APIRouter(prefix="/reports", tags=["reports"])

COMPLIANCE_MODELS = {
    "attendance": AttendanceLog,
    "complaints": Complaint,
    "credentials": Credential,
    "externships": Externship,
    "skills": SkillCheckoff,
    "withdrawals": Withdrawal,
    "refunds": Refund,
    "transcripts": Transcript,
}


def _serialize_record(record, db: Session) -> Dict[str, Any]:
    row: Dict[str, Any] = {}

    # Add decrypted student name FIRST if record has user_id
    if hasattr(record, 'user_id') and record.user_id:
        user = db.query(User).filter(User.id == record.user_id).first()
        if user:
            first_name = decrypt_value(db, user.first_name)
            last_name = decrypt_value(db, user.last_name)
            row['student_name'] = f"{first_name} {last_name}"

    # Then add all other fields
    for column in record.__table__.columns:  # type: ignore[attr-defined]
        value = getattr(record, column.name)
        if isinstance(value, (datetime, Decimal)):
            row[column.name] = value.isoformat() if isinstance(value, datetime) else str(value)
        else:
            row[column.name] = str(value) if value is not None else None

    return row


def _generate_csv(rows: List[Dict[str, Any]], filename: str) -> StreamingResponse:
    buffer = StringIO()
    if rows:
        writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    response = StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
    )
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    return response


def _generate_pdf(rows: List[Dict[str, Any]], filename: str) -> StreamingResponse:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = inch
    y = height - margin

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(margin, y, f"{filename.title()} Report")
    y -= 0.4 * inch

    pdf.setFont("Helvetica", 10)
    for row in rows or [{}]:
        if not row:
            pdf.drawString(margin, y, "No data available.")
            break
        line = ", ".join(f"{key}: {value}" for key, value in row.items())
        if y < margin:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y = height - margin
        pdf.drawString(margin, y, line)
        y -= 0.25 * inch

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    response = StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="application/pdf",
    )
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
    return response


@router.get("/health")
def health() -> Dict[str, str]:
    return {"reports": "ok"}


@router.get("/compliance/{resource}")
def export_compliance_report(
    resource: str,
    format: str = Query(
        default="csv",
        pattern="^(csv|pdf)$",
        description="Choose csv or pdf export format.",
    ),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    model = COMPLIANCE_MODELS.get(resource)
    if not model:
        raise HTTPException(status_code=404, detail="Compliance resource not found.")
    records = db.query(model).all()
    rows = [_serialize_record(record, db) for record in records]
    filename = f"{resource}_report"
    if format == "csv":
        return _generate_csv(rows, filename)
    return _generate_pdf(rows, filename)
