import sys
import os

# Ensure we can import modules
sys.path.append(os.getcwd())

try:
    from mcp_skill_agent.bash_tools.filesystem import list_directory
    
    print("--- Test 1: List mcp_skill_agent/bash_tools ---")
    # This directory should have a few files
    print(list_directory("mcp_skill_agent/bash_tools"))
    
    print("\n--- Test 2: List non-existent path ---")
    print(list_directory("non_existent_path_123"))

except ImportError as e:
    print(f"ImportError: {e}")
    # Fallback to verify simply by running the function code if import fails due to mcp
    print("Could not import directly, might be due to mcp decorator side effects.")
except Exception as e:
    print(f"Error during test: {e}")
