@echo off
echo.
echo ========================================
echo   ASAN DEVNEST - ADMIN ACCESS
echo ========================================
echo.
echo Creating admin account...
echo.

python run.py seed-demo

echo.
echo ========================================
echo   ADMIN LOGIN CREDENTIALS
echo ========================================
echo.
echo   ADMIN URL: http://localhost:5000/auth/admin-login
echo.
echo   Email: admin@asandevnest.com
echo   Password: admin123
echo.
echo ========================================
echo.
echo Press any key to open ADMIN login page...
pause > nul

start http://localhost:5000/auth/admin-login

echo.
echo Admin login page opened in your browser!
echo Use the credentials above to login.
echo.
pause
