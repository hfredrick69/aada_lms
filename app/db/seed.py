from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path
from typing import List, Tuple
from uuid import uuid4

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from sqlalchemy import text

from app.core.security import get_password_hash
from app.db.models.compliance.attendance import AttendanceLog
from app.db.models.compliance.complaint import Complaint
from app.db.models.compliance.credential import Credential
from app.db.models.compliance.extern import Externship
from app.db.models.compliance.finance import FinancialLedger
from app.db.models.compliance.skills import SkillCheckoff
from app.db.models.compliance.transcript import Transcript
from app.db.models.compliance.withdraw_refund import Refund, Withdrawal
from app.db.models.enrollment import Enrollment, ModuleProgress
from app.db.models.program import Module, Program
from app.db.models.role import Role
from app.db.models.user import User
from app.db.models.xapi import XapiStatement
from app.db.session import SessionLocal


GENERATED_DIR = Path("generated/transcripts")


def _reset_database(session) -> None:
    session.execute(
        text(
            """
            TRUNCATE
                compliance.attendance_logs,
                compliance.skills_checkoffs,
                compliance.externships,
                compliance.financial_ledgers,
                compliance.withdrawals,
                compliance.refunds,
                compliance.complaints,
                compliance.credentials,
                compliance.transcripts,
                module_progress,
                enrollments,
                modules,
                programs,
                user_roles,
                roles,
                users,
                xapi_statements
            RESTART IDENTITY CASCADE
            """
        )
    )
    session.commit()


def _render_transcript_pdf(
    transcript: Transcript,
    student: User,
    program: Program,
    module_details: List[Tuple[ModuleProgress, Module]],
) -> str:
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
    pdf.drawString(margin, y, f"Student: {student.first_name} {student.last_name}")
    y -= 0.25 * inch
    pdf.drawString(margin, y, f"Program: {program.name} ({program.code})")
    y -= 0.25 * inch
    if transcript.gpa is not None:
        pdf.drawString(margin, y, f"GPA: {float(transcript.gpa):.2f}")
        y -= 0.25 * inch
    pdf.drawString(margin, y, f"Issued: {transcript.generated_at.date().isoformat()}")
    y -= 0.4 * inch

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(margin, y, "Modules")
    y -= 0.3 * inch

    pdf.setFont("Helvetica", 11)
    for progress, module in module_details:
        module_title = module.title
        module_code = module.code
        line = (
            f"{module_code} - {module_title} | Score: {progress.score if progress.score is not None else 'N/A'} "
            f"| Progress: {progress.progress_pct if progress.progress_pct is not None else 'N/A'}%"
        )
        if y < margin:
            pdf.showPage()
            pdf.setFont("Helvetica", 11)
            y = height - margin
        pdf.drawString(margin, y, line)
        y -= 0.22 * inch

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    pdf_path.write_bytes(buffer.getvalue())
    return str(pdf_path)


