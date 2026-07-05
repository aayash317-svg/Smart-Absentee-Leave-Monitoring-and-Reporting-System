# 🎓 Smart Absentee Leave Monitoring and Reporting System

> An enterprise-grade FastAPI backend with a fully modular architecture for managing student attendance, leave applications, fine enforcement, role-based reporting, and real-time notifications across a college ERP.

---

## 📌 Project Overview

The **Smart Absentee Leave Monitoring and Reporting System** is a full-stack college ERP built to automate the entire lifecycle of student attendance management — from marking absences and submitting leave applications to generating PDF/Excel reports, sending SMS/email alerts, and enforcing progressive fine policies.

| Layer | Technology |
|---|---|
| Backend Framework | FastAPI (Python 3.11) |
| Database | MongoDB (via Motor async driver) |
| Authentication | JWT (Access + Refresh tokens) |
| Password Security | bcrypt hashing |
| Report Generation | ReportLab (PDF), openpyxl (Excel) |
| Notifications | SMTP Email + Twilio SMS |
| Frontend | Vanilla HTML/CSS/JS |
| Testing | pytest + pytest-asyncio |

---

## 🗂️ Project Structure

```
Smart-Absentee-Leave-Monitoring-and-Reporting-System/
│
├── backend/
│   ├── app/
│   │   ├── api/                    ← Route handlers (REST endpoints)
│   │   │   ├── auth.py             ← Login, logout, token refresh
│   │   │   ├── student.py          ← Apply leave, view attendance
│   │   │   ├── coordinator.py      ← Mark absentees, process leaves
│   │   │   ├── hod.py              ← Department reports, leave approval
│   │   │   ├── dean.py             ← Institution-wide analytics
│   │   │   ├── admin.py            ← Audit logs, user management
│   │   │   └── deps.py             ← Shared dependency injectors
│   │   │
│   │   ├── core/                   ← Security and config layer
│   │   │   ├── config.py           ← Environment settings (.env)
│   │   │   ├── jwt.py              ← Token encode/decode/validate
│   │   │   ├── password.py         ← bcrypt hash/verify + strength check
│   │   │   ├── permissions.py      ← Role-based access guards (RBAC)
│   │   │   └── security.py         ← Unified re-export of all security modules
│   │   │
│   │   ├── middleware/             ← Global request pipeline
│   │   │   ├── jwt.py              ← JWT extraction middleware
│   │   │   ├── logging.py          ← Request/response duration logger
│   │   │   ├── cors.py             ← CORS policy (localhost origins)
│   │   │   └── rate_limit.py       ← Sliding-window IP throttle (10 req/min on auth)
│   │   │
│   │   ├── models/                 ← MongoDB document schemas (Pydantic)
│   │   │   ├── user.py             ← User collection schema
│   │   │   ├── student.py          ← Student profile schema
│   │   │   ├── leave.py            ← Leave application schema
│   │   │   ├── fine.py             ← Fine payment schema
│   │   │   └── attendance.py       ← Absentee log schema
│   │   │
│   │   ├── services/               ← Business logic layer
│   │   │   ├── auth_service.py     ← Login verification, token generation
│   │   │   ├── leave_service.py    ← Leave logic + progressive fine rules
│   │   │   ├── email_service.py    ← SMTP email client
│   │   │   ├── sms_service.py      ← Twilio SMS dispatcher
│   │   │   ├── notification_service.py ← Combined in-app + SMS + email alerts
│   │   │   ├── pdf_service.py      ← ReportLab PDF attendance report
│   │   │   ├── excel_service.py    ← openpyxl Excel workbook exporter
│   │   │   └── report_service.py   ← Report compilation orchestrator
│   │   │
│   │   ├── database/
│   │   │   └── connection.py       ← Motor async MongoDB client
│   │   │
│   │   ├── utils/
│   │   │   └── upload.py           ← File upload validator (5MB, pdf/png/jpg)
│   │   │
│   │   └── main.py                 ← App entrypoint (middlewares + routers + static mount)
│   │
│   └── requirements.txt
│
├── stitch_smart_absence_erp/       ← Frontend HTML pages (33 screens)
│   ├── login_attendance_hub/       ← Login page
│   ├── student_dashboard/          ← Student home
│   ├── coordinator_dashboard/      ← Coordinator home
│   ├── hod_dashboard/              ← HOD home
│   ├── dean_dashboard/             ← Dean home
│   ├── apply_for_leave/            ← Student leave application form
│   ├── fine_management/            ← Fine list and payment
│   ├── faculty_attendance_marking/ ← Mark daily attendance
│   ├── notification_center_1/      ← Notification inbox
│   └── ... (33 total pages)
│
└── tests/
    ├── test_auth.py                ← bcrypt, JWT, password strength tests
    ├── test_student.py             ← File upload, leave schema tests
    ├── test_leave.py               ← Progressive fine delay calculation tests
    └── test_reports.py             ← PDF/Excel binary output tests
```

