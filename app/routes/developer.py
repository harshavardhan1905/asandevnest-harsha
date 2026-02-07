"""
Developer Routes - Developer dashboard and management
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, DeveloperProfile, Article, Appointment, Project, Team, TeamMember, KYCDocument
from app.utils.decorators import developer_required, verified_developer_required
from app.utils.helpers import save_file
from datetime import datetime
import json

developer_bp = Blueprint('developer', __name__)


@developer_bp.route('/dashboard')
@login_required
@developer_required
def dashboard():
    """Developer dashboard"""
    profile = current_user.developer_profile
    
    if not profile:
        profile = DeveloperProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
    
    stats = {
        'total_articles': Article.query.filter_by(developer_id=profile.id).count(),
        'published_articles': Article.query.filter_by(developer_id=profile.id, status='approved').count(),
        'pending_articles': Article.query.filter_by(developer_id=profile.id, status='pending').count(),
        'total_views': db.session.query(db.func.sum(Article.views_count)).filter_by(developer_id=profile.id).scalar() or 0,
        'upcoming_appointments': Appointment.query.filter(
            Appointment.developer_id == profile.id,
            Appointment.scheduled_at > datetime.utcnow(),
            Appointment.status.in_(['pending', 'confirmed'])
        ).count()
    }
    
    recent_articles = Article.query.filter_by(developer_id=profile.id).order_by(Article.created_at.desc()).limit(5).all()
    upcoming_appointments = Appointment.query.filter(
        Appointment.developer_id == profile.id,
        Appointment.scheduled_at > datetime.utcnow()
    ).order_by(Appointment.scheduled_at).limit(5).all()
    team_memberships = TeamMember.query.filter_by(developer_id=profile.id, status='active').all()
    
    return render_template('developer/dashboard.html', profile=profile, stats=stats,
                         recent_articles=recent_articles, upcoming_appointments=upcoming_appointments,
                         team_memberships=team_memberships)


@developer_bp.route('/verification-pending')
@login_required
@developer_required
def verification_pending():
    if current_user.is_verified():
        return redirect(url_for('developer.dashboard'))
    kyc_docs = KYCDocument.query.filter_by(user_id=current_user.id).all()
    return render_template('developer/verification_pending.html', kyc_docs=kyc_docs)


@developer_bp.route('/kyc', methods=['GET', 'POST'])
@login_required
@developer_required
def kyc():
    if request.method == 'POST':
        document_type = request.form.get('document_type')
        document_number = request.form.get('document_number', '')
        
        if 'document_file' not in request.files or not request.files['document_file'].filename:
            flash('Please upload a document.', 'danger')
            return redirect(url_for('developer.kyc'))
        
        filename = save_file(request.files['document_file'], 'kyc')
        if not filename:
            flash('Invalid file type.', 'danger')
            return redirect(url_for('developer.kyc'))
        
        kyc_doc = KYCDocument(
            user_id=current_user.id,
            document_type=document_type,
            document_number=document_number[-4:] if document_number else '',
            document_path=filename
        )
        db.session.add(kyc_doc)
        db.session.commit()
        
        flash('Document submitted for verification.', 'success')
        return redirect(url_for('developer.verification_pending'))
    
    kyc_docs = KYCDocument.query.filter_by(user_id=current_user.id).all()
    return render_template('developer/kyc.html', kyc_docs=kyc_docs)


@developer_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@developer_required
def profile():
    profile = current_user.developer_profile
    
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name', current_user.full_name)
        current_user.phone = request.form.get('phone', current_user.phone)
        
        profile.tagline = request.form.get('tagline', '')
        profile.bio = request.form.get('bio', '')
        profile.experience_years = request.form.get('experience_years', 0, type=int)
        profile.hourly_rate = request.form.get('hourly_rate', type=float)
        profile.availability = request.form.get('availability', 'available')
        
        skills = request.form.get('skills', '')
        domains = request.form.get('domains', '')
        profile.set_skills_list([s.strip() for s in skills.split(',') if s.strip()])
        profile.set_domains_list([d.strip() for d in domains.split(',') if d.strip()])
        
        profile.offers_classes = request.form.get('offers_classes') == 'on'
        profile.offers_consulting = request.form.get('offers_consulting') == 'on'
        profile.offers_support = request.form.get('offers_support') == 'on'
        
        profile.portfolio_url = request.form.get('portfolio_url', '')
        profile.linkedin_url = request.form.get('linkedin_url', '')
        profile.github_url = request.form.get('github_url', '')
        
        if 'avatar' in request.files and request.files['avatar'].filename:
            filename = save_file(request.files['avatar'], 'avatars')
            if filename:
                current_user.avatar = filename
        
        db.session.commit()
        flash('Profile updated.', 'success')
    
    return render_template('developer/profile.html', profile=profile)


@developer_bp.route('/articles')
@login_required
@developer_required
def articles():
    profile = current_user.developer_profile
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = Article.query.filter_by(developer_id=profile.id)
    if status:
        query = query.filter_by(status=status)
    
    articles = query.order_by(Article.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('developer/articles.html', articles=articles, current_status=status)


@developer_bp.route('/article/new', methods=['GET', 'POST'])
@login_required
@verified_developer_required
def new_article():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '')
        
        if not title or not content:
            flash('Title and content required.', 'danger')
            return render_template('developer/article_form.html')
        
        article = Article(
            developer_id=current_user.developer_profile.id,
            title=title,
            excerpt=request.form.get('excerpt', ''),
            content=content,
            article_type=request.form.get('article_type', 'tutorial'),
            domain=request.form.get('domain', ''),
            status='pending' if request.form.get('submit_type') == 'publish' else 'draft'
        )
        
        techs = request.form.get('technologies', '')
        article.set_technologies_list([t.strip() for t in techs.split(',') if t.strip()])
        article.generate_slug()
        
        if 'cover_image' in request.files and request.files['cover_image'].filename:
            article.cover_image = save_file(request.files['cover_image'], 'articles')
        
        db.session.add(article)
        db.session.commit()
        flash('Article saved.', 'success')
        return redirect(url_for('developer.articles'))
    
    return render_template('developer/article_form.html')


@developer_bp.route('/article/<int:article_id>/edit', methods=['GET', 'POST'])
@login_required
@developer_required
def edit_article(article_id):
    article = Article.query.get_or_404(article_id)
    if article.developer_id != current_user.developer_profile.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('developer.articles'))
    
    if request.method == 'POST':
        article.title = request.form.get('title', '')
        article.excerpt = request.form.get('excerpt', '')
        article.content = request.form.get('content', '')
        article.article_type = request.form.get('article_type', 'tutorial')
        article.domain = request.form.get('domain', '')
        
        techs = request.form.get('technologies', '')
        article.set_technologies_list([t.strip() for t in techs.split(',') if t.strip()])
        
        if request.form.get('submit_type') == 'publish' and article.status == 'draft':
            article.status = 'pending'
        
        db.session.commit()
        flash('Article updated.', 'success')
        return redirect(url_for('developer.articles'))
    
    return render_template('developer/article_form.html', article=article)


@developer_bp.route('/appointments')
@login_required
@developer_required
def appointments():
    profile = current_user.developer_profile
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = Appointment.query.filter_by(developer_id=profile.id)
    
    if status:
        query = query.filter_by(status=status)
        
    appointments = query.order_by(Appointment.scheduled_at.desc()).paginate(page=page, per_page=10)
    return render_template('developer/appointments.html', appointments=appointments, current_status=status)


@developer_bp.route('/appointment/<int:id>/confirm', methods=['POST'])
@login_required
@developer_required
def confirm_appointment(id):
    appt = Appointment.query.get_or_404(id)
    if appt.developer_id != current_user.developer_profile.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('developer.appointments'))
    link = request.form.get('meeting_link', '').strip()
    if link and not link.startswith(('http://', 'https://')):
        link = 'https://' + link
    appt.confirm(link)
    db.session.commit()
    flash('Appointment confirmed.', 'success')
    return redirect(url_for('developer.appointments'))


@developer_bp.route('/appointment/<int:id>')
@login_required
@developer_required
def appointment_detail(id):
    appt = Appointment.query.get_or_404(id)
    if appt.developer_id != current_user.developer_profile.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('developer.appointments'))
    return render_template('developer/appointment_detail.html', appt=appt)


@developer_bp.route('/appointment/<int:id>/cancel', methods=['POST'])
@login_required
@developer_required
def cancel_appointment(id):
    appt = Appointment.query.get_or_404(id)
    if appt.developer_id != current_user.developer_profile.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('developer.appointments'))
    
    appt.cancel(current_user.id, request.form.get('reason', 'Developer cancelled'))
    db.session.commit()
    flash('Appointment cancelled.', 'info')
    return redirect(url_for('developer.appointments'))


@developer_bp.route('/teams')
@login_required
@developer_required
def teams():
    profile = current_user.developer_profile
    memberships = TeamMember.query.filter_by(developer_id=profile.id).all()
    return render_template('developer/teams.html', memberships=memberships)


@developer_bp.route('/project/<int:project_id>')
@login_required
@developer_required
def project_detail(project_id):
    """View project details"""
    project = Project.query.get_or_404(project_id)
    # Verify developer is member of the team assigned to this project
    is_member = False
    if project.team:
        for member in project.team.members:
            if member.developer_id == current_user.developer_profile.id:
                is_member = True
                break
    
    if not is_member:
        flash('Access denied. You are not a member of this project team.', 'danger')
        return redirect(url_for('developer.teams'))
        
    return render_template('developer/project_detail.html', project=project)
