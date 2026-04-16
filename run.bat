@echo off
echo ========================================
echo    CareerHub - Automated Setup Script
echo ========================================

echo Setting up CareerHub project...

echo.
echo Step 1: Installing backend dependencies...
cd backend
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)

echo.
echo Step 2: Installing frontend dependencies...
cd ../frontend
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)

echo.
echo Step 3: Installing scraper dependencies...
cd ../scraper
call ..\storefront_new\Scripts\activate.bat
call pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install scraper dependencies
    pause
    exit /b 1
)

echo.
echo Step 4: Setting up environment variables...
cd ../backend
if not exist .env (
    copy .env.example .env
    echo Created .env file from .env.example
    echo Please edit backend\.env to set your MongoDB connection string
    echo Press any key after editing .env...
    pause
)

echo.
echo Step 5: Starting MongoDB service...
net start MongoDB 2>nul
if %errorlevel% neq 0 (
    echo WARNING: Could not start MongoDB service. Make sure MongoDB is installed.
    echo You can also use MongoDB Atlas - update the MONGODB_URI in .env
)

echo.
echo Step 6: Running scraper to populate database...
cd ../scraper
start "Scraper" cmd /c "python scraper.py && echo Scraper completed. && pause"
timeout /t 5 /nobreak > nul

echo.
echo Step 7: Starting backend server...
cd ../backend
start "Backend Server" cmd /c "npm run dev"

echo.
echo Step 8: Starting frontend...
cd ../frontend
start "Frontend" cmd /c "npm start"

echo.
echo ========================================
echo    CareerHub is starting up!
echo ========================================
echo.
echo - Backend API: http://localhost:5000
echo - Frontend UI: http://localhost:3000
echo - MongoDB: localhost:27017 (if using local)
echo.
echo Press any key to close this window...
echo (Other windows will remain open)
pause > nul
