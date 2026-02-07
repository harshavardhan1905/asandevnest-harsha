"""
Lead and Project Management Models
"""

from datetime import datetime
from app import db
import json

class Lead(db.Model):
    """Student Lead Management"""
    __tablename__ = 'leads'
    
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    college = db.Column(db.String(200))
    domain = db.Column(db.String(100))  # AI, Web, IoT, etc.
    source = db.Column(db.String(50))  # call, WhatsApp, referral, website
    requirement_summary = db.Column(db.Text)
    status = db.Column(db.String(30), default='New Lead')  # New, Follow-up, Interested, Confirmed, Dropped
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    follow_ups = db.relationship('LeadFollowUp', backref='lead', lazy=True, cascade="all, delete-orphan")
    confirmed_project = db.relationship('StudentProject', backref='lead', uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'student_name': self.student_name,
            'phone': self.phone,
            'email': self.email,
            'college': self.college,
            'domain': self.domain,
            'source': self.source,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class LeadFollowUp(db.Model):
    """Follow-up tracking for Leads"""
    __tablename__ = 'lead_follow_ups'
    
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=False)
    interaction_notes = db.Column(db.Text, nullable=False)
    callback_datetime = db.Column(db.DateTime)
    status_at_time = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # Admin who made the call
    
    # Relationship
    user = db.relationship('User', foreign_keys=[created_by])

class StudentProject(db.Model):
    """Confirmed Student Projects"""
    __tablename__ = 'student_projects'
    
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), unique=True) # Linked if converted from lead
    
    # Responsibility tracking
    closed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Sales rep / Admin who closed the deal
    confirmed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Admin who performed confirmation

    
    # Project Details
    title = db.Column(db.String(200), nullable=False)
    scope = db.Column(db.Text)
    tech_stack = db.Column(db.Text)  # JSON array
    timeline_weeks = db.Column(db.Integer)
    academic_requirements = db.Column(db.Text)  # College specific format/needs
    github_link = db.Column(db.String(255))
    
    # Status
    status = db.Column(db.String(30), default='Confirmed')  # Confirmed, In Progress, Delivered, Completed
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    payments = db.relationship('Payment', backref='project', lazy=True, cascade="all, delete-orphan")
    documents = db.relationship('ProjectDocument', backref='project', lazy=True, cascade="all, delete-orphan")
    assignments = db.relationship('DeveloperAssignment', backref='project', lazy=True, cascade="all, delete-orphan")
    milestones = db.relationship('ProjectMilestone', backref='project', lazy=True, cascade="all, delete-orphan", order_by="ProjectMilestone.id")

    # User Relationships
    closed_by = db.relationship('User', foreign_keys=[closed_by_id])
    confirmed_by = db.relationship('User', foreign_keys=[confirmed_by_id])


    def get_tech_stack_list(self):
        if self.tech_stack:
            try:
                return json.loads(self.tech_stack)
            except:
                return []
        return []

    def set_tech_stack_list(self, tech_list):
        self.tech_stack = json.dumps(tech_list)

class Payment(db.Model):
    """Commercials and Payments"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('student_projects.id'), nullable=False)
    
    total_cost = db.Column(db.Numeric(12, 2), nullable=False)
    payment_structure = db.Column(db.String(100))  # e.g., "50% Advance, 50% Delivery"
    amount_paid = db.Column(db.Numeric(12, 2), default=0.0)
    pending_balance = db.Column(db.Numeric(12, 2))
    payment_mode = db.Column(db.String(50))  # UPI, Cash, Bank Transfer
    invoice_ref = db.Column(db.String(50))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('PaymentTransaction', backref='payment', lazy=True, cascade="all, delete-orphan")

class PaymentTransaction(db.Model):
    """Individual payment record / history"""
    __tablename__ = 'payment_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=False)
    
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_mode = db.Column(db.String(50))
    invoice_ref = db.Column(db.String(100))
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

class ProjectDocument(db.Model):
    """Project Documents Mapping"""
    __tablename__ = 'project_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('student_projects.id'), nullable=False)
    
    document_type = db.Column(db.String(50))  # Proposal, SRS, PPT, Source Code, Delivery
    file_path = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255))
    
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProjectMilestone(db.Model):
    """Milestones for Student Projects"""
    __tablename__ = 'project_milestones'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('student_projects.id'), nullable=False)
    
    title = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='Pending') # Pending, Completed
    completed_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DeveloperAssignment(db.Model):
    """Assignments for Student Projects"""
    __tablename__ = 'developer_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('student_projects.id'), nullable=False)
    developer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    role = db.Column(db.String(50), default='Developer')  # Developer, Mentor
    payout_amount = db.Column(db.Numeric(12, 2), default=0.0)
    internal_notes = db.Column(db.Text)
    
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to get developer info easily
    developer = db.relationship('User', foreign_keys=[developer_id])