def seed():
    session = SessionLocal()
    try:
        _reset_database(session)
        now = datetime.now(timezone.utc)
        semester_start = date.today().replace(day=1) - timedelta(days=60)

        admin = User(
            email="admin@aada.edu",
            password_hash=get_password_hash("AdminPass!23"),
            first_name="Ada",
            last_name="Administrator",
        )
        alice = User(
            email="alice.student@aada.edu",
            password_hash=get_password_hash("AlicePass!23"),
            first_name="Alice",
            last_name="Student",
        )
        bob = User(
            email="bob.student@aada.edu",
            password_hash=get_password_hash("BobPass!23"),
            first_name="Bob",
            last_name="Learner",
        )
        session.add_all([admin, alice, bob])
        session.commit()

        admin_role = Role(name="Admin", description="Full system access")
        instructor_role = Role(name="Instructor", description="Manage academics and externships")
        finance_role = Role(name="Finance", description="Handle payments and refunds")
        registrar_role = Role(name="Registrar", description="Manage students and records")
        session.add_all([admin_role, instructor_role, finance_role, registrar_role])
        session.commit()

        admin.roles = [admin_role, finance_role]
        alice.roles = [registrar_role]
        bob.roles = [instructor_role]
        session.add_all([admin, alice, bob])
        session.commit()

        ma_program = Program(
            code="MA-2025",
            name="Medical Assistant Diploma",
            credential_level="certificate",
            total_clock_hours=480,
        )
        session.add(ma_program)
        session.commit()

        modules = [
            Module(
                program_id=ma_program.id,
                code="MA-101",
                title="Medical Foundations",
                delivery_type="hybrid",
                clock_hours=120,
                requires_in_person=True,
                position=1,
            ),
            Module(
                program_id=ma_program.id,
                code="MA-201",
                title="Clinical Procedures",
                delivery_type="in_person",
                clock_hours=180,
                requires_in_person=True,
                position=2,
            ),
            Module(
                program_id=ma_program.id,
                code="MA-301",
                title="Externship",
                delivery_type="externship",
                clock_hours=180,
                requires_in_person=True,
                position=3,
            ),
        ]
        session.add_all(modules)
        session.commit()

        alice_enrollment = Enrollment(
            user_id=alice.id,
            program_id=ma_program.id,
            start_date=semester_start,
            expected_end_date=semester_start + timedelta(days=180),
            status="active",
        )
        bob_enrollment = Enrollment(
            user_id=bob.id,
            program_id=ma_program.id,
            start_date=semester_start,
            expected_end_date=semester_start + timedelta(days=180),
            status="withdrawn",
        )
        session.add_all([alice_enrollment, bob_enrollment])
        session.commit()

        alice_progress = []
        for module in modules:
            alice_progress.append(
                ModuleProgress(
                    enrollment_id=alice_enrollment.id,
                    module_id=module.id,
                    scorm_status="completed",
                    score=95 if module.code != "MA-301" else 98,
                    progress_pct=100,
                )
            )
        bob_progress = [
            ModuleProgress(
                enrollment_id=bob_enrollment.id,
                module_id=modules[0].id,
                scorm_status="incomplete",
                score=70,
                progress_pct=40,
            ),
            ModuleProgress(
                enrollment_id=bob_enrollment.id,
                module_id=modules[1].id,
                scorm_status="not_attempted",
                score=None,
                progress_pct=10,
            ),
        ]
        session.add_all(alice_progress + bob_progress)
        session.commit()

        attendance_entries = [
            AttendanceLog(
                user_id=alice.id,
                module_id=modules[0].id,
                session_type="live",
                session_ref="Zoom-12345",
                started_at=now - timedelta(days=14, hours=3),
                ended_at=now - timedelta(days=14, hours=2),
            ),
            AttendanceLog(
                user_id=alice.id,
                module_id=modules[1].id,
                session_type="lab",
                session_ref="LAB-22",
                started_at=now - timedelta(days=7, hours=4),
                ended_at=now - timedelta(days=7, hours=1),
            ),
            AttendanceLog(
                user_id=alice.id,
                module_id=modules[2].id,
                session_type="externship",
                session_ref="CLINIC-ACME",
                started_at=now - timedelta(days=2, hours=5),
                ended_at=now - timedelta(days=2, hours=1),
            ),
        ]
        session.add_all(attendance_entries)
        session.commit()

        skills = [
            SkillCheckoff(
                user_id=alice.id,
                module_id=modules[1].id,
                skill_code="BP_MEASURE",
                status="approved",
                evaluator_name="Dr. Smith",
                evaluator_license="RN12345",
                evidence_url="https://cdn.aada.edu/skills/bp_measure_alice.mp4",
                signed_at=now - timedelta(days=5),
            ),
            SkillCheckoff(
                user_id=bob.id,
                module_id=modules[0].id,
                skill_code="HIST_COLLECTION",
                status="in_review",
            ),
        ]
        session.add_all(skills)
        session.commit()

        externship = Externship(
            user_id=alice.id,
            site_name="Acme Care Clinic",
            site_address="123 Wellness Way, Atlanta, GA",
            supervisor_name="Jordan Lee",
            supervisor_email="jordan.lee@acmecare.org",
            total_hours=180,
            verification_doc_url="https://cdn.aada.edu/docs/externship/alice.pdf",
            verified=True,
            verified_at=now - timedelta(days=1),
        )
        session.add(externship)
        session.commit()

        ledgers = [
            FinancialLedger(
                user_id=alice.id,
                program_id=ma_program.id,
                line_type="tuition",
                amount_cents=800000,
                description="Program tuition charge",
                created_at=now - timedelta(days=60),
            ),
            FinancialLedger(
                user_id=alice.id,
                program_id=ma_program.id,
                line_type="payment",
                amount_cents=-400000,
                description="Scholarship payment",
                created_at=now - timedelta(days=50),
            ),
            FinancialLedger(
                user_id=bob.id,
                program_id=ma_program.id,
                line_type="tuition",
                amount_cents=800000,
                description="Program tuition charge",
                created_at=now - timedelta(days=60),
            ),
        ]
        session.add_all(ledgers)
        session.commit()

        withdrawal = Withdrawal(
            enrollment_id=bob_enrollment.id,
            requested_at=now - timedelta(days=10),
            reason="Scheduling conflicts",
            progress_pct_at_withdrawal=40,
            admin_processed_at=now - timedelta(days=9),
        )
        session.add(withdrawal)
        session.commit()

        refund_amount = int(round(800000 * (1 - (withdrawal.progress_pct_at_withdrawal or 0) / 100)))
        refund = Refund(
            withdrawal_id=withdrawal.id,
            amount_cents=refund_amount,
            policy_basis=f"Prorated refund based on {withdrawal.progress_pct_at_withdrawal}% completion.",
            approved_by=admin.id,
            approved_at=now - timedelta(days=9),
            remitted_at=now - timedelta(days=2),
        )
        session.add(refund)
        session.commit()

        complaints = [
            Complaint(
                user_id=alice.id,
                submitted_at=now - timedelta(days=15),
                category="instruction",
                details="Instructor cancelled lab without notice.",
                status="resolved",
                resolution_notes="Provided make-up lab and tutoring.",
                resolution_at=now - timedelta(days=12),
            ),
            Complaint(
                user_id=bob.id,
                submitted_at=now - timedelta(days=5),
                category="finance",
                details="Tuition refund timeline unclear.",
                status="in_review",
            ),
        ]
        session.add_all(complaints)
        session.commit()

        credential = Credential(
            user_id=alice.id,
            program_id=ma_program.id,
            credential_type="certificate",
            issued_at=now - timedelta(days=1),
            cert_serial="CERT-ALICE-2025",
        )
        session.add(credential)
        session.commit()

        gpa_scores = [progress.score for progress in alice_progress if progress.score is not None]
        gpa = round(min(4.0, sum(gpa_scores) / len(gpa_scores) / 25), 2)
        transcript = Transcript(
            user_id=alice.id,
            program_id=ma_program.id,
            gpa=gpa,
            generated_at=now - timedelta(days=1),
        )
        session.add(transcript)
        session.commit()

        # Ensure Module instances are attached to progress entries for PDF rendering
        progress_with_modules = []
        for progress in alice_progress:
            module = next(m for m in modules if m.id == progress.module_id)
            progress_with_modules.append((progress, module))
        transcript.pdf_url = _render_transcript_pdf(transcript, alice, ma_program, progress_with_modules)
        session.add(transcript)
        session.commit()

        xapi_records = [
            XapiStatement(
                actor={"mbox": "mailto:alice.student@aada.edu", "name": "Alice Student"},
                verb={"id": "http://adlnet.gov/expapi/verbs/launched", "display": {"en-US": "launched"}},
                object={"id": "module:MA-101", "definition": {"name": "Medical Foundations"}},
                result={"completion": True},
                context={"platform": "lms"},
                timestamp=now - timedelta(days=14),
            ),
            XapiStatement(
                actor={"mbox": "mailto:alice.student@aada.edu", "name": "Alice Student"},
                verb={"id": "http://adlnet.gov/expapi/verbs/completed", "display": {"en-US": "completed"}},
                object={"id": "module:MA-201", "definition": {"name": "Clinical Procedures"}},
                result={"score": {"raw": 95}},
                context={"platform": "lms"},
                timestamp=now - timedelta(days=7),
            ),
            XapiStatement(
                actor={"mbox": "mailto:bob.student@aada.edu", "name": "Bob Learner"},
                verb={"id": "http://adlnet.gov/expapi/verbs/terminated", "display": {"en-US": "terminated"}},
                object={"id": "module:MA-101", "definition": {"name": "Medical Foundations"}},
                result={"completion": False},
                context={"platform": "lms"},
                timestamp=now - timedelta(days=10),
            ),
        ]
        session.add_all(xapi_records)
        session.commit()

        print("Seed data created successfully!")
        print(f"  Users: {session.query(User).count()}")
        print(f"  Programs: {session.query(Program).count()}")
        print(f"  Enrollments: {session.query(Enrollment).count()}")
        print(f"  Attendance logs: {session.query(AttendanceLog).count()}")
        print(f"  Skills checkoffs: {session.query(SkillCheckoff).count()}")
        print(f"  Externships: {session.query(Externship).count()}")
        print(f"  Complaints: {session.query(Complaint).count()}")
        print(f"  Credentials: {session.query(Credential).count()}")
        print(f"  Transcripts: {session.query(Transcript).count()}")
        print(f"  xAPI statements: {session.query(XapiStatement).count()}")
    finally:
        session.close()


if __name__ == "__main__":
    seed()
