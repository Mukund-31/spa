@echo off
REM Setup script for Kafka Fraud Detection System

echo ========================================
echo Kafka Fraud Detection System Setup
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env and add your Gemini API key!
    echo.
    pause
)

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment and install dependencies
echo Installing Python dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env and add your Gemini API key
echo 2. Start Docker containers: docker-compose up -d
echo 3. Run the system: python run.py
echo.
echo Or test the agents: python test_agents.py
echo.
pause
