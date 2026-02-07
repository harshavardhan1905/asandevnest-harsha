"""
API Routes - JSON API endpoints
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import User, DeveloperProfile, Article, Project
from app import db

api_bp = Blueprint('api', __name__)


@api_bp.route('/search')
def search():
    """Global search endpoint"""
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'all')
    
    results = {'developers': [], 'articles': []}
    
    if not query:
        return jsonify(results)
    
    if search_type in ['all', 'developers']:
        developers = DeveloperProfile.query.join(User).filter(
            User.status == 'verified',
            (User.full_name.ilike(f'%{query}%')) |
            (DeveloperProfile.skills.ilike(f'%{query}%')) |
            (DeveloperProfile.domains.ilike(f'%{query}%'))
        ).limit(5).all()
        
        results['developers'] = [{
            'id': d.id,
            'name': d.user.full_name,
            'tagline': d.tagline,
            'skills': d.get_skills_list()[:3]
        } for d in developers]
    
    if search_type in ['all', 'articles']:
        articles = Article.query.filter(
            Article.status == 'approved',
            (Article.title.ilike(f'%{query}%')) |
            (Article.technologies.ilike(f'%{query}%'))
        ).limit(5).all()
        
        results['articles'] = [{
            'id': a.id,
            'title': a.title,
            'slug': a.slug,
            'excerpt': a.excerpt[:100] if a.excerpt else ''
        } for a in articles]
    
    return jsonify(results)


@api_bp.route('/developers')
def get_developers():
    """Get verified developers"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    skill = request.args.get('skill', '')
    domain = request.args.get('domain', '')
    
    query = DeveloperProfile.query.join(User).filter(User.status == 'verified')
    
    if skill:
        query = query.filter(DeveloperProfile.skills.contains(skill))
    if domain:
        query = query.filter(DeveloperProfile.domains.contains(domain))
    
    pagination = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'developers': [d.to_dict() for d in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@api_bp.route('/articles')
def get_articles():
    """Get published articles"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Article.query.filter_by(status='approved')
    pagination = query.order_by(Article.published_at.desc()).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'articles': [a.to_dict() for a in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@api_bp.route('/stats')
def get_stats():
    """Platform statistics"""
    return jsonify({
        'verified_developers': User.query.filter_by(role='developer', status='verified').count(),
        'published_articles': Article.query.filter_by(status='approved').count(),
        'total_clients': User.query.filter_by(role='client').count(),
        'projects_completed': Project.query.filter_by(status='completed').count()
    })
