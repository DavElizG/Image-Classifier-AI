#!/bin/bash
# Script to start the application on Railway

# Ensure python3 is installed
command -v python3 >/dev/null 2>&1 || { echo >&2 "Python3 is required but not installed. Aborting."; exit 1; }

# Activate virtual environment if it exists
if [ -d "/opt/venv" ]; then
    source /opt/venv/bin/activate
fi

# Start the application
exec python3 app_fixed.py
