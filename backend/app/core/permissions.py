"""
Role-based access control (RBAC) permission guards.
Used as FastAPI dependencies on protected routes.
"""
from fastapi import HTTPException, status


# Role hierarchy definitions
STAFF_ROLES = {"Dean", "HOD", "Coordinator", "Faculty"}
MANAGEMENT_ROLES = {"Dean", "HOD", "Coordinator"}
ADMIN_ROLES = {"Dean"}
ALL_ROLES = {"Dean", "HOD", "Coordinator", "Faculty", "Student"}


def require_roles(*allowed_roles: str):
    """
    Factory that returns a role-checker function for a given set of roles.
    Usage: Depends(require_roles("Dean", "HOD"))
    """
    def checker(role: str) -> str:
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(allowed_roles)}"
            )
        return role
    return checker


def require_staff(role: str) -> str:
    """Allow only Staff roles: Dean, HOD, Coordinator, Faculty."""
    if role not in STAFF_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff members can perform this action"
        )
    return role


def require_management(role: str) -> str:
    """Allow only management roles: Dean, HOD, Coordinator."""
    if role not in MANAGEMENT_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Dean, HOD, or Coordinator can perform this action"
        )
    return role


def require_student(role: str) -> str:
    """Allow only Student role."""
    if role != "Student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can perform this action"
        )
    return role


def require_dean(role: str) -> str:
    """Allow only Dean role."""
    if role != "Dean":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the Dean can perform this action"
        )
    return role


def check_department_scope(user_role: str, user_dept_id, target_dept_id) -> None:
    """
    Enforce department-level scope for Faculty.
    Faculty can only act on students in their own department.
    Dean / HOD / Coordinator have cross-department access.
    """
    if user_role == "Faculty":
        if user_dept_id and target_dept_id:
            if str(user_dept_id) != str(target_dept_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Faculty can only access students in their own department"
                )
