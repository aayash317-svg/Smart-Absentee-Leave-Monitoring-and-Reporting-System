from fastapi import HTTPException, status

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
ALLOWED_MIME_TYPES = {"application/pdf", "image/png", "image/jpeg"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

def validate_uploaded_file(filename: str, content_type: str, file_size: int) -> bool:
    # 1. Validate extension
    try:
        ext = filename.split(".")[-1].lower()
    except Exception:
        ext = ""
        
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Only PDF, PNG, JPG, and JPEG are allowed."
        )
        
    # 2. Validate MIME type
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Only PDF, PNG, and JPEG formats are allowed."
        )
        
    # 3. Validate file size
    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size of 5 MB."
        )
        
    return True
