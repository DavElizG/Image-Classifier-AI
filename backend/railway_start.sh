#!/bin/bash
# Railway specific startup script

set -e  # Exit immediately if a command exits with non-zero status

echo "Starting Railway deployment script"

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

echo "Using Python command: $PYTHON_CMD"

# Create virtual environment
echo "Creating virtual environment"
$PYTHON_CMD -m venv /tmp/venv

# Activate virtual environment
echo "Activating virtual environment"
source /tmp/venv/bin/activate

# Upgrade pip
echo "Upgrading pip"
pip install --upgrade pip

# Install requirements
echo "Installing requirements"
pip install -r requirements.txt

# Start application
echo "Starting application"
exec python app_fixed.py
