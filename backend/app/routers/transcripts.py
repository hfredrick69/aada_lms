from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from io import BytesIO
from pathlib import Path
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session

from app.db.models.compliance.transcript import Transcript
from app.db.models.enrollment import Enrollment, ModuleProgress
from app.db.models.program import Module, Program
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.transcripts import ModuleResult, TranscriptGenerate, TranscriptRead

router = APIRouter(prefix="/transcripts", tags=["transcripts"])

GENERATED_DIR = Path("generated/transcripts")


def _latest_enrollment(db: Session, user_id: UUID, program_id: UUID) -> Enrollment:
    enrollment = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == user_id, Enrollment.program_id == program_id)
        .order_by(Enrollment.start_date.desc())
        .first()
    )
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found for transcript generation.",
        )
    return enrollment


def _module_results(db: Session, enrollment: Enrollment) -> List[ModuleResult]:
    records = (
        db.query(ModuleProgress, Module)
        .join(Module, Module.id == ModuleProgress.module_id)
        .filter(ModuleProgress.enrollment_id == enrollment.id)
        .order_by(Module.position.asc())
        .all()
    )
    if not records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No module progress data available to generate transcript.",
        )
    results: List[ModuleResult] = []
    for progress, module in records:
        results.append(
            ModuleResult(
                module_id=module.id,
                module_code=module.code,
                module_title=module.title,
                score=progress.score,
                progress_pct=progress.progress_pct,
                scorm_status=progress.scorm_status,
            )
        )
    return results


def _calculate_gpa(results: List[ModuleResult]) -> Decimal | None:
    scores = [module.score for module in results if module.score is not None]
    if not scores:
        return None
    avg_score = sum(scores) / len(scores)
    gpa = min(4.0, avg_score / 25)
    return Decimal(str(gpa)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _fetch_user_program(db: Session, user_id: UUID, program_id: UUID) -> tuple[User, Program]:
    user = db.get(User, user_id)
    program = db.get(Program, program_id)
    if not user or not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User or program not found for transcript generation.",
        )
    return user, program


def _render_transcript_pdf(
    user: User,
    program: Program,
    transcript: Transcript,
    modules: List[ModuleResult],
    gpa: Decimal | None,
) -> Path:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = GENERATED_DIR / f"{transcript.id}.pdf"
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = inch
    y = height - margin

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(margin, y, "AADA Official Transcript")
    y -= 0.5 * inch

    pdf.setFont("Helvetica", 12)
    pdf.drawString(margin, y, f"Student: {user.first_name} {user.last_name}")
    y -= 0.25 * inch
    pdf.drawString(margin, y, f"Program: {program.name} ({program.code})")
    y -= 0.25 * inch
    if gpa is not None:
        pdf.drawString(margin, y, f"GPA: {float(gpa):.2f}")
        y -= 0.25 * inch
    pdf.drawString(margin, y, f"Issued: {transcript.generated_at.date().isoformat()}")
    y -= 0.4 * inch

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(margin, y, "Modules")
    y -= 0.3 * inch

    pdf.setFont("Helvetica", 11)
    for module in modules:
        if y < margin:
            pdf.showPage()
            y = height - margin
            pdf.setFont("Helvetica", 11)
        pdf.drawString(
            margin,
            y,
            f"{module.module_code} - {module.module_title} | Score: "
            f"{module.score if module.score is not None else 'N/A'} | "
            f"Progress: {module.progress_pct if module.progress_pct is not None else 'N/A'}%",
        )
        y -= 0.22 * inch

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    pdf_path.write_bytes(buffer.getvalue())
    return pdf_path


def _serialize_transcript(
    transcript: Transcript, modules: List[ModuleResult]
) -> TranscriptRead:
    return TranscriptRead.from_orm_with_modules(transcript, modules)


@router.get("", response_model=List[TranscriptRead])
def list_transcripts(db: Session = Depends(get_db)) -> List[TranscriptRead]:
    records = db.query(Transcript).order_by(Transcript.generated_at.desc()).all()
    serialized: List[TranscriptRead] = []
    for record in records:
        try:
            enrollment = _latest_enrollment(db, record.user_id, record.program_id)
            modules = _module_results(db, enrollment)
            serialized.append(_serialize_transcript(record, modules))
        except HTTPException:
            # Skip transcripts with no enrollment or module data
            continue
    return serialized


@router.post("", response_model=TranscriptRead, status_code=status.HTTP_201_CREATED)
def generate_transcript(
    payload: TranscriptGenerate, db: Session = Depends(get_db)
) -> TranscriptRead:
    enrollment = _latest_enrollment(db, payload.user_id, payload.program_id)
    modules = _module_results(db, enrollment)
    gpa = _calculate_gpa(modules)
    transcript = Transcript(
        user_id=payload.user_id,
        program_id=payload.program_id,
        gpa=gpa,
        generated_at=datetime.now(timezone.utc),
    )
    db.add(transcript)
    db.commit()
    db.refresh(transcript)
    user, program = _fetch_user_program(db, payload.user_id, payload.program_id)
    pdf_path = _render_transcript_pdf(user, program, transcript, modules, gpa)
    transcript.pdf_url = str(pdf_path)
    db.add(transcript)
    db.commit()
    db.refresh(transcript)
    return _serialize_transcript(transcript, modules)


@router.get("/{transcript_id}", response_model=TranscriptRead)
def get_transcript(transcript_id: UUID, db: Session = Depends(get_db)) -> TranscriptRead:
    transcript = db.get(Transcript, transcript_id)
    if not transcript:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcript not found")
    enrollment = _latest_enrollment(db, transcript.user_id, transcript.program_id)
    modules = _module_results(db, enrollment)
    return _serialize_transcript(transcript, modules)


@router.get("/{transcript_id}/pdf")
def download_transcript_pdf(transcript_id: UUID, db: Session = Depends(get_db)) -> FileResponse:
    transcript = db.get(Transcript, transcript_id)
    if not transcript or not transcript.pdf_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcript PDF not available")
    pdf_path = Path(transcript.pdf_url)
    if not pdf_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcript PDF missing on server")
    return FileResponse(path=pdf_path, filename=pdf_path.name, media_type="application/pdf")


@router.delete("/{transcript_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transcript(transcript_id: UUID, db: Session = Depends(get_db)) -> None:
    transcript = db.get(Transcript, transcript_id)
    if not transcript:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcript not found")
    pdf_url = Path(transcript.pdf_url) if transcript.pdf_url else None
    db.delete(transcript)
    db.commit()
    if pdf_url and pdf_url.exists():
        pdf_url.unlink(missing_ok=True)
