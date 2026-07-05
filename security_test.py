"""
Security Feature Test Suite
Tests all security fixes applied to the Smart Student Absentees & Attendance ERP.
Run AFTER the server is started: python -m backend.main (in d:\collge att)
"""

import requests
import time
import json

BASE = "http://127.0.0.1:8000"

PASS = "\033[92m[PASS]\033[0m"
FAIL = "\033[91m[FAIL]\033[0m"
INFO = "\033[94m[INFO]\033[0m"
HEAD = "\033[1;95m"
END  = "\033[0m"

results = {"passed": 0, "failed": 0}

def check(label, condition, detail=""):
    if condition:
        results["passed"] += 1
        print(f"  {PASS} {label}")
        if detail: print(f"         {detail}")
    else:
        results["failed"] += 1
        print(f"  {FAIL} {label}")
        if detail: print(f"         {detail}")

def section(title):
    print(f"\n{HEAD}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{END}")

# ─────────────────────────────────────────────
# Test 1 – Server is Running
# ─────────────────────────────────────────────
section("TEST 1 — Server Health")
try:
    r = requests.get(BASE + "/", timeout=5, allow_redirects=False)
    check("Server is reachable", r.status_code in [200, 302, 307], f"Status: {r.status_code}")
except Exception as e:
    check("Server is reachable", False, f"Error: {e}")
    print("\n  [ABORT] Cannot reach server. Start it first:\n  python -m uvicorn backend.main:app --port 8000\n")
    exit(1)

# ─────────────────────────────────────────────
# Test 2 – Security HTTP Headers
# ─────────────────────────────────────────────
section("TEST 2 — Security Response Headers")
r = requests.get(BASE + "/erp/login_attendance_hub/code.html", allow_redirects=True)
headers = r.headers

check("X-Content-Type-Options: nosniff",
      headers.get("x-content-type-options","").lower() == "nosniff",
      f"Got: {headers.get('x-content-type-options','MISSING')}")

check("X-Frame-Options: DENY (clickjacking protection)",
      headers.get("x-frame-options","").upper() == "DENY",
      f"Got: {headers.get('x-frame-options','MISSING')}")

check("X-XSS-Protection header present",
      "x-xss-protection" in headers,
      f"Got: {headers.get('x-xss-protection','MISSING')}")

check("Referrer-Policy header present",
      "referrer-policy" in headers,
      f"Got: {headers.get('referrer-policy','MISSING')}")

check("Content-Security-Policy header present",
      "content-security-policy" in headers,
      f"Got: {headers.get('content-security-policy','MISSING')[:60]}...")

# ─────────────────────────────────────────────
# Test 3 – CORS Is Restricted (no wildcard *)
# ─────────────────────────────────────────────
section("TEST 3 — CORS Origin Restriction")
evil_origin = "http://evil-attacker.com"
r = requests.options(BASE + "/api/auth/login",
                     headers={"Origin": evil_origin,
                               "Access-Control-Request-Method": "POST"})
acao = r.headers.get("Access-Control-Allow-Origin", "")
check("Evil origin is NOT allowed by CORS",
      evil_origin not in acao and acao != "*",
      f"Allow-Origin header: '{acao}'")

# Allowed origin should work
good_origin = "http://localhost:8000"
r2 = requests.options(BASE + "/api/auth/login",
                      headers={"Origin": good_origin,
                                "Access-Control-Request-Method": "POST"})
acao2 = r2.headers.get("Access-Control-Allow-Origin", "")
check("Localhost origin IS allowed",
      good_origin in acao2 or acao2 == good_origin,
      f"Allow-Origin header: '{acao2}'")

# ─────────────────────────────────────────────
# Test 4 – Input Validation (Login)
# ─────────────────────────────────────────────
section("TEST 4 — Input Validation")

# Too-short password
r = requests.post(BASE + "/api/auth/login",
                  json={"email": "test@test.com", "password": "abc"},
                  headers={"Content-Type": "application/json"})
check("Short password (<6 chars) rejected with 422",
      r.status_code == 422,
      f"Status: {r.status_code}")

# Oversized password (>128 chars)
r = requests.post(BASE + "/api/auth/login",
                  json={"email": "test@test.com", "password": "A" * 200},
                  headers={"Content-Type": "application/json"})
check("Oversized password (200 chars) rejected with 422",
      r.status_code == 422,
      f"Status: {r.status_code}")

# Invalid email format
r = requests.post(BASE + "/api/auth/login",
                  json={"email": "notanemail", "password": "password123"},
                  headers={"Content-Type": "application/json"})
check("Invalid email format rejected with 422",
      r.status_code == 422,
      f"Status: {r.status_code}")

# ─────────────────────────────────────────────
# Test 5 – Brute Force Rate Limiting
# ─────────────────────────────────────────────
section("TEST 5 — Brute-Force Rate Limiting (5 attempts → blocked)")
print(f"  {INFO} Sending 6 wrong login attempts... (this may take a few seconds)")

last_status = None
blocked = False
for i in range(6):
    r = requests.post(BASE + "/api/auth/login",
                      json={"email": "bruteforce@test.com", "password": "wrongpass1"},
                      headers={"Content-Type": "application/json"})
    last_status = r.status_code
    print(f"         Attempt {i+1}: HTTP {r.status_code}")
    if r.status_code == 429:
        blocked = True
        break

