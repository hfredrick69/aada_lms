"""
Role-Based Access Control (RBAC) for HIPAA compliance.

Ensures users can only access data they're authorized to see.
"""
from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.user import User


# Import get_current_user lazily to avoid circular imports
def _get_current_user():
    from app.routers.auth import get_current_user
    return get_current_user


def require_roles(allowed_roles: List[str]):
    """
    Dependency factory to require specific roles.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_roles(["Admin"]))])

    Args:
        allowed_roles: List of role names that are allowed access

    Returns:
        Dependency function that checks user roles
    """
    async def check_roles(current_user: User = Depends(_get_current_user())):
        user_roles = [r.name for r in current_user.roles]

        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user

    return check_roles


def require_admin(current_user: User = Depends(_get_current_user())):
    """
    Dependency to require Admin role.

    Usage:
        @router.get("/admin-endpoint", dependencies=[Depends(require_admin)])
    """
    user_roles = [r.name for r in current_user.roles]

    if "Admin" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_staff(current_user: User = Depends(_get_current_user())):
    """
    Dependency to require staff roles (Admin, Registrar, Instructor, Finance).

    Usage:
        @router.get("/staff-endpoint", dependencies=[Depends(require_staff)])
    """
    user_roles = [r.name for r in current_user.roles]
    staff_roles = ["Admin", "Registrar", "Instructor", "Finance"]

    if not any(role in staff_roles for role in user_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff access required"
        )
    return current_user


def filter_by_user_access(
    db: Session,
    query,
    model_user_id_field: str,
    current_user: User
):
    """
    Filter query results based on user access rights.

    - Students can only see their own data
    - Staff can see all data

    Args:
        db: Database session
        query: SQLAlchemy query to filter
        model_user_id_field: Name of the user_id field in the model
        current_user: Current authenticated user

    Returns:
        Filtered query
    """
    user_roles = [r.name for r in current_user.roles]
    staff_roles = ["Admin", "Registrar", "Instructor", "Finance"]

    # Staff can see all data
    if any(role in staff_roles for role in user_roles):
        return query

    # Students can only see their own data
    return query.filter(getattr(query.column_descriptions[0]['entity'], model_user_id_field) == current_user.id)


def can_access_user_data(resource_user_id: str, current_user: User) -> bool:
    """
    Check if current user can access data belonging to another user.

    Rules:
    - Users can access their own data
    - Staff can access any user's data
    - Students cannot access other students' data

    Args:
        resource_user_id: ID of the user who owns the resource
        current_user: Current authenticated user

    Returns:
        True if access is allowed, False otherwise

    Raises:
        HTTPException if access is denied
    """
    user_roles = [r.name for r in current_user.roles]
    staff_roles = ["Admin", "Registrar", "Instructor", "Finance"]

    # User accessing their own data
    if str(resource_user_id) == str(current_user.id):
        return True

    # Staff can access any data
    if any(role in staff_roles for role in user_roles):
        return True

    # Deny access
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to access this resource"
    )


class RBACChecker:
    """
    Helper class for checking RBAC permissions.

    Usage:
        rbac = RBACChecker(current_user)
        if rbac.is_admin():
            # Admin-only logic
        if rbac.is_staff():
            # Staff logic
        if rbac.can_access(resource_user_id):
            # Access allowed
    """

    def __init__(self, user: User):
        self.user = user
        self.roles = [r.name for r in user.roles]

    def is_admin(self) -> bool:
        """Check if user has Admin role."""
        return "Admin" in self.roles

    def is_staff(self) -> bool:
        """Check if user has any staff role."""
        staff_roles = ["Admin", "Registrar", "Instructor", "Finance"]
        return any(role in staff_roles for role in self.roles)

    def is_student(self) -> bool:
        """Check if user has Student role."""
        return "Student" in self.roles

    def can_access(self, resource_user_id: str) -> bool:
        """
        Check if user can access resource owned by another user.

        Returns True/False without raising exceptions.
        """
        try:
            can_access_user_data(resource_user_id, self.user)
            return True
        except HTTPException:
            return False

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        return role_name in self.roles

    def has_any_role(self, role_names: List[str]) -> bool:
        """Check if user has any of the specified roles."""
        return any(role in self.roles for role in role_names)
