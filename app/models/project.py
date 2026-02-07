"""
Project Models - Client ideas and project management
"""

from datetime import datetime
from app import db
import json


class Project(db.Model):
    """Client project ideas and submissions"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client_profiles.id'), nullable=False)
    
    # Project Details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    detailed_requirements = db.Column(db.Text)
    
    # Classification
    project_type = db.Column(db.String(50))  # web_app, mobile_app, api, ai_ml, etc.
    technologies = db.Column(db.Text)  # JSON array
    domain = db.Column(db.String(100))  # Industry domain
    
    # Budget & Timeline
    budget_min = db.Column(db.Numeric(12, 2))
    budget_max = db.Column(db.Numeric(12, 2))
    budget_currency = db.Column(db.String(10), default='USD')
    timeline_weeks = db.Column(db.Integer)
    preferred_start_date = db.Column(db.Date)
    
    # Status
    status = db.Column(db.String(30), default='submitted')
    # submitted -> reviewing -> approved -> team_forming -> in_progress -> delivered -> completed
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    
    # Assignment
    assigned_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    assigned_at = db.Column(db.DateTime)
    
    # Delivery
    deadline = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    completion_notes = db.Column(db.Text)
    
    # Admin Notes
    admin_notes = db.Column(db.Text)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewed_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    team = db.relationship('Team', foreign_keys='Team.project_id', backref='project', uselist=False)
    messages = db.relationship('ProjectMessage', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])
    
    def get_technologies_list(self):
        """Return technologies as Python list"""
        if self.technologies:
            try:
                return json.loads(self.technologies)
            except:
                return []
        return []
    
    def set_technologies_list(self, tech_list):
        """Set technologies from Python list"""
        self.technologies = json.dumps(tech_list)
    
    def get_budget_display(self):
        """Return formatted budget range"""
        if self.budget_min and self.budget_max:
            return f"{self.budget_currency} {self.budget_min:,.0f} - {self.budget_max:,.0f}"
        elif self.budget_min:
            return f"{self.budget_currency} {self.budget_min:,.0f}+"
        return "Budget not specified"
    
    def get_status_badge_class(self):
        """Return CSS class for status badge"""
        status_classes = {
            'submitted': 'bg-blue-100 text-blue-800',
            'reviewing': 'bg-yellow-100 text-yellow-800',
            'approved': 'bg-green-100 text-green-800',
            'team_forming': 'bg-purple-100 text-purple-800',
            'in_progress': 'bg-indigo-100 text-indigo-800',
            'delivered': 'bg-emerald-100 text-emerald-800',
            'completed': 'bg-green-100 text-green-800',
            'cancelled': 'bg-red-100 text-red-800'
        }
        return status_classes.get(self.status, 'bg-gray-100 text-gray-800')
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'title': self.title,
            'description': self.description,
            'project_type': self.project_type,
            'technologies': self.get_technologies_list(),
            'domain': self.domain,
            'budget_display': self.get_budget_display(),
            'timeline_weeks': self.timeline_weeks,
            'status': self.status,
            'priority': self.priority,
            'team_id': self.assigned_team_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Project {self.title}>'


class ProjectMessage(db.Model):
    """Messages/updates for projects"""
    __tablename__ = 'project_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    message_type = db.Column(db.String(30), default='message')  # message, update, milestone, file
    content = db.Column(db.Text, nullable=False)
    attachment = db.Column(db.String(255))  # File path
    
    is_internal = db.Column(db.Boolean, default=False)  # Admin-only message
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sender = db.relationship('User', backref='project_messages')
    
    def get_attachment_url(self):
        if self.attachment:
            return f'/uploads/projects/{self.attachment}'
        return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'sender': self.sender.to_dict() if self.sender else None,
            'message_type': self.message_type,
            'content': self.content,
            'attachment': self.get_attachment_url(),
            'is_internal': self.is_internal,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ProjectMessage {self.id}>'
