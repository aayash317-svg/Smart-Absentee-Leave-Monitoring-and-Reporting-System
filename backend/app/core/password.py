"""
Password hashing and verification utilities.
Uses bcrypt with cost factor 12 for strong security.
"""
import bcrypt


# Pre-computed real bcrypt hash of a dummy string.
# Used in constant-time login checks to prevent email enumeration timing attacks.
# Generated with: bcrypt.hashpw(b"__dummy__", bcrypt.gensalt(12))
_DUMMY_HASH = "$2b$12$eImiTXuWVxfM37uY4JANjQe5ps2zrPHERosOoXj4bLFcPcqtqXWom"


def hash_password(plain: str) -> str:
    """Hash a plain-text password using bcrypt (cost=12)."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """
    Constant-time password verification.
    Always runs bcrypt regardless of whether hashed is real or dummy,
    preventing timing-based email enumeration.
    """
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def get_dummy_hash() -> str:
    """
    Return the pre-computed dummy hash used as a fallback during login
    when the user does not exist — ensures bcrypt always runs.
    """
    return _DUMMY_HASH

# Aliases and helpers for test compatibility
get_password_hash = hash_password

def validate_password_strength(password: str) -> bool:
    """Enforce: 8+ chars, at least 1 uppercase, 1 lowercase, 1 digit, 1 special char."""
    import re
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

