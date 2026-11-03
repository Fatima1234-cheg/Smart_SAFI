@echo off
REM SmartSafi - Smart City Management System
REM Setup Script for Windows

echo ==================================
echo SmartSafi Setup Script
echo ==================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install Python 3.9 or higher.
    pause
    exit /b 1
)

for /f "tokens=2" %%a in ('python --version') do set PYTHON_VERSION=%%a
echo [OK] Python version: %PYTHON_VERSION%

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not installed. Please install pip.
    pause
    exit /b 1
)
echo [OK] pip is installed

REM Create virtual environment
echo.
echo [INFO] Creating virtual environment...
if exist venv (
    echo [WARNING] Virtual environment already exists. Removing...
    rmdir /s /q venv
)

python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)
echo [OK] Virtual environment created

REM Activate virtual environment
echo.
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo.
echo [INFO] Installing requirements...
if exist requirements.txt (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install requirements.
        pause
        exit /b 1
    )
    echo [OK] Requirements installed
) else (
    echo [WARNING] requirements.txt not found
)

REM Setup environment variables
echo.
echo [INFO] Setting up environment variables...
if not exist .env (
    if exist .env.example (
        copy .env.example .env
        echo [OK] .env file created from .env.example
        echo [WARNING] Please edit .env and update the configuration values
    ) else (
        echo [WARNING] .env.example not found
    )
) else (
    echo [WARNING] .env file already exists
)

REM Create required directories
echo.
echo [INFO] Creating required directories...
if not exist logs mkdir logs
if not exist uploads mkdir uploads
if not exist backups mkdir backups
if not exist instance mkdir instance
echo [OK] Directories created

REM Final message
echo.
echo ==================================
echo [OK] Setup completed successfully!
echo ==================================
echo.
echo Next steps:
echo 1. Edit .env file with your configuration
echo 2. Ensure MongoDB is running
echo 3. Ensure MQTT broker is running (optional)
echo 4. Run: flask init-db
echo 5. Run: flask create-admin
echo 6. Start the server: python run.py
echo.
echo Access the application at: http://localhost:5000
echo.

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat

pause
