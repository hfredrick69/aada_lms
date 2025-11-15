from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from uuid import uuid4
from typing import Iterable, List, Optional

from app.core.security import get_password_hash
from app.db.models.compliance.finance import FinancialLedger
from app.db.models.enrollment import Enrollment, ModuleProgress
from app.db.models.program import Module, Program
from app.db.models.role import Role
from app.db.models.user import User
from app.utils.encryption import encrypt_value

ModuleProgressSeed = dict


def create_user_with_roles(
    db,
    *,
    email: str,
    password: str,
    first_name: str = "Unit",
    last_name: str = "Test",
    roles: Optional[list[str]] = None,
):
    """Create (or replace) a user with encrypted fields and optional roles."""
    encrypted_email = encrypt_value(db, email)
    encrypted_first = encrypt_value(db, first_name)
    encrypted_last = encrypt_value(db, last_name)

    user = db.query(User).filter(User.email == encrypted_email).first()
    if user:
        user.password_hash = get_password_hash(password)
        user.first_name = encrypted_first
        user.last_name = encrypted_last
        user.status = "active"
    else:
        user = User(
            email=encrypted_email,
            password_hash=get_password_hash(password),
            first_name=encrypted_first,
            last_name=encrypted_last,
            status="active",
        )
    db.add(user)
    db.commit()
    db.refresh(user)

    for role_name in roles or []:
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            role = Role(name=role_name, description=f"{role_name.title()} role")
            db.add(role)
            db.commit()
            db.refresh(role)
        if role not in user.roles:
            user.roles.append(role)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def seed_student_program(
    db,
    *,
    module_progress: Optional[Iterable[ModuleProgressSeed]] = None,
    start_date: Optional[date] = None,
    ledger_amount_cents: int = 100_000,
) -> dict:
    """Seed baseline user/program/enrollment data for compliance tests."""
    module_progress = module_progress or (
        {"progress_pct": 100, "score": 95, "scorm_status": "completed"},
        {"progress_pct": 100, "score": 97, "scorm_status": "passed"},
    )
    start_date = start_date or (date.today() - timedelta(days=30))
    now = datetime.now(timezone.utc)

    student_id = uuid4()
    admin_id = uuid4()
    program_id = uuid4()
    enrollment_id = uuid4()

    student = create_user_with_roles(
        db,
        email=f"{student_id.hex[:12]}@student.test",
        password="StudentPass!23",
        first_name="Test",
        last_name="Student",
        roles=["student", "registrar"],
    )
    admin = create_user_with_roles(
        db,
        email=f"{admin_id.hex[:12]}@admin.test",
        password="AdminPass!23",
        first_name="Admin",
        last_name="User",
        roles=["admin"],
    )

    program = Program(
        id=program_id,
        code=f"PRG-{program_id.hex[:6]}",
        name="Test Program",
        credential_level="certificate",
        total_clock_hours=120,
    )
    db.add(program)
    db.commit()
    db.refresh(program)

    modules: List[Module] = []
    for idx, progress_data in enumerate(module_progress, start=1):
        module = Module(
            id=uuid4(),
            program_id=program.id,
            code=f"MOD-{idx}",
            title=f"Module {idx}",
            delivery_type="online",
            clock_hours=40,
            requires_in_person=False,
            position=idx,
        )
        modules.append(module)
    db.add_all(modules)
    db.commit()
    for module in modules:
        db.refresh(module)

    enrollment = Enrollment(
        id=enrollment_id,
        user_id=student.id,
        program_id=program.id,
        start_date=start_date,
        expected_end_date=start_date + timedelta(days=90),
        status="active",
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    progresses: List[ModuleProgress] = []
    for module, progress_data in zip(modules, module_progress):
        progresses.append(
            ModuleProgress(
                id=uuid4(),
                enrollment_id=enrollment.id,
                module_id=module.id,
                scorm_status=progress_data.get("scorm_status"),
                score=progress_data.get("score"),
                progress_pct=progress_data.get("progress_pct"),
            )
        )
    db.add_all(progresses)
    db.commit()
    for progress in progresses:
        db.refresh(progress)

    ledger = FinancialLedger(
        id=uuid4(),
        user_id=student.id,
        program_id=program.id,
        line_type="tuition",
        amount_cents=ledger_amount_cents,
        description="Tuition charge",
        created_at=now,
    )
    db.add(ledger)
    db.commit()
    db.refresh(ledger)

    return {
        "student": student,
        "admin": admin,
        "program": program,
        "modules": modules,
        "progresses": progresses,
        "enrollment": enrollment,
        "ledger": ledger,
        "now": now,
    }
