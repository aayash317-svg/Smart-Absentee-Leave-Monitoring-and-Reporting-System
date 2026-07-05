import pytest
from fastapi import HTTPException
from backend.app.utils.upload import validate_uploaded_file
from backend.app.schemas.student import LeaveApply

def test_file_upload_validation():
    # Valid PDF upload
    assert validate_uploaded_file("medical_certificate.pdf", "application/pdf", 1024 * 1024) is True
    # Valid Image upload
    assert validate_uploaded_file("receipt.png", "image/png", 4 * 1024 * 1024) is True
    
    # Invalid extension
    with pytest.raises(HTTPException) as exc_info:
        validate_uploaded_file("malicious.exe", "application/octet-stream", 1000)
    assert exc_info.value.status_code == 400
    assert "Unsupported file format" in exc_info.value.detail
        
    # Invalid MIME type
    with pytest.raises(HTTPException) as exc_info:
        validate_uploaded_file("script.pdf", "application/javascript", 1000)
    assert exc_info.value.status_code == 400
    assert "Invalid file type" in exc_info.value.detail
        
    # File too large (6 MB)
    with pytest.raises(HTTPException) as exc_info:
        validate_uploaded_file("huge.png", "image/png", 6 * 1024 * 1024)
    assert exc_info.value.status_code == 400
    assert "File exceeds maximum allowed size" in exc_info.value.detail

def test_leave_apply_schema():
    req = LeaveApply(
        startDate="2026-07-05",
        endDate="2026-07-06",
        leaveType="Full Day Leave",
        reason="Medical emergency",
        certificateUrl="http://example.com/certificate.pdf"
    )
    assert req.startDate == "2026-07-05"
    assert req.endDate == "2026-07-06"
    assert req.leaveType == "Full Day Leave"
