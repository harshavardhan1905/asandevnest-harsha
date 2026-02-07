"""
Admin Lead & Student Project Management Routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import (
    User, Lead, LeadFollowUp, StudentProject, 
    Payment, PaymentTransaction, ProjectDocument, DeveloperAssignment, DeveloperProfile,
    ProjectMilestone
)
from app.utils.decorators import admin_required
from app.utils.helpers import save_file
from datetime import datetime
from decimal import Decimal
import os
import json

admin_leads_bp = Blueprint('admin_leads', __name__)

@admin_leads_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Lead Management Dashboard"""
    # Financial Stats
    total_revenue = db.session.query(db.func.sum(Payment.total_cost)).scalar() or 0
    total_dev_cost = db.session.query(db.func.sum(DeveloperAssignment.payout_amount)).scalar() or 0
    total_profit = Decimal(total_revenue) - Decimal(total_dev_cost)
    
    stats = {
        'total_leads': Lead.query.count(),
        'active_follow_ups': Lead.query.filter(Lead.status.in_(['New Lead', 'Follow-up'])).count(),
        'confirmed_projects': StudentProject.query.count(),
        'ongoing_projects': StudentProject.query.filter(StudentProject.status == 'In Progress').count(),
        'completed_projects': StudentProject.query.filter(StudentProject.status == 'Completed').count(),
        'pending_payments': db.session.query(db.func.sum(Payment.pending_balance)).scalar() or 0,
        'total_revenue': total_revenue,
        'total_dev_cost': total_dev_cost,
        'total_profit': total_profit
    }
    
    recent_leads = Lead.query.order_by(Lead.created_at.desc()).limit(5).all()
    upcoming_callbacks = LeadFollowUp.query.filter(LeadFollowUp.callback_datetime >= datetime.utcnow())\
        .order_by(LeadFollowUp.callback_datetime.asc()).limit(5).all()
        
    # Sales Leaderboard
    leaderboard = db.session.query(
        User,
        db.func.count(StudentProject.id).label('project_count'),
        db.func.sum(Payment.total_cost).label('revenue')
    ).join(StudentProject, User.id == StudentProject.closed_by_id)\
     .join(Payment, StudentProject.id == Payment.project_id)\
     .group_by(User.id)\
     .order_by(db.desc('revenue')).all()
    
    return render_template('admin/leads/dashboard.html', 
                         stats=stats, 
                         recent_leads=recent_leads,
                         upcoming_callbacks=upcoming_callbacks,
                         leaderboard=leaderboard)

@admin_leads_bp.route('/leads')
@login_required
@admin_required
def lead_list():
    """List and filter leads"""
    status = request.args.get('status')
    domain = request.args.get('domain')
    
    query = Lead.query
    if status:
        query = query.filter_by(status=status)
    if domain:
        query = query.filter_by(domain=domain)
        
    leads = query.order_by(Lead.created_at.desc()).all()
    return render_template('admin/leads/list.html', leads=leads)

@admin_leads_bp.route('/leads/export')
@login_required
@admin_required
def export_leads():
    """Export leads to CSV"""
    import csv
    import io
    from flask import make_response
    
    leads = Lead.query.order_by(Lead.created_at.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['ID', 'Student Name', 'Phone', 'Email', 'College', 'Domain', 'Source', 'Status', 'Confirm Project', 'Created At'])
    
    for lead in leads:
        writer.writerow([
            lead.id,
            lead.student_name,
            lead.phone,
            lead.email or '',
            lead.college or '',
            lead.domain or '',
            lead.source or '',
            lead.status,
            lead.confirmed_project.title if lead.confirmed_project else 'N/A',
            lead.created_at.strftime('%Y-%m-%d %H:%M')
        ])
        
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=leads_export.csv"
    response.headers["Content-Type"] = "text/csv"
    return response

