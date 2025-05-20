# Simple wrapper script to run the app with virtual env support
import os
import subprocess
import sys
import shutil

def find_python_in_venv():
    """Find the Python executable in the virtual environment."""
    venv_paths = ["/opt/venv/bin/python", "/tmp/venv/bin/python"]
    for path in venv_paths:
        if os.path.exists(path):
            return path
    return None

if __name__ == "__main__":
    # First try to use Python from virtual environment
    venv_python = find_python_in_venv()
    if venv_python:
        print(f"Using Python from virtual environment: {venv_python}")
        try:
            subprocess.run([venv_python, "app_fixed.py"], check=True)
            sys.exit(0)
        except subprocess.SubprocessError as e:
            print(f"Error running with venv Python: {e}")
    
    # If venv Python not found or failed, try with system Python
    python_cmds = ["python3", "python"]
    for cmd in python_cmds:
        if shutil.which(cmd):
            try:
                print(f"Attempting to run with {cmd}")
                subprocess.run([cmd, "app_fixed.py"], check=True)
                sys.exit(0)
            except subprocess.SubprocessError as e:
                print(f"Error running with {cmd}: {e}")
    
    print("Failed to start the application with any available Python interpreter.")
    sys.exit(1)
