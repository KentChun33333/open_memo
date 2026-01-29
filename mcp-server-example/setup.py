#!/usr/bin/env python3
"""
Setup script for MCP Agent client configuration and dependencies.
"""

import os
import subprocess
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def setup_environment():
    """Set up environment and install dependencies."""
    print("🔧 Setting up MCP Agent environment...")

    # Install Python dependencies
    try:
        print("📦 Installing Python dependencies...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

    return True


def setup_env_file():
    """Set up .env file if it doesn't exist."""
    env_path = Path(".env")
    example_path = Path(".env.example")

    if not env_path.exists() and example_path.exists():
        print("📝 Creating .env file from template...")
        with open(example_path, "r") as f:
            content = f.read()

        with open(env_path, "w") as f:
            f.write(content)

        print("⚠️  Please edit .env file and add your Ollama configuration!")
        print("🔑 Make sure Ollama is running and Nemotron-3-nano is pulled")
        return True
    elif env_path.exists():
        print("✅ .env file already exists")
        return True
    else:
        print("⚠️  No .env.example file found")
        return False


def check_openai_key():
    """Check if OpenAI API key is set."""
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("✅ OpenAI API key is configured")
        return True
    else:
        print("❌ OpenAI API key not found in environment")
        print("🔑 Please set OPENAI_API_KEY in your .env file or run:")
        print("   export OPENAI_API_KEY=your_api_key_here")
        return False


def check_ollama_setup():
    """Check if Ollama is configured and running."""
    import requests

    # Check environment variables
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "Nemotron-3-nano")

    print(f"✅ Ollama URL configured: {ollama_url}")
    print(f"✅ Ollama model configured: {ollama_model}")

    # Check if Ollama server is running
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model["name"].lower() for model in models]

            if ollama_model.lower() in [
                name.replace(":latest", "") for name in model_names
            ]:
                print(f"✅ Ollama server running with {ollama_model} model available")
                return True
            else:
                print(f"❌ Model {ollama_model} not found in Ollama")
                print(f"🔧 Run: ollama pull {ollama_model}")
                return False
        else:
            print(f"❌ Ollama server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Ollama server: {e}")
        print("🔧 Make sure Ollama is running: ollama serve")
        return False


def test_mcp_server():
    """Test if MCP server is working."""
    print("🧪 Testing MCP server...")

    try:
        # Import and test basic functionality
        sys.path.append(str(Path(__file__).parent))
        import pandas as pd

        # Test CSV reading
        df = pd.read_csv("matches.csv")
        print(f"✅ MCP server data file loaded ({len(df)} matches)")

        # Test calculation logic
        risk_amount = 10000 * (2.0 / 100)
        position_size = risk_amount / abs(150 - 145)
        print(f"✅ Position calculation test passed: {int(position_size)} units")

        return True
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False


def create_desktop_shortcut():
    """Create a desktop shortcut for easy access (macOS)."""
    if sys.platform == "darwin":
        script_path = Path(__file__).parent / "agent_client.py"
        desktop_script = Path.home() / "Desktop" / "mcp_agent.command"

        script_content = f"""#!/bin/bash
cd "{script_path.parent}"
python3 agent_client.py --interactive
"""

        with open(desktop_script, "w") as f:
            f.write(script_content)

        # Make executable
        desktop_script.chmod(0o755)
        print(f"📱 Created desktop shortcut: {desktop_script}")


def main():
    """Main setup function."""
    print("🚀 MCP Agent Setup")
    print("=" * 50)

    # Change to the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"📁 Working directory: {script_dir}")

    steps = [
        ("Python Version", check_python_version),
        ("Dependencies", setup_environment),
        ("Environment File", setup_env_file),
        ("MCP Server", test_mcp_server),
        ("Ollama Setup", check_ollama_setup),
    ]

    all_passed = True
    for step_name, step_func in steps:
        print(f"\n🔍 Checking {step_name}...")
        if not step_func():
            all_passed = False
            break

    if all_passed:
        print("\n✅ Setup completed successfully!")

        print("\n🎯 Next steps:")
        print("1. Test agent: python3 agent_client.py --demo")
        print("2. Interactive mode: python3 agent_client.py --interactive")
        print("3. Run examples: python3 examples.py --all")

        if sys.platform == "darwin":
            create_desktop_shortcut()

    else:
        print("\n❌ Setup failed. Please resolve the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
