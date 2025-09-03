#!/usr/bin/env python3
"""
Setup script for Arbo Dental Care AI Agent
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install Python dependencies"""
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['data', 'chroma_db', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def setup_environment():
    """Set up environment file"""
    env_file = Path('.env')
    env_example = Path('env.example')
    
    if not env_example.exists():
        print("❌ env.example file not found")
        return False
    
    if env_file.exists():
        print("⚠️  .env file already exists, skipping...")
        return True
    
    try:
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your OpenAI API key and other settings")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def check_openai_key():
    """Check if OpenAI API key is set"""
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  .env file not found, cannot check OpenAI API key")
        return False
    
    try:
        with open(env_file, 'r') as f:
            content = f.read()
            if 'your_openai_api_key_here' in content:
                print("⚠️  Please set your OpenAI API key in the .env file")
                return False
            elif 'OPENAI_API_KEY=' in content:
                print("✅ OpenAI API key appears to be configured")
                return True
            else:
                print("⚠️  OpenAI API key configuration not found")
                return False
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

def main():
    """Main setup function"""
    print("🦷 Arbo Dental Care AI Agent Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Set up environment
    if not setup_environment():
        print("❌ Setup failed during environment setup")
        sys.exit(1)
    
    # Check OpenAI key
    check_openai_key()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your OpenAI API key")
    print("2. Run: python data_preparation/web_scraper.py")
    print("3. Run: python data_preparation/knowledge_base.py")
    print("4. Run: python chatbot_interface/app.py")
    print("5. Open http://localhost:5000 in your browser")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main()


