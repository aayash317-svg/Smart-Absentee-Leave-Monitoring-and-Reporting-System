"""
Unified entry point for backend security module.
Re-exports functions from password, jwt, and permissions.
"""
from .password import get_password_hash, verify_password, validate_password_strength, hash_password
from .jwt import create_access_token, create_refresh_token, decode_token, decode_access_token, safe_object_id
from .permissions import (
    require_roles,
    require_staff,
    require_management,
    require_student,
    require_dean,
    check_department_scope
)
