import unittest
import os
import shutil
from typing import List, Dict, Any

# Adjust path to import from parent directory (open_memo)
import sys
# script is in open_memo/mcp_skill_agent/tests/
# We want to add open_memo/ to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp_skill_agent.memory.session_memory import SessionMemoryManager

class TestContextOptimization(unittest.TestCase):
    def setUp(self):
        self.test_dir =  "test_workspace_context_opt"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        self.manager = SessionMemoryManager(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_recent_file_paths(self):
        # step 1: read file A
        self.manager.log_tool_usage("agent", 1, 1, "read_file", {"path": "fileA.txt"})
        # step 1: read file B
        self.manager.log_tool_usage("agent", 1, 2, "read_file", {"path": "fileB.txt"})
        
        # step 2: read file C
        self.manager.log_tool_usage("agent", 2, 1, "read_file", {"path": "fileC.txt"})
        
        # step 3: read file D
        self.manager.log_tool_usage("agent", 3, 1, "read_file", {"path": "fileD.txt"})
        
        # Lookback 2: Should get files from Step 3 and Step 2 (C, D)
        paths = self.manager.get_recent_file_paths(2)
        print(f"Paths (lookback 2): {paths}")
        self.assertIn("fileD.txt", paths)
        self.assertIn("fileC.txt", paths)
        self.assertNotIn("fileA.txt", paths)
        self.assertNotIn("fileB.txt", paths)
        
        # Lookback 3: Should get A, B, C, D
        paths_3 = self.manager.get_recent_file_paths(3)
        self.assertIn("fileA.txt", paths_3)
        
    def test_clipboard_subset(self):
        # Setup clipboard
        self.manager.update_clipboard("fileA.txt", "contentA")
        self.manager.update_clipboard("sub/fileB.txt", "contentB")
        
        # Match exact
        subset = self.manager.get_clipboard_subset(["fileA.txt"])
        self.assertEqual(len(subset), 1)
        self.assertEqual(subset["fileA.txt"], "contentA")
        
        # Match relative vs absolute
        abs_path_b = os.path.abspath(os.path.join(self.test_dir, "sub/fileB.txt"))
        subset_b = self.manager.get_clipboard_subset([abs_path_b])
        # The key in clipboard is "sub/fileB.txt" (relative because update_clipboard normalizes it)
        # Let's verify how update_clipboard stores it first
        # In session_memory.py: store_key = os.path.relpath(...) if abs and inside workspace
        
        print(f"Clipboard keys: {self.manager.get_clipboard().keys()}")
        self.assertIn("sub/fileB.txt", subset_b)

if __name__ == "__main__":
    unittest.main()
