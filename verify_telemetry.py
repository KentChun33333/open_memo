from mcp_skill_agent.telemetry import TelemetryManager
import sys

def test_telemetry():
    print("Initializing TelemetryManager...")
    tm = TelemetryManager()
    
    print("Logging Test Event...")
    tm.log_event(
        event_type="TEST_EVENT",
        step_id=1,
        agent_name="Tester",
        details={"status": "success", "value": 42}
    )
    print("Telemetry Test Complete.")

if __name__ == "__main__":
    test_telemetry()
