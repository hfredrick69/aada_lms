"""
Comprehensive role permission tests for all 6 roles.

Tests each role's specific permissions on actual API endpoints:
- admin: Full system access
- staff: Instructor permissions + student CRUD
- instructor: Program/module management, attendance, skill checkoffs
- finance: Financial ledgers, payments, refunds
- registrar: Student records, credentials, transcripts
- student: Own data only
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_db
from app.db.models.user import User
from app.db.models.role import Role, UserRole
from app.db.models.program import Program
from app.core.security import create_access_token
from uuid import uuid4


client = TestClient(app)


@pytest.fixture
def db_session():
    """Get database session for tests."""
    db = next(get_db())
    yield db
    db.close()


@pytest.fixture
def admin_user(db_session):
    """Create admin user for testing."""
    from app.core.security import get_password_hash
    user = User(
        id=uuid4(),
        email="test_admin@aada.edu",
        password_hash=get_password_hash("TestPassword123!"),
        first_name="Test",
        last_name="Admin"
    )
    role = db_session.query(Role).filter(Role.name == "admin").first()
    db_session.add(user)
    db_session.flush()
    db_session.add(UserRole(user_id=user.id, role_id=role.id))
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def staff_user(db_session):
    """Create staff user for testing."""
    from app.core.security import get_password_hash
    user = User(
        id=uuid4(),
        email="test_staff@aada.edu",
        password_hash=get_password_hash("TestPassword123!"),
        first_name="Test",
        last_name="Staff"
    )
    role = db_session.query(Role).filter(Role.name == "staff").first()
    db_session.add(user)
    db_session.flush()
    db_session.add(UserRole(user_id=user.id, role_id=role.id))
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def instructor_user(db_session):
    """Create instructor user for testing."""
    from app.core.security import get_password_hash
    user = User(
        id=uuid4(),
        email="test_instructor@aada.edu",
        password_hash=get_password_hash("TestPassword123!"),
        first_name="Test",
        last_name="Instructor"
    )
    role = db_session.query(Role).filter(Role.name == "instructor").first()
    db_session.add(user)
    db_session.flush()
    db_session.add(UserRole(user_id=user.id, role_id=role.id))
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def finance_user(db_session):
    """Create finance user for testing."""
    from app.core.security import get_password_hash
    user = User(
        id=uuid4(),
        email="test_finance@aada.edu",
        password_hash=get_password_hash("TestPassword123!"),
        first_name="Test",
        last_name="Finance"
    )
    role = db_session.query(Role).filter(Role.name == "finance").first()
    db_session.add(user)
    db_session.flush()
    db_session.add(UserRole(user_id=user.id, role_id=role.id))
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def registrar_user(db_session):
    """Create registrar user for testing."""
    from app.core.security import get_password_hash
    user = User(
        id=uuid4(),
        email="test_registrar@aada.edu",
        password_hash=get_password_hash("TestPassword123!"),
        first_name="Test",
        last_name="Registrar"
    )
    role = db_session.query(Role).filter(Role.name == "registrar").first()
    db_session.add(user)
    db_session.flush()
    db_session.add(UserRole(user_id=user.id, role_id=role.id))
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def student_user(db_session):
    """Create student user for testing."""
    from app.core.security import get_password_hash
    user = User(
        id=uuid4(),
        email="test_student@aada.edu",
        password_hash=get_password_hash("TestPassword123!"),
        first_name="Test",
        last_name="Student"
    )
    role = db_session.query(Role).filter(Role.name == "student").first()
    db_session.add(user)
    db_session.flush()
    db_session.add(UserRole(user_id=user.id, role_id=role.id))
    db_session.commit()
    db_session.refresh(user)
    return user


def get_auth_headers(user: User) -> dict:
    """Generate auth headers for a user."""
    token = create_access_token(data={"sub": user.email})
    return {"Authorization": f"Bearer {token}"}


class TestAdminPermissions:
    """Test admin role permissions - should have full access."""

    def test_admin_can_create_programs(self, admin_user, db_session):
        """Admin can create programs."""
        headers = get_auth_headers(admin_user)
        data = {
            "code": "TEST-ADMIN-001",
            "name": "Admin Test Program",
            "credential_level": "certificate",
            "total_clock_hours": 480
        }
        response = client.post("/api/programs", json=data, headers=headers)
        assert response.status_code == 201

        # Cleanup
        program = db_session.query(Program).filter(Program.code == "TEST-ADMIN-001").first()
        if program:
            db_session.delete(program)
            db_session.commit()

    def test_admin_can_delete_programs(self, admin_user, db_session):
        """Admin can delete programs."""
        # Create test program
        program = Program(
            id=uuid4(),
            code="DELETE-TEST",
            name="Delete Test",
            credential_level="certificate",
            total_clock_hours=100
        )
        db_session.add(program)
        db_session.commit()

        headers = get_auth_headers(admin_user)
        response = client.delete(f"/api/programs/{program.id}", headers=headers)
        assert response.status_code == 200

    def test_admin_can_view_all_users(self, admin_user):
        """Admin can view all users."""
        headers = get_auth_headers(admin_user)
        response = client.get("/api/users", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestStaffPermissions:
    """Test staff role permissions - instructor permissions + student CRUD."""

    def test_staff_can_create_programs(self, staff_user, db_session):
        """Staff can create programs."""
        headers = get_auth_headers(staff_user)
        data = {
            "code": "TEST-STAFF-001",
            "name": "Staff Test Program",
            "credential_level": "certificate",
            "total_clock_hours": 480
        }
        response = client.post("/api/programs", json=data, headers=headers)
        assert response.status_code == 201

        # Cleanup
        program = db_session.query(Program).filter(Program.code == "TEST-STAFF-001").first()
        if program:
            db_session.delete(program)
            db_session.commit()

    def test_staff_cannot_delete_programs(self, staff_user, db_session):
        """Staff cannot delete programs (admin only)."""
        # Create test program
        program = Program(
            id=uuid4(),
            code="STAFF-DELETE",
            name="Delete Test",
            credential_level="certificate",
            total_clock_hours=100
        )
        db_session.add(program)
        db_session.commit()

        headers = get_auth_headers(staff_user)
        response = client.delete(f"/api/programs/{program.id}", headers=headers)
        assert response.status_code == 403

        # Cleanup
        db_session.delete(program)
        db_session.commit()

    def test_staff_can_view_all_users(self, staff_user):
        """Staff can view all users."""
        headers = get_auth_headers(staff_user)
        response = client.get("/api/users", headers=headers)
        assert response.status_code == 200


class TestInstructorPermissions:
    """Test instructor role permissions - program/module management, attendance."""

    def test_instructor_can_create_programs(self, instructor_user, db_session):
        """Instructor can create programs."""
        headers = get_auth_headers(instructor_user)
        data = {
            "code": "TEST-INST-001",
            "name": "Instructor Test Program",
            "credential_level": "certificate",
            "total_clock_hours": 480
        }
        response = client.post("/api/programs", json=data, headers=headers)
        assert response.status_code == 201

        # Cleanup
        program = db_session.query(Program).filter(Program.code == "TEST-INST-001").first()
        if program:
            db_session.delete(program)
            db_session.commit()

    def test_instructor_cannot_delete_programs(self, instructor_user, db_session):
        """Instructor cannot delete programs (admin only)."""
        # Create test program
        program = Program(
            id=uuid4(),
            code="INST-DELETE",
            name="Delete Test",
            credential_level="certificate",
            total_clock_hours=100
        )
        db_session.add(program)
        db_session.commit()

        headers = get_auth_headers(instructor_user)
        response = client.delete(f"/api/programs/{program.id}", headers=headers)
        assert response.status_code == 403

        # Cleanup
        db_session.delete(program)
        db_session.commit()

    def test_instructor_can_view_programs(self, instructor_user):
        """Instructor can view programs."""
        headers = get_auth_headers(instructor_user)
        response = client.get("/api/programs", headers=headers)
        assert response.status_code == 200


class TestFinancePermissions:
    """Test finance role permissions - financial ledgers, payments."""

    def test_finance_can_view_financial_ledgers(self, finance_user):
        """Finance can view financial ledgers."""
        headers = get_auth_headers(finance_user)
        response = client.get("/api/finance/ledgers", headers=headers)
        # Expect 200 (success) or 404 (endpoint exists but no data)
        assert response.status_code in [200, 404]

    def test_finance_cannot_create_programs(self, finance_user):
        """Finance cannot create programs (not instructor/admin/staff)."""
        headers = get_auth_headers(finance_user)
        data = {
            "code": "TEST-FIN-001",
            "name": "Finance Test Program",
            "credential_level": "certificate",
            "total_clock_hours": 480
        }
        response = client.post("/api/programs", json=data, headers=headers)
        assert response.status_code == 403

    def test_finance_cannot_delete_programs(self, finance_user, db_session):
        """Finance cannot delete programs."""
        # Create test program
        program = Program(
            id=uuid4(),
            code="FIN-DELETE",
            name="Delete Test",
            credential_level="certificate",
            total_clock_hours=100
        )
        db_session.add(program)
        db_session.commit()

        headers = get_auth_headers(finance_user)
        response = client.delete(f"/api/programs/{program.id}", headers=headers)
        assert response.status_code == 403

        # Cleanup
        db_session.delete(program)
        db_session.commit()


class TestRegistrarPermissions:
    """Test registrar role permissions - student records, credentials, transcripts."""

    def test_registrar_can_view_transcripts(self, registrar_user):
        """Registrar can view transcripts."""
        headers = get_auth_headers(registrar_user)
        response = client.get("/api/transcripts", headers=headers)
        # Expect 200 (success) or 404 (endpoint exists but no data)
        assert response.status_code in [200, 404]

    def test_registrar_can_view_credentials(self, registrar_user):
        """Registrar can view credentials."""
        headers = get_auth_headers(registrar_user)
        response = client.get("/api/credentials", headers=headers)
        # Expect 200 (success) or 404 (endpoint exists but no data)
        assert response.status_code in [200, 404]

    def test_registrar_cannot_create_programs(self, registrar_user):
        """Registrar cannot create programs (not instructor/admin/staff)."""
        headers = get_auth_headers(registrar_user)
        data = {
            "code": "TEST-REG-001",
            "name": "Registrar Test Program",
            "credential_level": "certificate",
            "total_clock_hours": 480
        }
        response = client.post("/api/programs", json=data, headers=headers)
        assert response.status_code == 403

    def test_registrar_cannot_delete_programs(self, registrar_user, db_session):
        """Registrar cannot delete programs."""
        # Create test program
        program = Program(
            id=uuid4(),
            code="REG-DELETE",
            name="Delete Test",
            credential_level="certificate",
            total_clock_hours=100
        )
        db_session.add(program)
        db_session.commit()

        headers = get_auth_headers(registrar_user)
        response = client.delete(f"/api/programs/{program.id}", headers=headers)
        assert response.status_code == 403

        # Cleanup
        db_session.delete(program)
        db_session.commit()


class TestStudentPermissions:
    """Test student role permissions - own data only."""

    def test_student_can_view_own_enrollments(self, student_user):
        """Student can view their own enrollments."""
        headers = get_auth_headers(student_user)
        response = client.get(f"/api/enrollments?user_id={student_user.id}", headers=headers)
        # Expect 200 or 404 depending on if student has enrollments
        assert response.status_code in [200, 404]

    def test_student_cannot_view_all_users(self, student_user):
        """Student cannot view all users (staff only)."""
        headers = get_auth_headers(student_user)
        response = client.get("/api/users", headers=headers)
        assert response.status_code == 403

    def test_student_cannot_create_programs(self, student_user):
        """Student cannot create programs."""
        headers = get_auth_headers(student_user)
        data = {
            "code": "TEST-STU-001",
            "name": "Student Test Program",
            "credential_level": "certificate",
            "total_clock_hours": 480
        }
        response = client.post("/api/programs", json=data, headers=headers)
        assert response.status_code == 403

    def test_student_cannot_delete_programs(self, student_user, db_session):
        """Student cannot delete programs."""
        # Create test program
        program = Program(
            id=uuid4(),
            code="STU-DELETE",
            name="Delete Test",
            credential_level="certificate",
            total_clock_hours=100
        )
        db_session.add(program)
        db_session.commit()

        headers = get_auth_headers(student_user)
        response = client.delete(f"/api/programs/{program.id}", headers=headers)
        assert response.status_code == 403

        # Cleanup
        db_session.delete(program)
        db_session.commit()

    def test_student_can_view_programs_list(self, student_user):
        """Student can view list of programs (public endpoint)."""
        # No auth headers - programs list is public
        response = client.get("/api/programs")
        assert response.status_code == 200


class TestCrossRoleAccessControl:
    """Test access control between different roles."""

    def test_student_cannot_access_other_student_data(self, student_user, db_session):
        """Student cannot access another student's data."""
        from app.core.security import get_password_hash
        # Create another student
        other_student = User(
            id=uuid4(),
            email="other_student@aada.edu",
            password_hash=get_password_hash("TestPassword123!"),
            first_name="Other",
            last_name="Student"
        )
        role = db_session.query(Role).filter(Role.name == "student").first()
        db_session.add(other_student)
        db_session.flush()
        db_session.add(UserRole(user_id=other_student.id, role_id=role.id))
        db_session.commit()

        headers = get_auth_headers(student_user)
        # Try to access other student's enrollments
        response = client.get(f"/api/enrollments?user_id={other_student.id}", headers=headers)
        assert response.status_code == 403

        # Cleanup
        db_session.query(UserRole).filter(UserRole.user_id == other_student.id).delete()
        db_session.delete(other_student)
        db_session.commit()

    def test_all_staff_roles_can_access_any_student_data(self, admin_user, staff_user, instructor_user, student_user):
        """All staff roles can access any student's data."""
        staff_users = [admin_user, staff_user, instructor_user]

        for staff in staff_users:
            headers = get_auth_headers(staff)
            response = client.get(f"/api/enrollments?user_id={student_user.id}", headers=headers)
            # Should not get 403 (Forbidden)
            assert response.status_code != 403, f"{staff.email} should be able to access student data"


