"""
Authentication system for vocabulary review application.
Provides passcode-based authentication with session management.
"""

from functools import wraps
from flask import session, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
import hashlib
import time
from typing import Optional, Tuple
from config.api_config import api_config


class AuthManager:
    """Manages authentication state and security features."""

    # Session keys
    SESSION_AUTHENTICATED = 'authenticated'
    SESSION_LOGIN_TIME = 'login_time'
    SESSION_FAILED_ATTEMPTS = 'failed_attempts'
    SESSION_LAST_ACTIVITY = 'last_activity'
    SESSION_BLOCKED_UNTIL = 'blocked_until'

    @staticmethod
    def is_passcode_required() -> bool:
        """Check if passcode authentication is required."""
        return api_config.is_passcode_configured()

    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is currently authenticated."""
        if not AuthManager.is_passcode_required():
            return True  # No passcode configured, always authenticated

        # Check basic authentication status
        if not session.get(AuthManager.SESSION_AUTHENTICATED, False):
            return False

        # Check auto-logout
        if AuthManager._is_session_expired():
            AuthManager.logout()
            return False

        # Update last activity
        session[AuthManager.SESSION_LAST_ACTIVITY] = datetime.now().isoformat()
        return True

    @staticmethod
    def _is_session_expired() -> bool:
        """Check if current session has expired."""
        if not api_config.is_auto_logout_enabled():
            return False

        login_time_str = session.get(AuthManager.SESSION_LOGIN_TIME)
        if not login_time_str:
            return True

        try:
            login_time = datetime.fromisoformat(login_time_str)
            auto_logout_hours = api_config.get_auto_logout_hours()
            expiry_time = login_time + timedelta(hours=auto_logout_hours)
            return datetime.now() > expiry_time
        except (ValueError, TypeError):
            return True

    @staticmethod
    def is_blocked() -> Tuple[bool, Optional[int]]:
        """
        Check if user is temporarily blocked due to failed attempts.

        Returns:
            Tuple of (is_blocked, seconds_until_unblock)
        """
        blocked_until_str = session.get(AuthManager.SESSION_BLOCKED_UNTIL)
        if not blocked_until_str:
            return False, None

        try:
            blocked_until = datetime.fromisoformat(blocked_until_str)
            now = datetime.now()

            if now < blocked_until:
                seconds_left = int((blocked_until - now).total_seconds())
                return True, seconds_left
            else:
                # Block period has expired, clear it
                session.pop(AuthManager.SESSION_BLOCKED_UNTIL, None)
                session.pop(AuthManager.SESSION_FAILED_ATTEMPTS, None)
                return False, None
        except (ValueError, TypeError):
            return False, None

    @staticmethod
    def authenticate(passcode: str) -> Tuple[bool, str]:
        """
        Attempt to authenticate with passcode.

        Args:
            passcode: User input passcode

        Returns:
            Tuple of (success, message)
        """
        # Check if blocked
        is_blocked, seconds_left = AuthManager.is_blocked()
        if is_blocked:
            minutes_left = max(1, seconds_left // 60)
            return False, f"嘗試次數過多，請等待 {minutes_left} 分鐘後再試"

        # Verify passcode
        if api_config.verify_passcode(passcode):
            # Successful login
            AuthManager._set_authenticated()
            return True, "登入成功"
        else:
            # Failed login
            AuthManager._record_failed_attempt()
            failed_attempts = session.get(AuthManager.SESSION_FAILED_ATTEMPTS, 0)
            max_attempts = api_config.get_max_failed_attempts()

            if failed_attempts >= max_attempts:
                AuthManager._block_user()
                return False, "嘗試次數過多，已暫時封鎖 30 分鐘"
            else:
                remaining = max_attempts - failed_attempts
                return False, f"通行碼錯誤，還有 {remaining} 次機會"

    @staticmethod
    def _set_authenticated():
        """Set user as authenticated in session."""
        now = datetime.now()
        session[AuthManager.SESSION_AUTHENTICATED] = True
        session[AuthManager.SESSION_LOGIN_TIME] = now.isoformat()
        session[AuthManager.SESSION_LAST_ACTIVITY] = now.isoformat()
        session.permanent = True

        # Clear failed attempts
        session.pop(AuthManager.SESSION_FAILED_ATTEMPTS, None)
        session.pop(AuthManager.SESSION_BLOCKED_UNTIL, None)

    @staticmethod
    def _record_failed_attempt():
        """Record a failed authentication attempt."""
        failed_attempts = session.get(AuthManager.SESSION_FAILED_ATTEMPTS, 0)
        session[AuthManager.SESSION_FAILED_ATTEMPTS] = failed_attempts + 1

    @staticmethod
    def _block_user():
        """Block user for a period after too many failed attempts."""
        block_duration = timedelta(minutes=30)  # Block for 30 minutes
        blocked_until = datetime.now() + block_duration
        session[AuthManager.SESSION_BLOCKED_UNTIL] = blocked_until.isoformat()

    @staticmethod
    def logout():
        """Logout user and clear session."""
        session.pop(AuthManager.SESSION_AUTHENTICATED, None)
        session.pop(AuthManager.SESSION_LOGIN_TIME, None)
        session.pop(AuthManager.SESSION_LAST_ACTIVITY, None)
        session.pop(AuthManager.SESSION_FAILED_ATTEMPTS, None)
        session.pop(AuthManager.SESSION_BLOCKED_UNTIL, None)

    @staticmethod
    def get_session_info() -> dict:
        """Get current session information."""
        if not AuthManager.is_authenticated():
            return {"authenticated": False}

        login_time_str = session.get(AuthManager.SESSION_LOGIN_TIME)
        last_activity_str = session.get(AuthManager.SESSION_LAST_ACTIVITY)

        info = {
            "authenticated": True,
            "login_time": login_time_str,
            "last_activity": last_activity_str,
            "auto_logout_enabled": api_config.is_auto_logout_enabled()
        }

        if api_config.is_auto_logout_enabled() and login_time_str:
            try:
                login_time = datetime.fromisoformat(login_time_str)
                auto_logout_hours = api_config.get_auto_logout_hours()
                expiry_time = login_time + timedelta(hours=auto_logout_hours)
                info["expires_at"] = expiry_time.isoformat()
                info["time_remaining_minutes"] = max(0, int((expiry_time - datetime.now()).total_seconds() / 60))
            except (ValueError, TypeError):
                pass

        return info


def require_auth(f):
    """
    Decorator to require authentication for routes.
    Redirects to login page if not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not AuthManager.is_authenticated():
            # Store the original URL for redirect after login
            session['next_url'] = request.url
            flash('請輸入通行碼以繼續', 'info')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def require_auth_api(f):
    """
    Decorator to require authentication for API routes.
    Returns JSON error if not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not AuthManager.is_authenticated():
            return jsonify({
                'success': False,
                'message': '需要身份驗證',
                'error_code': 'AUTH_REQUIRED'
            }), 401
        return f(*args, **kwargs)
    return decorated_function


def optional_auth(f):
    """
    Decorator that checks authentication but doesn't require it.
    Sets 'user_authenticated' in kwargs.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        kwargs['user_authenticated'] = AuthManager.is_authenticated()
        return f(*args, **kwargs)
    return decorated_function
