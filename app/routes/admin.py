"""
Admin Routes - Admin dashboard and management
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, DeveloperProfile, ClientProfile, Article, Project, Team, TeamMember, Appointment, KYCDocument
from app.utils.decorators import admin_required
from app.utils.helpers import save_file
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with analytics"""
    # Get counts
    stats = {
        'total_developers': User.query.filter_by(role='developer').count(),
        'verified_developers': User.query.filter_by(role='developer', status='verified').count(),
        'pending_developers': User.query.filter_by(role='developer', status='pending').count(),
        'total_clients': User.query.filter_by(role='client').count(),
        'total_articles': Article.query.count(),
        'pending_articles': Article.query.filter_by(status='pending').count(),
        'total_projects': Project.query.count(),
        'active_projects': Project.query.filter(Project.status.in_(['reviewing', 'team_forming', 'in_progress'])).count(),
        'total_teams': Team.query.count(),
        'active_teams': Team.query.filter_by(status='active').count(),
        'total_appointments': Appointment.query.count(),
        'pending_kyc': KYCDocument.query.filter_by(status='pending').count()
    }
    
    # Recent activities
    recent_developers = User.query.filter_by(role='developer')\
        .order_by(User.created_at.desc()).limit(5).all()
    
    pending_articles = Article.query.filter_by(status='pending')\
        .order_by(Article.created_at.desc()).limit(5).all()
    
    recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
    
    pending_kyc = KYCDocument.query.filter_by(status='pending')\
        .order_by(KYCDocument.submitted_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_developers=recent_developers,
                         pending_articles=pending_articles,
                         recent_projects=recent_projects,
                         pending_kyc=pending_kyc)



# ============ User Management ============