check("Brute force blocked with HTTP 429 after 5 failed attempts",
      blocked,
      f"Last status: {last_status}")

if blocked:
    body = r.json()
    check("429 response includes rate limit message",
          "Too many failed" in body.get("detail", ""),
          f"Message: {body.get('detail','')}")

# ─────────────────────────────────────────────
# Test 6 – Email Enumeration Prevention
# ─────────────────────────────────────────────
section("TEST 6 — Email Enumeration Prevention (Timing Attack)")
print(f"  {INFO} Comparing response times for existing vs non-existing email...")

# Wait for rate limit to partially reset (or use fresh email pattern)
time.sleep(2)

# Measure response time for a likely-existing email
t1 = time.time()
requests.post(BASE + "/api/auth/login",
              json={"email": "dean@university.edu", "password": "wrongpassword1"},
              headers={"Content-Type": "application/json"})
t_existing = time.time() - t1

# Measure response time for a definitely-non-existing email
t2 = time.time()
requests.post(BASE + "/api/auth/login",
              json={"email": "totally_fake_xyz_99@noreply.io", "password": "wrongpassword1"},
              headers={"Content-Type": "application/json"})
t_nonexisting = time.time() - t2

diff_ms = abs(t_existing - t_nonexisting) * 1000
print(f"         Existing email time:     {t_existing*1000:.0f}ms")
print(f"         Non-existing email time: {t_nonexisting*1000:.0f}ms")
print(f"         Difference:              {diff_ms:.0f}ms")

check("Timing difference < 500ms (constant-time check prevents enumeration)",
      diff_ms < 500,
      f"Difference: {diff_ms:.0f}ms")

# ─────────────────────────────────────────────
# Test 7 – Authentication: Protected Routes
# ─────────────────────────────────────────────
section("TEST 7 — Authentication: All Protected Routes Require Token")

routes_to_check = [
    ("GET",  "/api/auth/me"),
    ("GET",  "/api/dashboard/metrics"),
    ("GET",  "/api/leave/history"),
    ("POST", "/api/leave/apply"),
    ("GET",  "/api/fines/student"),
    ("GET",  "/api/attendance/notifications"),
]

for method, path in routes_to_check:
    r = requests.request(method, BASE + path)
    check(f"{method} {path} → 401 without token",
          r.status_code == 401,
          f"Got: {r.status_code}")

# ─────────────────────────────────────────────
# Test 8 – Invalid / Tampered JWT
# ─────────────────────────────────────────────
section("TEST 8 — JWT Tampering Detection")

fake_token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJoYWNrZXIiLCJyb2xlIjoiRGVhbiJ9.FAKESIGNATURE"
r = requests.get(BASE + "/api/auth/me",
                 headers={"Authorization": f"Bearer {fake_token}"})
check("Tampered/fake JWT rejected with 401",
      r.status_code == 401,
      f"Status: {r.status_code}, Detail: {r.json().get('detail','')}")

# Malformed (no signature section)
r2 = requests.get(BASE + "/api/auth/me",
                  headers={"Authorization": "Bearer notajwtatall"})
check("Malformed token rejected with 401",
      r2.status_code == 401,
      f"Status: {r2.status_code}")

# No token at all
r3 = requests.get(BASE + "/api/auth/me",
                  headers={"Authorization": "NotBearer sometoken"})
check("Wrong token type (not Bearer) rejected with 401",
      r3.status_code == 401,
      f"Status: {r3.status_code}")

# ─────────────────────────────────────────────
# Test 9 – Invalid ObjectId (no crash)
# ─────────────────────────────────────────────
section("TEST 9 — Malformed ObjectId: No 500 Crash")

# Need a valid token first – attempt login with seeded user
print(f"  {INFO} Logging in as dean to get a valid token...")
r = requests.post(BASE + "/api/auth/login",
                  json={"email": "dean@university.edu", "password": "password123"},
                  headers={"Content-Type": "application/json"})

if r.status_code == 200:
    token = r.json()["access_token"]
    auth_hdr = {"Authorization": f"Bearer {token}"}
    print(f"  {INFO} Login successful, token acquired.")

    r2 = requests.get(BASE + "/api/fines/receipt/NOTANOBJECTID", headers=auth_hdr)
    check("Invalid ObjectId path param returns 400, NOT 500",
          r2.status_code in [400, 404],
          f"Status: {r2.status_code}, Detail: {r2.json().get('detail','')}")

    r3 = requests.post(BASE + "/api/fines/pay/BADID",
                       json={"paymentMode": "Online"},
                       headers={**auth_hdr, "Content-Type": "application/json"})
    check("Invalid ObjectId on pay endpoint returns 400/404, NOT 500",
          r3.status_code in [400, 404],
          f"Status: {r3.status_code}")

else:
    print(f"  {INFO} Could not login (DB may not be seeded). Skipping ObjectId tests. Status: {r.status_code}")

# ─────────────────────────────────────────────
# FINAL RESULTS
# ─────────────────────────────────────────────
total = results["passed"] + results["failed"]
pct   = int(results["passed"] / total * 100) if total else 0

print(f"\n{HEAD}{'='*60}")
print(f"  SECURITY TEST RESULTS")
print(f"{'='*60}{END}")
print(f"  Passed : \033[92m{results['passed']}\033[0m / {total}")
print(f"  Failed : \033[91m{results['failed']}\033[0m / {total}")
print(f"  Score  : {pct}%")
print()

