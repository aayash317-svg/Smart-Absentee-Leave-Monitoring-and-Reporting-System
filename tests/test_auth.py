from backend.app.core.password import get_password_hash, verify_password, validate_password_strength
from backend.app.core.jwt import create_access_token, decode_token

def test_password_hashing():
    pwd = "SecureStudentPass@2026"
    hashed = get_password_hash(pwd)
    assert verify_password(pwd, hashed) is True
    assert verify_password("incorrect_pass", hashed) is False

def test_password_strength():
    assert validate_password_strength("Weak1") is False  # Too short
    assert validate_password_strength("lowercaseonly123!") is False  # No uppercase
    assert validate_password_strength("UPPERCASEONLY123!") is False  # No lowercase
    assert validate_password_strength("NoSpecial12345678") is False  # No special char
    assert validate_password_strength("NoDigitsHere@Hello") is False  # No digit
    assert validate_password_strength("ValidPassword@2026") is True

def test_jwt_tokens():
    token = create_access_token(subject="65f4c568f12a34b5678cd90a", role="Dean")
    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == "65f4c568f12a34b5678cd90a"
    assert decoded["role"] == "Dean"
    assert decoded["type"] == "access"
