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
from app.db.models.crm import Lead, LeadSource, Activity
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
        db.execute(text(
            "TRUNCATE TABLE crm.leads, crm.activities, crm.lead_custom_fields "
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
        admissions_counselor_role = Role(
            id=uuid4(),
            name="admissions_counselor",
            description="Admissions counselor managing leads"
        )
        admissions_manager_role = Role(
            id=uuid4(),
            name="admissions_manager",
            description="Admissions manager overseeing recruitment"
        )

        db.add_all([
            admin_role, student_role, instructor_role, staff_role,
            finance_role, registrar_role, admissions_counselor_role, admissions_manager_role
        ])
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
        admissions_counselor_user = User(
            id=uuid4(),
            email="counselor@aada.edu",
            password_hash=hash_password_for_seed("CounselorPass!23"),
            first_name="Carl",
            last_name="Counselor",
            status="active"
        )
        admissions_manager_user = User(
            id=uuid4(),
            email="admissions@aada.edu",
            password_hash=hash_password_for_seed("AdmissionsPass!23"),
            first_name="Amy",
            last_name="Admissions",
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
            admissions_counselor_user,
            admissions_manager_user,
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
        db.add(UserRole(user_id=admissions_counselor_user.id, role_id=admissions_counselor_role.id))
        db.add(UserRole(user_id=admissions_manager_user.id, role_id=admissions_manager_role.id))
        db.add(UserRole(user_id=alice_user.id, role_id=student_role.id))
        db.add(UserRole(user_id=bob_user.id, role_id=student_role.id))

        # Assign student role to generic users
        for user in users[9:]:
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

        # Create enrollments for all users (cycle through programs if needed)
        enrollments = []
        for i, user in enumerate(users):
            enrollment = Enrollment(
                id=uuid4(),
                user_id=user.id,
                program_id=programs[i % len(programs)].id,
                start_date=datetime.now().date() - timedelta(days=60 - i*5),
                expected_end_date=datetime.now().date() + timedelta(days=120),
                status="active" if i < 12 else "withdrawn"
            )
            enrollments.append(enrollment)
            db.add(enrollment)

        db.commit()
        print(f"✅ Created {len(enrollments)} enrollments")

        # Create attendance logs (2 per user, cycle through modules)
        for i, user in enumerate(users):
            for j in range(2):
                log_entry = AttendanceLog(
                    id=uuid4(),
                    user_id=user.id,
                    module_id=modules[(i*3) % len(modules)].id,
                    session_type="live" if j == 0 else "lab",
                    session_ref=f"SESSION-{i}-{j}",
                    started_at=datetime.now() - timedelta(days=30 - i*2, hours=j*2),
                    ended_at=datetime.now() - timedelta(days=30 - i*2, hours=j*2 - 1)
                )
                db.add(log_entry)

        db.commit()
        print(f"✅ Created {len(users)*2} attendance logs")

        # Create skill checkoffs for all users
        for i, user in enumerate(users):
            checkoff = SkillCheckoff(
                id=uuid4(),
                user_id=user.id,
                module_id=modules[(i*3) % len(modules)].id,
                skill_code=f"SKILL_{i:03d}",
                status="approved" if i < 10 else "pending",
                evaluator_name=f"Instructor {i}" if i < 10 else None,
                evaluator_license=f"LIC-{i:04d}" if i < 10 else None,
                signed_at=datetime.now() - timedelta(days=15 - i) if i < 10 else None
            )
            db.add(checkoff)

        db.commit()
        print(f"✅ Created {len(users)} skill checkoffs")

        # Create externships for all users
        for i, user in enumerate(users):
            externship = Externship(
                id=uuid4(),
                user_id=user.id,
                site_name=f"Clinic Site {i+1}",
                site_address=f"{100+i} Medical Plaza, Atlanta, GA",
                supervisor_name=f"Dr. Supervisor {i+1}",
                supervisor_email=f"supervisor{i+1}@clinic.com",
                total_hours=80 + i*10,
                verified=i < 10,
                verified_at=datetime.now() - timedelta(days=10) if i < 10 else None
            )
            db.add(externship)

        db.commit()
        print(f"✅ Created {len(users)} externships")

        # Create financial ledger entries for all users
        for i, user in enumerate(users):
            ledger = FinancialLedger(
                id=uuid4(),
                user_id=user.id,
                program_id=programs[i % len(programs)].id,
                line_type="tuition",
                amount_cents=850000 + i*1000,
                description="Tuition for {}".format(programs[i % len(programs)].name)
            )
            db.add(ledger)

        db.commit()
        print(f"✅ Created {len(users)} financial ledger entries")

        # Create withdrawals for last 2 students
        withdrawals = []
        for i in range(12, 14):
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
        print(f"✅ Created {len(withdrawals)} withdrawals")

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
        print(f"✅ Created {len(users)} complaints")

        # Create credentials for completed students
        for i, user in enumerate(users[:10]):
            if i < 7:  # Only completed students get credentials
                credential = Credential(
                    id=uuid4(),
                    user_id=user.id,
                    program_id=programs[i % len(programs)].id,
                    credential_type="certificate",
                    issued_at=datetime.now() - timedelta(days=5),
                    cert_serial=f"CERT-2025-{i+1:04d}"
                )
                db.add(credential)

        db.commit()
        print("✅ Created credentials")

        # Create transcripts for completed students
        for i, user in enumerate(users[:10]):
            if i < 7:
                transcript = Transcript(
                    id=uuid4(),
                    user_id=user.id,
                    program_id=programs[i % len(programs)].id,
                    gpa=3.5 + (i * 0.05),
                    generated_at=datetime.now() - timedelta(days=3),
                    pdf_url=f"/transcripts/{user.id}.pdf"
                )
                db.add(transcript)

        db.commit()
        print("✅ Created transcripts")

        # Create xAPI statements for all users
        for i, user in enumerate(users):
            statement = XapiStatement(
                id=uuid4(),
                actor={"mbox": f"mailto:{user.email}", "name": f"{user.first_name} {user.last_name}"},
                verb={"id": "http://adlnet.gov/expapi/verbs/completed"},
                object={"id": f"http://aada.edu/modules/{modules[(i*3) % len(modules)].id}"},
                timestamp=datetime.now() - timedelta(days=i)
            )
            db.add(statement)

        db.commit()
        print(f"✅ Created {len(users)} xAPI statements")

        # Fetch lead sources from database (created by migration)
        lead_sources = db.query(LeadSource).all()
        if not lead_sources:
            print("⚠️  No lead sources found - run migrations first")
        else:
            # Create 15 sample leads with variety - assigned to admissions team
            lead_data = [
                ("Sarah", "Johnson", "sarah.j@gmail.com", "404-555-0101",
                 "new", 0, None),
                ("Michael", "Chen", "mchen@yahoo.com", "678-555-0102",
                 "contacted", 5, admissions_counselor_user.id),
                ("Jennifer", "Martinez", "jmartinez@outlook.com", "770-555-0103",
                 "qualified", 15, admissions_counselor_user.id),
                ("David", "Williams", "dwilliams@gmail.com", "470-555-0104",
                 "application_sent", 25, admissions_manager_user.id),
                ("Lisa", "Anderson", "landerson@aol.com", "404-555-0105",
                 "enrolled", 40, admissions_manager_user.id),
                ("Robert", "Taylor", "rtaylor@icloud.com", "678-555-0106",
                 "new", 0, None),
                ("Maria", "Garcia", "mgarcia@gmail.com", "770-555-0107",
                 "contacted", 8, admissions_counselor_user.id),
                ("James", "Brown", "jbrown@yahoo.com", "470-555-0108",
                 "qualified", 12, admissions_counselor_user.id),
                ("Patricia", "Moore", "pmoore@gmail.com", "404-555-0109",
                 "lost", 5, None),
                ("Christopher", "Davis", "cdavis@outlook.com", "678-555-0110",
                 "new", 0, None),
                ("Linda", "Miller", "lmiller@gmail.com", "770-555-0111",
                 "contacted", 10, admissions_counselor_user.id),
                ("Daniel", "Wilson", "dwilson@yahoo.com", "470-555-0112",
                 "qualified", 18, admissions_manager_user.id),
                ("Karen", "Thompson", "kthompson@gmail.com", "404-555-0113",
                 "application_sent", 22, admissions_manager_user.id),
                ("Steven", "Lee", "slee@icloud.com", "678-555-0114",
                 "new", 0, None),
                ("Nancy", "White", "nwhite@gmail.com", "770-555-0115",
                 "contacted", 7, admissions_counselor_user.id)
            ]

            leads = []
            for i, (first, last, email, phone, status, score, assigned_to) in enumerate(lead_data):
                lead = Lead(
                    id=uuid4(),
                    first_name=first,
                    last_name=last,
                    email=email,
                    phone=phone,
                    lead_source_id=lead_sources[i % len(lead_sources)].id,
                    program_interest_id=programs[i % len(programs)].id,
                    lead_status=status,
                    lead_score=score,
                    assigned_to_id=assigned_to,
                    notes=f"Sample lead {i+1} - interested in {programs[i % len(programs)].name}"
                )
                leads.append(lead)
                db.add(lead)

            db.commit()
            print(f"✅ Created {len(leads)} sample leads")

            # Create activities for some leads
            activity_data = [
                (0, "call", "Initial contact call", "Spoke with Sarah, very interested in MA program"),
                (1, "email", "Follow-up email sent", "Sent program brochure and pricing information"),
                (2, "meeting", "Campus tour scheduled", "Scheduled for next Tuesday at 10 AM"),
                (3, "call", "Application support", "Helped with application questions"),
                (6, "call", "Follow-up call", "Discussed financial aid options"),
                (7, "email", "Program details sent", "Sent detailed curriculum information"),
                (10, "meeting", "In-person meeting", "Met to discuss career goals"),
                (12, "call", "Application status check", "Confirmed all documents received"),
            ]

            for lead_idx, activity_type, subject, description in activity_data:
                activity = Activity(
                    id=uuid4(),
                    entity_type="lead",
                    entity_id=leads[lead_idx].id,
                    activity_type=activity_type,
                    subject=subject,
                    description=description,
                    created_by_id=admissions_counselor_user.id if lead_idx % 2 == 0 else admissions_manager_user.id
                )
                db.add(activity)

            db.commit()
            print(f"✅ Created {len(activity_data)} lead activities")

        print("\n🎉 Database seeded successfully with test data for all roles!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    reset_and_seed()
