"""
Role-based Access Control Decorators
"""

from functools import wraps
from flask import redirect, url_for, flash, abort
from flask_login import current_user


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin():
            flash('You do not have permission to access this page.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def developer_required(f):
    """Decorator to require developer role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_developer():
            flash('This page is only accessible to developers.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def verified_developer_required(f):
    """Decorator to require verified developer"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_developer():
            flash('This page is only accessible to developers.', 'danger')
            abort(403)
        if not current_user.is_verified():
            flash('Your account must be verified to access this feature.', 'warning')
            return redirect(url_for('developer.verification_pending'))
        return f(*args, **kwargs)
    return decorated_function


def client_required(f):
    """Decorator to require client role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_client():
            flash('This page is only accessible to clients.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def login_required_with_redirect(f):
    """Decorator that stores intended URL and redirects to login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to continue.', 'info')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
