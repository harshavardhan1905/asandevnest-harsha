"""
KYC Models - Document verification for developers
"""

from datetime import datetime
from app import db


class KYCDocument(db.Model):
    """KYC documents submitted by developers"""
    __tablename__ = 'kyc_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Document Info
    document_type = db.Column(db.String(50), nullable=False)  # aadhar, pan, passport, driving_license
    document_number = db.Column(db.String(100))  # Masked/partial number
    document_path = db.Column(db.String(255), nullable=False)  # File path
    
    # Additional Info
    full_name_on_document = db.Column(db.String(200))
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.Text)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    rejection_reason = db.Column(db.Text)
    
    # Admin
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewed_at = db.Column(db.DateTime)
    admin_notes = db.Column(db.Text)  # Internal notes
    
    # Timestamps
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='kyc_reviews')
    
    def get_document_type_display(self):
        """Return human-readable document type"""
        types = {
            'aadhar': 'Aadhaar Card',
            'pan': 'PAN Card',
            'passport': 'Passport',
            'driving_license': 'Driving License',
            'voter_id': 'Voter ID'
        }
        return types.get(self.document_type, self.document_type)
    
    def get_document_url(self):
        """Return document file URL"""
        if self.document_path:
            return f'/uploads/kyc/{self.document_path}'
        return None
    
    def get_status_badge_class(self):
        """Return CSS class for status badge"""
        status_classes = {
            'pending': 'bg-yellow-100 text-yellow-800',
            'approved': 'bg-green-100 text-green-800',
            'rejected': 'bg-red-100 text-red-800'
        }
        return status_classes.get(self.status, 'bg-gray-100 text-gray-800')
    
    def approve(self, admin_id, notes=None):
        """Approve the KYC document"""
        self.status = 'approved'
        self.reviewed_by = admin_id
        self.reviewed_at = datetime.utcnow()
        self.admin_notes = notes
    
    def reject(self, admin_id, reason, notes=None):
        """Reject the KYC document"""
        self.status = 'rejected'
        self.rejection_reason = reason
        self.reviewed_by = admin_id
        self.reviewed_at = datetime.utcnow()
        self.admin_notes = notes
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'document_type': self.document_type,
            'document_type_display': self.get_document_type_display(),
            'document_url': self.get_document_url(),
            'status': self.status,
            'rejection_reason': self.rejection_reason,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None
        }
    
    def __repr__(self):
        return f'<KYCDocument {self.id}>'
