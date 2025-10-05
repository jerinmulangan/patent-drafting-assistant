@echo off
REM Patent NLP Frontend Development Server Startup Script

echo 🚀 Starting Patent NLP Frontend Development Server...
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 16+ to continue.
    echo    Download from: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js version: 
node --version

REM Check if we're in the frontend directory
if not exist "package.json" (
    echo ❌ package.json not found. Please run this script from the frontend directory.
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    npm install
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies. Please check your internet connection and try again.
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed successfully
)

REM Check if backend is running
echo 🔍 Checking backend connection...
curl -s http://localhost:8000/api/v1/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend API is running on http://localhost:8000
) else (
    echo ⚠️  Backend API is not running on http://localhost:8000
    echo    Please start the backend server before using the frontend.
    echo    The frontend will still start but API calls will fail.
)

echo.
echo 🌐 Starting development server...
echo    Frontend will be available at: http://localhost:3000
echo    Press Ctrl+C to stop the server
echo.

REM Start the development server
npm start

