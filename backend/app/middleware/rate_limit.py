"""
Rate limiting middleware / utility.
Blocks brute-force attacks by limiting failed login attempts per client IP.
"""
import datetime
from collections import defaultdict
from fastapi import HTTPException, status

# Tracks (ip -> [attempt_timestamps]) for login rate limiting
_login_attempts = defaultdict(list)
_MAX_ATTEMPTS = 5          # max failed logins
_WINDOW_SECONDS = 15 * 60  # within 15 minutes (900 seconds)

def check_login_rate_limit(ip: str):
    """Raise 429 if the IP has exceeded login attempt limit."""
    now = datetime.datetime.utcnow()
    cutoff = now - datetime.timedelta(seconds=_WINDOW_SECONDS)
    
    # Keep only attempts within the window
    _login_attempts[ip] = [t for t in _login_attempts[ip] if t > cutoff]
    
    if len(_login_attempts[ip]) >= _MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed login attempts. Please wait {_WINDOW_SECONDS // 60} minutes before trying again."
        )

def record_failed_login_attempt(ip: str):
    """Record a failed login attempt for an IP."""
    _login_attempts[ip].append(datetime.datetime.utcnow())

def clear_login_attempts(ip: str):
    """Clear login history for an IP (call on successful login)."""
    _login_attempts.pop(ip, None)
