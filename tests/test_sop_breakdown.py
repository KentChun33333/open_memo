import sys
import os
import unittest
import logging

# Add parent directory to path to import mcp_skill_agent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcp_skill_agent.sop_agent import SOPController, SkillStep

# Configure logging to see output
logging.basicConfig(level=logging.INFO)

class TestSOPBreakdown(unittest.TestCase):
    def test_breakdown_flow(self):
        # 1. Setup initial steps
        steps = [
            SkillStep(id=1, title="Step 1", content="Do step 1"),
            SkillStep(id=2, title="Step 2", content="Do step 2")
        ]
        sop = SOPController(steps)
        
        # 2. Verify initial state
        current = sop.get_current_step()
        self.assertEqual(current.id, 1)
        self.assertEqual(current.title, "Step 1")
        
        # 3. Simulate Breakdown of Step 1
        print("\n--- Expanding Step 1 ---")
        sub_steps = [
            {"title": "Step 1.1", "content": "Content 1.1"},
            {"title": "Step 1.2", "content": "Content 1.2"}
        ]
        sop.expand_step(1, sub_steps)
        
        # 4. Verify traversal into sub-steps
        # Current step should NOW be the first sub-step, because get_current_step recursive logic finds first pending
        current = sop.get_current_step()
        print(f"Current Step after expansion: {current.id} - {current.title}")
        self.assertEqual(current.id, 11) # Logic was parent_id * 10 + index + 1? No, logic was f"{target.id}{i+1}" -> "11"
        self.assertEqual(current.title, "Step 1.1")
        
        # 5. Advance Step 1.1
        print("\n--- Advancing Step 1.1 ---")
        sop.advance_step()
        
        # 6. Verify next is Step 1.2
        current = sop.get_current_step()
        print(f"Current Step: {current.id} - {current.title}")
        self.assertEqual(current.id, 12)
        
        # 7. Advance Step 1.2
        print("\n--- Advancing Step 1.2 ---")
        sop.advance_step()
        
        # 8. Step 1 (parent) should be done, and we should be at Step 2
        # Logic: advance_step marks 1.2 done. Then _check_and_update_parents() sees 1.1 and 1.2 done, so marks 1 done.
        # Then loop checks if root step (1) is done, increments index to 2.
        current = sop.get_current_step()
        if current:
            print(f"Current Step: {current.id} - {current.title}")
        else:
            print("Current Step: None")
            
        self.assertEqual(current.id, 2)
        self.assertEqual(sop.steps[0].status, "done")
        
        # 9. Verify Summary nesting
        summary = sop.get_progress_summary()
        print("\nSummary:\n" + summary)
        self.assertIn("[x] Step 1:", summary)
        self.assertIn("  [x] Step 11:", summary)
        self.assertIn("[>] Step 2:", summary)

if __name__ == "__main__":
    unittest.main()
