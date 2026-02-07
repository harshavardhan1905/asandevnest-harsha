"""
Authentication Routes - Login, Register, Logout
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import User, DeveloperProfile, ClientProfile
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(get_dashboard_url())
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Check if user is suspended
            if user.status == 'suspended':
                flash('Your account has been suspended. Please contact support.', 'danger')
                return render_template('auth/login.html')
            
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash(f'Welcome back, {user.full_name}!', 'success')
            
            # Redirect to intended page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(get_dashboard_url())
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Admin-only login page"""
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Access denied. Admin credentials required.', 'danger')
            logout_user()
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Check if user is admin
            if not user.is_admin():
                flash('Access denied. This portal is for administrators only.', 'danger')
                return render_template('auth/admin_login.html')
            
            # Check if admin is suspended
            if user.status == 'suspended':
                flash('Your admin account has been suspended. Please contact support.', 'danger')
                return render_template('auth/admin_login.html')
            
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash(f'Welcome, {user.full_name}!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
    
    return render_template('auth/admin_login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(get_dashboard_url())
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        role = request.form.get('role', 'client')
        
        # Validation
        errors = []
        
        if not email:
            errors.append('Email is required.')
        elif User.query.filter_by(email=email).first():
            errors.append('Email already registered.')
        
        if not password or len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        if not full_name:
            errors.append('Full name is required.')
        
        if role not in ['developer', 'client']:
            errors.append('Invalid role selected.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html', 
                                 email=email, full_name=full_name, phone=phone, role=role)
        
        # Create user
        user = User(
            email=email,
            full_name=full_name,
            phone=phone,
            role=role,
            status='pending' if role == 'developer' else 'verified'  # Developers need verification
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.flush()
        
        # Create role-specific profile
        if role == 'developer':
            profile = DeveloperProfile(user_id=user.id)
            db.session.add(profile)
        else:
            company_name = request.form.get('company_name', '').strip()
            profile = ClientProfile(
                user_id=user.id,
                company_name=company_name
            )
            db.session.add(profile)
        
        db.session.commit()
        
        # Log in the user
        login_user(user)
        
        if role == 'developer':
            flash('Registration successful! Please complete KYC verification to access all features.', 'info')
            return redirect(url_for('developer.kyc'))
        else:
            flash('Registration successful! Welcome to Asan DevNest.', 'success')
            return redirect(url_for('client.dashboard'))
    
    return render_template('auth/register.html')


@auth_bp.route('/register/developer')
def register_developer():
    """Developer registration page"""
    if current_user.is_authenticated:
        return redirect(get_dashboard_url())
    return render_template('auth/register.html', role='developer')


@auth_bp.route('/register/client')
def register_client():
    """Client registration page"""
    if current_user.is_authenticated:
        return redirect(get_dashboard_url())
    return render_template('auth/register.html', role='client')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password page"""
    if current_user.is_authenticated:
        return redirect(get_dashboard_url())
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()
        
        # Always show success message for security
        flash('If an account exists for this email, you will receive password reset instructions.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')


def get_dashboard_url():
    """Get dashboard URL based on user role"""
    if current_user.is_admin():
        return url_for('admin.dashboard')
    elif current_user.is_developer():
        return url_for('developer.dashboard')
    else:
        return url_for('client.dashboard')
