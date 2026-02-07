
from app import create_app, db
from app.models import User
from flask import url_for

app = create_app()

with app.app_context():
    email = 'admin@asandevnest.com'
    password = 'admin123'
    
    print(f"Checking user: {email}")
    user = User.query.filter_by(email=email).first()
    
    if not user:
        print("❌ User not found!")
    else:
        print(f"✅ User found: {user.full_name}, Role: {user.role}, Status: {user.status}")
        
        if user.check_password(password):
            print("✅ Password check passed!")
        else:
            print("❌ Password check failed!")
            
        print(f"Is Admin? {user.is_admin()}")
        print(f"Is Suspended? {user.status == 'suspended'}")
