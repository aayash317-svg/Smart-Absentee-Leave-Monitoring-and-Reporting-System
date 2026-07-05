import requests
import jwt
import datetime
import time

BASE = "http://127.0.0.1:8000"
SECRET = "super-secret-attendance-hub-key-2026"
passed = 0
failed = 0

def check(label, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print("  [PASS] " + label)
    else:
        failed += 1
        print("  [FAIL] " + label)
    if detail:
        print("         " + str(detail))

def section(title):
    print("")
    print("=" * 55)
    print("  " + title)
    print("=" * 55)

# ── Helper: craft a valid JWT directly (bypasses login) ──────
def make_token(user_id="000000000000000000000001", role="Dean"):
    payload = {
        "sub": user_id,
        "role": role,
        "email": "test@test.com",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")

# ═══════════════════════════════════════════════════════
# TEST 1 — Server Health
# ═══════════════════════════════════════════════════════
section("TEST 1 — Server Health")
try:
    r = requests.get(BASE + "/", timeout=5, allow_redirects=False)
    check("Server is reachable", r.status_code in [200, 302, 307], "Status: " + str(r.status_code))
except Exception as e:
    check("Server is reachable", False, str(e))

# ═══════════════════════════════════════════════════════
# TEST 2 — Security Response Headers
# ═══════════════════════════════════════════════════════
section("TEST 2 — Security Response Headers")
r = requests.get(BASE + "/erp/login_attendance_hub/code.html", allow_redirects=True)
h = r.headers
check("X-Content-Type-Options: nosniff",       h.get("x-content-type-options","").lower() == "nosniff",         "Got: " + h.get("x-content-type-options","MISSING"))
check("X-Frame-Options: DENY",                  h.get("x-frame-options","").upper() == "DENY",                   "Got: " + h.get("x-frame-options","MISSING"))
check("X-XSS-Protection header present",        "x-xss-protection" in h,                                         "Got: " + h.get("x-xss-protection","MISSING"))
check("Referrer-Policy header present",         "referrer-policy" in h,                                          "Got: " + h.get("referrer-policy","MISSING"))
check("Content-Security-Policy header present", "content-security-policy" in h,                                  "Got: " + h.get("content-security-policy","MISSING")[:55])

# ═══════════════════════════════════════════════════════
# TEST 3 — CORS Restriction
# ═══════════════════════════════════════════════════════
section("TEST 3 — CORS Origin Restriction")
evil = "http://evil-attacker.com"
r = requests.options(BASE + "/api/auth/login",
    headers={"Origin": evil, "Access-Control-Request-Method": "POST"})
acao = r.headers.get("Access-Control-Allow-Origin", "")
check("Evil origin blocked by CORS",   evil not in acao and acao != "*", "Header: '" + acao + "'")

good = "http://localhost:8000"
r2 = requests.options(BASE + "/api/auth/login",
    headers={"Origin": good, "Access-Control-Request-Method": "POST"})
acao2 = r2.headers.get("Access-Control-Allow-Origin", "")
check("Localhost origin allowed",      good in acao2 or acao2 == good,  "Header: '" + acao2 + "'")

# ═══════════════════════════════════════════════════════
# TEST 4 — Input Validation
# ═══════════════════════════════════════════════════════
section("TEST 4 — Input Validation on Login")
r = requests.post(BASE + "/api/auth/login", json={"email": "t@t.com", "password": "abc"}, headers={"Content-Type": "application/json"})
check("Short password (<6 chars) -> 422",   r.status_code == 422, "Status: " + str(r.status_code))

r = requests.post(BASE + "/api/auth/login", json={"email": "t@t.com", "password": "A"*200}, headers={"Content-Type": "application/json"})
check("Oversized password (200 chars) -> 422", r.status_code == 422, "Status: " + str(r.status_code))

r = requests.post(BASE + "/api/auth/login", json={"email": "notanemail", "password": "pass1234"}, headers={"Content-Type": "application/json"})
check("Invalid email format -> 422",        r.status_code == 422, "Status: " + str(r.status_code))

r = requests.post(BASE + "/api/auth/login", json={"email": "t@t.com", "password": ""}, headers={"Content-Type": "application/json"})
check("Empty password -> 422",              r.status_code == 422, "Status: " + str(r.status_code))

# ═══════════════════════════════════════════════════════
# TEST 5 — Brute-Force Rate Limiting
# ═══════════════════════════════════════════════════════
section("TEST 5 — Brute-Force Rate Limiting")
print("  Sending 6 wrong login attempts to a fresh email...")
blocked = False
last_status = None
for i in range(6):
    r = requests.post(BASE + "/api/auth/login",
        json={"email": "brutetest" + str(i) + "@nowhere.io", "password": "wrongpass1"},
        headers={"Content-Type": "application/json"})
    last_status = r.status_code
    print("  Attempt " + str(i+1) + ": HTTP " + str(r.status_code))
    if r.status_code == 429:
        blocked = True
        break

check("Rate limiter fires HTTP 429 after 5 failed attempts", blocked, "Last status: " + str(last_status))
if blocked:
    body = r.json()
    check("429 message mentions wait time", "wait" in body.get("detail","").lower(), "Msg: " + body.get("detail",""))

# ═══════════════════════════════════════════════════════
# TEST 6 — Email Enumeration / Timing Attack
# ═══════════════════════════════════════════════════════
section("TEST 6 — Email Enumeration Prevention")
print("  Comparing bcrypt timing for existing vs non-existing email...")
time.sleep(2)

t1 = time.time()
requests.post(BASE + "/api/auth/login",
    json={"email": "dean@university.edu", "password": "wrongpassword1"},
    headers={"Content-Type": "application/json"})
t_exist = time.time() - t1

t2 = time.time()
requests.post(BASE + "/api/auth/login",
    json={"email": "xyz_fake_99999@noreply.io", "password": "wrongpassword1"},
    headers={"Content-Type": "application/json"})
t_noexist = time.time() - t2

diff = abs(t_exist - t_noexist) * 1000
print("  Existing email:     " + str(round(t_exist*1000)) + "ms")
print("  Non-existing email: " + str(round(t_noexist*1000)) + "ms")
print("  Difference:         " + str(round(diff)) + "ms")
check("Timing difference < 500ms (constant-time bcrypt check)", diff < 500, "Diff: " + str(round(diff)) + "ms")

# ═══════════════════════════════════════════════════════
# TEST 7 — All Protected Routes Require Token
# ═══════════════════════════════════════════════════════
section("TEST 7 — Protected Routes Require JWT Token")
routes = [
    ("GET",  "/api/auth/me"),
    ("GET",  "/api/dashboard/metrics"),
    ("GET",  "/api/leave/history"),
    ("POST", "/api/leave/apply"),
    ("GET",  "/api/fines/student"),
    ("GET",  "/api/fines/rules"),
    ("GET",  "/api/attendance/notifications"),
    ("POST", "/api/attendance/mark"),
]
for method, path in routes:
    r = requests.request(method, BASE + path)
    check(method + " " + path + " -> 401 without token", r.status_code == 401, "Got: " + str(r.status_code))

# ═══════════════════════════════════════════════════════
# TEST 8 — JWT Tampering Detection
# ═══════════════════════════════════════════════════════
section("TEST 8 — JWT Tampering & Forgery Detection")
fake = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJoYWNrZXIiLCJyb2xlIjoiRGVhbiJ9.FAKESIGNATURE"
r = requests.get(BASE + "/api/auth/me", headers={"Authorization": "Bearer " + fake})
check("Tampered JWT rejected -> 401",    r.status_code == 401, "Detail: " + r.json().get("detail",""))

r = requests.get(BASE + "/api/auth/me", headers={"Authorization": "Bearer notajwtatall"})
check("Malformed token rejected -> 401", r.status_code == 401, "Status: " + str(r.status_code))

r = requests.get(BASE + "/api/auth/me", headers={"Authorization": "Basic dXNlcjpwYXNz"})
check("Wrong auth scheme (Basic) -> 401", r.status_code == 401, "Status: " + str(r.status_code))

expired_payload = {
    "sub": "000000000000000000000001",
    "role": "Dean",
    "exp": datetime.datetime.utcnow() - datetime.timedelta(hours=2)
}
expired_token = jwt.encode(expired_payload, SECRET, algorithm="HS256")
r = requests.get(BASE + "/api/auth/me", headers={"Authorization": "Bearer " + expired_token})
check("Expired token rejected -> 401", r.status_code == 401, "Detail: " + r.json().get("detail",""))

# ═══════════════════════════════════════════════════════
# TEST 9 — Malformed ObjectId (No 500 Crash)
# ═══════════════════════════════════════════════════════
section("TEST 9 — Malformed ObjectId: No 500 Crash")
tok = make_token()
ah = {"Authorization": "Bearer " + tok}

r = requests.get(BASE + "/api/fines/receipt/NOTANOBJECTID", headers=ah)
check("Bad ObjectId on receipt -> 400/404 not 500", r.status_code in [400,404], "Status: " + str(r.status_code) + " | " + r.text[:60])

r = requests.post(BASE + "/api/fines/pay/BADID999",
    json={"paymentMode": "Online"},
    headers={**ah, "Content-Type": "application/json"})
check("Bad ObjectId on pay -> 400/404 not 500", r.status_code in [400,404], "Status: " + str(r.status_code) + " | " + r.text[:60])

r = requests.put(BASE + "/api/leave/approve/INVALIDID", headers=ah)
check("Bad ObjectId on approve -> 400/404 not 500", r.status_code in [400,404], "Status: " + str(r.status_code) + " | " + r.text[:60])

r = requests.put(BASE + "/api/attendance/notifications/read/BADOBJECTID", headers=ah)
check("Bad ObjectId on notif read -> 400/404 not 500", r.status_code in [400,404], "Status: " + str(r.status_code) + " | " + r.text[:60])

# ═══════════════════════════════════════════════════════
# TEST 10 — Fine Ownership (Authorization)
# ═══════════════════════════════════════════════════════
section("TEST 10 — Fine Payment Ownership Check")
student_token = make_token(user_id="000000000000000000000002", role="Student")
sh = {"Authorization": "Bearer " + student_token, "Content-Type": "application/json"}
r = requests.post(BASE + "/api/fines/pay/000000000000000000000099",
    json={"paymentMode": "Online"}, headers=sh)
check("Student cannot pay another student fine -> 403/404", r.status_code in [403,404], "Status: " + str(r.status_code))

# ═══════════════════════════════════════════════════════
# FINAL SUMMARY
# ═══════════════════════════════════════════════════════
total = passed + failed
pct = int(passed / total * 100) if total else 0
print("")
print("=" * 55)
print("  SECURITY TEST RESULTS")
print("=" * 55)
print("  Passed : " + str(passed) + " / " + str(total))
print("  Failed : " + str(failed) + " / " + str(total))
print("  Score  : " + str(pct) + "%")
if pct == 100:
    print("  STATUS : ALL SECURITY TESTS PASSED!")
else:
    print("  STATUS : " + str(failed) + " TEST(S) NEED ATTENTION")
print("")
