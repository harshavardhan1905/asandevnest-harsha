"""
Routes Package - Flask Blueprints
"""

from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.admin import admin_bp
from app.routes.developer import developer_bp
from app.routes.client import client_bp
from app.routes.articles import articles_bp
from app.routes.api import api_bp

__all__ = [
    'main_bp',
    'auth_bp',
    'admin_bp',
    'developer_bp',
    'client_bp',
    'articles_bp',
    'api_bp'
]
