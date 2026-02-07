"""
Client Routes - Client dashboard and features
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, DeveloperProfile, ClientProfile, Article, Project, Appointment
from app.utils.decorators import client_required
from datetime import datetime
import json

client_bp = Blueprint('client', __name__)


@client_bp.route('/dashboard')
@login_required
@client_required
def dashboard():
    """Client dashboard"""
    profile = current_user.client_profile
    
    if not profile:
        profile = ClientProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
    
    stats = {
        'total_projects': Project.query.filter_by(client_id=profile.id).count(),
        'active_projects': Project.query.filter(
            Project.client_id == profile.id,
            Project.status.in_(['reviewing', 'team_forming', 'in_progress'])
        ).count(),
        'completed_projects': Project.query.filter_by(client_id=profile.id, status='completed').count(),
        'total_appointments': Appointment.query.filter_by(client_id=profile.id).count()
    }
    
    recent_projects = Project.query.filter_by(client_id=profile.id)\
        .order_by(Project.created_at.desc()).limit(5).all()
    
    upcoming_appointments = Appointment.query.filter(
        Appointment.client_id == profile.id,
        Appointment.scheduled_at > datetime.utcnow()
    ).order_by(Appointment.scheduled_at).limit(5).all()
    
    return render_template('client/dashboard.html', profile=profile, stats=stats,
                         recent_projects=recent_projects, upcoming_appointments=upcoming_appointments)


@client_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@client_required
def profile():
    """Client profile management"""
    profile = current_user.client_profile
    
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name', current_user.full_name)
        current_user.phone = request.form.get('phone', current_user.phone)
        
        profile.company_name = request.form.get('company_name', '')
        profile.company_size = request.form.get('company_size', '')
        profile.industry = request.form.get('industry', '')
        profile.website = request.form.get('website', '')
        profile.contact_name = request.form.get('contact_name', '')
        profile.contact_position = request.form.get('contact_position', '')
        
        db.session.commit()
        flash('Profile updated.', 'success')
    
    return render_template('client/profile.html', profile=profile)


@client_bp.route('/projects')
@login_required
@client_required
def projects():
    """List client's projects"""
    profile = current_user.client_profile
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = Project.query.filter_by(client_id=profile.id)
    if status:
        query = query.filter_by(status=status)
    
    projects = query.order_by(Project.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('client/projects.html', projects=projects, current_status=status)


@client_bp.route('/project/new', methods=['GET', 'POST'])
@login_required
@client_required
def new_project():
    """Submit new project idea"""
    if request.method == 'POST':
        project = Project(
            client_id=current_user.client_profile.id,
            title=request.form.get('title', ''),
            description=request.form.get('description', ''),
            detailed_requirements=request.form.get('detailed_requirements', ''),
            project_type=request.form.get('project_type', 'web_app'),
            domain=request.form.get('domain', ''),
            budget_min=request.form.get('budget_min', type=float),
            budget_max=request.form.get('budget_max', type=float),
            timeline_weeks=request.form.get('timeline_weeks', type=int)
        )
        
        techs = request.form.get('technologies', '')
        project.set_technologies_list([t.strip() for t in techs.split(',') if t.strip()])
        
        db.session.add(project)
        current_user.client_profile.projects_submitted += 1
        db.session.commit()
        
        flash('Project submitted! Asan team will review and contact you.', 'success')
        return redirect(url_for('client.projects'))
    
    return render_template('client/project_form.html')


@client_bp.route('/project/<int:project_id>')
@login_required
@client_required
def project_detail(project_id):
    """Project detail"""
    project = Project.query.get_or_404(project_id)
    if project.client_id != current_user.client_profile.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('client.projects'))
    return render_template('client/project_detail.html', project=project)


@client_bp.route('/appointments')
@login_required
@client_required
def appointments():
    """List client's appointments"""
    profile = current_user.client_profile
    page = request.args.get('page', 1, type=int)
    
    status = request.args.get('status')
    
    query = Appointment.query.filter_by(client_id=profile.id)
    if status:
        query = query.filter_by(status=status)
    
    appointments = query.order_by(Appointment.scheduled_at.desc()).paginate(page=page, per_page=10)
    return render_template('client/appointments.html', appointments=appointments, current_status=status)


@client_bp.route('/book-appointment/<int:developer_id>', methods=['GET', 'POST'])
@login_required
@client_required
def book_appointment(developer_id):
    """Book appointment with developer"""
    developer = DeveloperProfile.query.get_or_404(developer_id)
    
    if developer.user.status != 'verified':
        flash('Developer not available.', 'danger')
        return redirect(url_for('main.developers_list'))
    
    if request.method == 'POST':
        scheduled_date = request.form.get('scheduled_date')
        scheduled_time = request.form.get('scheduled_time')
        
        scheduled_at = datetime.strptime(f"{scheduled_date} {scheduled_time}", '%Y-%m-%d %H:%M')
        
        appointment = Appointment(
            client_id=current_user.client_profile.id,
            developer_id=developer_id,
            appointment_type=request.form.get('appointment_type', 'consulting'),
            title=request.form.get('title', ''),
            description=request.form.get('description', ''),
            scheduled_at=scheduled_at,
            duration_minutes=request.form.get('duration', 60, type=int),
            client_notes=request.form.get('notes', '')
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        flash('Appointment request sent! Developer will confirm.', 'success')
        return redirect(url_for('client.appointments'))
    
    return render_template('client/book_appointment.html', developer=developer)


@client_bp.route('/appointment/<int:id>/cancel', methods=['POST'])
@login_required
@client_required
def cancel_appointment(id):
    """Cancel appointment"""
    appt = Appointment.query.get_or_404(id)
    if appt.client_id != current_user.client_profile.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('client.appointments'))
    
    appt.cancel(current_user.id, request.form.get('reason', ''))
    db.session.commit()
    flash('Appointment cancelled.', 'info')
    return redirect(url_for('client.appointments'))
