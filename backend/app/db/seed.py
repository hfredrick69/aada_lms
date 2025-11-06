"""
Expanded seed data for AADA LMS - 10 records per table
"""
from datetime import datetime, timedelta
from sqlalchemy import text
from app.db.session import SessionLocal
from app.db.models.user import User
from app.db.models.role import Role, UserRole
from app.db.models.program import Program, Module
from app.db.models.enrollment import Enrollment
from app.db.models.compliance.attendance import AttendanceLog
from app.db.models.compliance.skills import SkillCheckoff
from app.db.models.compliance.extern import Externship
from app.db.models.compliance.finance import FinancialLedger
from app.db.models.compliance.withdraw_refund import Withdrawal, Refund
from app.db.models.compliance.complaint import Complaint
from app.db.models.compliance.credential import Credential
from app.db.models.compliance.transcript import Transcript
from app.db.models.xapi import XapiStatement
import bcrypt
from uuid import uuid4


def hash_password_for_seed(password: str) -> str:
    """Hash password using bcrypt directly (avoids passlib version detection bug)."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def reset_and_seed():
    """Clears all data and creates comprehensive test records"""
    db = SessionLocal()

    try:
        # TRUNCATE all tables with CASCADE
        db.execute(text(
            "TRUNCATE TABLE users, roles, user_roles, programs, modules, "
            "enrollments, module_progress, scorm_records, xapi_statements "
            "RESTART IDENTITY CASCADE"
        ))
        db.execute(text(
            "TRUNCATE TABLE compliance.attendance_logs, "
            "compliance.skills_checkoffs, compliance.externships "
            "RESTART IDENTITY CASCADE"
        ))
        db.execute(text(
            "TRUNCATE TABLE compliance.financial_ledgers, "
            "compliance.withdrawals, compliance.refunds "
            "RESTART IDENTITY CASCADE"
        ))
        db.execute(text(
            "TRUNCATE TABLE compliance.complaints, "
            "compliance.credentials, compliance.transcripts "
            "RESTART IDENTITY CASCADE"
        ))
        db.commit()
        print("✅ Database reset complete")

        # Create roles (all lowercase)
        admin_role = Role(id=uuid4(), name="admin", description="System Administrator with full access")
        student_role = Role(id=uuid4(), name="student", description="Student with access to own records")
        instructor_role = Role(
            id=uuid4(),
            name="instructor",
            description="Instructor with course and student management"
        )
        staff_role = Role(
            id=uuid4(),
            name="staff",
            description="Staff with instructor permissions plus student CRUD"
        )
        finance_role = Role(id=uuid4(), name="finance", description="Finance staff with payment access")
        registrar_role = Role(id=uuid4(), name="registrar", description="Registrar with student records access")

        db.add_all([admin_role, student_role, instructor_role, staff_role, finance_role, registrar_role])
        db.commit()

        # Create specific test accounts for each role
        admin_user = User(
            id=uuid4(),
            email="admin@aada.edu",
            password_hash=hash_password_for_seed("AdminPass!23"),
            first_name="Ada",
            last_name="Administrator",
            status="active"
        )
        staff_user = User(
            id=uuid4(),
            email="staff@aada.edu",
            password_hash=hash_password_for_seed("StaffPass!23"),
            first_name="Sam",
            last_name="Staffer",
            status="active"
        )
        instructor_user = User(
            id=uuid4(),
            email="instructor@aada.edu",
            password_hash=hash_password_for_seed("InstructorPass!23"),
            first_name="Ian",
            last_name="Instructor",
            status="active"
        )
        finance_user = User(
            id=uuid4(),
            email="finance@aada.edu",
            password_hash=hash_password_for_seed("FinancePass!23"),
            first_name="Fiona",
            last_name="Finance",
            status="active"
        )
        registrar_user = User(
            id=uuid4(),
            email="registrar@aada.edu",
            password_hash=hash_password_for_seed("RegistrarPass!23"),
            first_name="Rita",
            last_name="Registrar",
            status="active"
        )
        alice_user = User(
            id=uuid4(),
            email="alice.student@aada.edu",
            password_hash=hash_password_for_seed("AlicePass!23"),
            first_name="Alice",
            last_name="Student",
            status="active"
        )
        bob_user = User(
            id=uuid4(),
            email="bob.student@aada.edu",
            password_hash=hash_password_for_seed("BobLearner!23"),
            first_name="Bob",
            last_name="Learner",
            status="active"
        )

        users = [
            admin_user,
            staff_user,
            instructor_user,
            finance_user,
            registrar_user,
            alice_user,
            bob_user
        ]
        db.add_all(users)

        # Create additional generic users
        for i in range(1, 8):
            user = User(
                id=uuid4(),
                email=f"user{i}@aada.edu",
                password_hash=hash_password_for_seed("Pass123!Word"),
                first_name=f"Student{i}",
                last_name="Tester",
                status="active"
            )
            users.append(user)
            db.add(user)

        db.commit()
        print(f"✅ Created {len(users)} users")

        # Assign roles to specific test accounts
        db.add(UserRole(user_id=admin_user.id, role_id=admin_role.id))
        db.add(UserRole(user_id=staff_user.id, role_id=staff_role.id))
        db.add(UserRole(user_id=instructor_user.id, role_id=instructor_role.id))
        db.add(UserRole(user_id=finance_user.id, role_id=finance_role.id))
        db.add(UserRole(user_id=registrar_user.id, role_id=registrar_role.id))
        db.add(UserRole(user_id=alice_user.id, role_id=student_role.id))
        db.add(UserRole(user_id=bob_user.id, role_id=student_role.id))

        # Assign student role to generic users
        for user in users[7:]:
            db.add(UserRole(user_id=user.id, role_id=student_role.id))
        db.commit()

        # Create Medical Assistant Diploma Program (with Module 1 H5P content)
        ma_program = Program(
            id=uuid4(),
            code="MA-2025",
            name="Medical Assistant Diploma",
            credential_level="certificate",
            total_clock_hours=480
        )
        db.add(ma_program)
        db.commit()  # Commit MA program before adding modules

        # Create real modules including Module 1 with H5P content
        modules = [
            Module(
                id=uuid4(),
                program_id=ma_program.id,
                code="MA-101",
                title="Orientation & Professional Foundations",
                delivery_type="hybrid",
                clock_hours=120,
                requires_in_person=True,
                position=1
            ),
            Module(
                id=uuid4(),
                program_id=ma_program.id,
                code="MA-201",
                title="Clinical Procedures",
                delivery_type="in_person",
                clock_hours=180,
                requires_in_person=True,
                position=2
            ),
            Module(
                id=uuid4(),
                program_id=ma_program.id,
                code="MA-301",
                title="Externship",
                delivery_type="externship",
                clock_hours=180,
                requires_in_person=True,
                position=3
            ),
        ]

        # Add generic test programs
        programs = [ma_program]
        for i in range(2, 11):
            program = Program(
                id=uuid4(),
                code=f"PROG-{i:03d}",
                name=f"Test Program {i}",
                credential_level="certificate",
                total_clock_hours=480 + (i * 10)
            )
            programs.append(program)
            db.add(program)

        db.commit()  # Commit all programs before adding modules

        # Add modules for test programs
        for program in programs[1:]:  # Skip ma_program (already has modules)
            for j in range(1, 4):
                modules.append(Module(
                    id=uuid4(),
                    program_id=program.id,
                    code=f"{program.code}-M{j}",
                    title=f"Module {j} - {program.name}",
                    delivery_type="online",
                    clock_hours=40 + (j * 10),
                    requires_in_person=False,
                    position=j
                ))

        db.add_all(modules)
        db.commit()
        print(f"✅ Created {len(programs)} programs")
        print(f"✅ Created {len(modules)} modules")

        # Create 10 Enrollments
        enrollments = []
        for i, user in enumerate(users):
            enrollment = Enrollment(
                id=uuid4(),
                user_id=user.id,
                program_id=programs[i].id,
                start_date=datetime.now().date() - timedelta(days=60 - i*5),
                expected_end_date=datetime.now().date() + timedelta(days=120),
                status="active" if i < 8 else "withdrawn"
            )
            enrollments.append(enrollment)
            db.add(enrollment)

        db.commit()
        print(f"✅ Created {len(enrollments)} enrollments")

        # Create 20 Attendance Logs (2 per user)
        for i, user in enumerate(users):
            for j in range(2):
                log_entry = AttendanceLog(
                    id=uuid4(),
                    user_id=user.id,
                    module_id=modules[i*3].id,
                    session_type="live" if j == 0 else "lab",
                    session_ref=f"SESSION-{i}-{j}",
                    started_at=datetime.now() - timedelta(days=30 - i*2, hours=j*2),
                    ended_at=datetime.now() - timedelta(days=30 - i*2, hours=j*2 - 1)
                )
                db.add(log_entry)

        db.commit()
        print("✅ Created 20 attendance logs")

        # Create 10 Skill Checkoffs
        for i, user in enumerate(users):
            checkoff = SkillCheckoff(
                id=uuid4(),
                user_id=user.id,
                module_id=modules[i*3].id,
                skill_code=f"SKILL_{i:03d}",
                status="approved" if i < 7 else "pending",
                evaluator_name=f"Instructor {i}" if i < 7 else None,
                evaluator_license=f"LIC-{i:04d}" if i < 7 else None,
                signed_at=datetime.now() - timedelta(days=15 - i) if i < 7 else None
            )
            db.add(checkoff)

        db.commit()
        print("✅ Created 10 skill checkoffs")

        # Create 10 Externships
        for i, user in enumerate(users):
            externship = Externship(
                id=uuid4(),
                user_id=user.id,
                site_name=f"Clinic Site {i+1}",
                site_address=f"{100+i} Medical Plaza, Atlanta, GA",
                supervisor_name=f"Dr. Supervisor {i+1}",
                supervisor_email=f"supervisor{i+1}@clinic.com",
                total_hours=80 + i*10,
                verified=i < 6,
                verified_at=datetime.now() - timedelta(days=10) if i < 6 else None
            )
            db.add(externship)

        db.commit()
        print("✅ Created 10 externships")

        # Create 10 Financial Ledger entries
        for i, user in enumerate(users):
            ledger = FinancialLedger(
                id=uuid4(),
                user_id=user.id,
                program_id=programs[i].id,
                line_type="tuition",
                amount_cents=850000 + i*1000,
                description="Tuition for {}".format(programs[i].name)
            )
            db.add(ledger)

        db.commit()
        print("✅ Created 10 financial ledger entries")

        # Create 10 Withdrawals (for last 2 students who are withdrawn)
        withdrawals = []
        for i in range(8, 10):
            withdrawal = Withdrawal(
                id=uuid4(),
                enrollment_id=enrollments[i].id,
                requested_at=datetime.now() - timedelta(days=5),
                reason=f"Personal reasons - User {i+1}",
                admin_processed_at=datetime.now() - timedelta(days=3),
                progress_pct_at_withdrawal=30 + i*5
            )
            withdrawals.append(withdrawal)
            db.add(withdrawal)

        db.commit()
        print("✅ Created 2 withdrawals (expanded to 10 if needed)")

        # Create 10 Refunds
        for withdrawal in withdrawals:
            refund = Refund(
                id=uuid4(),
                withdrawal_id=withdrawal.id,
                amount_cents=300000,
                policy_basis="GNPEC Standard 12 - Prorated refund",
                approved_at=datetime.now() - timedelta(days=2),
                remitted_at=datetime.now() - timedelta(days=1)
            )
            db.add(refund)

        db.commit()
        print("✅ Created refunds")

        # Create 10 Complaints
        for i, user in enumerate(users):
            complaint = Complaint(
                id=uuid4(),
                user_id=user.id,
                submitted_at=datetime.now() - timedelta(days=20 - i),
                category="Academic" if i % 2 == 0 else "Administrative",
                details=f"Test complaint from user {i+1}",
                status="resolved" if i < 6 else "in_review",
                resolution_notes=f"Resolved complaint {i+1}" if i < 6 else None,
                resolution_at=datetime.now() - timedelta(days=10) if i < 6 else None
            )
            db.add(complaint)

        db.commit()
        print("✅ Created 10 complaints")

        # Create 10 Credentials
        for i, user in enumerate(users[:10]):
            if i < 7:  # Only completed students get credentials
                credential = Credential(
                    id=uuid4(),
                    user_id=user.id,
                    program_id=programs[i].id,
                    credential_type="certificate",
                    issued_at=datetime.now() - timedelta(days=5),
                    cert_serial=f"CERT-2025-{i+1:04d}"
                )
                db.add(credential)

        db.commit()
        print("✅ Created credentials")

        # Create 10 Transcripts
        for i, user in enumerate(users[:10]):
            if i < 7:
                transcript = Transcript(
                    id=uuid4(),
                    user_id=user.id,
                    program_id=programs[i].id,
                    gpa=3.5 + (i * 0.05),
                    generated_at=datetime.now() - timedelta(days=3),
                    pdf_url=f"/transcripts/{user.id}.pdf"
                )
                db.add(transcript)

        db.commit()
        print("✅ Created transcripts")

        # Create 10 xAPI Statements
        for i, user in enumerate(users):
            statement = XapiStatement(
                id=uuid4(),
                actor={"mbox": f"mailto:{user.email}", "name": f"{user.first_name} {user.last_name}"},
                verb={"id": "http://adlnet.gov/expapi/verbs/completed"},
                object={"id": f"http://aada.edu/modules/{modules[i*3].id}"},
                timestamp=datetime.now() - timedelta(days=i)
            )
            db.add(statement)

        db.commit()
        print("✅ Created 10 xAPI statements")

        print("\n🎉 Database seeded with 10+ records per table!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    reset_and_seed()
