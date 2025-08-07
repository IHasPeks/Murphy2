#!/bin/bash

echo "========================================"
echo "   MurphyAI Twitch Bot - Starting..."
echo "========================================"
echo

# Check if Python 3.11+ is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed"
    echo "Please install Python 3.11+ from https://www.python.org/"
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "ERROR: Python $required_version or higher is required (you have $python_version)"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Creating .env from env.example..."
    cp env.example .env
    echo
    echo "IMPORTANT: Please edit .env with your configuration"
    echo "Opening .env in default editor..."
    
    # Try to open in default editor
    if command -v nano &> /dev/null; then
        nano .env
    elif command -v vi &> /dev/null; then
        vi .env
    else
        echo "Please manually edit the .env file with your configuration"
    fi
    
    echo
    echo "After configuring, press Enter to continue..."
    read
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update requirements
echo "Checking dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Clear screen and start bot
clear
echo "========================================"
echo "   MurphyAI Twitch Bot - Running"
echo "========================================"
echo
echo "Press Ctrl+C to stop the bot"
echo

# Start the bot
python3 main.py

# If bot exits, pause to see any error messages
echo
echo "========================================"
echo "   Bot has stopped"
echo "========================================"
echo "Press Enter to exit..."
read
