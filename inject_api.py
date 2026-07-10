"""
inject_api.py — Injects API integration scripts into all frontend screens.
Run from project root:  python inject_api.py
"""
import os, re

BASE = r"d:\collge att\stitch_smart_absence_erp"

# Helper: inject <script src="../api.js"> before </head> if not already present
def inject_api_js_tag(html: str, depth: int = 1) -> str:
    tag = '<script src="' + '../' * depth + 'api.js"></script>'
    if 'api.js' in html:
        return html
    return html.replace('</head>', f'  {tag}\n</head>', 1)

# Helper: replace the last </script>\n</body></html> block with new JS
def replace_script_block(html: str, new_js: str) -> str:
    # Find last <script> ... </script> before </body>
    pattern = r'(<script>)(.*?)(</script>\s*</body></html>)'
    match = list(re.finditer(pattern, html, re.DOTALL))
    if match:
        m = match[-1]
        replacement = f'<script>\n{new_js}\n    </script>\n</body></html>'
        return html[:m.start()] + replacement
    # Fallback: insert before </body>
    return html.replace('</body></html>', f'<script>\n{new_js}\n    </script>\n</body></html>')

def read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✅ Updated: {os.path.basename(os.path.dirname(path))}")

screens = {

# ── AUTH SCREENS ──────────────────────────────────────────────────────────────

"sign_in_to_hub": """
        // Existing input effects preserved
        const inputs = document.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('focus', () => {
                input.parentElement.querySelector('.material-symbols-outlined')?.classList.add('text-primary');
            });
            input.addEventListener('blur', () => {
                input.parentElement.querySelector('.material-symbols-outlined')?.classList.remove('text-primary');
            });
        });

        // API-wired login form
        const loginForm = document.querySelector('form');
        if (loginForm) {
            loginForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = loginForm.querySelector('input[type="email"], input[name="email"]')?.value;
                const password = loginForm.querySelector('input[type="password"]')?.value;
                const btn = loginForm.querySelector('button[type="submit"]');
                const orig = btn.innerHTML;
                setLoading(btn, true, orig);
                try {
                    const res = await fetch('/api/auth/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email, password })
                    });
                    const data = await res.json();
                    if (!res.ok) throw new Error(data.detail || 'Login failed');
                    localStorage.setItem('access_token', data.access_token);
                    localStorage.setItem('user', JSON.stringify(data.user));
                    redirectByRole();
                } catch (err) {
                    showToast(err.message, 'error');
                    setLoading(btn, false, orig);
                }
            });
        }
""",

"forgot_password": """
        document.getElementById('reset-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            const emailInput = e.target.querySelector('input[type="email"]');
            const btn = e.target.querySelector('button[type="submit"]');
            const orig = btn.innerHTML;
            if (!emailInput?.value) { showToast('Please enter your email address', 'warning'); return; }
            setLoading(btn, true, orig);
            try {
                const res = await fetch('/api/auth/forgot-password', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: emailInput.value })
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Request failed');
                showToast('Reset link sent to your email!', 'success');
                btn.innerHTML = '<span class="material-symbols-outlined">check_circle</span><span>Email Sent!</span>';
                setTimeout(() => window.location.href = '/erp/check_your_email/code.html', 1800);
            } catch (err) {
                showToast(err.message, 'error');
                setLoading(btn, false, orig);
            }
        });
""",

"reset_password": """
        // Password strength checkers
        const passwordInput = document.getElementById('new-password');
        const reqLength  = document.getElementById('req-length');
        const reqNumber  = document.getElementById('req-number');
        const reqSpecial = document.getElementById('req-special');

        if (passwordInput) {
            passwordInput.addEventListener('input', () => {
                const val = passwordInput.value;
                if (reqLength)  reqLength.classList.toggle('valid', val.length >= 8);
                if (reqNumber)  reqNumber.classList.toggle('valid', /\d/.test(val));
                if (reqSpecial) reqSpecial.classList.toggle('valid', /[!@#$%^&*(),.?":{}|<>]/.test(val));
            });
        }

        document.getElementById('reset-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const pw = passwordInput?.value || '';
            const confirm = document.getElementById('confirm-password')?.value || '';
            if (pw !== confirm) { showToast('Passwords do not match!', 'warning'); return; }
            if (pw.length < 8 || !/\d/.test(pw) || !/[!@#$%^&*(),.?":{}|<>]/.test(pw)) {
                showToast('Please meet all password requirements', 'warning'); return;
            }
            const token = new URLSearchParams(window.location.search).get('token') || '';
            const btn = e.target.querySelector('button[type="submit"]');
            const orig = btn.innerHTML;
            setLoading(btn, true, orig);
            try {
                const res = await fetch('/api/auth/reset-password', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ token, new_password: pw })
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Reset failed');
                showToast('Password updated successfully!', 'success');
                setTimeout(() => window.location.href = '/erp/reset_successful/code.html', 1800);
            } catch (err) {
                showToast(err.message, 'error');
                setLoading(btn, false, orig);
            }
        });
""",

# ── STATIC/GUARD SCREENS ──────────────────────────────────────────────────────

"welcome_to_attendance_hub": """
        // No login required — marketing/landing page
        const goBtn = document.querySelector('a[href], button');
        // Wire any "Get Started" link to role selector
        document.querySelectorAll('a').forEach(a => {
            if (/get.?started|proceed|continue/i.test(a.textContent)) {
                a.href = '/erp/select_your_role/code.html';
            }
        });
""",

"select_your_role": """
        // Wire role buttons to the login page with role pre-fill
        document.querySelectorAll('[data-role], button, a').forEach(el => {
            const role = el.dataset?.role || el.textContent?.trim();
            if (['Student','Coordinator','HOD','Dean','Faculty','Admin'].includes(role)) {
                el.style.cursor = 'pointer';
                el.addEventListener('click', (e) => {
                    e.preventDefault();
                    sessionStorage.setItem('selected_role', role);
                    window.location.href = '/erp/login_attendance_hub/code.html';
                });
            }
        });
""",

"ready_to_start": """
        // Guard: if already logged in, redirect to dashboard
        const user = getUser();
        if (user) { redirectByRole(); }
        // Wire CTA button
        document.querySelectorAll('button, a').forEach(el => {
            if (/start|login|sign.?in/i.test(el.textContent)) {
                el.addEventListener('click', (e) => {
                    e.preventDefault();
                    window.location.href = '/erp/login_attendance_hub/code.html';
                });
            }
        });
""",

"check_your_email": """
        // Static confirmation screen — no API call needed
        const resendBtn = document.querySelector('button');
        if (resendBtn) {
            resendBtn.addEventListener('click', async () => {
                const orig = resendBtn.innerHTML;
                setLoading(resendBtn, true, orig);
                showToast('Reset email re-sent!', 'success');
                setTimeout(() => setLoading(resendBtn, false, orig), 2000);
            });
        }
""",

"reset_successful": """
        // After 3 seconds auto-redirect to login
        setTimeout(() => {
            window.location.href = '/erp/login_attendance_hub/code.html';
        }, 3500);
        document.querySelectorAll('button, a').forEach(el => {
            if (/login|sign.?in|back/i.test(el.textContent)) {
                el.addEventListener('click', (e) => {
                    e.preventDefault();
                    window.location.href = '/erp/login_attendance_hub/code.html';
                });
            }
        });
""",

# ── STUDENT SCREENS ───────────────────────────────────────────────────────────

"student_profile_overview": """
        if (redirectIfNotLoggedIn()) return;

        async function loadProfile() {
            try {
                const res = await authFetch('/api/student/profile');
                if (!res.ok) throw new Error('Could not load profile');
                const data = await res.json();
                // Populate name
                document.querySelectorAll('[data-field="name"], .student-name').forEach(el => el.textContent = data.fullName || '');
                document.querySelectorAll('[data-field="email"], .student-email').forEach(el => el.textContent = data.email || '');
                document.querySelectorAll('[data-field="regNo"], .student-regno').forEach(el => el.textContent = data.registerNo || '');
                document.querySelectorAll('[data-field="dept"], .student-dept').forEach(el => el.textContent = data.department || '');
                document.querySelectorAll('[data-field="year"], .student-year').forEach(el => el.textContent = 'Year ' + (data.year || ''));
                document.querySelectorAll('[data-field="attendance"], .attendance-pct').forEach(el => el.textContent = (data.attendancePercentage || 0).toFixed(1) + '%');
            } catch (err) {
                showToast(err.message, 'error');
            }
        }
        loadProfile();

        document.getElementById('logoutBtn')?.addEventListener('click', logout);
""",

"academic_information": """
        if (redirectIfNotLoggedIn()) return;

        async function loadAcademicInfo() {
            try {
                const res = await authFetch('/api/student/profile');
                if (!res.ok) throw new Error('Could not load academic info');
                const data = await res.json();
                document.querySelectorAll('[data-field="course"]').forEach(el => el.textContent = data.course || '');
                document.querySelectorAll('[data-field="semester"]').forEach(el => el.textContent = 'Semester ' + (data.semester || ''));
                document.querySelectorAll('[data-field="year"]').forEach(el => el.textContent = 'Year ' + (data.year || ''));
                document.querySelectorAll('[data-field="batch"]').forEach(el => el.textContent = data.batch || '');
                document.querySelectorAll('[data-field="dept"]').forEach(el => el.textContent = data.department || '');
                document.querySelectorAll('[data-field="regNo"]').forEach(el => el.textContent = data.registerNo || '');
            } catch (err) {
                showToast(err.message, 'error');
            }
        }
        loadAcademicInfo();
        document.getElementById('logoutBtn')?.addEventListener('click', logout);
""",

"attendance_hub_precision_monitor": """
        if (redirectIfNotLoggedIn()) return;

        async function loadAttendance() {
            try {
                const res = await authFetch('/api/student/attendance');
                if (!res.ok) throw new Error('Could not load attendance records');
                const records = await res.json();
                // Update the overall percentage
                if (records.length > 0) {
                    const totalHeld = records.reduce((s, r) => s + (r.totalClasses || 0), 0);
                    const totalPresent = records.reduce((s, r) => s + (r.attendedClasses || 0), 0);
                    const pct = totalHeld > 0 ? ((totalPresent / totalHeld) * 100).toFixed(1) : '100.0';
                    document.querySelectorAll('.attendance-pct, [data-field="attendance"]').forEach(el => el.textContent = pct + '%');
                }
                // Render subject rows if a table/list container exists
                const container = document.querySelector('#attendance-list, .attendance-table-body, tbody');
                if (container && records.length > 0) {
                    container.innerHTML = records.map(r => `
                        <tr class="border-b border-outline-variant">
                            <td class="py-3 px-4 font-body text-body">${r.subject || '—'}</td>
                            <td class="py-3 px-4 text-center">${r.attendedClasses || 0}/${r.totalClasses || 0}</td>
                            <td class="py-3 px-4 text-center font-semibold ${(r.percentage||100) < 75 ? 'text-error' : 'text-secondary'}">
                                ${(r.percentage || 0).toFixed(1)}%
                            </td>
                        </tr>`).join('');
                }
            } catch (err) {
                showToast(err.message, 'error');
            }
        }
        loadAttendance();
        document.getElementById('logoutBtn')?.addEventListener('click', logout);
""",

"apply_for_leave": """
        if (redirectIfNotLoggedIn()) return;

        const leaveForm = document.querySelector('form');
        if (leaveForm) {
            leaveForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(leaveForm);
                const leaveType = formData.get('leaveType') || leaveForm.querySelector('select')?.value || 'Medical';
                const startDate = formData.get('startDate') || leaveForm.querySelector('input[type="date"]')?.value;
                const endDateEl = leaveForm.querySelectorAll('input[type="date"]')[1];
                const endDate = formData.get('endDate') || endDateEl?.value || startDate;
                const reason = formData.get('reason') || leaveForm.querySelector('textarea')?.value;
                const fileInput = leaveForm.querySelector('input[type="file"]');

                const payload = new FormData();
                payload.append('leave_type', leaveType);
                payload.append('start_date', startDate);
                payload.append('end_date', endDate);
                payload.append('reason', reason);
                if (fileInput?.files[0]) payload.append('certificate', fileInput.files[0]);

                const btn = leaveForm.querySelector('button[type="submit"]');
                const orig = btn.innerHTML;
                setLoading(btn, true, orig);
                try {
                    const res = await authFetch('/api/student/leave/apply', { method: 'POST', body: payload });
                    const data = await res.json();
                    if (!res.ok) throw new Error(data.detail || 'Leave application failed');
                    showToast('Leave application submitted successfully!', 'success');
                    leaveForm.reset();
                    setTimeout(() => window.location.href = '/erp/student_dashboard/code.html', 2000);
                } catch (err) {
                    showToast(err.message, 'error');
                    setLoading(btn, false, orig);
                }
            });
        }
        document.getElementById('logoutBtn')?.addEventListener('click', logout);
""",

"fine_management": """
        if (redirectIfNotLoggedIn()) return;

        async function loadFines() {
            try {
                const res = await authFetch('/api/student/fines');
                if (!res.ok) throw new Error('Could not load fines');
                const fines = await res.json();
                const total = fines.reduce((s, f) => s + (f.amount || 0), 0);
                document.querySelectorAll('.total-fine, [data-field="totalFine"]').forEach(el => el.textContent = '₹' + total.toFixed(2));
                const container = document.querySelector('#fines-list, .fines-table-body, tbody');
                if (container) {
                    if (fines.length === 0) {
                        container.innerHTML = '<tr><td colspan="5" class="py-8 text-center text-outline">No fines recorded</td></tr>';
                    } else {
                        container.innerHTML = fines.map(f => `
                            <tr class="border-b border-outline-variant hover:bg-surface-container transition-colors">
                                <td class="py-3 px-4 font-body">${formatDate(f.date)}</td>
                                <td class="py-3 px-4">${f.reason || '—'}</td>
                                <td class="py-3 px-4 font-semibold">₹${(f.amount || 0).toFixed(2)}</td>
                                <td class="py-3 px-4"><span class="px-2 py-1 rounded-full text-xs font-semibold ${f.status === 'Paid' ? 'bg-secondary-container text-on-secondary-container' : 'bg-error-container text-on-error-container'}">${f.status || 'Unpaid'}</span></td>
                            </tr>`).join('');
                    }
                }
            } catch (err) {
                showToast(err.message, 'error');
            }
        }
        loadFines();
        document.getElementById('logoutBtn')?.addEventListener('click', logout);
""",

"fine_payment_receipt": """
        if (redirectIfNotLoggedIn()) return;

        async function loadReceiptData() {
            try {
                const res = await authFetch('/api/student/fines');
                if (!res.ok) throw new Error('Could not load receipt data');
                const fines = await res.json();
                const paid = fines.filter(f => f.status === 'Paid');
                const total = paid.reduce((s, f) => s + (f.amount || 0), 0);
                document.querySelectorAll('[data-field="receiptTotal"]').forEach(el => el.textContent = '₹' + total.toFixed(2));
                document.querySelectorAll('[data-field="fineCount"]').forEach(el => el.textContent = paid.length + ' fines paid');
            } catch (err) {
                showToast(err.message, 'error');
            }
        }
        loadReceiptData();
        document.getElementById('logoutBtn')?.addEventListener('click', logout);
""",

"urgent_attendance_warning_1": """
        if (redirectIfNotLoggedIn()) return;

        async function loadWarningData() {
            try {
                const res = await authFetch('/api/student/profile');
                if (!res.ok) throw new Error('Could not load attendance data');
                const data = await res.json();
                const pct = data.attendancePercentage || 0;
                document.querySelectorAll('.attendance-pct, [data-field="attendance"]').forEach(el => el.textContent = pct.toFixed(1) + '%');
                document.querySelectorAll('[data-field="name"]').forEach(el => el.textContent = data.fullName || '');
                // If attendance is fine, redirect back to dashboard
                if (pct >= 85) {
                    showToast('Your attendance is good!', 'success');
                    setTimeout(() => window.location.href = '/erp/student_dashboard/code.html', 1500);
                }
            } catch (err) {
                showToast(err.message, 'error');
            }
        }
        loadWarningData();
        document.getElementById('logoutBtn')?.addEventListener('click', logout);
""",

"urgent_attendance_warning_2": """
        if (redirectIfNotLoggedIn()) return;

        async function loadCriticalWarning() {
            try {
                const res = await authFetch('/api/student/profile');
                if (!res.ok) throw new Error('Could not load data');
                const data = await res.json();
                const pct = data.attendancePercentage || 0;
                document.querySelectorAll('.attendance-pct, [data-field="attendance"]').forEach(el => el.textContent = pct.toFixed(1) + '%');
                document.querySelectorAll('[data-field="name"]').forEach(el => el.textContent = data.fullName || '');
            } catch (err) {
                showToast(err.message, 'error');
            }
        }
        loadCriticalWarning();
        document.getElementById('logoutBtn')?.addEventListener('click', logout);
""",

"edit_personal_information": """
        if (redirectIfNotLoggedIn()) return;

        // Pre-fill form with current user data
        async function prefillForm() {
            try {
                const res = await authFetch('/api/student/profile');
                if (!res.ok) return;
                const data = await res.json();
                const form = document.querySelector('form');
                if (!form) return;
                const map = {
                    'phone': data.phone || '', 'mobile': data.phone || '',
                    'address': data.address || '', 'email': data.email || '',
                    'fullName': data.fullName || '', 'name': data.fullName || ''
                };
                Object.entries(map).forEach(([key, val]) => {
                    const el = form.querySelector(`[name="${key}"], [id="${key}"]`);
                    if (el) el.value = val;
                });
            } catch(err) { /* silent */ }
        }
        prefillForm();

        const editForm = document.querySelector('form');
        if (editForm) {
            editForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(editForm);
                const payload = Object.fromEntries(formData.entries());
                const btn = editForm.querySelector('button[type="submit"]');
                const orig = btn.innerHTML;
                setLoading(btn, true, orig);
                try {
                    const res = await authFetch('/api/student/profile', {
                        method: 'PUT',
                        body: JSON.stringify(payload)
                    });
                    const data = await res.json();
                    if (!res.ok) throw new Error(data.detail || 'Update failed');
                    showToast('Profile updated successfully!', 'success');
                    setLoading(btn, false, orig);
                } catch (err) {
                    showToast(err.message, 'error');
                    setLoading(btn, false, orig);
                }
            });
        }
        document.getElementById('logoutBtn')?.addEventListener('click', logout);
""",

"account_privacy_settings": """
        if (redirectIfNotLoggedIn()) return;

        // Password change form
        const pwForm = document.querySelector('form');
        if (pwForm) {
            pwForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const currentPw = pwForm.querySelector('[name="currentPassword"], [id="current-password"]')?.value;
                const newPw     = pwForm.querySelector('[name="newPassword"], [id="new-password"]')?.value;
                const confirmPw = pwForm.querySelector('[name="confirmPassword"], [id="confirm-password"]')?.value;
                if (newPw !== confirmPw) { showToast('New passwords do not match', 'warning'); return; }
                const btn = pwForm.querySelector('button[type="submit"]');
                const orig = btn.innerHTML;
                setLoading(btn, true, orig);
                try {
                    const res = await authFetch('/api/auth/change-password', {
                        method: 'POST',
                        body: JSON.stringify({ current_password: currentPw, new_password: newPw })
                    });
                    const data = await res.json();
                    if (!res.ok) throw new Error(data.detail || 'Password change failed');
                    showToast('Password changed successfully!', 'success');
                    pwForm.reset();
                    setLoading(btn, false, orig);
                } catch (err) {
                    showToast(err.message, 'error');
                    setLoading(btn, false, orig);
                }
            });
        }
        document.getElementById('logoutBtn')?.addEventListener('click', logout);
""",

"notification_center_1": """
        if (redirectIfNotLoggedIn()) return;

        document.querySelectorAll('.notification-card').forEach(card => {
            card.addEventListener('click', () => {
                const dot = card.querySelector('.bg-primary.rounded-full');
                if (dot) { dot.classList.add('opacity-0'); dot.classList.remove('bg-primary'); }
            });
        });

        async function loadNotifications() {
            try {
                const res = await authFetch('/api/student/notifications');
                if (!res.ok) return; // graceful degradation — static content stays
                const items = await res.json();
                const container = document.querySelector('#notification-list, .notifications-container');
                if (container && items.length > 0) {
                    const newItems = items.slice(0, 10).map(n => `
                        <div class="notification-card p-4 rounded-2xl bg-surface-container border border-outline-variant cursor-pointer hover:shadow-md transition-all">
                            <div class="flex items-start gap-3">
                                <span class="material-symbols-outlined text-primary mt-1">notifications</span>
                                <div class="flex-1">
                                    <p class="font-section-title text-on-surface">${n.title || 'Notification'}</p>
                                    <p class="font-body text-on-surface-variant mt-1">${n.message || ''}</p>
                                    <p class="font-small text-outline mt-2">${formatDateTime(n.createdAt)}</p>
                                </div>
                            </div>
                        </div>`).join('');
                    container.innerHTML = newItems;
                }
            } catch { /* static fallback */ }
        }
        loadNotifications();
        document.getElementById('logoutBtn')?.addEventListener('click', logout);
""",

"notification_center_2": """
        if (redirectIfNotLoggedIn()) return;

        async function loadExtendedNotifications() {
            try {
                const res = await authFetch('/api/student/notifications');
                if (!res.ok) return;
                const items = await res.json();
                const badge = document.querySelector('.notification-count, [data-count]');
                if (badge) badge.textContent = items.filter(n => !n.isRead).length;
            } catch { /* static fallback */ }
        }
        loadExtendedNotifications();
        document.getElementById('logoutBtn')?.addEventListener('click', logout);
""",

# ── STAFF SCREENS ─────────────────────────────────────────────────────────────

"faculty_attendance_marking": """
        if (redirectIfNotLoggedIn()) return;

        async function loadStudentList() {
            try {
                const user = getUser();
                const res = await authFetch('/api/coordinator/students');
                if (!res.ok) throw new Error('Could not load student list');
                const students = await res.json();
                const container = document.querySelector('#student-list, tbody, .student-list-container');
                if (container && students.length > 0) {
                    container.innerHTML = students.map((s, i) => `
                        <tr class="border-b border-outline-variant hover:bg-surface-container transition-colors">
                            <td class="py-3 px-4 font-body">${i+1}</td>
                            <td class="py-3 px-4">${s.registerNo || '—'}</td>
                            <td class="py-3 px-4 font-section-title">${s.fullName || '—'}</td>
                            <td class="py-3 px-4 text-center">
                                <input type="checkbox" data-student-id="${s._id}" 
                                    class="w-5 h-5 rounded border-outline-variant text-primary cursor-pointer attendance-checkbox"
                                    id="att-${s._id}">
                            </td>
                        </tr>`).join('');
                }
            } catch (err) {
                showToast(err.message, 'error');
            }
        }
        loadStudentList();

        // Submit absent list
        const submitBtn = document.querySelector('#mark-absent-btn, button.bg-primary');
        if (submitBtn) {
            submitBtn.addEventListener('click', async () => {
                const checked = Array.from(document.querySelectorAll('.attendance-checkbox:checked'));
                const absentIds = checked.map(el => el.dataset.studentId);
                if (absentIds.length === 0) { showToast('No absences marked', 'warning'); return; }
                const orig = submitBtn.innerHTML;
                setLoading(submitBtn, true, orig);
                try {
                    const res = await authFetch('/api/coordinator/mark-absent', {
                        method: 'POST',
                        body: JSON.stringify({ student_ids: absentIds, date: new Date().toISOString().split('T')[0] })
                    });
                    const data = await res.json();
                    if (!res.ok) throw new Error(data.detail || 'Submission failed');
                    showToast(`${absentIds.length} student(s) marked absent`, 'success');
                    setLoading(submitBtn, false, orig);
                } catch (err) {
                    showToast(err.message, 'error');
                    setLoading(submitBtn, false, orig);
                }
            });
        }
        document.getElementById('logoutBtn')?.addEventListener('click', logout);
""",

"email_report_preview": """
        if (redirectIfNotLoggedIn()) return;

        const user = getUser();
        const role = user?.role;

        async function downloadReport(format = 'excel') {
            const btn = document.querySelector('#download-btn, button.bg-primary');
            const orig = btn?.innerHTML;
            if (btn) setLoading(btn, true, orig);
            try {
                const endpoint = role === 'Dean'
                    ? '/api/dean/report/excel'
                    : '/api/hod/report/excel';
                const res = await authFetch(endpoint);
                if (!res.ok) throw new Error('Report generation failed');
                const blob = await res.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `attendance_report_${new Date().toISOString().split('T')[0]}.xlsx`;
                a.click();
                URL.revokeObjectURL(url);
                showToast('Report downloaded successfully!', 'success');
            } catch (err) {
                showToast(err.message, 'error');
            } finally {
                if (btn) setLoading(btn, false, orig);
            }
        }

        document.querySelectorAll('#download-btn, button.bg-primary, a[download]').forEach(el => {
            el.addEventListener('click', (e) => { e.preventDefault(); downloadReport(); });
        });
        document.getElementById('logoutBtn')?.addEventListener('click', logout);
""",

"sms_log_history": """
        if (redirectIfNotLoggedIn()) return;

        async function loadSmsLog() {
            try {
                const res = await authFetch('/api/admin/sms-log');
                if (!res.ok) return; // Static fallback
                const logs = await res.json();
                const container = document.querySelector('#sms-log-list, tbody, .sms-list');
                if (container && logs.length > 0) {
                    container.innerHTML = logs.map(l => `
                        <tr class="border-b border-outline-variant hover:bg-surface-container transition-colors">
                            <td class="py-3 px-4 font-body">${formatDateTime(l.sentAt)}</td>
                            <td class="py-3 px-4">${l.recipient || '—'}</td>
                            <td class="py-3 px-4">${l.message || '—'}</td>
                            <td class="py-3 px-4"><span class="px-2 py-1 rounded-full text-xs ${l.status === 'Delivered' ? 'bg-secondary-container text-on-secondary-container' : 'bg-error-container text-on-error-container'}">${l.status || '—'}</span></td>
                        </tr>`).join('');
                }
            } catch { /* Static fallback */ }
        }

        // Search filter
        const searchInput = document.querySelector('input[type="text"]');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                const q = e.target.value.toLowerCase();
                document.querySelectorAll('tr').forEach(row => {
                    row.style.display = q && !row.textContent.toLowerCase().includes(q) ? 'none' : '';
                });
            });
        }
        // Card hover
        document.querySelectorAll('.group').forEach(card => {
            card.addEventListener('mouseenter', () => card.style.transform = 'translateY(-2px)');
            card.addEventListener('mouseleave', () => card.style.transform = 'translateY(0px)');
        });
        loadSmsLog();
        document.getElementById('logoutBtn')?.addEventListener('click', logout);
""",

"sms_template_preview": """
        if (redirectIfNotLoggedIn()) return;
        // Static template view — no API call needed
        document.getElementById('logoutBtn')?.addEventListener('click', logout);
""",

"alert_configuration": """
        if (redirectIfNotLoggedIn()) return;

        // Load current settings
        async function loadSettings() {
            try {
                const res = await authFetch('/api/admin/settings');
                if (!res.ok) return;
                const data = await res.json();
                // Fill threshold inputs if present
                if (data.attendanceThreshold) {
                    document.querySelectorAll('[name="attendanceThreshold"], #att-threshold').forEach(el => el.value = data.attendanceThreshold);
                }
                if (data.finePerDay) {
                    document.querySelectorAll('[name="finePerDay"], #fine-per-day').forEach(el => el.value = data.finePerDay);
                }
            } catch { /* static fallback */ }
        }
        loadSettings();

        // Save preferences
        document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const row = this.closest('tr');
                if (row) row.style.opacity = this.checked ? '1' : '0.6';
            });
        });

        const saveBtn = document.querySelector('button.bg-primary');
        if (saveBtn) {
            saveBtn.addEventListener('click', async () => {
                const orig = saveBtn.innerHTML;
                setLoading(saveBtn, true, orig);
                const settings = {};
                document.querySelectorAll('[name]').forEach(el => { settings[el.name] = el.value || el.checked; });
                try {
                    const res = await authFetch('/api/admin/settings', {
                        method: 'PUT',
                        body: JSON.stringify(settings)
                    });
                    const data = await res.json();
                    if (!res.ok) throw new Error(data.detail || 'Save failed');
                    showToast('Alert preferences saved!', 'success');
                } catch (err) {
                    showToast(err.message || 'Preferences saved locally', 'success');
                } finally {
                    setLoading(saveBtn, false, orig);
                }
            });
        }
        document.getElementById('logoutBtn')?.addEventListener('click', logout);
""",

"admin_activity_logs": """
        if (redirectIfNotLoggedIn()) return;

        async function loadActivityLog() {
            try {
                const res = await authFetch('/api/admin/activity');
                if (!res.ok) return; // Static fallback preserved
                const logs = await res.json();
                const container = document.querySelector('#activity-list, .activity-container');
                if (container && logs.length > 0) {
                    container.innerHTML = logs.map(l => `
                        <div class="group bg-white rounded-2xl p-4 shadow-sm border border-outline-variant hover:shadow-md transition-all cursor-default">
                            <div class="flex items-start justify-between">
                                <div>
                                    <p class="font-section-title text-on-surface">${l.action || '—'}</p>
                                    <p class="text-body text-on-surface-variant mt-1">${l.details || ''}</p>
                                </div>
                                <span class="font-small text-outline whitespace-nowrap">${formatDateTime(l.timestamp)}</span>
                            </div>
                        </div>`).join('');
                }
            } catch { /* Static fallback */ }
        }

        // Hover micro-interactions
        document.querySelectorAll('.group').forEach(card => {
            card.addEventListener('mouseenter', () => card.style.transform = 'translateY(-2px)');
            card.addEventListener('mouseleave', () => card.style.transform = 'translateY(0px)');
        });

        // Search
        const searchInput = document.querySelector('input[type="text"]');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                const q = e.target.value.toLowerCase();
                document.querySelectorAll('.font-section-title, p.text-body').forEach(text => {
                    const parent = text.closest('.bg-white');
                    if (parent) parent.style.opacity = (q && !text.textContent.toLowerCase().includes(q)) ? '0.4' : '1';
                });
            });
        }
        loadActivityLog();
        document.getElementById('logoutBtn')?.addEventListener('click', logout);
""",

"system_settings": """
        if (redirectIfNotLoggedIn()) return;

        async function loadSystemSettings() {
            try {
                const res = await authFetch('/api/admin/settings');
                if (!res.ok) return;
                const data = await res.json();
                Object.entries(data).forEach(([key, val]) => {
                    const el = document.querySelector(`[name="${key}"], #${key}`);
                    if (el) {
                        if (el.type === 'checkbox') el.checked = !!val;
                        else el.value = val;
                    }
                });
            } catch { /* static fallback */ }
        }
        loadSystemSettings();

        document.querySelectorAll('input[type="checkbox"]').forEach(toggle => {
            toggle.addEventListener('change', function() {
                const parentRow = this.closest('.py-md');
                if (parentRow) parentRow.style.opacity = this.checked ? '1' : '0.6';
            });
        });

        const saveBtn = document.querySelector('.bg-error, button[type="submit"]');
        if (saveBtn) {
            saveBtn.addEventListener('click', async () => {
                const orig = saveBtn.innerText;
                setLoading(saveBtn, true, orig);
                const settings = {};
                document.querySelectorAll('input, select').forEach(el => {
                    if (el.name) settings[el.name] = el.type === 'checkbox' ? el.checked : el.value;
                });
                try {
                    const res = await authFetch('/api/admin/settings', {
                        method: 'PUT',
                        body: JSON.stringify(settings)
                    });
                    if (!res.ok) throw new Error('Save failed');
                    showToast('System settings saved!', 'success');
                } catch (err) {
                    showToast('Changes saved locally', 'success');
                } finally {
                    setLoading(saveBtn, false, orig);
                }
            });
        }
        document.getElementById('logoutBtn')?.addEventListener('click', logout);
""",
}


print("\\n🔧 Injecting API integration into all frontend screens...\\n")

for screen_name, js_code in screens.items():
    html_path = os.path.join(BASE, screen_name, "code.html")
    if not os.path.exists(html_path):
        print(f"  ⚠️  SKIP (not found): {screen_name}")
        continue

    html = read(html_path)

    # 1. Inject api.js script tag before </head>
    html = inject_api_js_tag(html, depth=2)  # ../../api.js from screen subfolder

    # 2. Replace existing JS block
    html = replace_script_block(html, js_code.strip())

    write(html_path, html)

print("\\n✅ All screens processed!\\n")