@admin_leads_bp.route('/leads/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_lead():
    """Manual lead entry"""
    if request.method == 'POST':
        lead = Lead(
            student_name=request.form.get('student_name'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            college=request.form.get('college'),
            domain=request.form.get('domain'),
            source=request.form.get('source'),
            requirement_summary=request.form.get('requirement_summary'),
            status='New Lead'
        )
        db.session.add(lead)
        db.session.commit()
        flash('Lead added successfully.', 'success')
        return redirect(url_for('admin_leads.lead_list'))
        
    return render_template('admin/leads/add_lead.html')

@admin_leads_bp.route('/leads/<int:lead_id>')
@login_required
@admin_required
def lead_detail(lead_id):
    """Lead details and follow-up timeline"""
    lead = Lead.query.get_or_404(lead_id)
    admins = User.query.filter_by(role='admin').all()
    return render_template('admin/leads/lead_detail.html', lead=lead, admins=admins)

@admin_leads_bp.route('/leads/<int:lead_id>/follow-up', methods=['POST'])
@login_required
@admin_required
def add_follow_up(lead_id):
    """Add follow-up note"""
    lead = Lead.query.get_or_404(lead_id)
    
    callback_date = request.form.get('callback_date')
    callback_time = request.form.get('callback_time')
    callback_dt = None
    if callback_date and callback_time:
        callback_dt = datetime.strptime(f"{callback_date} {callback_time}", '%Y-%m-%d %H:%M')
        
    
    # Determine who made the interaction
    interacted_by_id = request.form.get('interacted_by_id')
    print(f"DEBUG: interacted_by_id received: {interacted_by_id}") # Debug logging
    
    creator_id = current_user.id
    if interacted_by_id and interacted_by_id.isdigit():
        creator_id = int(interacted_by_id)
        
    follow_up = LeadFollowUp(
        lead_id=lead_id,
        interaction_notes=request.form.get('notes'),
        callback_datetime=callback_dt,
        status_at_time=request.form.get('status'),
        created_by=creator_id
    )
    
    lead.status = request.form.get('status')
    db.session.add(follow_up)
    db.session.commit()
    
    flash('Follow-up record added.', 'success')
    return redirect(url_for('admin_leads.lead_detail', lead_id=lead_id))

@admin_leads_bp.route('/leads/<int:lead_id>/confirm', methods=['GET', 'POST'])
@login_required
@admin_required
def confirm_project(lead_id):
    """Convert lead to confirmed project"""
    lead = Lead.query.get_or_404(lead_id)
    
    if request.method == 'POST':
        # Create student project
        project = StudentProject(
            lead_id=lead_id,
            title=request.form.get('title'),
            scope=request.form.get('scope'),
            timeline_weeks=request.form.get('timeline_weeks'),
            academic_requirements=request.form.get('academic_requirements'),
            status='Confirmed'
        )
        project.set_tech_stack_list(request.form.getlist('tech_stack'))
        
        # Create initial payment/commercial record
        total_cost = Decimal(request.form.get('total_cost', '0'))
        payment = Payment(
            project=project,
            total_cost=total_cost,
            payment_structure=request.form.get('payment_structure'),
            pending_balance=total_cost
        )
        
        # Handle Developer Assignment
        developer_id = request.form.get('developer_id')
        payout_amount = Decimal(request.form.get('payout_amount', '0'))
        
        if developer_id == 'admin_built':
            # Option to build from admin side
            # Check if specific admin assignee is selected
            admin_assignee_id = request.form.get('admin_assignee_id')
            assigned_dev_id = current_user.id
            role = 'Admin Builder'
            
            if admin_assignee_id:
                assigned_dev_id = int(admin_assignee_id)
                role = 'Admin Builder (Assigned)'
            
            assignment = DeveloperAssignment(
                project=project,
                developer_id=assigned_dev_id, 
                role=role,
                payout_amount=payout_amount,
                internal_notes='Project being built directly by Admin Team.'
            )
            db.session.add(assignment)
        elif developer_id:
            # Assign specific developer
            assignment = DeveloperAssignment(
                project=project,
                developer_id=int(developer_id),
                role='Lead Developer',
                payout_amount=payout_amount
            )
            db.session.add(assignment)

        # Confirm metadata
        project.closed_by_id = request.form.get('closed_by_id')
        project.confirmed_by_id = current_user.id

        lead.status = 'Confirmed'
        # Create default milestones
        default_milestones = [
            'Project Confirmed & Advance Received',
            'Review 1',
            'Developer Assignment',
            'Review 2 Demo',
            'Delivery of the Projects'
        ]
        
        for title in default_milestones:
            milestone = ProjectMilestone(project=project, title=title)
            db.session.add(milestone)

        flash('Project confirmed and developer assigned successfully.', 'success')
        db.session.commit()
        
        return redirect(url_for('admin_leads.project_detail', project_id=project.id))
    
    # Get verified developers for assignment
    developers = User.query.filter_by(role='developer', status='verified').all()
    # Get all admins for responsibility tracking
    admins = User.query.filter_by(role='admin').all()
    
    return render_template('admin/leads/confirm_project.html', lead=lead, developers=developers, admins=admins)

@admin_leads_bp.route('/projects/<int:project_id>')
@login_required
@admin_required
def project_detail(project_id):
    """Project details including commercials, assignments, and docs"""
    project = StudentProject.query.get_or_404(project_id)
    developers = User.query.filter_by(role='developer', status='verified').all()
    
    return render_template('admin/leads/project_detail.html', 
                         project=project, 
                         developers=developers)

@admin_leads_bp.route('/projects/<int:project_id>/update-commercials', methods=['POST'])
@login_required
@admin_required
def update_commercials(project_id):
    """Update payment and balance"""
    project = StudentProject.query.get_or_404(project_id)
    payment = Payment.query.filter_by(project_id=project_id).first()
    
    amount_paid = Decimal(request.form.get('amount_paid', '0'))
    payment.amount_paid += amount_paid
    payment.pending_balance = Decimal(payment.total_cost) - Decimal(payment.amount_paid)
    payment.payment_mode = request.form.get('payment_mode')
    payment.invoice_ref = request.form.get('invoice_ref')
    
    # Record individual transaction history
    transaction = PaymentTransaction(
        payment=payment,
        amount=amount_paid,
        payment_mode=request.form.get('payment_mode'),
        invoice_ref=request.form.get('invoice_ref'),
        notes=f"Recorded on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    db.session.add(transaction)
    
    db.session.commit()
    flash('Payment details updated.', 'success')
    return redirect(url_for('admin_leads.project_detail', project_id=project_id))

@admin_leads_bp.route('/projects/<int:project_id>/invoice/<int:transaction_id>')
@login_required
@admin_required
def download_invoice(project_id, transaction_id):
    """Generate and download PDF invoice"""
    from app.utils.invoice_generator import generate_invoice_pdf
    from flask import send_file
    
    project = StudentProject.query.get_or_404(project_id)
    transaction = PaymentTransaction.query.get_or_404(transaction_id)
    
    # Ensure transaction belongs to project
    if transaction.payment.project_id != project.id:
        flash('Invalid transaction for this project', 'error')
        return redirect(url_for('admin_leads.project_detail', project_id=project_id))
        
    pdf_buffer = generate_invoice_pdf(transaction, project, project.lead)
    
    pdf_buffer = generate_invoice_pdf(transaction, project, project.lead)
    
    # Check if view mode is requested
    as_attachment = True
    if request.args.get('view') == 'true':
        as_attachment = False
        
    return send_file(
        pdf_buffer,
        as_attachment=as_attachment,
        download_name=f"Invoice_{transaction.invoice_ref or transaction.id}.pdf",
        mimetype='application/pdf'
    )

@admin_leads_bp.route('/projects/<int:project_id>/milestone/<int:milestone_id>/toggle')
@login_required
@admin_required
def toggle_milestone(project_id, milestone_id):
    """Toggle milestone status"""
    project = StudentProject.query.get_or_404(project_id)
    milestone = ProjectMilestone.query.get_or_404(milestone_id)
    
    if milestone.project_id != project.id:
        flash('Invalid milestone', 'error')
        return redirect(url_for('admin_leads.project_detail', project_id=project_id))
        
    if milestone.status == 'Pending':
        milestone.status = 'Completed'
        milestone.completed_at = datetime.utcnow()
    else:
        milestone.status = 'Pending'
        milestone.completed_at = None
        
    db.session.commit()
    return redirect(url_for('admin_leads.project_detail', project_id=project_id))

@admin_leads_bp.route('/projects/<int:project_id>/upload-doc', methods=['POST'])
@login_required
@admin_required
def upload_doc(project_id):
    """Upload project document"""
    project = StudentProject.query.get_or_404(project_id)
    
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('admin_leads.project_detail', project_id=project_id))
        
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('admin_leads.project_detail', project_id=project_id))
        
    if file:
        filename = save_file(file, 'projects')
        doc = ProjectDocument(
            project_id=project_id,
            document_type=request.form.get('doc_type'),
            file_path=filename,
            original_name=file.filename
        )
        db.session.add(doc)
        db.session.commit()
        flash('Document uploaded successfully.', 'success')
        
    return redirect(url_for('admin_leads.project_detail', project_id=project_id))

@admin_leads_bp.route('/projects/<int:project_id>/assign', methods=['POST'])
@login_required
@admin_required
def assign_developer(project_id):
    """Assign developer to project"""
    project = StudentProject.query.get_or_404(project_id)
    
    assignment = DeveloperAssignment(
        project_id=project_id,
        developer_id=int(request.form.get('developer_id')),
        role=request.form.get('role'),
        payout_amount=Decimal(request.form.get('payout_amount', '0')),
        internal_notes=request.form.get('internal_notes')
    )
    
    db.session.add(assignment)
    db.session.commit()
    flash('Developer assigned.', 'success')
    return redirect(url_for('admin_leads.project_detail', project_id=project_id))

@admin_leads_bp.route('/projects/<int:project_id>/update-repo', methods=['POST'])
@login_required
@admin_required
def update_repo(project_id):
    """Update GitHub repository link"""
    project = StudentProject.query.get_or_404(project_id)
    repo_link = request.form.get('github_link')
    
    project.github_link = repo_link
    db.session.commit()
    
    flash('Repository link updated successfully.', 'success')
    return redirect(url_for('admin_leads.project_detail', project_id=project_id))

@admin_leads_bp.route('/projects')
@login_required
@admin_required
def project_list():
    """List student projects"""
    projects = StudentProject.query.order_by(StudentProject.created_at.desc()).all()
    return render_template('admin/leads/project_list.html', projects=projects)