---

## 🔐 Security Design

### Password Security
All passwords are hashed using **bcrypt** — they are never stored in plaintext. Even the developer cannot recover the original password.

```
User creates password
      ↓
bcrypt hashes it → $2b$12$P2U4jM1r6gL2QW0fN...
      ↓
Stored in MongoDB
```

On login:
```
User enters password → bcrypt compare → Match? → Login Success
```

### JWT Authentication
Every protected API call requires a valid JWT access token:
```
Login → Server verifies credentials → Issues JWT → Client stores token
→ Every API request sends token in Authorization header
→ Backend validates on every request (never trust the frontend)
```

### Role-Based Access Control (RBAC)

| Role | Access |
|---|---|
| **Student** | Apply leave, view own attendance history |
| **Coordinator** | Mark absentees, process leave applications |
| **HOD** | Department reports, approve leaves, download spreadsheets |
| **Dean** | Institution-wide comparative reports |
| **Admin** | Full system access, audit logs, user management |

---

## 🚀 Running the Project Locally

### Prerequisites
- Python 3.11+
- MongoDB running on `localhost:27017`

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Set Up Environment Variables
Create a `.env` file inside `backend/`:
```env
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=smart_erp
SECRET_KEY=your-super-secret-jwt-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Twilio SMS (optional)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_FROM_NUMBER=+1234567890
```

### 3. Start the Server
```bash
python -m uvicorn backend.app.main:app --reload
```

### 4. Access
| URL | Description |
|---|---|
| `http://localhost:8000/` | Frontend (Login Page) |
| `http://localhost:8000/docs` | Interactive Swagger API Docs |
| `http://localhost:8000/redoc` | ReDoc API Reference |

---

## 🧪 Running Tests
```bash
python -m pytest
```

All 8 tests pass:
```
tests/test_auth.py      ...   [Password hashing, JWT encode/decode, strength rules]
tests/test_leave.py     .     [Progressive fine delay calculation]
tests/test_reports.py   ..    [PDF binary magic bytes, Excel ZIP archive check]
tests/test_student.py   ..    [File upload constraints, leave schema validation]
======================== 8 passed in ~3s =========================
```

---

## 📋 API Endpoints Summary

### Auth
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/login` | Login with username + password |
| `POST` | `/auth/refresh` | Refresh access token |
| `POST` | `/auth/logout` | Invalidate session |

### Student
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/student/attendance` | View own attendance percentage |
| `POST` | `/student/leave/apply` | Submit a leave application |
| `GET` | `/student/leave/history` | View past leave applications |
| `GET` | `/student/fines` | View outstanding fines |

### Coordinator
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/coordinator/attendance/mark` | Mark daily absentees |
| `GET` | `/coordinator/leaves/pending` | List pending leave requests |
| `PATCH` | `/coordinator/leave/{id}/approve` | Approve/reject a leave |

### HOD
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/hod/dashboard` | Department attendance overview |
| `GET` | `/hod/report/pdf` | Download department PDF report |
| `GET` | `/hod/report/excel` | Download department Excel report |

### Dean
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/dean/dashboard` | Institution-wide attendance stats |
| `GET` | `/dean/report/excel` | Download institution-wide Excel report |

### Admin
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/admin/audit-logs` | View all system audit logs |
| `PATCH` | `/admin/user/{id}/toggle` | Activate/deactivate a user |
| `DELETE` | `/admin/user/{id}` | Soft delete a user |

---

## 🖥️ Frontend Pages (33 Screens)

