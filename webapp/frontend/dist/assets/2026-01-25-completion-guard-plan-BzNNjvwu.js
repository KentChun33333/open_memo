import{j as e}from"./index-DL95azgn.js";const i={title:"Task Completion Guard - Implementation Plan",date:"2026-01-25",tags:["architecture","agent","analysis"],summary:"An analysis report on agent architecture."};function s(r){const n={blockquote:"blockquote",code:"code",h1:"h1",h2:"h2",h3:"h3",hr:"hr",input:"input",li:"li",ol:"ol",p:"p",pre:"pre",strong:"strong",table:"table",tbody:"tbody",td:"td",th:"th",thead:"thead",tr:"tr",ul:"ul",...r.components};return e.jsxs(e.Fragment,{children:[e.jsx(n.h1,{children:"P1: Task Completion Guard - Implementation Plan"}),`
`,e.jsxs(n.blockquote,{children:[`
`,e.jsx(n.p,{children:"General-purpose early exit mechanism for the orchestrator loop"}),`
`]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Goal"}),`
`,e.jsxs(n.p,{children:["Detect when a task is ",e.jsx(n.strong,{children:"already complete"})," (or becomes complete) and exit gracefully, preventing:"]}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsx(n.li,{children:"Unnecessary step re-execution"}),`
`,e.jsx(n.li,{children:"MCP server restarts for redundant workers"}),`
`,e.jsx(n.li,{children:"Resource waste on completed work"}),`
`]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Design Principles"}),`
`,e.jsxs(n.table,{children:[e.jsx(n.thead,{children:e.jsxs(n.tr,{children:[e.jsx(n.th,{children:"Principle"}),e.jsx(n.th,{children:"Description"})]})}),e.jsxs(n.tbody,{children:[e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"General"})}),e.jsx(n.td,{children:"Works for ANY skill, not hardcoded to specific files"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Declarative"})}),e.jsx(n.td,{children:"Completion defined in plan, not orchestrator logic"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Multi-Signal"})}),e.jsx(n.td,{children:"Supports file-based, command-based, and LLM-based completion"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Early Exit"})}),e.jsx(n.td,{children:"Checks BEFORE each step, not just at end"})]})]})]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Architecture"}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-mermaid",children:`graph TD
    subgraph AtomicPlanner
        P[Plan Generation] --> TC[completion_criteria]
    end
    
    subgraph Orchestrator
        L[Step Loop] --> CC{CompletionChecker}
        CC -->|Complete| EXIT[Early Exit]
        CC -->|Incomplete| EXEC[Execute Step]
    end
    
    TC --> CC
`})}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Proposed Changes"}),`
`,e.jsxs(n.h3,{children:["1. [NEW] ",e.jsx(n.code,{children:"completion_checker.py"})]}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Path"}),": ",e.jsx(n.code,{children:"orchestrator/completion_checker.py"})]}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-python",children:`@dataclass
class CompletionCriteria:
    """Declarative completion conditions."""
    required_artifacts: List[str] = field(default_factory=list)
    success_signals: List[str] = field(default_factory=list)
    command_checks: List[str] = field(default_factory=list)

class CompletionChecker:
    """General-purpose task completion detector."""
    
    def __init__(self, memory_manager, workspace_root: str):
        self.memory = memory_manager
        self.workspace = workspace_root
    
    def is_complete(self, criteria: CompletionCriteria) -> Tuple[bool, str]:
        """Returns (is_complete, reason)"""
        ...
`})}),`
`,e.jsx(n.hr,{}),`
`,e.jsxs(n.h3,{children:["2. [MODIFY] ",e.jsx(n.code,{children:"structs.py"})," - Add completion_criteria to plan"]}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-diff",children:`@dataclass
class AtomicPlannerOutput:
    steps: List[SkillStep]
    reasoning: str = ""
+   completion_criteria: CompletionCriteria = None
`})}),`
`,e.jsx(n.hr,{}),`
`,e.jsxs(n.h3,{children:["3. [MODIFY] ",e.jsx(n.code,{children:"orchestrator.py"})," - Integrate guard"]}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-diff",children:`+ from .completion_checker import CompletionChecker, CompletionCriteria

  async def run(self, query: str):
      ...
+     checker = CompletionChecker(self.memory_manager, WORKSPACE_ROOT)
+     
+     # Derive criteria from plan's final step
+     criteria = self._derive_completion_criteria(plan_output)
      
      while step_idx < len(steps):
+         # EARLY EXIT: Check if already complete
+         is_done, reason = checker.is_complete(criteria)
+         if is_done:
+             logger.info(f"Task already complete: {reason}")
+             break
          
          current_step = steps[step_idx]
          ...
`})}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"CompletionChecker Logic"}),`
`,e.jsx(n.h3,{children:"Multi-Signal Detection"}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-python",children:`def is_complete(self, criteria: CompletionCriteria) -> Tuple[bool, str]:
    # 1. Check required artifacts exist
    for artifact in criteria.required_artifacts:
        path = self._resolve_path(artifact)
        if os.path.exists(path):
            return True, f"Artifact exists: {artifact}"
    
    # 2. Check success signals in memory
    for signal in criteria.success_signals:
        if self.memory.has_signal(signal):
            return True, f"Signal found: {signal}"
    
    # 3. Run command checks (e.g., "ls bundle.html")
    for cmd in criteria.command_checks:
        if self._run_check(cmd):
            return True, f"Check passed: {cmd}"
    
    return False, "Not complete"
`})}),`
`,e.jsx(n.h3,{children:"Auto-Derive from Plan"}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-python",children:`def _derive_completion_criteria(self, plan: AtomicPlannerOutput) -> CompletionCriteria:
    """Infer completion from final step's expected_artifacts."""
    if not plan.steps:
        return CompletionCriteria()
    
    final_step = plan.steps[-1]
    return CompletionCriteria(
        required_artifacts=final_step.expected_artifacts,
        success_signals=["MISSION_COMPLETE", "TASK_DONE"]
    )
`})}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Example: Web Artifact Skill"}),`
`,e.jsx(n.p,{children:'For a task "Create MCP demo app", the derived criteria:'}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-yaml",children:`completion_criteria:
  required_artifacts:
    - "mcp-demo/bundle.html"
    - "mcp-demo/dist/index.html"
  success_signals:
    - "BUNDLE_SUCCESS"
  command_checks:
    - "test -f mcp-demo/bundle.html"
`})}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Files to Modify"}),`
`,e.jsxs(n.table,{children:[e.jsx(n.thead,{children:e.jsxs(n.tr,{children:[e.jsx(n.th,{children:"File"}),e.jsx(n.th,{children:"Change"})]})}),e.jsxs(n.tbody,{children:[e.jsxs(n.tr,{children:[e.jsxs(n.td,{children:["[NEW] ",e.jsx(n.code,{children:"orchestrator/completion_checker.py"})]}),e.jsx(n.td,{children:"CompletionChecker class"})]}),e.jsxs(n.tr,{children:[e.jsxs(n.td,{children:["[MODIFY] ",e.jsx(n.code,{children:"orchestrator/structs.py"})]}),e.jsxs(n.td,{children:["Add ",e.jsx(n.code,{children:"CompletionCriteria"})," dataclass"]})]}),e.jsxs(n.tr,{children:[e.jsxs(n.td,{children:["[MODIFY] ",e.jsx(n.code,{children:"orchestrator/orchestrator.py"})]}),e.jsx(n.td,{children:"Integrate checker in loop"})]}),e.jsxs(n.tr,{children:[e.jsxs(n.td,{children:["[MODIFY] ",e.jsx(n.code,{children:"orchestrator/atomic_planner.py"})]}),e.jsx(n.td,{children:"Set criteria in plan output"})]})]})]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Verification Plan"}),`
`,e.jsx(n.h3,{children:"Test Cases"}),`
`,e.jsxs(n.ol,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Already Complete"}),": Run orchestrator when ",e.jsx(n.code,{children:"bundle.html"})," exists → should exit immediately"]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Mid-Execution Complete"}),": Step 2 creates final artifact → should skip steps 3+"]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Not Complete"}),": No artifacts → should execute all steps"]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Custom Criteria"}),": Skill-defined completion → should respect"]}),`
`]}),`
`,e.jsx(n.h3,{children:"Commands"}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-bash",children:`# Test 1: Pre-existing artifact
touch mcp-demo/bundle.html
python orchestrator.py "Build MCP demo"
# Expected: "Task already complete: Artifact exists"

# Test 2: Clean run
rm -rf mcp-demo
python orchestrator.py "Build MCP demo"
# Expected: Executes all steps
`})}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Next Steps"}),`
`,e.jsxs(n.ol,{className:"contains-task-list",children:[`
`,e.jsxs(n.li,{className:"task-list-item",children:[e.jsx(n.input,{type:"checkbox",disabled:!0})," ","Create ",e.jsx(n.code,{children:"completion_checker.py"})," with ",e.jsx(n.code,{children:"CompletionChecker"})," class"]}),`
`,e.jsxs(n.li,{className:"task-list-item",children:[e.jsx(n.input,{type:"checkbox",disabled:!0})," ","Add ",e.jsx(n.code,{children:"CompletionCriteria"})," to ",e.jsx(n.code,{children:"structs.py"})]}),`
`,e.jsxs(n.li,{className:"task-list-item",children:[e.jsx(n.input,{type:"checkbox",disabled:!0})," ","Integrate guard in ",e.jsx(n.code,{children:"orchestrator.py"})," loop"]}),`
`,e.jsxs(n.li,{className:"task-list-item",children:[e.jsx(n.input,{type:"checkbox",disabled:!0})," ","Enhance ",e.jsx(n.code,{children:"AtomicPlanner"})," to populate criteria"]}),`
`,e.jsxs(n.li,{className:"task-list-item",children:[e.jsx(n.input,{type:"checkbox",disabled:!0})," ","Test with web-artifacts-builder skill"]}),`
`]})]})}function c(r={}){const{wrapper:n}=r.components||{};return n?e.jsx(n,{...r,children:e.jsx(s,{...r})}):s(r)}export{c as default,i as frontmatter};
