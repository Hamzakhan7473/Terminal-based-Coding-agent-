#!/usr/bin/env python3
"""
Setup script for Terminal-based AI Coding Agent.

This script provides an easy way to install and configure the coding agent.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_example.exists():
        try:
            shutil.copy(env_example, env_file)
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file with your API keys")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("⚠️  env.example not found, creating basic .env file")
        try:
            with open(env_file, "w") as f:
                f.write("""# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Configuration  
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# E2B Sandbox Configuration
E2B_API_KEY=your_e2b_api_key_here

# Default LLM Provider (openai, anthropic)
DEFAULT_LLM_PROVIDER=openai

# Default Model
DEFAULT_MODEL=gpt-4

# Execution timeout (seconds)
EXECUTION_TIMEOUT=30

# Max file size for processing (MB)
MAX_FILE_SIZE_MB=10

# Enable debug mode
DEBUG=false
""")
            print("✅ Created basic .env file")
            print("⚠️  Please edit .env file with your API keys")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False


def install_package():
    """Install the package in development mode."""
    print("🔧 Installing package in development mode...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
        print("✅ Package installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install package: {e}")
        return False


def verify_installation():
    """Verify that the installation was successful."""
    print("🔍 Verifying installation...")
    try:
        # Try importing the main module
        import coding_agent
        print("✅ Package import successful")
        
        # Check if CLI command is available
        result = subprocess.run([sys.executable, "-m", "coding_agent.cli", "--help"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ CLI command available")
            return True
        else:
            print("⚠️  CLI command may not be working properly")
            return False
            
    except ImportError as e:
        print(f"❌ Package import failed: {e}")
        return False
    except subprocess.TimeoutExpired:
        print("⚠️  CLI command test timed out")
        return False
    except Exception as e:
        print(f"⚠️  Verification failed: {e}")
        return False


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "="*60)
    print("🎉 Installation completed successfully!")
    print("="*60)
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys:")
    print("   - OpenAI API key (required for GPT-4)")
    print("   - Anthropic API key (optional, for Claude)")
    print("   - E2B API key (optional, for sandbox execution)")
    print("\n2. Test the installation:")
    print("   python -m coding_agent.cli")
    print("\n3. Or install as a command:")
    print("   coding-agent")
    print("\n4. Read the documentation:")
    print("   - README.md for usage instructions")
    print("   - examples/basic_usage.py for code examples")
    print("\n5. Get help:")
    print("   - GitHub: https://github.com/Hamzakhan7473/Terminal-based-Coding-agent-")
    print("   - Email: hamzakhan@taxora.ai")
    print("\n🚀 Happy coding with AI!")


def main():
    """Main setup function."""
    print("🤖 Terminal-based AI Coding Agent Setup")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Install package
    if not install_package():
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("⚠️  Installation completed but verification failed")
        print("You may still be able to use the package")
    
    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    main()
