"""
Articles Routes - Community page and article discovery
"""

from flask import Blueprint, render_template, request, redirect, url_for
from app.models import Article, DeveloperProfile, User
from app import db

articles_bp = Blueprint('articles', __name__)


@articles_bp.route('/')
def community():
    """Community articles page - main discovery hub"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Filters
    search = request.args.get('search', '')
    technology = request.args.get('technology', '')
    domain = request.args.get('domain', '')
    article_type = request.args.get('type', '')
    
    query = Article.query.filter_by(status='approved')
    
    if search:
        query = query.filter(
            (Article.title.ilike(f'%{search}%')) |
            (Article.excerpt.ilike(f'%{search}%')) |
            (Article.content.ilike(f'%{search}%'))
        )
    
    if technology:
        query = query.filter(Article.technologies.contains(technology))
    
    if domain:
        query = query.filter(Article.domain == domain)
    
    if article_type:
        query = query.filter(Article.article_type == article_type)
    
    articles = query.order_by(Article.published_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get filter options
    all_technologies = ['Python', 'JavaScript', 'React', 'Node.js', 'Flutter', 'AWS', 
                       'Docker', 'Kubernetes', 'TensorFlow', 'PyTorch', 'Vue.js', 'Angular']
    all_domains = ['FinTech', 'HealthTech', 'E-commerce', 'SaaS', 'AI/ML', 
                  'Mobile Apps', 'Cloud Infrastructure', 'EdTech', 'IoT']
    article_types = [
        ('case_study', 'Case Study'),
        ('research', 'Research'),
        ('tutorial', 'Tutorial'),
        ('insight', 'Industry Insight')
    ]
    
    # Featured articles (top 3 by views)
    featured = Article.query.filter_by(status='approved')\
        .order_by(Article.views_count.desc()).limit(3).all()
    
    return render_template('articles/community.html',
                         articles=articles,
                         featured=featured,
                         all_technologies=all_technologies,
                         all_domains=all_domains,
                         article_types=article_types,
                         search=search,
                         current_technology=technology,
                         current_domain=domain,
                         current_type=article_type)


@articles_bp.route('/article/<slug>')
def article_detail(slug):
    """Single article view"""
    article = Article.query.filter_by(slug=slug, status='approved').first_or_404()
    
    # Increment view count
    article.views_count += 1
    db.session.commit()
    
    # Get related articles
    related = Article.query.filter(
        Article.id != article.id,
        Article.status == 'approved',
        (Article.domain == article.domain) | 
        (Article.developer_id == article.developer_id)
    ).order_by(Article.published_at.desc()).limit(3).all()
    
    return render_template('articles/article_detail.html',
                         article=article,
                         related=related)


@articles_bp.route('/technology/<technology>')
def by_technology(technology):
    """Articles filtered by technology"""
    return redirect(url_for('articles.community', technology=technology))


@articles_bp.route('/domain/<domain>')
def by_domain(domain):
    """Articles filtered by domain"""
    return redirect(url_for('articles.community', domain=domain))


@articles_bp.route('/type/<article_type>')
def by_type(article_type):
    """Articles filtered by type"""
    return redirect(url_for('articles.community', type=article_type))
