import{j as e}from"./index-DL95azgn.js";const i={title:"Working Directory Management Solution",date:"2026-02-07",tags:["architecture","agent","analysis"],summary:"An analysis report on agent architecture."};function t(r){const n={code:"code",h1:"h1",h2:"h2",h3:"h3",hr:"hr",li:"li",p:"p",pre:"pre",strong:"strong",table:"table",tbody:"tbody",td:"td",th:"th",thead:"thead",tr:"tr",ul:"ul",...r.components};return e.jsxs(e.Fragment,{children:[e.jsx(n.h1,{children:"Working Directory Management: Nanobot Benchmark & Proposed Solution"}),`
`,e.jsx(n.h2,{children:"Problem Statement"}),`
`,e.jsxs(n.p,{children:["The trajectory analysis revealed that the agent ran ",e.jsx(n.code,{children:"init-artifact.sh mcp-demo"})," from ",e.jsx(n.strong,{children:"9 different directories"}),", creating duplicate projects in 3 locations. The root cause: ",e.jsxs(n.strong,{children:[e.jsx(n.code,{children:"os.getcwd()"})," returns unpredictable values"]})," across MCP server restarts."]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Benchmark: Nanobot's Approach"}),`
`,e.jsx(n.h3,{children:"How Nanobot Handles Working Directory"}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-python",children:`# From nanobot/agent/loop.py (lines 79-83)
self.tools.register(ExecTool(
    working_dir=str(self.workspace),  # ✅ Fixed at startup
    timeout=self.exec_config.timeout,
    restrict_to_workspace=self.exec_config.restrict_to_workspace,
))
`})}),`
`,e.jsx(n.h3,{children:"Key Design Principles"}),`
`,e.jsxs(n.table,{children:[e.jsx(n.thead,{children:e.jsxs(n.tr,{children:[e.jsx(n.th,{children:"Principle"}),e.jsx(n.th,{children:"Implementation"})]})}),e.jsxs(n.tbody,{children:[e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Single Source of Truth"})}),e.jsxs(n.td,{children:[e.jsx(n.code,{children:"workspace"})," path set once at agent startup"]})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Immutable Default"})}),e.jsxs(n.td,{children:[e.jsx(n.code,{children:"working_dir"})," is stored in ",e.jsx(n.code,{children:"ExecTool.__init__"})]})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Explicit Override"})}),e.jsxs(n.td,{children:["Agent can still pass ",e.jsx(n.code,{children:"working_dir"})," per-call"]})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Context Injection"})}),e.jsx(n.td,{children:"Workspace path injected into system prompt"})]})]})]}),`
`,e.jsx(n.h3,{children:"Why It Works"}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{children:`context.py (line 91):
  "Your workspace is at: {workspace_path}"
  
loop.py (line 80):
  working_dir=str(self.workspace)
`})}),`
`,e.jsxs(n.p,{children:["The agent ",e.jsx(n.strong,{children:"always knows"})," where home base is, and commands default to that location."]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Current MCP Implementation (The Problem)"}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-python",children:`# From file_server.py (line 210)
async def execute_command(command: str, working_dir: Optional[str] = None) -> str:
    cwd = working_dir or os.getcwd()  # ❌ PROBLEM: os.getcwd() is unpredictable
`})}),`
`,e.jsx(n.h3,{children:"Why This Fails"}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-mermaid",children:`sequenceDiagram
    participant Agent
    participant MCP Server 1
    participant MCP Server 2 (after crash)
    
    Agent->>MCP Server 1: execute_command(init-artifact.sh, cwd=None)
    Note over MCP Server 1: os.getcwd() = /mcp_skill_agent
    MCP Server 1-->>Agent: Created in /mcp_skill_agent/mcp-demo
    
    Note over MCP Server 1: 💥 CRASH
    
    Agent->>MCP Server 2: execute_command(init-artifact.sh, cwd=None)
    Note over MCP Server 2: os.getcwd() = /open_memo 
    MCP Server 2-->>Agent: Created in /open_memo/mcp-demo
`})}),`
`,e.jsxs(n.p,{children:["The ",e.jsx(n.code,{children:"os.getcwd()"})," value depends on ",e.jsx(n.strong,{children:"where the MCP server was started"}),", which can change after crashes/restarts."]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Proposed Solution"}),`
`,e.jsx(n.h3,{children:"Option A: Fixed Workspace (Nanobot-Style)"}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Change:"})," Set a fixed ",e.jsx(n.code,{children:"WORKSPACE_ROOT"})," at server startup."]}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-python",children:`# In file_server.py

# Option 1: Environment variable (flexible)
WORKSPACE_ROOT = os.getenv("MCP_WORKSPACE", "/Users/kentchiu/Documents/Github/open_memo")

# Option 2: Config file
# WORKSPACE_ROOT = load_config()["workspace_root"]

@mcp.tool()
async def execute_command(command: str, working_dir: Optional[str] = None) -> str:
    """Execute a shell command. Defaults to workspace root if no dir specified."""
    cwd = working_dir or WORKSPACE_ROOT  # ✅ Predictable default
    log_tool_call("execute_command", {"command": command, "cwd": cwd})
    # ... rest of implementation
`})}),`
`,e.jsx(n.p,{children:e.jsx(n.strong,{children:"Pros:"})}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsx(n.li,{children:"Simple, one-line fix"}),`
`,e.jsx(n.li,{children:"Matches nanobot's proven approach"}),`
`,e.jsx(n.li,{children:"Immediate stability improvement"}),`
`]}),`
`,e.jsx(n.p,{children:e.jsx(n.strong,{children:"Cons:"})}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsx(n.li,{children:"Requires setting env variable or config"}),`
`,e.jsx(n.li,{children:"All commands default to one location"}),`
`]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h3,{children:"Option B: State-Aware CWD Tracking"}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Change:"}),' Track the "current project directory" in session state.']}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-python",children:`# New module: cwd_tracker.py

class CWDTracker:
    """Tracks working directory across MCP server restarts."""
    
    STATE_FILE = Path.home() / ".mcp_skill_agent" / "cwd_state.json"
    
    def __init__(self):
        self._current_project: Optional[str] = None
        self._initialized_projects: dict[str, str] = {}  # name -> path
        self._load_state()
    
    def _load_state(self):
        if self.STATE_FILE.exists():
            data = json.loads(self.STATE_FILE.read_text())
            self._current_project = data.get("current_project")
            self._initialized_projects = data.get("initialized_projects", {})
    
    def _save_state(self):
        self.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.STATE_FILE.write_text(json.dumps({
            "current_project": self._current_project,
            "initialized_projects": self._initialized_projects
        }))
    
    def get_cwd(self, fallback: str) -> str:
        """Get current working directory, with fallback."""
        if self._current_project:
            return self._current_project
        return fallback
    
    def set_project(self, name: str, path: str):
        """Record that a project was initialized."""
        self._initialized_projects[name] = path
        self._current_project = path
        self._save_state()
    
    def is_initialized(self, name: str) -> bool:
        """Check if project already exists."""
        return name in self._initialized_projects

# Global instance
cwd_tracker = CWDTracker()
`})}),`
`,e.jsx(n.p,{children:e.jsx(n.strong,{children:"Usage in file_server.py:"})}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-python",children:`from cwd_tracker import cwd_tracker

@mcp.tool()
async def execute_command(command: str, working_dir: Optional[str] = None) -> str:
    # Use tracked CWD if available
    cwd = working_dir or cwd_tracker.get_cwd(WORKSPACE_ROOT)
    
    # Track init-artifact.sh calls
    if "init-artifact.sh" in command:
        # Extract artifact name
        match = re.search(r"init-artifact\\.sh\\s+(\\S+)", command)
        if match:
            artifact_name = match.group(1)
            artifact_path = os.path.join(cwd, artifact_name)
            cwd_tracker.set_project(artifact_name, artifact_path)
    
    # ... rest of implementation
`})}),`
`,e.jsx(n.p,{children:e.jsx(n.strong,{children:"Pros:"})}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsx(n.li,{children:"Survives server restarts"}),`
`,e.jsx(n.li,{children:"Prevents duplicate project creation"}),`
`,e.jsx(n.li,{children:'Enables "return to last project" behavior'}),`
`]}),`
`,e.jsx(n.p,{children:e.jsx(n.strong,{children:"Cons:"})}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsx(n.li,{children:"More complex implementation"}),`
`,e.jsx(n.li,{children:"State file management overhead"}),`
`]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h3,{children:"Option C: Agent-Side Rules (No Code Changes)"}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Change:"})," Add strict rules to the agent's system prompt."]}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-markdown",children:`## Working Directory Rules

CRITICAL: Before running \`init-artifact.sh\`:
1. Use \`list_dir\` to check if the target directory already exists
2. If it exists with package.json, DO NOT re-run init
3. Always specify ABSOLUTE PATHS in working_dir parameter
4. NEVER rely on default working directory

Example - CORRECT:
  execute_command(
    command="bash /path/to/init-artifact.sh mcp-demo",
    working_dir="/Users/kentchiu/Documents/Github/open_memo"  # ✅ Explicit
  )

Example - WRONG:
  execute_command(
    command="bash init-artifact.sh mcp-demo"
    # ❌ Missing working_dir - will use unpredictable os.getcwd()
  )
`})}),`
`,e.jsx(n.p,{children:e.jsx(n.strong,{children:"Pros:"})}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsx(n.li,{children:"No code changes required"}),`
`,e.jsx(n.li,{children:"Immediately deployable"}),`
`]}),`
`,e.jsx(n.p,{children:e.jsx(n.strong,{children:"Cons:"})}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsx(n.li,{children:"Relies on agent following rules (not guaranteed)"}),`
`,e.jsx(n.li,{children:"Doesn't fix root cause"}),`
`]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Recommendation"}),`
`,e.jsx(n.h3,{children:"Implement Both Option A + Option B"}),`
`,e.jsxs(n.table,{children:[e.jsx(n.thead,{children:e.jsxs(n.tr,{children:[e.jsx(n.th,{children:"Phase"}),e.jsx(n.th,{children:"Action"}),e.jsx(n.th,{children:"Effort"})]})}),e.jsxs(n.tbody,{children:[e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Immediate"})}),e.jsxs(n.td,{children:["Option A: Add ",e.jsx(n.code,{children:"WORKSPACE_ROOT"})," constant"]}),e.jsx(n.td,{children:"5 min"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Short-term"})}),e.jsxs(n.td,{children:["Option B: Implement ",e.jsx(n.code,{children:"CWDTracker"})," with persistence"]}),e.jsx(n.td,{children:"2 hours"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Optional"})}),e.jsx(n.td,{children:"Option C: Add agent prompt rules"}),e.jsx(n.td,{children:"10 min"})]})]})]}),`
`,e.jsx(n.h3,{children:"Implementation Priority"}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{children:`1. file_server.py: Add WORKSPACE_ROOT fallback
2. Create cwd_tracker.py module  
3. Integrate tracker with execute_command
4. Add state file to .gitignore
5. Update agent prompt with explicit CWD rules
`})}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Expected Outcome"}),`
`,e.jsxs(n.table,{children:[e.jsx(n.thead,{children:e.jsxs(n.tr,{children:[e.jsx(n.th,{children:"Metric"}),e.jsx(n.th,{children:"Before"}),e.jsx(n.th,{children:"After (Option A)"}),e.jsx(n.th,{children:"After (A+B)"})]})}),e.jsxs(n.tbody,{children:[e.jsxs(n.tr,{children:[e.jsx(n.td,{children:"Duplicate projects"}),e.jsx(n.td,{children:"2+"}),e.jsx(n.td,{children:"0"}),e.jsx(n.td,{children:"0"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:"CWD confusion"}),e.jsx(n.td,{children:"Frequent"}),e.jsx(n.td,{children:"Rare"}),e.jsx(n.td,{children:"None"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:"Survives restart"}),e.jsx(n.td,{children:"❌"}),e.jsx(n.td,{children:"✅"}),e.jsx(n.td,{children:"✅"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:"Tracks projects"}),e.jsx(n.td,{children:"❌"}),e.jsx(n.td,{children:"❌"}),e.jsx(n.td,{children:"✅"})]})]})]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Code Diff Preview (Option A - Minimal Fix)"}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-diff",children:`# file_server.py

+# Workspace root - single source of truth for default CWD
+WORKSPACE_ROOT = os.getenv(
+    "MCP_WORKSPACE", 
+    str(Path(__file__).parent.parent)  # Fallback to repo root
+)

 @mcp.tool()
 async def execute_command(command: str, working_dir: Optional[str] = None) -> str:
     """Execute a shell command and return its output. Use with caution."""
-    cwd = working_dir or os.getcwd()
+    cwd = working_dir or WORKSPACE_ROOT
     log_tool_call("execute_command", {"command": command, "cwd": cwd})
`})}),`
`,e.jsxs(n.p,{children:["This single-line change would have prevented ",e.jsx(n.strong,{children:"all 3 duplicate project creations"})," observed in the trajectory."]})]})}function c(r={}){const{wrapper:n}=r.components||{};return n?e.jsx(n,{...r,children:e.jsx(t,{...r})}):t(r)}export{c as default,i as frontmatter};
