try:
    import sys
    import os
    # Add current directory to path
    sys.path.append(os.getcwd())

    from mcp_skill_agent.orchestrator.orchestrator import Orchestrator

    print("Attempting to instantiate Orchestrator...")
    orch = Orchestrator()
    print("Orchestrator instantiated successfully.")
    
    # Check telemetry
    if hasattr(orch, 'telemetry'):
        print("Telemetry attached.")
    else:
        print("Telemetry MISSING.")
        exit(1)
        
except Exception as e:
    print(f"Integration Verification Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
