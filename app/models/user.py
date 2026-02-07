"""
User Models - Admin, Developer, Client
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
import json


class User(UserMixin, db.Model):
    """Base User model for all roles"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='client')  # admin, developer, client
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    avatar = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')  # pending, verified, rejected, suspended
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    developer_profile = db.relationship('DeveloperProfile', backref='user', uselist=False, lazy=True)
    client_profile = db.relationship('ClientProfile', backref='user', uselist=False, lazy=True)
    kyc_documents = db.relationship('KYCDocument', foreign_keys='KYCDocument.user_id', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_developer(self):
        return self.role == 'developer'
    
    def is_client(self):
        return self.role == 'client'
    
    def is_verified(self):
        return self.status == 'verified'
    
    def get_avatar_url(self):
        """Return avatar URL or default"""
        if self.avatar:
            return f'/uploads/avatars/{self.avatar}'
        return '/static/images/default-avatar.png'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'status': self.status,
            'avatar': self.get_avatar_url(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'


class DeveloperProfile(db.Model):
    """Developer-specific profile information"""
    __tablename__ = 'developer_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Professional Info
    tagline = db.Column(db.String(200))  # Short professional tagline
    bio = db.Column(db.Text)
    experience_years = db.Column(db.Integer, default=0)
    
    # Skills & Expertise (stored as JSON)
    skills = db.Column(db.Text)  # JSON array: ["Python", "React", "AWS"]
    domains = db.Column(db.Text)  # JSON array: ["FinTech", "HealthTech", "AI"]
    
    # Availability & Rates
    availability = db.Column(db.String(20), default='available')  # available, busy, unavailable
    hourly_rate = db.Column(db.Numeric(10, 2))
    offers_classes = db.Column(db.Boolean, default=False)
    offers_consulting = db.Column(db.Boolean, default=False)
    offers_support = db.Column(db.Boolean, default=False)
    
    # External Links
    portfolio_url = db.Column(db.String(255))
    linkedin_url = db.Column(db.String(255))
    github_url = db.Column(db.String(255))
    twitter_url = db.Column(db.String(255))
    
    # Stats
    articles_count = db.Column(db.Integer, default=0)
    projects_completed = db.Column(db.Integer, default=0)
    rating = db.Column(db.Numeric(3, 2), default=0.0)
    reviews_count = db.Column(db.Integer, default=0)
    
    # Relationships
    articles = db.relationship('Article', backref='developer', lazy='dynamic')
    team_memberships = db.relationship('TeamMember', backref='developer', lazy='dynamic')
    
    def get_skills_list(self):
        """Return skills as Python list"""
        if self.skills:
            try:
                return json.loads(self.skills)
            except:
                return []
        return []
    
    def set_skills_list(self, skills_list):
        """Set skills from Python list"""
        self.skills = json.dumps(skills_list)
    
    def get_domains_list(self):
        """Return domains as Python list"""
        if self.domains:
            try:
                return json.loads(self.domains)
            except:
                return []
        return []
    
    def set_domains_list(self, domains_list):
        """Set domains from Python list"""
        self.domains = json.dumps(domains_list)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tagline': self.tagline,
            'bio': self.bio,
            'experience_years': self.experience_years,
            'skills': self.get_skills_list(),
            'domains': self.get_domains_list(),
            'availability': self.availability,
            'hourly_rate': float(self.hourly_rate) if self.hourly_rate else None,
            'rating': float(self.rating) if self.rating else 0,
            'reviews_count': self.reviews_count,
            'articles_count': self.articles_count,
            'projects_completed': self.projects_completed
        }
    
    def __repr__(self):
        return f'<DeveloperProfile {self.user_id}>'


class ClientProfile(db.Model):
    """Client-specific profile information"""
    __tablename__ = 'client_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Company Info
    company_name = db.Column(db.String(200))
    company_size = db.Column(db.String(50))  # startup, small, medium, enterprise
    industry = db.Column(db.String(100))
    website = db.Column(db.String(255))
    
    # Contact
    contact_name = db.Column(db.String(100))
    contact_position = db.Column(db.String(100))
    
    # Stats
    projects_submitted = db.Column(db.Integer, default=0)
    projects_completed = db.Column(db.Integer, default=0)
    
    # Relationships
    projects = db.relationship('Project', backref='client', lazy='dynamic')
    appointments = db.relationship('Appointment', backref='client', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_name': self.company_name,
            'company_size': self.company_size,
            'industry': self.industry,
            'website': self.website,
            'projects_submitted': self.projects_submitted,
            'projects_completed': self.projects_completed
        }
    
    def __repr__(self):
        return f'<ClientProfile {self.user_id}>'