@admin_bp.route('/admins', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_admins():
    """Manage Admin Users"""
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
        else:
            user = User(
                email=email,
                full_name=name,
                role='admin',
                status='verified'
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('New Admin added successfully.', 'success')
            
        return redirect(url_for('admin.manage_admins'))
        
    admins = User.query.filter_by(role='admin').all()
    return render_template('admin/manage_admins.html', admins=admins)


# ============ Developer Management ============


@admin_bp.route('/developers')
@login_required
@admin_required
def developers():
    """List all developers"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    
    query = User.query.filter_by(role='developer')
    
    if status:
        query = query.filter_by(status=status)
    
    if search:
        query = query.filter(
            (User.full_name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    
    developers = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/developers.html',
                         developers=developers,
                         current_status=status,
                         search=search)


@admin_bp.route('/developer/<int:user_id>')
@login_required
@admin_required
def developer_detail(user_id):
    """Developer detail page"""
    user = User.query.filter_by(id=user_id, role='developer').first_or_404()
    kyc_docs = KYCDocument.query.filter_by(user_id=user_id).all()
    articles = Article.query.filter_by(developer_id=user.developer_profile.id if user.developer_profile else 0).all()
    
    return render_template('admin/developer_detail.html',
                         user=user,
                         kyc_docs=kyc_docs,
                         articles=articles)


@admin_bp.route('/developer/<int:user_id>/verify', methods=['POST'])
@login_required
@admin_required
def verify_developer(user_id):
    """Verify a developer"""
    user = User.query.filter_by(id=user_id, role='developer').first_or_404()
    user.status = 'verified'
    db.session.commit()
    
    flash(f'{user.full_name} has been verified successfully.', 'success')
    return redirect(url_for('admin.developer_detail', user_id=user_id))


@admin_bp.route('/developer/<int:user_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_developer(user_id):
    """Reject a developer"""
    user = User.query.filter_by(id=user_id, role='developer').first_or_404()
    reason = request.form.get('reason', '')
    
    user.status = 'rejected'
    db.session.commit()
    
    flash(f'{user.full_name} has been rejected.', 'warning')
    return redirect(url_for('admin.developer_detail', user_id=user_id))


@admin_bp.route('/developer/<int:user_id>/suspend', methods=['POST'])
@login_required
@admin_required
def suspend_developer(user_id):
    """Suspend a developer"""
    user = User.query.filter_by(id=user_id, role='developer').first_or_404()
    user.status = 'suspended'
    db.session.commit()
    
    flash(f'{user.full_name} has been suspended.', 'warning')
    return redirect(url_for('admin.developer_detail', user_id=user_id))


# ============ KYC Management ============

@admin_bp.route('/kyc')
@login_required
@admin_required
def kyc_list():
    """List all KYC submissions"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'pending')
    
    query = KYCDocument.query
    
    if status:
        query = query.filter_by(status=status)
    
    kyc_docs = query.order_by(KYCDocument.submitted_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/kyc_list.html',
                         kyc_docs=kyc_docs,
                         current_status=status)


@admin_bp.route('/kyc/<int:kyc_id>')
@login_required
@admin_required
def kyc_detail(kyc_id):
    """KYC document detail"""
    kyc = KYCDocument.query.get_or_404(kyc_id)
    return render_template('admin/kyc_detail.html', kyc=kyc)


@admin_bp.route('/kyc/<int:kyc_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_kyc(kyc_id):
    """Approve KYC document"""
    kyc = KYCDocument.query.get_or_404(kyc_id)
    notes = request.form.get('notes', '')
    
    kyc.approve(current_user.id, notes)
    
    # Check if all KYC documents are approved
    all_approved = all(doc.status == 'approved' for doc in kyc.user.kyc_documents)
    if all_approved:
        kyc.user.status = 'verified'
    
    db.session.commit()
    
    flash('KYC document approved successfully.', 'success')
    return redirect(url_for('admin.kyc_list'))


@admin_bp.route('/kyc/<int:kyc_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_kyc(kyc_id):
    """Reject KYC document"""
    kyc = KYCDocument.query.get_or_404(kyc_id)
    reason = request.form.get('reason', 'Document rejected')
    notes = request.form.get('notes', '')
    
    kyc.reject(current_user.id, reason, notes)
    db.session.commit()
    
    flash('KYC document rejected.', 'warning')
    return redirect(url_for('admin.kyc_list'))


# ============ Article Management ============

@admin_bp.route('/articles')
@login_required
@admin_required
def articles():
    """List all articles"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = Article.query
    
    if status:
        query = query.filter_by(status=status)
    
    articles = query.order_by(Article.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/articles.html',
                         articles=articles,
                         current_status=status)


@admin_bp.route('/article/<int:article_id>')
@login_required
@admin_required
def article_detail(article_id):
    """Article detail for review"""
    article = Article.query.get_or_404(article_id)
    return render_template('admin/article_detail.html', article=article)


@admin_bp.route('/article/<int:article_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_article(article_id):
    """Approve an article"""
    article = Article.query.get_or_404(article_id)
    article.status = 'approved'
    article.reviewed_by = current_user.id
    article.reviewed_at = datetime.utcnow()
    article.published_at = datetime.utcnow()
    
    # Update developer's article count
    if article.developer:
        article.developer.articles_count = Article.query.filter_by(
            developer_id=article.developer_id, status='approved'
        ).count() + 1
    
    db.session.commit()
    
    flash('Article approved and published.', 'success')
    return redirect(url_for('admin.articles'))


@admin_bp.route('/article/<int:article_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_article(article_id):
    """Reject an article"""
    article = Article.query.get_or_404(article_id)
    reason = request.form.get('reason', '')
    
    article.status = 'rejected'
    article.rejection_reason = reason
    article.reviewed_by = current_user.id
    article.reviewed_at = datetime.utcnow()
    
    db.session.commit()
    
    flash('Article rejected.', 'warning')
    return redirect(url_for('admin.articles'))


@admin_bp.route('/article/<int:article_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_article(article_id):
    """Edit article content"""
    article = Article.query.get_or_404(article_id)
    
    if request.method == 'POST':
        article.title = request.form.get('title')
        article.excerpt = request.form.get('excerpt')
        article.content = request.form.get('content')
        article.article_type = request.form.get('article_type')
        article.domain = request.form.get('domain')
        
        # Parse technologies
        tech_str = request.form.get('technologies', '')
        if tech_str:
            tech_list = [t.strip() for t in tech_str.split(',') if t.strip()]
            article.set_technologies_list(tech_list)
        else:
            article.set_technologies_list([])
            
        # Handle Cover Image
        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file and file.filename:
                # Save new file
                filename = save_file(file, 'articles')
                if filename:
                    # Update article
                    article.cover_image = filename
                else:
                    flash('Invalid image file. Allowed formats: PNG, JPG, JPEG, GIF.', 'warning')
            else:
                 flash('No file selected.', 'warning')
            
        # Update slug if title changed (optional, but good for SEO)
        # article.generate_slug() 
        # Commented out to avoid breaking existing links unless desired
        
        db.session.commit()
        
        flash('Article updated successfully.', 'success')
        return redirect(url_for('admin.article_detail', article_id=article.id))
        
    return render_template('admin/edit_article.html', article=article)


@admin_bp.route('/article/<int:article_id>/hide', methods=['POST'])
@login_required
@admin_required
def hide_article(article_id):
    """Hide (unpublish) an article"""
    article = Article.query.get_or_404(article_id)
    article.status = 'hidden'
    db.session.commit()
    
    flash('Article has been hidden from the community.', 'info')
    return redirect(url_for('admin.articles'))


@admin_bp.route('/article/<int:article_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_article(article_id):
    """Delete an article permanently"""
    article = Article.query.get_or_404(article_id)
    
    # Delete cover image if exists
    if article.cover_image:
        from app.utils.helpers import delete_file
        delete_file(article.cover_image, 'articles')
        
    db.session.delete(article)
    db.session.commit()
    
    flash('Article deleted permanently.', 'success')
    return redirect(url_for('admin.articles'))


# ============ Project Management ============

@admin_bp.route('/projects')
@login_required
@admin_required
def projects():
    """List all projects"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = Project.query
    
    if status:
        query = query.filter_by(status=status)
    
    projects = query.order_by(Project.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/projects.html',
                         projects=projects,
                         current_status=status)


@admin_bp.route('/project/<int:project_id>')
@login_required
@admin_required
def project_detail(project_id):
    """Project detail page"""
    project = Project.query.get_or_404(project_id)
    
    # Get available developers for team formation
    available_developers = DeveloperProfile.query\
        .join(User)\
        .filter(User.status == 'verified')\
        .filter(DeveloperProfile.availability == 'available')\
        .all()
    
    return render_template('admin/project_detail.html',
                         project=project,
                         available_developers=available_developers)


@admin_bp.route('/project/<int:project_id>/update-status', methods=['POST'])
@login_required
@admin_required
def update_project_status(project_id):
    """Update project status"""
    project = Project.query.get_or_404(project_id)
    new_status = request.form.get('status')
    notes = request.form.get('notes', '')
    
    if new_status:
        project.status = new_status
        if notes:
            project.admin_notes = notes
        project.reviewed_by = current_user.id
        project.reviewed_at = datetime.utcnow()
        db.session.commit()
        
        flash(f'Project status updated to {new_status}.', 'success')
    
    return redirect(url_for('admin.project_detail', project_id=project_id))


# ============ Team Management ============

@admin_bp.route('/teams')
@login_required
@admin_required
def teams():
    """List all teams"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = Team.query
    
    if status:
        query = query.filter_by(status=status)
    
    teams = query.order_by(Team.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/teams.html',
                         teams=teams,
                         current_status=status)


@admin_bp.route('/team/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_team():
    """Create a new team"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        project_id = request.form.get('project_id', type=int)
        lead_developer_id = request.form.get('lead_developer_id', type=int)
        deadline = request.form.get('deadline')
        
        team = Team(
            name=name,
            description=description,
            project_id=project_id,
            lead_developer_id=lead_developer_id,
            created_by=current_user.id
        )
        
        if deadline:
            team.deadline = datetime.strptime(deadline, '%Y-%m-%d')
        
        db.session.add(team)
        db.session.flush()
        
        # Add lead as team member
        if lead_developer_id:
            lead_member = TeamMember(
                team_id=team.id,
                developer_id=lead_developer_id,
                role='Team Lead'
            )
            db.session.add(lead_member)
        
        # Update project status if linked
        if project_id:
            project = Project.query.get(project_id)
            if project:
                project.status = 'team_forming'
                project.assigned_team_id = team.id
        
        db.session.commit()
        
        flash('Team created successfully.', 'success')
        return redirect(url_for('admin.team_detail', team_id=team.id))
    
    # Get projects without teams
    available_projects = Project.query.filter(
        Project.assigned_team_id.is_(None),
        Project.status.in_(['submitted', 'reviewing', 'approved'])
    ).all()
    
    available_developers = DeveloperProfile.query\
        .join(User)\
        .filter(User.status == 'verified')\
        .all()
    
    return render_template('admin/create_team.html',
                         available_projects=available_projects,
                         available_developers=available_developers)


@admin_bp.route('/team/<int:team_id>')
@login_required
@admin_required
def team_detail(team_id):
    """Team detail page"""
    team = Team.query.get_or_404(team_id)
    
    available_developers = DeveloperProfile.query\
        .join(User)\
        .filter(User.status == 'verified')\
        .all()
    
    return render_template('admin/team_detail.html',
                         team=team,
                         available_developers=available_developers)


@admin_bp.route('/team/<int:team_id>/add-member', methods=['POST'])
@login_required
@admin_required
def add_team_member(team_id):
    """Add member to team"""
    team = Team.query.get_or_404(team_id)
    developer_id = request.form.get('developer_id', type=int)
    role = request.form.get('role', '')
    
    # Check if already a member
    existing = TeamMember.query.filter_by(
        team_id=team_id, developer_id=developer_id
    ).first()
    
    if existing:
        flash('Developer is already a team member.', 'warning')
    else:
        member = TeamMember(
            team_id=team_id,
            developer_id=developer_id,
            role=role
        )
        db.session.add(member)
        db.session.commit()
        flash('Team member added successfully.', 'success')
    
    return redirect(url_for('admin.team_detail', team_id=team_id))


@admin_bp.route('/team/<int:team_id>/remove-member/<int:member_id>', methods=['POST'])
@login_required
@admin_required
def remove_team_member(team_id, member_id):
    """Remove member from team"""
    member = TeamMember.query.filter_by(id=member_id, team_id=team_id).first_or_404()
    db.session.delete(member)
    db.session.commit()
    
    flash('Team member removed.', 'info')
    return redirect(url_for('admin.team_detail', team_id=team_id))


@admin_bp.route('/team/<int:team_id>/start', methods=['POST'])
@login_required
@admin_required
def start_team(team_id):
    """Start team work"""
    team = Team.query.get_or_404(team_id)
    team.start()
    
    if team.project:
        team.project.status = 'in_progress'
    
    db.session.commit()
    
    flash('Team work started.', 'success')
    return redirect(url_for('admin.team_detail', team_id=team_id))


# ============ Client Management ============

@admin_bp.route('/clients')
@login_required
@admin_required
def clients():
    """List all clients"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = User.query.filter_by(role='client')
    
    if search:
        query = query.filter(
            (User.full_name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    
    clients = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/clients.html',
                         clients=clients,
                         search=search)


@admin_bp.route('/client/<int:user_id>')
@login_required
@admin_required
def client_detail(user_id):
    """Client detail page"""
    user = User.query.filter_by(id=user_id, role='client').first_or_404()
    projects = Project.query.filter_by(client_id=user.client_profile.id if user.client_profile else 0).all()
    appointments = Appointment.query.filter_by(client_id=user.client_profile.id if user.client_profile else 0).all()
    
    return render_template('admin/client_detail.html',
                         user=user,
                         projects=projects,
                         appointments=appointments)


# ============ Appointments Management ============

@admin_bp.route('/appointments')
@login_required
@admin_required
def appointments():
    """List all appointments"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = Appointment.query
    
    if status:
        query = query.filter_by(status=status)
    
    appointments = query.order_by(Appointment.scheduled_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/appointments.html',
                         appointments=appointments,
                         current_status=status)
