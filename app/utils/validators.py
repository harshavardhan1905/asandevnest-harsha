"""
Input Validators
"""

import re


def validate_email(email):
    """Validate email format"""
    if not email:
        return False, "Email is required"
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    return True, None


def validate_password(password):
    """
    Validate password strength
    - At least 8 characters
    - Contains uppercase, lowercase, and number
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, None


def validate_phone(phone):
    """Validate phone number format"""
    if not phone:
        return True, None  # Phone is optional
    
    # Remove spaces and dashes
    cleaned = re.sub(r'[\s\-]', '', phone)
    
    # Check if it's a valid phone number (10-15 digits, optional + prefix)
    pattern = r'^\+?\d{10,15}$'
    if not re.match(pattern, cleaned):
        return False, "Invalid phone number format"
    
    return True, None


def validate_url(url):
    """Validate URL format"""
    if not url:
        return True, None  # URL is optional
    
    pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    if not re.match(pattern, url):
        return False, "Invalid URL format"
    
    return True, None


def sanitize_html(content):
    """
    Basic HTML sanitization
    In production, use a proper library like bleach
    """
    if not content:
        return ''
    
    # Remove script tags
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove on* event handlers
    content = re.sub(r'\s+on\w+\s*=\s*["\'][^"\']*["\']', '', content, flags=re.IGNORECASE)
    
    return content


def validate_required_fields(data, required_fields):
    """
    Validate that all required fields are present and non-empty
    Returns (is_valid, error_message)
    """
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"{field.replace('_', ' ').title()} is required"
    return True, None