| Page | Path |
|---|---|
| Login | `login_attendance_hub/` |
| Select Role | `select_your_role/` |
| Student Dashboard | `student_dashboard/` |
| Apply for Leave | `apply_for_leave/` |
| Attendance Precision Monitor | `precision_monitor/` |
| Fine Management | `fine_management/` |
| Fine Payment Receipt | `fine_payment_receipt/` |
| Coordinator Dashboard | `coordinator_dashboard/` |
| Faculty Attendance Marking | `faculty_attendance_marking/` |
| HOD Dashboard | `hod_dashboard/` |
| Dean Dashboard | `dean_dashboard/` |
| Notification Center | `notification_center_1/`, `notification_center_2/` |
| Urgent Attendance Warning | `urgent_attendance_warning_1/`, `urgent_attendance_warning_2/` |
| Student Profile | `student_profile_overview/` |
| Edit Personal Info | `edit_personal_information/` |
| Academic Information | `academic_information/` |
| Admin Activity Logs | `admin_activity_logs/` |
| SMS Log History | `sms_log_history/` |
| System Settings | `system_settings/` |
| Alert Configuration | `alert_configuration/` |
| Forgot Password | `forgot_password/` |
| Reset Password | `reset_password/` |
| Reset Successful | `reset_successful/` |
| Check Your Email | `check_your_email/` |
| Welcome Screen | `welcome_to_attendance_hub/` |
| Ready to Start | `ready_to_start/` |
| Email Report Preview | `email_report_preview/` |
| SMS Template Preview | `sms_template_preview/` |
| Account & Privacy Settings | `account_privacy_settings/` |
| Attendance Hub Monitor | `attendance_hub_precision_monitor/` |
| Sign In to Hub | `sign_in_to_hub/` |

---

## 🔧 Upcoming Work (TODO)

> These are the items that still need to be completed before the system is production-ready.

### 🔴 High Priority

- [ ] **Frontend ↔ Backend Integration** — Wire all 33 HTML pages to the live FastAPI REST endpoints using `fetch()` / `axios`. Currently all frontend pages are static.
- [ ] **Database Seeding** — Create a `seed_data.py` or Mongo script to populate initial data: departments, sample students, coordinator accounts, and HOD/Dean/Admin users so the system can be tested end-to-end.
- [ ] **`.env` File Setup for Production** — Document and finalize all required environment variables. Add a `.env.example` file to the repo.

### 🟡 Medium Priority

- [ ] **Forgot Password / OTP Flow** — The `forgot_password/`, `check_your_email/`, `reset_password/`, and `reset_successful/` pages exist in the frontend but the backend OTP generation and email-based reset flow needs to be implemented in `auth.py`.
- [ ] **Real-time Notifications** — Replace the current polling-based notification system with WebSocket support so students and staff receive alerts instantly without refreshing the page.
- [ ] **Fine Payment Integration** — The fine payment receipt and fine management pages need to be connected to a payment gateway (Razorpay / Stripe) or at least a manual "mark as paid" workflow in the admin panel.
- [ ] **Attendance Auto-Alert Trigger** — Automatically send SMS and email when a student's attendance drops below the threshold (75% or configurable). The `notification_service.py` exists but the trigger logic in `leave_service.py` needs to be connected.
- [ ] **Student Profile Photo Upload** — The profile page allows uploading a photo but the backend endpoint and file storage (local or cloud S3) need to be implemented.

### 🟢 Lower Priority

- [ ] **Admin Dashboard UI** — The `admin_activity_logs/` and `system_settings/` pages need to be connected to the `/admin/*` endpoints.
- [ ] **SMS Template Editor** — The `sms_template_preview/` page allows editing SMS templates. The backend needs a template collection in MongoDB and a CRUD API.
- [ ] **Alert Configuration** — The `alert_configuration/` page needs a backend API to read/write configurable threshold values (e.g., "send warning at 80% attendance").
- [ ] **Export Scheduling** — Allow HODs and Deans to schedule automatic weekly/monthly report emails via a cron job.
- [ ] **Docker Setup** — Add a `Dockerfile` and `docker-compose.yml` so the entire stack (FastAPI + MongoDB) can be launched with a single command.
- [ ] **Production Deployment** — Deploy backend on a cloud server (e.g., Railway, Render, or VPS). Configure a domain and HTTPS.
- [ ] **API Rate Limiting Tuning** — Extend rate limiting beyond auth endpoints to apply to all sensitive write operations.
- [ ] **Pagination on All List Endpoints** — Add `skip` / `limit` parameters to all list endpoints (attendance logs, leaves, students) to handle large datasets.

---

## 👥 Roles and Contributors

| Role | Name |
|---|---|
| Developer | Aayash A |
| Repository | [aayash317-svg](https://github.com/aayash317-svg) |

---

## 📄 License

This project is for academic and educational purposes.
