from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from .routes import auth, dashboard, leave, fines, attendance

app = FastAPI(title="Smart Student Absentees & Attendance ERP API")

# --- SECURITY FIX: Restrict CORS to known local origins only ---
# In production, replace this list with your actual deployed domain(s).
ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",  # If running a dev frontend separately
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# --- SECURITY: Add security headers to every response ---
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self';"
    )
    return response

# Register API Routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(leave.router)
app.include_router(fines.router)
app.include_router(attendance.router)

# Mount the frontend directory as static files
# E.g. http://localhost:8000/erp/login_attendance_hub/code.html
app.mount("/erp", StaticFiles(directory="stitch_smart_absence_erp"), name="erp")

@app.get("/")
def index_redirect():
    # Redirect root path to the login screen
    return RedirectResponse(url="/erp/login_attendance_hub/code.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
