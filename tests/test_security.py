"""
Comprehensive Security Features Test Suite

Tests:
1. Password Hashing & Constant-time Verification (bcrypt)
2. Password Complexity / Strength Validation
3. JWT Creation, Verification & Tamper Detection
4. Safe ObjectId Conversion (MongoDB injection protection)
5. Role-Based Access Control (RBAC Permission Guards)
6. Department Scope Enforcement
7. File Upload Security (Extensions, MIME-types, File size limits)
"""

import pytest
import datetime
from fastapi import HTTPException
from bson.objectid import ObjectId

from backend.app.core.password import get_password_hash, verify_password, validate_password_strength
from backend.app.core.jwt import create_access_token, create_refresh_token, decode_token, decode_access_token, safe_object_id
from backend.app.core.permissions import (
    require_dean, require_hod, require_admin, require_student,
    require_staff, require_management, check_department_scope
)
from backend.app.utils.upload import validate_uploaded_file


# ── 1. Password Security Tests ──────────────────────────────────────────────

def test_password_hashing_and_verification():
    raw_password = "ComplexPassword@2026"
    hashed = get_password_hash(raw_password)
    
    # Assert password is not stored in plain text
    assert hashed != raw_password
    assert hashed.startswith("$2b$")  # bcrypt prefix
    
    # Assert correct verification
    assert verify_password(raw_password, hashed) is True
    # Assert incorrect password rejection
    assert verify_password("WrongPassword@2026", hashed) is False


def test_password_strength_enforcement():
    # Fail cases
    assert validate_password_strength("short1!") is False            # < 8 chars
    assert validate_password_strength("alllowercase123!") is False   # No uppercase
    assert validate_password_strength("ALLUPPERCASE123!") is False   # No lowercase
    assert validate_password_strength("NoSpecialChar123") is False    # No special char
    assert validate_password_strength("NoDigitsHere@Password") is False # No digits
    
    # Pass cases
    assert validate_password_strength("ValidPass@2026") is True
    assert validate_password_strength("Secure#Admin99") is True


# ── 2. JWT Security & Tamper Detection ──────────────────────────────────────

def test_jwt_creation_and_payload_verification():
    subject_id = str(ObjectId())
    token = create_access_token(subject=subject_id, role="Dean", email="dean@college.edu")
    
    decoded = decode_access_token(token)
    assert decoded["sub"] == subject_id
    assert decoded["role"] == "Dean"
    assert decoded["email"] == "dean@college.edu"
    assert decoded["type"] == "access"


def test_jwt_tamper_detection():
    token = create_access_token(subject="user123", role="Student")
    
    # Modify payload string to simulate tampering
    tampered_token = token[:-5] + "XXXXX"
    
    # Safe decode returns None
    assert decode_token(tampered_token) is None
    
    # Decode access token raises HTTP 401
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(tampered_token)
    assert exc_info.value.status_code == 401
    assert "invalid or has been tampered with" in exc_info.value.detail.lower()


# ── 3. ObjectId Security & Injection Protection ──────────────────────────────

def test_safe_object_id_validation():
    valid_id_str = str(ObjectId())
    obj_id = safe_object_id(valid_id_str)
    assert isinstance(obj_id, ObjectId)
    assert str(obj_id) == valid_id_str

    # Malicious / invalid string format tests
    invalid_inputs = ["invalid_id", "' OR '1'='1", "12345", "../../etc/passwd"]
    for bad_input in invalid_inputs:
        with pytest.raises(HTTPException) as exc_info:
            safe_object_id(bad_input)
        assert exc_info.value.status_code == 400
        assert "Invalid ID format" in exc_info.value.detail


# ── 4. Role-Based Access Control (RBAC) Tests ───────────────────────────────

def test_rbac_permission_guards():
    dean_user = {"id": "1", "role": "Dean"}
    hod_user = {"id": "2", "role": "HOD"}
    student_user = {"id": "3", "role": "Student"}

    # Dean Guard
    assert require_dean(dean_user) == dean_user
    with pytest.raises(HTTPException) as exc:
        require_dean(hod_user)
    assert exc.value.status_code == 403

    # HOD Guard
    assert require_hod(hod_user) == hod_user
    with pytest.raises(HTTPException) as exc:
        require_hod(student_user)
    assert exc.value.status_code == 403

    # Student Guard
    assert require_student(student_user) == student_user
    with pytest.raises(HTTPException) as exc:
        require_student(dean_user)
    assert exc.value.status_code == 403

    # Staff Guard (Dean, HOD, Coordinator, Faculty allowed)
    assert require_staff(dean_user) == dean_user
    assert require_staff(hod_user) == hod_user
    with pytest.raises(HTTPException) as exc:
        require_staff(student_user)
    assert exc.value.status_code == 403


# ── 5. Department Scope Security Tests ──────────────────────────────────────

def test_department_scope_enforcement():
    dept_cs_id = str(ObjectId())
    dept_it_id = str(ObjectId())

    # Faculty in CS trying to access CS student -> Allowed
    check_department_scope(user_role="Faculty", user_dept_id=dept_cs_id, target_dept_id=dept_cs_id)

    # Faculty in CS trying to access IT student -> Denied (HTTP 403)
    with pytest.raises(HTTPException) as exc_info:
        check_department_scope(user_role="Faculty", user_dept_id=dept_cs_id, target_dept_id=dept_it_id)
    assert exc_info.value.status_code == 403
    assert "Faculty can only access students in their own department" in exc_info.value.detail

    # Dean / HOD level roles are cross-department -> Allowed
    check_department_scope(user_role="Dean", user_dept_id=dept_cs_id, target_dept_id=dept_it_id)


# ── 6. File Upload Security Tests ───────────────────────────────────────────

def test_file_upload_security_constraints():
    # 1. Allowed file types
    assert validate_uploaded_file("medical_certificate.pdf", "application/pdf", 2 * 1024 * 1024) is True
    assert validate_uploaded_file("doctor_note.png", "image/png", 1 * 1024 * 1024) is True

    # 2. Block executable / dangerous extensions
    dangerous_files = ["script.exe", "attack.sh", "payload.py", "shell.php", "page.html"]
    for filename in dangerous_files:
        with pytest.raises(HTTPException) as exc_info:
            validate_uploaded_file(filename, "application/octet-stream", 1000)
        assert exc_info.value.status_code == 400
        assert "Unsupported file format" in exc_info.value.detail

    # 3. Block spoofed MIME types
    with pytest.raises(HTTPException) as exc_info:
        validate_uploaded_file("malicious.pdf", "application/javascript", 1000)
    assert exc_info.value.status_code == 400
    assert "Invalid file type" in exc_info.value.detail

    # 4. Enforce max file size (5MB limit)
    with pytest.raises(HTTPException) as exc_info:
        validate_uploaded_file("large_document.pdf", "application/pdf", 6 * 1024 * 1024)
    assert exc_info.value.status_code == 400
    assert "File exceeds maximum allowed size" in exc_info.value.detail
