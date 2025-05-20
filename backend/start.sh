#!/bin/bash
# Script to start the application on Railway

# Check if virtual environment exists
if [ -d "/opt/venv" ]; then
    echo "Using virtual environment at /opt/venv"
    # Use Python from the virtual environment directly
    PYTHON_CMD="/opt/venv/bin/python"
else
    echo "No virtual environment found at /opt/venv"
    # Try to create a virtual environment
    echo "Attempting to create virtual environment..."
    python3 -m venv /tmp/venv
    if [ $? -eq 0 ]; then
        echo "Virtual environment created at /tmp/venv"
        PYTHON_CMD="/tmp/venv/bin/python"
        source /tmp/venv/bin/activate
        pip install --no-cache-dir -r requirements.txt
    else
        echo "Failed to create virtual environment. Using system Python"
        PYTHON_CMD="python3"
    fi
fi

# Start the application
echo "Starting application with $PYTHON_CMD"
exec $PYTHON_CMD app_fixed.py
