import sys
import os
print(f"CWD: {os.getcwd()}")
print(f"Path: {sys.path}")
try:
    # Mimic skill_server.py imports
    from skill_manager import SkillManager
    print("Import Successful")
    
    # Initialize Manager
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skills_path = os.path.join(base_dir, ".agent", "skills")
    print(f"Skills Path: {skills_path}")
    
    sm = SkillManager(skills_dir=skills_path)
    print("SkillManager Initialized")
    
    from mcp.server import FastMCP
    print("FastMCP Imported")
    
    mcp = FastMCP("Debug-Server")
    print("FastMCP Instantiated")
    
except Exception as e:
    print(f"Import Failed: {e}")
    import traceback
    traceback.print_exc()
