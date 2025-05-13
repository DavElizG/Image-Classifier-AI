"""
Setup script for configuring MongoDB in the Image Classifier API.
This script helps you set up MongoDB locally or connect to MongoDB Atlas.
"""
import os
import sys
import platform
import subprocess
import time
from pathlib import Path

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 50)
    print(" " + text)
    print("=" * 50)

def print_step(step, text):
    """Print a formatted step."""
    print(f"\n[{step}] {text}")

def get_input(prompt, default=None):
    """Get user input with a default value."""
    if default:
        result = input(f"{prompt} [{default}]: ").strip()
        return result if result else default
    return input(f"{prompt}: ").strip()

def setup_mongodb():
    """Guide user through MongoDB setup."""
    print_header("MongoDB Setup for Image Classifier API")
    
    print("\nThis script will help you set up MongoDB for your Image Classifier API.")
    print("You can either use a local MongoDB instance or connect to MongoDB Atlas (cloud).")
    
    # Check if MongoDB is installed locally
    print_step(1, "Checking for local MongoDB installation")
    mongo_installed = False
    try:
        # Check if MongoDB is installed
        if platform.system() == "Windows":
            result = subprocess.run(["where", "mongod"], capture_output=True, text=True)
            mongo_installed = result.returncode == 0
        else:
            result = subprocess.run(["which", "mongod"], capture_output=True, text=True)
            mongo_installed = result.returncode == 0
            
        if mongo_installed:
            print("✅ MongoDB is installed on your system.")
        else:
            print("❌ MongoDB is not installed locally.")
    except Exception as e:
        print(f"Error checking MongoDB installation: {e}")
        mongo_installed = False
    
    # Ask user which MongoDB setup they want to use
    print_step(2, "Choose MongoDB setup")
    print("1. Use local MongoDB (requires MongoDB to be installed)")
    print("2. Use MongoDB Atlas (cloud)")
    
    setup_choice = ""
    while setup_choice not in ["1", "2"]:
        setup_choice = input("Enter your choice (1 or 2): ").strip()
    
    mongo_uri = ""
    
    if setup_choice == "1":
        # Local MongoDB setup
        print_step(3, "Local MongoDB Setup")
        
        if not mongo_installed:
            print("\n⚠️ MongoDB doesn't appear to be installed on your system.")
            print("You'll need to install MongoDB first.")
            
            if platform.system() == "Windows":
                print("\nYou can download MongoDB from: https://www.mongodb.com/try/download/community")
            elif platform.system() == "Darwin":  # macOS
                print("\nYou can install MongoDB using Homebrew:")
                print("  brew tap mongodb/brew")
                print("  brew install mongodb-community")
            else:  # Linux
                print("\nYou can install MongoDB using your package manager:")
                print("  For Ubuntu/Debian: sudo apt install mongodb")
                print("  For RedHat/Fedora: sudo yum install mongodb")
            
            proceed = input("\nDo you want to proceed with the setup anyway? (y/n): ").lower().strip()
            if proceed != 'y':
                print("\nSetup aborted. Please install MongoDB and run this script again.")
                return
        
        # Get MongoDB connection details
        host = get_input("MongoDB host", "localhost")
        port = get_input("MongoDB port", "27017")
        db_name = get_input("Database name", "image_classifier_db")
        
        # Construct MongoDB URI
        mongo_uri = f"mongodb://{host}:{port}/{db_name}"
        
    else:
        # MongoDB Atlas setup
        print_step(3, "MongoDB Atlas Setup")
        
        print("\nTo use MongoDB Atlas, you need to create an account and a cluster.")
        print("1. Sign up or log in at https://www.mongodb.com/cloud/atlas")
        print("2. Create a free cluster")
        print("3. Create a database user")
        print("4. Configure network access (allowlist your IP)")
        print("5. Get your connection string")
        
        print("\nYour connection string should look like:")
        print("mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<dbname>")
        
        mongo_uri = get_input("\nPaste your MongoDB Atlas connection string")
        db_name = get_input("Database name", "image_classifier_db")
        
        # Check if the connection string already includes the database name
        if "?retryWrites" in mongo_uri and "/" in mongo_uri.split("?")[0]:
            parts = mongo_uri.split("?")
            base_uri = parts[0]
            if base_uri.endswith("/"):
                mongo_uri = f"{base_uri}{db_name}?{parts[1]}"
            else:
                uri_parts = base_uri.split("/")
                if len(uri_parts) > 3:  # There's already a DB name
                    uri_parts[-1] = db_name
                    mongo_uri = "/".join(uri_parts)
                    if len(parts) > 1:
                        mongo_uri = f"{mongo_uri}?{parts[1]}"
    
    # Update .env file
    print_step(4, "Updating environment configuration")
    
    env_file = Path(__file__).parent.parent / ".env"
    
    # Check if .env exists
    if env_file.exists():
        # Read existing .env content
        with open(env_file, "r") as f:
            env_content = f.read()
        
        # Check if the variables already exist
        db_storage_type_exists = "DB_STORAGE_TYPE=" in env_content
        mongo_uri_exists = "MONGO_URI=" in env_content
        mongo_db_name_exists = "MONGO_DB_NAME=" in env_content
        
        # Update or add variables
        with open(env_file, "a") as f:
            f.write("\n# MongoDB Configuration\n")
            if not db_storage_type_exists:
                f.write("DB_STORAGE_TYPE=mongodb\n")
            else:
                print("DB_STORAGE_TYPE already exists in .env file. Please update it manually to 'mongodb'.")
            
            if not mongo_uri_exists:
                f.write(f"MONGO_URI=\"{mongo_uri}\"\n")
            else:
                print("MONGO_URI already exists in .env file. Please update it manually if needed.")
            
            if not mongo_db_name_exists:
                f.write(f"MONGO_DB_NAME={db_name}\n")
            else:
                print("MONGO_DB_NAME already exists in .env file. Please update it manually if needed.")
    else:
        # Create new .env file
        with open(env_file, "w") as f:
            f.write("# MongoDB Configuration\n")
            f.write("DB_STORAGE_TYPE=mongodb\n")
            f.write(f"MONGO_URI=\"{mongo_uri}\"\n")
            f.write(f"MONGO_DB_NAME={db_name}\n")
    
    print("\n✅ Environment configuration updated.")
    
    # Migrate existing data
    print_step(5, "Migrate existing data")
    
    migrate = input("\nDo you want to migrate existing classification data to MongoDB? (y/n): ").lower().strip()
    
    if migrate == 'y':
        print("\nMigrating data to MongoDB...")
        try:
            # Import here to avoid circular imports
            from utils.migrate_to_mongodb import migrate_to_mongodb
            migrate_to_mongodb()
        except Exception as e:
            print(f"Error during migration: {e}")
            import traceback
            traceback.print_exc()
    
    # Final instructions
    print_step(6, "Setup Complete")
    
    print("\n✅ MongoDB configuration is complete!")
    print("\nTo start using MongoDB with your Image Classifier API:")
    print("1. Install the required dependencies:")
    print("   pip install -r requirements.txt")
    print("2. Start your API server:")
    print("   python app.py")
    
    print("\nIf you encounter any issues, check the logs for more information.")

if __name__ == "__main__":
    setup_mongodb()
