@echo off
title MurphyAI Twitch Bot
echo ========================================
echo    MurphyAI Twitch Bot - Starting...
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/
    echo.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Creating .env from env.example...
    copy env.example .env
    echo.
    echo IMPORTANT: Please edit .env with your configuration
    echo Opening .env in notepad...
    notepad .env
    echo.
    echo After configuring, close notepad and press any key to continue...
    pause
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update requirements
echo Checking dependencies...
pip install -q --upgrade pip
pip install -q -r requirements.txt

REM Clear screen and start bot
cls
echo ========================================
echo    MurphyAI Twitch Bot - Running
echo ========================================
echo.
echo Press Ctrl+C to stop the bot
echo.

REM Start the bot
python main.py

REM If bot exits, pause to see any error messages
echo.
echo ========================================
echo    Bot has stopped
echo ========================================
pause
