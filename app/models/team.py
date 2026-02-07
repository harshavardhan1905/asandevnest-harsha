"""
Team Models - Admin-managed team formation
"""

from datetime import datetime
from app import db


class Team(db.Model):
    """Teams formed by Asan for project execution"""
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Team Info
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Project Assignment
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), unique=True)
    
    # Team Lead
    lead_developer_id = db.Column(db.Integer, db.ForeignKey('developer_profiles.id'))
    
    # Status & Timeline
    status = db.Column(db.String(30), default='forming')  # forming, active, completed, disbanded
    deadline = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Admin
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    members = db.relationship('TeamMember', backref='team', lazy='dynamic', cascade='all, delete-orphan')
    lead = db.relationship('DeveloperProfile', foreign_keys=[lead_developer_id])
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def get_member_count(self):
        return self.members.count()
    
    def get_status_badge_class(self):
        """Return CSS class for status badge"""
        status_classes = {
            'forming': 'bg-yellow-100 text-yellow-800',
            'active': 'bg-green-100 text-green-800',
            'completed': 'bg-blue-100 text-blue-800',
            'disbanded': 'bg-red-100 text-red-800'
        }
        return status_classes.get(self.status, 'bg-gray-100 text-gray-800')
    
    def start(self):
        """Mark team as active"""
        self.status = 'active'
        self.started_at = datetime.utcnow()
    
    def complete(self):
        """Mark team as completed"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'project_id': self.project_id,
            'lead_developer_id': self.lead_developer_id,
            'status': self.status,
            'member_count': self.get_member_count(),
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Team {self.name}>'


class TeamMember(db.Model):
    """Team membership junction table"""
    __tablename__ = 'team_members'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    developer_id = db.Column(db.Integer, db.ForeignKey('developer_profiles.id'), nullable=False)
    
    # Role in team
    role = db.Column(db.String(100))  # Backend Developer, Frontend Developer, DevOps, etc.
    responsibilities = db.Column(db.Text)
    
    # Status
    status = db.Column(db.String(20), default='active')  # invited, active, left
    
    # Timestamps
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    left_at = db.Column(db.DateTime)
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('team_id', 'developer_id', name='unique_team_member'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'team_id': self.team_id,
            'developer_id': self.developer_id,
            'developer': self.developer.to_dict() if self.developer else None,
            'role': self.role,
            'responsibilities': self.responsibilities,
            'status': self.status,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None
        }
    
    def __repr__(self):
        return f'<TeamMember {self.developer_id} in {self.team_id}>'