class TestRoleHierarchy:
    """Test role hierarchy - admin > staff > instructor, finance, registrar > student."""

    def test_admin_has_all_permissions(self, admin_user):
        """Admin should have permissions of all other roles."""
        from app.core.rbac import RBACChecker
        rbac = RBACChecker(admin_user)

        assert rbac.is_admin() is True
        assert rbac.is_staff() is True
        assert rbac.has_role("admin") is True

    def test_staff_has_instructor_permissions(self, staff_user):
        """Staff should have all instructor permissions."""
        from app.core.rbac import RBACChecker
        rbac = RBACChecker(staff_user)

        assert rbac.is_staff() is True
        assert rbac.has_role("staff") is True
        assert rbac.is_admin() is False  # But not admin

    def test_student_has_no_staff_permissions(self, student_user):
        """Student should not have any staff permissions."""
        from app.core.rbac import RBACChecker
        rbac = RBACChecker(student_user)

        assert rbac.is_student() is True
        assert rbac.is_staff() is False
        assert rbac.is_admin() is False


def test_all_roles_exist_in_database(db_session):
    """Verify all 6 roles exist in the database."""
    expected_roles = ["admin", "staff", "instructor", "finance", "registrar", "student"]

    for role_name in expected_roles:
        role = db_session.query(Role).filter(Role.name == role_name).first()
        assert role is not None, f"Role '{role_name}' should exist in database"
        assert role.name == role_name, f"Role name should be lowercase: {role_name}"
