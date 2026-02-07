"""
Quick script to create admin account
"""
from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(email='admin@asandevnest.com').first()
    
    if admin:
        print("✅ Admin account already exists!")
        print(f"   Email: {admin.email}")
        print(f"   Name: {admin.full_name}")
        print(f"   Role: {admin.role}")
    else:
        # Create admin
        admin = User(
            email='admin@asandevnest.com',
            full_name='Asan Admin',
            role='admin',
            status='verified'
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        db.session.commit()
        
        print("✅ Admin account created successfully!")
    
    print("\n" + "="*50)
    print("ADMIN LOGIN CREDENTIALS")
    print("="*50)
    print(f"URL: http://localhost:5000/auth/admin-login")
    print(f"Email: admin@asandevnest.com")
    print(f"Password: admin123")
    print("="*50)
