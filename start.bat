@echo off
REM Dark Web Intelligence API - Quick Start Script
REM Windows Batch File

echo.
echo ========================================
echo   Dark Web Intelligence Platform
echo   Quick Start Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [✓] Python detected

REM Check if requirements are installed
echo [*] Installing dependencies...
pip install -q -r backend/requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [✓] Dependencies installed

REM Start the API server
echo.
echo [*] Starting Dark Web Intelligence API on port 5002...
echo [*] Access the frontend at: file:///c:/Users/PMLS/Downloads/darkweb-intel/frontend/index.html
echo [*] Press CTRL+C to stop the server
echo.

python backend/app.py

pause
