"""
Helper Functions
"""

import os
import uuid
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename


def allowed_file(filename):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'pdf'})


def generate_unique_filename(original_filename):
    """Generate a unique filename while preserving extension"""
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    unique_name = f"{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    return f"{unique_name}.{ext}" if ext else unique_name


def save_file(file, folder, custom_name=None):
    """
    Save uploaded file to specified folder
    Returns the saved filename or None if failed
    """
    if not file or not file.filename:
        return None
    
    if not allowed_file(file.filename):
        return None
    
    # Generate unique filename
    filename = custom_name or generate_unique_filename(secure_filename(file.filename))
    
    # Ensure upload folder exists
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(upload_path, exist_ok=True)
    
    # Save file
    file_path = os.path.join(upload_path, filename)
    file.save(file_path)
    
    return filename


def delete_file(filename, folder):
    """Delete a file from the specified folder"""
    if not filename:
        return False
    
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder, filename)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception:
        pass
    return False


def format_currency(amount, currency='USD'):
    """Format amount as currency"""
    if amount is None:
        return ''
    
    symbols = {
        'USD': '$',
        'INR': '₹',
        'EUR': '€',
        'GBP': '£'
    }
    symbol = symbols.get(currency, currency + ' ')
    return f"{symbol}{amount:,.2f}"


def format_datetime(dt, format='%B %d, %Y'):
    """Format datetime for display"""
    if not dt:
        return ''
    return dt.strftime(format)


def time_ago(dt):
    """Get human-readable time difference"""
    if not dt:
        return ''
    
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return 'just now'
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f'{hours} hour{"s" if hours > 1 else ""} ago'
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f'{days} day{"s" if days > 1 else ""} ago'
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f'{weeks} week{"s" if weeks > 1 else ""} ago'
    elif seconds < 31536000:
        months = int(seconds / 2592000)
        return f'{months} month{"s" if months > 1 else ""} ago'
    else:
        years = int(seconds / 31536000)
        return f'{years} year{"s" if years > 1 else ""} ago'


def truncate_text(text, length=150):
    """Truncate text to specified length with ellipsis"""
    if not text:
        return ''
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + '...'


def slugify_text(text):
    """Convert text to URL-friendly slug"""
    from slugify import slugify
    return slugify(text, max_length=100)
