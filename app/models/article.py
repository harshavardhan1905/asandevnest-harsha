"""
Article Models - Developer content & community
"""

from datetime import datetime
from app import db
from slugify import slugify
import json


class Article(db.Model):
    """Developer articles, case studies, and research"""
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    developer_id = db.Column(db.Integer, db.ForeignKey('developer_profiles.id'), nullable=False)
    
    # Content
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False, index=True)
    excerpt = db.Column(db.Text)  # Short summary
    content = db.Column(db.Text, nullable=False)  # Full content (HTML)
    cover_image = db.Column(db.String(255))
    
    # Classification
    article_type = db.Column(db.String(50), default='tutorial')  # case_study, research, tutorial, insight
    technologies = db.Column(db.Text)  # JSON array
    domain = db.Column(db.String(100))  # FinTech, HealthTech, SaaS, AI, etc.
    
    # Status & Moderation
    status = db.Column(db.String(20), default='draft')  # draft, pending, approved, rejected
    rejection_reason = db.Column(db.Text)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewed_at = db.Column(db.DateTime)
    
    # Stats
    views_count = db.Column(db.Integer, default=0)
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    
    # SEO
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.String(300))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    # Relationships
    comments = db.relationship('ArticleComment', backref='article', lazy='dynamic', cascade='all, delete-orphan')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])
    
    def generate_slug(self):
        """Generate unique slug from title"""
        base_slug = slugify(self.title)
        slug = base_slug
        counter = 1
        while Article.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        self.slug = slug
    
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
    
    def get_cover_url(self):
        """Return cover image URL or default"""
        if self.cover_image:
            return f'/uploads/articles/{self.cover_image}'
        return '/static/images/default-article-cover.jpg'
    
    def get_reading_time(self):
        """Estimate reading time in minutes"""
        words = len(self.content.split()) if self.content else 0
        return max(1, words // 200)
    
    def is_published(self):
        return self.status == 'approved' and self.published_at is not None
    
    def publish(self):
        """Mark article as published"""
        self.status = 'approved'
        self.published_at = datetime.utcnow()
    
    @property
    def reading_time_minutes(self):
        """Property for reading time"""
        return self.get_reading_time()
    
    def get_status_badge_class(self):
        """Return CSS class for status badge"""
        status_classes = {
            'draft': 'badge-secondary',
            'pending': 'badge-warning',
            'approved': 'badge-success',
            'rejected': 'badge-danger',
            'hidden': 'badge-secondary'
        }
        return status_classes.get(self.status, 'badge-secondary')
    
    def to_dict(self, include_content=False):
        data = {
            'id': self.id,
            'developer_id': self.developer_id,
            'title': self.title,
            'slug': self.slug,
            'excerpt': self.excerpt,
            'cover_image': self.get_cover_url(),
            'article_type': self.article_type,
            'technologies': self.get_technologies_list(),
            'domain': self.domain,
            'status': self.status,
            'views_count': self.views_count,
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'reading_time': self.get_reading_time(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }
        if include_content:
            data['content'] = self.content
        return data
    
    def __repr__(self):
        return f'<Article {self.title}>'


class ArticleComment(db.Model):
    """Comments on articles"""
    __tablename__ = 'article_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    content = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='comments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'article_id': self.article_id,
            'user': self.user.to_dict() if self.user else None,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ArticleComment {self.id}>'
