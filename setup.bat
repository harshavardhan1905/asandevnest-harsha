@echo off
echo ========================================
echo Asan DevNest - Quick Setup Script
echo ========================================
echo.

echo Step 1: Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo Step 2: Initializing database...
python run.py init-db
if %errorlevel% neq 0 (
    echo ERROR: Failed to initialize database
    pause
    exit /b 1
)
echo.

echo Step 3: Creating admin user...
python run.py create-admin
if %errorlevel% neq 0 (
    echo ERROR: Failed to create admin
    pause
    exit /b 1
)
echo.

echo Step 4: Seeding demo data (optional)...
set /p seed="Do you want to add demo data? (y/n): "
if /i "%seed%"=="y" (
    python run.py seed-demo
    echo Demo data added successfully!
)
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To run the application:
echo   python run.py
echo.
echo Then visit: http://localhost:5000
echo.
pause
