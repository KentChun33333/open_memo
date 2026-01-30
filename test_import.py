import sys
import os
sys.path.append(os.getcwd())

try:
    print(f"Python: {sys.executable}")
    import yaml
    print("YAML imported")
    from mcp_skill_agent.orchestrator import Orchestrator
    print("Orchestrator Imported Successfully")
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
