/**
 * api.js — Shared API utility for Smart Absentee ERP frontend.
 * Include this file in every protected page:
 *   <script src="../api.js"></script>
 *
 * Features:
 *  - getToken()            : Read JWT from localStorage
 *  - getUser()             : Read user object from localStorage
 *  - authFetch(url, opts)  : Fetch with Authorization header auto-attached
 *  - logout()              : Clear storage + redirect to login
 *  - redirectIfNotLoggedIn(): Guard for protected pages
 *  - redirectByRole()      : Send user to their dashboard
 *  - showToast(msg, type)  : Display a brief floating notification
 *  - formatDate(iso)       : Format ISO date string → readable
 *  - API_BASE               : Base URL constant
 */

const API_BASE = '/api';

// ── Auth helpers ──────────────────────────────────────────────────────────────

function getToken() {
    return localStorage.getItem('access_token') || '';
}

function getUser() {
    try {
        return JSON.parse(localStorage.getItem('user') || 'null');
    } catch {
        return null;
    }
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/erp/login_attendance_hub/code.html';
}

function redirectIfNotLoggedIn() {
    if (!getToken() || !getUser()) {
        logout();
        return true;
    }
    return false;
}

function redirectByRole() {
    const user = getUser();
    if (!user) { logout(); return; }
    const routes = {
        'Student':     '/erp/student_dashboard/code.html',
        'Coordinator': '/erp/coordinator_dashboard/code.html',
        'HOD':         '/erp/hod_dashboard/code.html',
        'Dean':        '/erp/dean_dashboard/code.html',
        'Faculty':     '/erp/faculty_attendance_marking/code.html',
        'Admin':       '/erp/admin_activity_logs/code.html',
    };
    const dest = routes[user.role];
    if (dest) window.location.href = dest;
}

// ── Fetch wrapper ─────────────────────────────────────────────────────────────

async function authFetch(url, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
    };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    // Strip Content-Type for FormData uploads
    if (options.body instanceof FormData) {
        delete headers['Content-Type'];
    }

    const res = await fetch(url, { ...options, headers });

    if (res.status === 401) {
        logout();
        throw new Error('Session expired. Please log in again.');
    }
    return res;
}

// ── UI helpers ────────────────────────────────────────────────────────────────

function showToast(message, type = 'info') {
    const existing = document.getElementById('erp-toast');
    if (existing) existing.remove();

    const colors = {
        info:    'bg-primary text-on-primary',
        success: 'bg-secondary text-on-secondary',
        error:   'bg-error text-on-error',
        warning: 'bg-tertiary text-on-tertiary',
    };

    const toast = document.createElement('div');
    toast.id = 'erp-toast';
    toast.className = `fixed bottom-6 left-1/2 -translate-x-1/2 z-[9999] px-6 py-3 rounded-2xl shadow-2xl font-section-title text-section-title flex items-center gap-2 transition-all ${colors[type] || colors.info}`;
    toast.innerHTML = `
        <span class="material-symbols-outlined text-[20px]">
            ${type === 'success' ? 'check_circle' : type === 'error' ? 'error' : type === 'warning' ? 'warning' : 'info'}
        </span>
        <span>${message}</span>`;
    document.body.appendChild(toast);

    setTimeout(() => toast.remove(), 3500);
}

function setLoading(btn, isLoading, originalHTML) {
    if (isLoading) {
        btn.disabled = true;
        btn.innerHTML = '<span class="material-symbols-outlined animate-spin text-[18px]">sync</span> Please wait...';
    } else {
        btn.disabled = false;
        btn.innerHTML = originalHTML;
    }
}

function formatDate(isoOrStr) {
    if (!isoOrStr) return '—';
    try {
        return new Date(isoOrStr).toLocaleDateString('en-IN', {
            day: '2-digit', month: 'short', year: 'numeric'
        });
    } catch { return isoOrStr; }
}

function formatDateTime(isoOrStr) {
    if (!isoOrStr) return '—';
    try {
        return new Date(isoOrStr).toLocaleString('en-IN', {
            day: '2-digit', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    } catch { return isoOrStr; }
}

// ── Name badge ────────────────────────────────────────────────────────────────

function injectUserBadge(nameSelector, roleSelector) {
    const user = getUser();
    if (!user) return;
    const nameEl = document.querySelector(nameSelector);
    const roleEl = document.querySelector(roleSelector);
    if (nameEl) nameEl.textContent = user.full_name || user.email || 'User';
    if (roleEl) roleEl.textContent = user.role || '';
}

// ── Logout wiring (auto-binds any element with id="logoutBtn") ────────────────
document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) logoutBtn.addEventListener('click', logout);
});
