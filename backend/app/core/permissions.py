"""
Role-based access control (RBAC) permission guards.
Each function is a FastAPI dependency that pulls the current user via get_current_user
and enforces the required role, raising HTTP 403 if not matched.
"""
from fastapi import Depends, HTTPException, status

# Import here — avoids circular import since deps imports from core.jwt, not core.permissions
def _get_current_user():
    from .jwt import decode_access_token, safe_object_id
    from ..database.connection import get_db
    from fastapi import Header
    from typing import Optional

    async def _dep(authorization: Optional[str] = Header(None)) -> dict:
        if not authorization:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")
        parts = authorization.split(" ", 1)
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header format")
        payload = decode_access_token(parts[1])
        db = get_db()
        user = await db.users.find_one({"_id": safe_object_id(payload["sub"])})
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        if user.get("status") != "Active":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is deactivated")
        user["id"] = str(user["_id"])
        return user
    return _dep


# Role hierarchy definitions
STAFF_ROLES = {"Dean", "HOD", "Coordinator", "Faculty"}
MANAGEMENT_ROLES = {"Dean", "HOD", "Coordinator"}


def require_dean(current_user: dict = Depends(_get_current_user())) -> dict:
    """Allow only Dean role."""
    if current_user.get("role") != "Dean":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the Dean can perform this action"
        )
    return current_user


def require_hod(current_user: dict = Depends(_get_current_user())) -> dict:
    """Allow only HOD role."""
    if current_user.get("role") != "HOD":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the HOD can perform this action"
        )
    return current_user


def require_admin(current_user: dict = Depends(_get_current_user())) -> dict:
    """Allow only Admin role."""
    if current_user.get("role") not in {"Admin", "Dean"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admin or Dean can perform this action"
        )
    return current_user


def require_management(current_user: dict = Depends(_get_current_user())) -> dict:
    """Allow Dean, HOD, or Coordinator."""
    if current_user.get("role") not in MANAGEMENT_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Dean, HOD, or Coordinator can perform this action"
        )
    return current_user


def require_staff(current_user: dict = Depends(_get_current_user())) -> dict:
    """Allow Staff roles: Dean, HOD, Coordinator, Faculty."""
    if current_user.get("role") not in STAFF_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff members can perform this action"
        )
    return current_user


def require_student(current_user: dict = Depends(_get_current_user())) -> dict:
    """Allow only Student role."""
    if current_user.get("role") != "Student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can perform this action"
        )
    return current_user


def require_roles(*allowed_roles: str):
    """
    Factory that returns a FastAPI dependency for a given set of allowed roles.
    Usage: Depends(require_roles("Dean", "HOD"))
    """
    def checker(current_user: dict = Depends(_get_current_user())) -> dict:
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(allowed_roles)}"
            )
        return current_user
    return checker


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
