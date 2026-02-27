import{j as e}from"./index-DL95azgn.js";const i={title:"Agentic Loop Issues Analysis",date:"2026-02-07",tags:["architecture","agent","analysis"],summary:"An analysis report on agent architecture."};function t(s){const n={br:"br",code:"code",h1:"h1",h2:"h2",h3:"h3",hr:"hr",input:"input",li:"li",ol:"ol",p:"p",pre:"pre",strong:"strong",table:"table",tbody:"tbody",td:"td",th:"th",thead:"thead",tr:"tr",ul:"ul",...s.components};return e.jsxs(e.Fragment,{children:[e.jsx(n.h1,{children:"Agentic Loop Issues Analysis"}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Date"}),": 2026-02-07",e.jsx(n.br,{}),`
`,e.jsx(n.strong,{children:"Context"}),": Analysis of MCP server restarts and repeated work in logs"]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Problem Summary"}),`
`,e.jsxs(n.p,{children:["After completing a task successfully (bundle.html created at 23:54:56), the MCP server restarted at 23:55:26 and the agent re-ran ",e.jsx(n.code,{children:"init-artifact.sh"}),", effectively duplicating work."]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Root Causes"}),`
`,e.jsx(n.h3,{children:"1. Ephemeral Worker Pattern"}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Location"}),": ",e.jsx(n.code,{children:"step_executor.py:61-64"})]}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-python",children:`worker = Agent(
    name=worker_name,
    instruction=subagent_instruction,
    server_names=["file-tools"] 
)
async with worker:  # Creates/destroys MCP connection per step
`})}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Impact"}),": Each step creates a new Agent with a fresh MCP connection. When the worker exits, the MCP server may restart."]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h3,{children:"2. No Overall Task Completion Check"}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Location"}),": ",e.jsx(n.code,{children:"orchestrator.py:54-195"})]}),`
`,e.jsx(n.p,{children:"The orchestrator continues to the next step after completing each step, but there's no check to see if the overall task is already done."}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-python",children:`while step_idx < len(steps):
    # Execute step...
    # No check: "Is the final artifact already created?"
    step_idx += 1
`})}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Impact"}),": Even after ",e.jsx(n.code,{children:"bundle.html"})," is created, the loop may continue and spawn new workers."]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h3,{children:"3. MCP Connection Per Worker"}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Location"}),": ",e.jsx(n.code,{children:"step_executor.py:74"})]}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-python",children:`async with worker:
    llm = await worker.attach_llm(OpenAIAugmentedLLM)
`})}),`
`,e.jsxs(n.p,{children:["The ",e.jsx(n.code,{children:"async with"})," context manager creates and destroys MCP connections for each worker."]}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Evidence from logs"}),":"]}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{children:`23:55:15 - write_file: final_bundle.html  ← Step completes
23:55:26 - Starting file-tools MCP server...  ← New worker spawns
23:55:32 - init-artifact.sh runs AGAIN  ← Worker has no memory
`})}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h3,{children:"4. State Amnesia Across Workers"}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Location"}),": ",e.jsx(n.code,{children:"step_executor.py:40-44"})]}),`
`,e.jsx(n.p,{children:"Workers are given a handover context, but it doesn't include:"}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsx(n.li,{children:"What files already exist"}),`
`,e.jsx(n.li,{children:"What commands have already been run"}),`
`,e.jsx(n.li,{children:"What the final artifact status is"}),`
`]}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-python",children:`handover = self._build_worker_context(
    current_step=current_step,
    task_input=task_input,
    retry_feedback=retry_feedback
)
`})}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Log Evidence"}),`
`,e.jsx(n.h3,{children:"Timeline (2026-02-06)"}),`
`,e.jsxs(n.table,{children:[e.jsx(n.thead,{children:e.jsxs(n.tr,{children:[e.jsx(n.th,{children:"Time"}),e.jsx(n.th,{children:"Event"}),e.jsx(n.th,{children:"Analysis"})]})}),e.jsxs(n.tbody,{children:[e.jsxs(n.tr,{children:[e.jsx(n.td,{children:"23:46:33"}),e.jsx(n.td,{children:"init-artifact.sh (1st)"}),e.jsx(n.td,{children:"Creates project in /open_memo"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:"23:47:03"}),e.jsx(n.td,{children:e.jsx(n.strong,{children:"MCP RESTART"})}),e.jsx(n.td,{children:"30s after init started"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:"23:47:07"}),e.jsx(n.td,{children:"init-artifact.sh (2nd)"}),e.jsx(n.td,{children:"Creates in /.agent/skills/... (different CWD!)"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:"23:54:56"}),e.jsx(n.td,{children:"ls bundle.html"}),e.jsx(n.td,{children:"Task DONE"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:"23:55:15"}),e.jsx(n.td,{children:"write final_bundle.html"}),e.jsx(n.td,{children:"Output saved"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:"23:55:26"}),e.jsx(n.td,{children:e.jsx(n.strong,{children:"MCP RESTART"})}),e.jsx(n.td,{children:"11s after completion"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:"23:55:32"}),e.jsx(n.td,{children:"init-artifact.sh (3rd)"}),e.jsx(n.td,{children:"Unnecessary re-init"})]})]})]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Recommended Fixes"}),`
`,e.jsx(n.h3,{children:"Priority 1: Task Completion Guard"}),`
`,e.jsx(n.p,{children:"Add early exit in orchestrator if final artifact exists:"}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-python",children:`# In orchestrator.py, before executing next step
if self._is_task_complete(task_input):
    logger.info("Final artifact exists. Mission complete.")
    break
`})}),`
`,e.jsx(n.h3,{children:"Priority 2: Reuse MCP Connections"}),`
`,e.jsx(n.p,{children:"Modify step_executor to reuse a shared MCP connection:"}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-python",children:`# Instead of per-worker connection
class StepExecutor:
    def __init__(self, ..., shared_agent=None):
        self.shared_agent = shared_agent  # Reuse across steps
`})}),`
`,e.jsx(n.h3,{children:"Priority 3: Skill-Level Guard"}),`
`,e.jsxs(n.p,{children:["Update ",e.jsx(n.code,{children:"init-artifact.sh"})," to skip if project exists:"]}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-bash",children:`if [ -d "$PROJECT_NAME" ]; then
    echo "Project '$PROJECT_NAME' already exists. Skipping init."
    exit 0
fi
`})}),`
`,e.jsx(n.h3,{children:"Priority 4: Enrich Worker Handover"}),`
`,e.jsx(n.p,{children:"Include existing artifacts in worker context:"}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-python",children:`handover = self._build_worker_context(
    current_step=current_step,
    task_input=task_input,
    retry_feedback=retry_feedback,
    existing_artifacts=self.memory_manager.get_all_artifacts()  # Add this
)
`})}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Metrics"}),`
`,e.jsxs(n.table,{children:[e.jsx(n.thead,{children:e.jsxs(n.tr,{children:[e.jsx(n.th,{children:"Metric"}),e.jsx(n.th,{children:"Observed"}),e.jsx(n.th,{children:"Optimal"})]})}),e.jsxs(n.tbody,{children:[e.jsxs(n.tr,{children:[e.jsx(n.td,{children:"MCP server restarts"}),e.jsx(n.td,{children:"6+"}),e.jsx(n.td,{children:"1"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:"init-artifact.sh runs"}),e.jsx(n.td,{children:"3"}),e.jsx(n.td,{children:"1"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:"Total time"}),e.jsx(n.td,{children:"~10 min"}),e.jsx(n.td,{children:"~3 min"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:"Redundant operations"}),e.jsx(n.td,{children:"~40%"}),e.jsx(n.td,{children:"0%"})]})]})]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Next Steps"}),`
`,e.jsxs(n.ol,{className:"contains-task-list",children:[`
`,e.jsxs(n.li,{className:"task-list-item",children:[e.jsx(n.input,{type:"checkbox",disabled:!0})," ","Implement task completion guard in orchestrator"]}),`
`,e.jsxs(n.li,{className:"task-list-item",children:[e.jsx(n.input,{type:"checkbox",disabled:!0})," ","Add project existence check to init-artifact.sh"]}),`
`,e.jsxs(n.li,{className:"task-list-item",children:[e.jsx(n.input,{type:"checkbox",disabled:!0})," ","Consider MCP connection pooling"]}),`
`,e.jsxs(n.li,{className:"task-list-item",children:[e.jsx(n.input,{type:"checkbox",disabled:!0})," ","Enrich worker handover with artifact state"]}),`
`]})]})}function c(s={}){const{wrapper:n}=s.components||{};return n?e.jsx(n,{...s,children:e.jsx(t,{...s})}):t(s)}export{c as default,i as frontmatter};
