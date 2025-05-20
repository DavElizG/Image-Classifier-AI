# Simple wrapper script to run the app
import os
import subprocess

if __name__ == "__main__":
    # Try to run the app with python3 first, then fallback to python if needed
    try:
        subprocess.run(["python3", "app_fixed.py"], check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        # If python3 command fails, try python
        try:
            subprocess.run(["python", "app_fixed.py"], check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            print("Failed to start the application with python or python3.")
            exit(1)
