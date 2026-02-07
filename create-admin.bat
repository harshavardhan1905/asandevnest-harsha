@echo off
echo.
echo ========================================
echo   CREATING ADMIN ACCOUNT
echo ========================================
echo.

python -c "from app import create_app, db; from app.models import User; app = create_app(); app.app_context().push(); admin = User.query.filter_by(email='admin@asandevnest.com').first(); print('Admin already exists!') if admin else (setattr((u := User(email='admin@asandevnest.com', full_name='Asan Admin', role='admin', status='verified')), 'password_hash', u.set_password('admin123') or u.password_hash), db.session.add(u), db.session.commit(), print('Admin created successfully!'))"

echo.
echo ========================================
echo   ADMIN CREDENTIALS
echo ========================================
echo.
echo   URL: http://localhost:5000/auth/admin-login
echo.
echo   Email: admin@asandevnest.com
echo   Password: admin123
echo.
echo ========================================
echo.
pause
