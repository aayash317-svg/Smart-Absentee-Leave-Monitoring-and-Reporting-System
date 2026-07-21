# 🎓 Smart Absentee Leave Monitoring and Reporting System

> A production-ready, full-stack College ERP built with FastAPI + MongoDB + Vanilla JS — automating the complete lifecycle of student attendance management, leave applications, fine enforcement, PDF/Excel reporting, and multi-channel notifications.

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green)](https://fastapi.tiangolo.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0-brightgreen)](https://mongodb.com)
[![Tests](https://img.shields.io/badge/Tests-8%2F8%20Passing-success)](tests/)
[![License](https://img.shields.io/badge/License-Academic-orange)](LICENSE)

---

## 📌 Project Overview

The **Smart Absentee Leave Monitoring and Reporting System** is a full-stack college ERP that automates the entire lifecycle of student attendance management — from marking daily absences to generating reports and sending low-attendance alerts.

### ✅ What's Fully Built & Working

| Feature | Status |
|---|---|
| JWT Authentication (access + refresh tokens) | ✅ Complete |
| Multi-identifier login (Email / Register No / ID No) | ✅ Complete |
| Role-Based Access Control (5 roles) | ✅ Complete |
| Password hashing (bcrypt, cost=12) | ✅ Complete |
| Brute-force lockout (5 attempts → 5 min ban) | ✅ Complete |
| Last login timestamp tracking | ✅ Complete |
| Token response includes full user object | ✅ Complete |
| All 32 frontend screens wired to live API | ✅ Complete |
| Student leave application + file upload | ✅ Complete |
| Progressive fine calculation | ✅ Complete |
| Coordinator bulk attendance marking | ✅ Complete |
| Department scope enforcement (Coordinator & HOD) | ✅ Complete |
| Tiered attendance notifications (75/70/65/60/50%) | ✅ Complete |
| HOD / Dean leave approval workflow | ✅ Complete |
| PDF + Excel report generation | ✅ Complete |
| In-app + SMS notification delivery logs | ✅ Complete |
| Forgot / Reset / Change password flow | ✅ Complete |
| Admin audit logs, user management | ✅ Complete |
| System settings (thresholds, toggles) | ✅ Complete |
| Database seeded with 10 students + all roles | ✅ Complete |
| 8 automated tests (pytest) | ✅ 8/8 Pass |
| Docker support | ✅ Complete |
| Security headers (CSP, X-Frame, XSS) | ✅ Complete |

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Backend Framework | FastAPI (Python 3.11) |
| Database | MongoDB (via Motor async driver) |
| Authentication | JWT — HS256 (Access + Refresh tokens) + multi-identifier login |
| Password Security | bcrypt (cost factor 12) |
| Report Generation | ReportLab (PDF), openpyxl (Excel) |
| Notifications | SMTP Email + Twilio SMS |
| Frontend | Vanilla HTML / Tailwind CSS / Vanilla JS |
| Shared Frontend Utility | `api.js` — authFetch, toast, logout, role routing |
| Testing | pytest + pytest-asyncio |
| Containerization | Docker + docker-compose |

---

## 🗂️ Project Structure

```
Smart-Absentee-Leave-Monitoring-and-Reporting-System/
│
├── backend/
│   ├── .env                            ← Environment config (never commit secrets!)
│   ├── .env.example                    ← Template for required env vars
│   ├── requirements.txt
│   └── app/
│       ├── main.py                     ← App entrypoint: middlewares + routers + static
│       │
│       ├── api/                        ← REST route handlers
│       │   ├── auth.py                 ← Login, register, forgot/reset/change password
│       │   ├── student.py              ← Profile, attendance, fines, leave, notifications
│       │   ├── coordinator.py          ← Mark absences, process leaves, student list
│       │   ├── hod.py                  ← Dept metrics, leave approval, Excel report
│       │   ├── dean.py                 ← Institution metrics, global Excel report
│       │   ├── admin.py                ← Users, audit logs, settings, SMS log, activity
│       │   ├── dashboard.py            ← Unified role-aware metrics endpoint
│       │   └── deps.py                 ← Shared auth dependencies (get_current_user, RoleChecker)
│       │
│       ├── core/                       ← Security & configuration
│       │   ├── config.py               ← Pydantic settings from .env
│       │   ├── jwt.py                  ← Token create / decode / validate
│       │   ├── password.py             ← bcrypt hash / verify / strength check
│       │   ├── permissions.py          ← RBAC guards (require_dean, require_hod, etc.)
│       │   └── security.py             ← Unified re-export of all security utilities
│       │
│       ├── middleware/
│       │   ├── jwt.py                  ← Security headers + Bearer token extraction
│       │   ├── logging.py              ← Structured request/response logger
│       │   ├── cors.py                 ← CORS allowlist (localhost origins)
│       │   └── rate_limit.py           ← Sliding-window IP throttle on auth routes
│       │
│       ├── models/                     ← MongoDB document schemas (Pydantic)
│       │   ├── user.py
│       │   ├── student.py
│       │   ├── leave.py
│       │   ├── fine.py
│       │   └── attendance.py
│       │
│       ├── repositories/               ← Data access layer (MongoDB queries)
│       │   ├── user.py
│       │   ├── student.py
│       │   ├── absentee.py
│       │   ├── fine.py
│       │   └── leave.py
│       │
│       ├── schemas/                    ← Request / response Pydantic models
│       │   ├── auth.py
│       │   ├── student.py
│       │   └── coordinator.py
│       │
│       ├── services/                   ← Business logic layer
│       │   ├── auth_service.py         ← Login, lockout, token refresh
│       │   ├── leave_service.py        ← Apply / approve / reject + fine calculation
│       │   ├── fine_service.py         ← Progressive delay fine rules
│       │   ├── email_service.py        ← SMTP email sender
│       │   ├── sms_service.py          ← Twilio SMS dispatcher
│       │   ├── notification_service.py ← In-app + email + SMS combined alerts
│       │   ├── pdf_service.py          ← ReportLab PDF attendance report
│       │   ├── excel_service.py        ← openpyxl Excel workbook exporter
│       │   └── report_service.py       ← Report compilation orchestrator
│       │
│       ├── database/
│       │   ├── connection.py           ← Motor async MongoDB client (singleton)
│       │   └── seed.py                 ← Database seeder (10 students + all roles)
│       │
│       └── utils/
│           ├── upload.py               ← File upload validator (5 MB limit, pdf/png/jpg)
│           └── attendance.py           ← Tiered attendance alert engine (75/70/65/60/50%)
│
├── stitch_smart_absence_erp/           ← 32 frontend HTML screens
│   ├── api.js                          ← Shared auth + fetch + toast utility
│   ├── index.html                      ← Hub index (role-aware redirect)
│   ├── login_attendance_hub/
│   ├── student_dashboard/
│   ├── coordinator_dashboard/
│   ├── hod_dashboard/
│   ├── dean_dashboard/
│   ├── apply_for_leave/
│   ├── fine_management/
│   ├── faculty_attendance_marking/
│   ├── notification_center_1/
│   ├── notification_center_2/
│   └── ... (32 total screens)
│
├── tests/
│   ├── test_auth.py                    ← bcrypt, JWT, password strength
│   ├── test_student.py                 ← File upload, leave schema
│   ├── test_leave.py                   ← Progressive fine delay calculation
│   └── test_reports.py                 ← PDF/Excel binary output
│
├── logs/
│   ├── app.log
│   └── error.log
│
├── Dockerfile
├── docker-compose.yml
└── inject_api.py                       ← Automation: wires api.js into all screens
```

---

## 🔐 Security Design

### 1. Password Security
All passwords hashed with **bcrypt (cost=12)** — never stored in plaintext. Constant-time comparison prevents timing attacks.

### 2. JWT Authentication
```
Login → Verify credentials → Issue Access Token (short-lived) + Refresh Token
→ Every API request sends: Authorization: Bearer <token>
→ Backend validates on every request
```

### 3. Multi-Identifier Login
Students and staff can log in using **any** of:
- ✉️ Official Email address (`student@college.edu`)
- 🪪 ID Number (`STU2026001`)
- 📋 Register Number (`REG2026CSE01`)

The backend does a case-insensitive lookup across `users` and `students` collections automatically.

### 4. Brute-Force Protection
```
Wrong password → Increment failedLoginAttempts counter in MongoDB
5 failures     → Account locked for 5 minutes (lockoutUntil timestamp)
Success        → Counter resets to 0, last_login timestamp updated
```

### 5. Department Scope Enforcement
Coordinators and HODs can **only** process attendance and leaves for students within their own department. Cross-department access returns `HTTP 403 Forbidden`.

### 4. Role-Based Access Control (RBAC)

| Role | Permissions |
|---|---|
| **Student** | View own profile, attendance, fines; apply for leave; change password |
| **Coordinator** | Mark absences (bulk), view/process pending leaves for their department |
| **HOD** | Dept metrics, approve/reject leaves, download dept Excel report |
| **Dean** | Institution-wide analytics, global attendance/leave reports |
| **Admin** | Full access: user management, audit logs, system settings, SMS logs |

### 5. Security Headers (every response)
```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'; ...
```

---

## 🚀 Running the Project Locally

### Prerequisites
- Python 3.11+
- MongoDB running on `localhost:27017`

### Step 1 — Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 2 — Configure Environment
The `backend/.env` file is already pre-configured for local development. To change settings, edit `backend/.env.example` and rename it to `.env`.

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=smart_absentee_db_v2
JWT_SECRET=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email (SMTP) — Optional
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Twilio SMS — Optional
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_FROM_NUMBER=+1234567890
```

### Step 3 — Seed the Database
```bash
# Windows PowerShell
$env:PYTHONPATH="d:\collge att"; python -m backend.app.database.seed

# Linux / Mac
PYTHONPATH=. python -m backend.app.database.seed
```

### Step 4 — Start the Server
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 5 — Open the App
| URL | Description |
|---|---|
| `http://127.0.0.1:8000` | Frontend (auto-redirects to login) |
| `http://127.0.0.1:8000/docs` | Interactive Swagger API Docs |
| `http://127.0.0.1:8000/redoc` | ReDoc API Reference |

---

## 🐳 Running with Docker

```bash
docker-compose up --build
```

The full stack (FastAPI + MongoDB) launches with a single command. App available at `http://localhost:8000`.

---

## 🧑‍💻 Demo Login Credentials

> **Password for ALL accounts: `Pass123!`**

### Staff Accounts

| Role | Email |
|---|---|
| Dean | `dean@college.edu` |
| HOD — Computer Science | `hod.cs@college.edu` |
| HOD — Information Technology | `hod.it@college.edu` |
| Coordinator — CS | `coord.cs@college.edu` |
| Coordinator — IT | `coord.it@college.edu` |

### Student Accounts (10 Students)

| # | Name | Email | Dept | Attendance | Fine |
|---|---|---|---|---|---|
| 1 | Arjun Kumar | `student.cs1@college.edu` | CSE | 92% | ₹0 |
| 2 | Priya Sharma | `student.cs2@college.edu` | CSE | 74% | ₹40 |
| 3 | Rohan Patel | `student.cs3@college.edu` | CSE | 88% | ₹0 |
| 4 | Neha Verma | `student.cs4@college.edu` | CSE | 65% | ₹80 |
| 5 | Aayash A | `student.it1@college.edu` | IT | 96% | ₹0 |
| 6 | Mohammed Salman | `student.it2@college.edu` | IT | 60% | ₹120 |
| 7 | Divya Nair | `student.it3@college.edu` | IT | 85% | ₹0 |
| 8 | Karan Singh | `student.it4@college.edu` | IT | 70% | ₹20 |
| 9 | Sneha Reddy | `student.ece1@college.edu` | ECE | 91% | ₹0 |
| 10 | Vikram Mehta | `student.ece2@college.edu` | ECE | 55% | ₹200 |

> 💡 Students 2, 4, 6, 10 have low attendance (below 75%) and are ideal for testing warning/fine/leave workflows.

---

## 🌐 API Endpoints — Complete Reference

### 🔑 Authentication (`/api/auth`)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/auth/login` | ❌ Public | Login via email / register no / ID → returns tokens + user object |
| `POST` | `/api/auth/register` | ❌ Public | Register a new user |
| `POST` | `/api/auth/refresh` | ❌ Public | Renew access token via refresh token |
| `GET` | `/api/auth/me` | ✅ JWT | Get logged-in user info |
| `POST` | `/api/auth/forgot-password` | ❌ Public | Request password reset link |
| `POST` | `/api/auth/reset-password` | ❌ Public | Reset password via token |
| `POST` | `/api/auth/change-password` | ✅ JWT | Change own password (requires current) |

### 👨‍🎓 Student (`/api/student`)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/student/profile` | ✅ Student | Own academic profile |
| `PUT` | `/api/student/profile` | ✅ Student | Update editable profile fields |
| `GET` | `/api/student/attendance` | ✅ Student | Subject-wise attendance records |
| `GET` | `/api/student/fines` | ✅ Student | Outstanding and paid fines |
| `GET` | `/api/student/notifications` | ✅ Student | In-app notification feed |
| `POST` | `/api/student/leave/apply` | ✅ Student | Submit leave (multipart + certificate) |
| `GET` | `/api/student/leave/history` | ✅ Student | Past leave applications |
| `GET` | `/api/student/absentee/history` | ✅ Student | Absentee date records |
| `GET` | `/api/student/fine/history` | ✅ Student | Fine history detail |

### 🏫 Coordinator (`/api/coordinator`)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/coordinator/students` | ✅ Staff | Department student list |
| `POST` | `/api/coordinator/mark-absent` | ✅ Staff | Bulk mark students absent (dept-scoped) |
| `POST` | `/api/coordinator/attendance/mark` | ✅ Staff | Single student absence mark |
| `GET` | `/api/coordinator/leave/pending` | ✅ Staff | Pending leave requests |
| `PUT` | `/api/coordinator/leave/action/{id}` | ✅ Staff | Approve or reject leave |
| `GET` | `/api/coordinator/students/search` | ✅ Staff | Search students by name/regNo |

### 📊 HOD (`/api/hod`)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/hod/metrics` | ✅ HOD | Department attendance metrics |
| `GET` | `/api/hod/report/excel` | ✅ HOD | Download dept Excel report |
| `GET` | `/api/hod/leaves/pending` | ✅ HOD | Pending leaves for approval |
| `POST` | `/api/hod/leaves/approve/{id}` | ✅ HOD | Approve a leave (dept-scoped) |
| `POST` | `/api/hod/leaves/reject/{id}` | ✅ HOD | Reject a leave (dept-scoped) |

### 🎓 Dean (`/api/dean`)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/dean/metrics` | ✅ Dean | Institution-wide stats |
| `GET` | `/api/dean/report/excel` | ✅ Dean | Global Excel attendance report |
| `GET` | `/api/dean/report/excel/department/{id}` | ✅ Dean | Per-dept Excel report |

### ⚙️ Admin (`/api/admin`)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/admin/users` | ✅ Admin | All registered users |
| `POST` | `/api/admin/users/{id}/toggle-status` | ✅ Admin | Activate / deactivate user |
| `DELETE` | `/api/admin/users/{id}` | ✅ Admin | Soft delete user |
| `GET` | `/api/admin/audit-logs` | ✅ Admin | System audit trail |
| `GET` | `/api/admin/activity` | ✅ Admin | Activity log (alias) |
| `GET` | `/api/admin/settings` | ✅ Admin | System configuration |
| `PUT` | `/api/admin/settings` | ✅ Admin | Update system configuration |
| `GET` | `/api/admin/sms-log` | ✅ Admin | SMS delivery history |

### 📈 Dashboard (`/api/dashboard`)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/dashboard/metrics` | ✅ JWT | Role-aware unified metrics |

---

## 🖥️ Frontend Screens (32 Screens)

All screens are served from `/erp/<screen_name>/code.html` and wired to the live backend via `stitch_smart_absence_erp/api.js`.

| Screen | Path | API Connected |
|---|---|---|
| Login | `login_attendance_hub/` | ✅ POST /auth/login |
| Sign In Hub | `sign_in_to_hub/` | ✅ POST /auth/login |
| Forgot Password | `forgot_password/` | ✅ POST /auth/forgot-password |
| Check Email | `check_your_email/` | ✅ Static |
| Reset Password | `reset_password/` | ✅ POST /auth/reset-password |
| Reset Successful | `reset_successful/` | ✅ Auto-redirect |
| Welcome Screen | `welcome_to_attendance_hub/` | ✅ Static |
| Select Role | `select_your_role/` | ✅ Static |
| Ready to Start | `ready_to_start/` | ✅ Auth guard |
| Student Dashboard | `student_dashboard/` | ✅ GET /student/profile |
| Student Profile | `student_profile_overview/` | ✅ GET /student/profile |
| Academic Info | `academic_information/` | ✅ GET /student/profile |
| Attendance Monitor | `attendance_hub_precision_monitor/` | ✅ GET /student/attendance |
| Apply Leave | `apply_for_leave/` | ✅ POST /student/leave/apply |
| Fine Management | `fine_management/` | ✅ GET /student/fines |
| Fine Receipt | `fine_payment_receipt/` | ✅ GET /student/fines |
| Low Attendance 1 | `urgent_attendance_warning_1/` | ✅ GET /student/profile |
| Low Attendance 2 | `urgent_attendance_warning_2/` | ✅ GET /student/profile |
| Edit Profile | `edit_personal_information/` | ✅ PUT /student/profile |
| Privacy Settings | `account_privacy_settings/` | ✅ POST /auth/change-password |
| Notifications 1 | `notification_center_1/` | ✅ GET /student/notifications |
| Notifications 2 | `notification_center_2/` | ✅ GET /student/notifications |
| Coordinator Dashboard | `coordinator_dashboard/` | ✅ GET /coordinator/leave/pending |
| Faculty Marking | `faculty_attendance_marking/` | ✅ GET /coordinator/students + POST /mark-absent |
| HOD Dashboard | `hod_dashboard/` | ✅ GET /hod/metrics |
| Dean Dashboard | `dean_dashboard/` | ✅ GET /dean/metrics |
| Email Report | `email_report_preview/` | ✅ GET /hod/report/excel |
| SMS Log | `sms_log_history/` | ✅ GET /admin/sms-log |
| SMS Template | `sms_template_preview/` | ✅ Static |
| Alert Config | `alert_configuration/` | ✅ GET/PUT /admin/settings |
| Activity Logs | `admin_activity_logs/` | ✅ GET /admin/activity |
| System Settings | `system_settings/` | ✅ GET/PUT /admin/settings |

---

## 🧪 Running Tests

```bash
# Windows
$env:PYTHONPATH="d:\collge att"; python -m pytest -v

# Linux / Mac
PYTHONPATH=. python -m pytest -v
```

**All 8 tests pass:**
```
tests/test_auth.py::test_password_hashing        PASSED
tests/test_auth.py::test_password_strength       PASSED
tests/test_auth.py::test_jwt_tokens              PASSED
tests/test_leave.py::test_calculate_delay_fine   PASSED
tests/test_reports.py::test_pdf_report_generation PASSED
tests/test_reports.py::test_excel_report_generation PASSED
tests/test_student.py::test_file_upload_validation PASSED
tests/test_student.py::test_leave_apply_schema   PASSED
======================== 8 passed in ~3s ============================
```

---

## 🔔 Tiered Attendance Notification System

When a student's attendance drops through any threshold, automatic notifications are triggered:

| Threshold | Alert Type | Recipient |
|---|---|---|
| Below **75%** | Low Attendance Warning | Student |
| Below **70%** | Parent Alert (logged) | Student |
| Below **65%** | Coordinator Notification | Coordinator of dept |
| Below **60%** | Defaulter List Alert | Student |
| Below **50%** | Critical HOD Alert | HOD of dept |

---

## 🔧 Fine Policy Rules

| Days Delay | Fine Amount |
|---|---|
| 0 days | ₹0 |
| 1 day | ₹10 |
| 2 days | ₹20 |
| 3 days | ₹40 |
| 4 days | ₹80 |
| 5+ days | ₹80 + ₹20 per additional day |

---

## 📄 License

This project is built for academic and educational purposes.

---

## 👤 Developer

**Aayash** — Full Stack Developer  
GitHub: [@aayash317-svg](https://github.com/aayash317-svg)  
Repo: [Smart-Absentee-Leave-Monitoring-and-Reporting-System](https://github.com/aayash317-svg/Smart-Absentee-Leave-Monitoring-and-Reporting-System)
