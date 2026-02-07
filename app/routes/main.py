"""
Main Routes - Public pages and landing
"""

from flask import Blueprint, render_template, request
from app.models import User, DeveloperProfile, Article

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page"""
    # Get featured developers (verified, with articles)
    featured_developers = DeveloperProfile.query\
        .join(User)\
        .filter(User.status == 'verified')\
        .order_by(DeveloperProfile.articles_count.desc())\
        .limit(4)\
        .all()
    
    # Get latest articles
    latest_articles = Article.query\
        .filter(Article.status == 'approved')\
        .order_by(Article.published_at.desc())\
        .limit(3)\
        .all()
    
    # Stats
    stats = {
        'developers': User.query.filter_by(role='developer', status='verified').count(),
        'articles': Article.query.filter_by(status='approved').count(),
        'clients': User.query.filter_by(role='client').count()
    }
    
    return render_template('public/index.html', 
                         featured_developers=featured_developers,
                         latest_articles=latest_articles,
                         stats=stats)


@main_bp.route('/about')
def about():
    """About Asan DevNest"""
    return render_template('public/about.html')


@main_bp.route('/how-it-works')
def how_it_works():
    """How Asan DevNest works"""
    return render_template('public/how_it_works.html')


@main_bp.route('/for-clients')
def for_clients():
    """Information for clients"""
    return render_template('public/for_clients.html')


@main_bp.route('/for-developers')
def for_developers():
    """Information for developers"""
    return render_template('public/for_developers.html')


@main_bp.route('/pricing')
def pricing():
    """Pricing information"""
    return render_template('public/pricing.html')


@main_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('public/contact.html')


@main_bp.route('/privacy')
def privacy():
    """Privacy policy"""
    return render_template('public/privacy.html')


@main_bp.route('/terms')
def terms():
    """Terms of service"""
    return render_template('public/terms.html')


@main_bp.route('/developers')
def developers_list():
    """Public list of verified developers"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Filters
    skill = request.args.get('skill', '')
    domain = request.args.get('domain', '')
    availability = request.args.get('availability', '')
    
    query = DeveloperProfile.query\
        .join(User)\
        .filter(User.status == 'verified')
    
    if skill:
        query = query.filter(DeveloperProfile.skills.contains(skill))
    
    if domain:
        query = query.filter(DeveloperProfile.domains.contains(domain))
    
    if availability:
        query = query.filter(DeveloperProfile.availability == availability)
    
    developers = query.order_by(DeveloperProfile.rating.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get all unique skills and domains for filters
    all_skills = ['Python', 'JavaScript', 'React', 'Node.js', 'Flutter', 'AWS', 'Docker', 'Kubernetes', 'TensorFlow', 'PyTorch']
    all_domains = ['FinTech', 'HealthTech', 'E-commerce', 'SaaS', 'AI/ML', 'Mobile Apps', 'Cloud Infrastructure', 'EdTech']
    
    return render_template('public/developers_list.html',
                         developers=developers,
                         all_skills=all_skills,
                         all_domains=all_domains,
                         current_skill=skill,
                         current_domain=domain,
                         current_availability=availability)


@main_bp.route('/developer/<int:developer_id>')
def developer_profile(developer_id):
    """Public developer profile"""
    developer = DeveloperProfile.query.get_or_404(developer_id)
    
    # Ensure developer is verified
    if developer.user.status != 'verified':
        return render_template('errors/404.html'), 404
    
    # Get developer's articles
    articles = Article.query\
        .filter_by(developer_id=developer_id, status='approved')\
        .order_by(Article.published_at.desc())\
        .limit(5)\
        .all()
    
    return render_template('public/developer_profile.html',
                         developer=developer,
                         articles=articles)
