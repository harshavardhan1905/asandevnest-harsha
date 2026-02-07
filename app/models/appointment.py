"""
Appointment Models - Booking system for 1-1 sessions
"""

from datetime import datetime
from app import db


class Appointment(db.Model):
    """Appointments between clients and developers"""
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client_profiles.id'), nullable=False)
    developer_id = db.Column(db.Integer, db.ForeignKey('developer_profiles.id'), nullable=False)
    
    # Appointment Details
    appointment_type = db.Column(db.String(50), nullable=False)  # class, consulting, support
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    
    # Schedule
    scheduled_at = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    timezone = db.Column(db.String(50), default='Asia/Kolkata')
    
    # Meeting Details
    meeting_link = db.Column(db.String(500))
    meeting_platform = db.Column(db.String(50))  # zoom, google_meet, teams
    
    # Status
    status = db.Column(db.String(30), default='pending')
    # pending -> confirmed -> in_progress -> completed / cancelled / no_show
    
    # Payment (optional)
    amount = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.String(10), default='USD')
    is_paid = db.Column(db.Boolean, default=False)
    
    # Notes & Feedback
    client_notes = db.Column(db.Text)  # Notes from client during booking
    developer_notes = db.Column(db.Text)  # Developer's internal notes
    feedback = db.Column(db.Text)  # Post-session feedback
    rating = db.Column(db.Integer)  # 1-5 rating
    
    # Cancellation
    cancelled_at = db.Column(db.DateTime)
    cancelled_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    cancellation_reason = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    developer = db.relationship('DeveloperProfile', backref='appointments')
    canceller = db.relationship('User', foreign_keys=[cancelled_by])
    
    def get_type_display(self):
        """Return human-readable appointment type"""
        types = {
            'class': 'Learning Session',
            'consulting': 'Consulting Call',
            'support': 'Technical Support'
        }
        return types.get(self.appointment_type, self.appointment_type)
    
    def get_status_badge_class(self):
        """Return CSS class for status badge"""
        status_classes = {
            'pending': 'bg-yellow-100 text-yellow-800',
            'confirmed': 'bg-blue-100 text-blue-800',
            'in_progress': 'bg-purple-100 text-purple-800',
            'completed': 'bg-green-100 text-green-800',
            'cancelled': 'bg-red-100 text-red-800',
            'no_show': 'bg-gray-100 text-gray-800'
        }
        return status_classes.get(self.status, 'bg-gray-100 text-gray-800')
    
    def confirm(self, meeting_link=None, platform='google_meet'):
        """Confirm the appointment"""
        self.status = 'confirmed'
        if meeting_link:
            self.meeting_link = meeting_link
            self.meeting_platform = platform
    
    def cancel(self, user_id, reason=None):
        """Cancel the appointment"""
        self.status = 'cancelled'
        self.cancelled_at = datetime.utcnow()
        self.cancelled_by = user_id
        self.cancellation_reason = reason
    
    def complete(self):
        """Mark appointment as completed"""
        self.status = 'completed'
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'developer_id': self.developer_id,
            'appointment_type': self.appointment_type,
            'type_display': self.get_type_display(),
            'title': self.title,
            'description': self.description,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'duration_minutes': self.duration_minutes,
            'meeting_link': self.meeting_link,
            'status': self.status,
            'amount': float(self.amount) if self.amount else None,
            'rating': self.rating,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Appointment {self.id}>'
